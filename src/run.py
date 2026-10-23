"""One command: python -m src.run [--refresh]

fetch (cached) -> sanity checks (stop on failure) -> analysis -> output/ CSVs, charts, summary.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src import analysis, charts, sofascore
from src.checks import run_checks
from src.fetch import DATA, ROOT, fetch

OUT = ROOT / "output"
SOFASCORE = DATA / "sofascore_manual.csv"
SPOTLIGHT = ["Sam Surridge", "Hany Mukhtar"]


def main(refresh: bool = False):
    OUT.mkdir(exist_ok=True)
    print("1/5 fetch")
    t = fetch(refresh=refresh)
    as_of = pd.to_datetime(t["games_2026"].date_time_utc.str.replace(" UTC", "")).max().strftime("%Y-%m-%d")

    print("2/5 sanity checks")
    check_notes = run_checks(t, verbose=False)

    print("3/5 analysis")
    team, parts = analysis.decompose(t)
    pairs, rtab = analysis.persistence(t)
    sens = analysis.sensitivity(t)
    proj = analysis.project(team, parts, rtab)
    players = analysis.player_table(t)
    keepers = analysis.keeper_table(t)
    hist = analysis.player_history(t, players[players.player.isin(SPOTLIGHT)].player_id.tolist())

    print("4/5 CSVs")
    _, names = analysis._names(t)
    team.to_csv(OUT / "team_2026.csv", index=False)
    parts.to_csv(OUT / "nashville_gd_decomposition.csv", index=False)
    players.to_csv(OUT / "players_2026.csv", index=False)
    hist.to_csv(OUT / "spotlight_player_history.csv", index=False)
    keepers.to_csv(OUT / "keepers_2026.csv", index=False)
    pairs.assign(entity=lambda d: d.entity_id.map(names).fillna(d.entity_id.map(
        t["teams"].set_index("team_id").team_abbreviation))).to_csv(OUT / "persistence_pairs.csv", index=False)
    rtab.to_csv(OUT / "persistence_summary.csv", index=False)
    sens.to_csv(OUT / "persistence_sensitivity.csv", index=False)
    proj.to_csv(OUT / "projection.csv", index=False)

    print("5/5 charts + summary")
    n = team[team.is_nashville].iloc[0]
    charts.waterfall(parts, n, OUT / "01_goal_difference_waterfall.png", as_of)
    sp = players.set_index("player")
    sk = keepers[keepers.is_nashville].iloc[0]
    marks = {
        "Player xG per 90 (control)": [(p.split()[-1], sp.loc[p, "xg_p90"]) for p in SPOTLIGHT],
        "Player finishing (goals - xG)": [(p.split()[-1], sp.loc[p, "g_minus_xg"]) for p in SPOTLIGHT],
        "Keeper goals prevented per 90": [(sk.keeper.split()[-1], sk.gp_p90)],
    }
    charts.persistence_panels(pairs, rtab, marks, OUT / "02_does_it_repeat.png")
    charts.league_context(team, OUT / "03_league_context.png", as_of)

    key = _key_numbers(n, parts, rtab, proj, sp, sk, as_of)
    (OUT / "key_numbers.json").write_text(json.dumps(key, indent=2))
    (OUT / "summary.md").write_text(_summary(key, check_notes, rtab, proj))
    sofascore.write_into_readme(sofascore.section(t, keepers))
    print("\n" + (OUT / "summary.md").read_text())


def _key_numbers(n, parts, rtab, proj, sp, sk, as_of) -> dict:
    r = rtab.set_index("metric").r
    p = proj.set_index("scenario")
    conv = parts[parts.type == "conversion"].goals.sum()
    return {
        "as_of": as_of, "games": int(n.count_games),
        "points": int(n.points), "xpoints": round(float(n.xpoints), 1), "rank_xpoints": int(n.rank_xpoints),
        "goal_difference": int(n.goal_difference), "xg_difference": round(float(n.xgoal_difference), 1),
        "conversion_goals": round(float(conv), 1), "conversion_share": round(float(conv / n.goal_difference), 3),
        "components": {row.component: round(float(row.goals), 1) for row in parts.itertuples()},
        "rank_goals_against": int(n.rank_goals_against), "rank_xgoals_against": int(n.rank_xgoals_against),
        "rank_xgd_pg": int(n.rank_xgoal_difference_pg),
        "r_player_xg90": round(float(r["Player xG per 90 (control)"]), 2),
        "r_player_finishing": round(float(r["Player finishing (goals - xG)"]), 2),
        "r_keeper_gp90": round(float(r["Keeper goals prevented per 90"]), 2),
        "r_team_finishing": round(float(r["Team finishing per game"]), 2),
        "r_team_opp_shooting": round(float(r["Team opponent-shooting per game"]), 2),
        "gd_pg_actual": round(float(p.loc["Actual 2026 results", "gd_per_game"]), 2),
        "gd_pg_projected": round(float(p.loc["Projected (regressed by year-to-year r)", "gd_per_game"]), 2),
        "p_win_90_actual": round(float(p.loc["Actual 2026 results", "p_win_90"]), 2),
        "p_win_90_projected": round(float(p.loc["Projected (regressed by year-to-year r)", "p_win_90"]), 2),
        "players": {pl: {k: round(float(sp.loc[pl, k]), 2) for k in
                         ["goals", "xgoals", "pen_goals", "np_goals", "np_xg", "g_minus_xg", "prior_g_minus_xg"]}
                    for pl in SPOTLIGHT},
        "keeper": {"name": sk.keeper, "goals_conceded": int(sk.goals_conceded),
                   "xg_faced": round(float(sk.xgoals_gk_faced), 1),
                   "goals_prevented": round(float(sk.goals_prevented), 1),
                   "rank": int(sk.rank_goals_prevented)},
    }


def _summary(k: dict, checks: list[str], rtab: pd.DataFrame, proj: pd.DataFrame) -> str:
    lines = [f"# Auto-generated summary (data through {k['as_of']}, {k['games']} games)", "",
             f"- Points {k['points']} vs xPoints {k['xpoints']} (rank {k['rank_xpoints']} on xPoints)",
             f"- Goal difference +{k['goal_difference']} vs xG difference +{k['xg_difference']}; "
             f"{k['conversion_share']:.0%} of GD from conversion terms"]
    lines += [f"  - {c}: {v:+.1f}" for c, v in k["components"].items()]
    lines += ["", "## Persistence (year N vs N+1)", "", rtab.to_markdown(index=False), "",
              "## Projection", "", proj.to_markdown(index=False), "",
              "## Sanity checks", ""] + [f"- {c}" for c in checks]
    lines += ["", "## Sofascore context (manual entry, not used in any calculation)", ""]
    if SOFASCORE.exists():
        lines.append(pd.read_csv(SOFASCORE).to_markdown(index=False))
    else:
        lines.append(f"_{SOFASCORE.name} not found: copy data/sofascore_manual.template.csv and fill it in._")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-pull from ASA instead of using data/ cache")
    main(refresh=ap.parse_args().refresh)
