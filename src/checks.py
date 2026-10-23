"""Sanity checks. Every number in the README should trace back to something asserted here.

Run on its own with `python -m src.checks`; src.run calls it before building outputs and
stops if anything fails.
"""
from __future__ import annotations

import pandas as pd

from src.fetch import NSH, SEASON, fetch

# Public reference: MLS standings table for Nashville SC after 30 games (week of 2026-10-21),
# found via web search on 2026-10-23. Update these when you rerun after Decision Day.
PUBLIC = dict(games=30, wins=20, draws=7, losses=3, points=67, goals_for=64, goals_against=23)


def _nsh_scoreboard(games: pd.DataFrame) -> dict:
    g = games[((games.home_team_id == NSH) | (games.away_team_id == NSH)) & (games.status == "FullTime")]
    home = g.home_team_id == NSH
    gf = g.home_score.where(home, g.away_score)
    ga = g.away_score.where(home, g.home_score)
    w, d = int((gf > ga).sum()), int((gf == ga).sum())
    return dict(games=len(g), wins=w, draws=d, losses=len(g) - w - d, points=3 * w + d,
                goals_for=int(gf.sum()), goals_against=int(ga.sum()))


def run_checks(t: dict | None = None, verbose: bool = True) -> list[str]:
    t = t or fetch()
    notes, fails = [], []

    def check(ok: bool, msg: str):
        (notes if ok else fails).append(("PASS " if ok else "FAIL ") + msg)

    team = t["team_xg_2026"].set_index("team_id").loc[NSH]
    team = team.apply(lambda v: int(v) if isinstance(v, float) and v.is_integer() else v)
    sb = _nsh_scoreboard(t["games_2026"])

    # 1. ASA game results vs public standings
    for k, v in PUBLIC.items():
        check(sb[k] == v, f"scoreboard {k} = {sb[k]} (public table: {v})")
    check(team.points == sb["points"], f"ASA team points {team.points} = scoreboard points {sb['points']}")
    check(team.count_games == sb["games"], f"ASA team games {team.count_games} = scoreboard games {sb['games']}")

    # 2. ASA's xG tables count shot goals only, so own goals drop out. Difference must be small,
    #    and goal difference must still match.
    og_for, og_against = sb["goals_for"] - team.goals_for, sb["goals_against"] - team.goals_against
    check(0 <= og_for <= 3 and 0 <= og_against <= 3,
          f"own goals implied: {og_for} for, {og_against} against (scoreboard minus ASA shot goals)")
    check(team.goal_difference == sb["goals_for"] - sb["goals_against"] - (og_for - og_against),
          f"ASA goal difference {team.goal_difference} reconciles with scoreboard after own goals")

    # 3. Players add up to the team
    ph = t["player_xg_hist"]
    nshp = ph[(ph.season_name == SEASON) & ph.team_id.str.contains(NSH)]
    multi = nshp.team_id.str.contains(r"\|").sum()
    check(multi == 0, f"no Nashville 2026 player split across clubs ({multi} found)")
    check(nshp.goals.sum() == team.goals_for, f"sum of player goals {nshp.goals.sum()} = team goals {team.goals_for}")
    xg_gap = nshp.xgoals.sum() / team.xgoals_for - 1
    # ASA's team xG is not a plain sum of player shot xG (it is slightly lower), so allow 5%.
    check(abs(xg_gap) < 0.05, f"sum of player xG {nshp.xgoals.sum():.2f} within 5% of team xG "
                              f"{team.xgoals_for:.2f} ({xg_gap:+.1%})")

    # 4. Keepers add up to the team, every team-season
    kt = t["keeper_xg_hist_by_team"].groupby(["team_id", "season_name"], as_index=False).goals_conceded.sum()
    th = t["team_xg_hist"].merge(kt, on=["team_id", "season_name"], how="left")
    bad = (th.goals_against != th.goals_conceded).sum()
    check(bad == 0, f"keeper goals conceded = team goals against in all {len(th)} team-seasons ({bad} mismatches)")

    # 5. Historical table's 2026 row matches the standalone 2026 pull
    h26 = t["team_xg_hist"].query("season_name == @SEASON").set_index("team_id").loc[NSH]
    check(abs(h26.xgoals_for - team.xgoals_for) < 1e-6 and h26.goals_for == team.goals_for,
          "2026 row in multi-season pull matches single-season pull")

    # 6. Names resolve
    missing = (~ph.player_id.isin(t["players"].player_id)).sum()
    check(missing == 0, f"all {len(ph)} player-season rows have a name ({missing} missing)")

    # 7. Season status
    remaining = 34 - sb["games"]
    notes.append(f"INFO Nashville have played {sb['games']} of 34; {remaining} regular-season games not yet in data")

    if verbose:
        print("\n".join(notes + fails))
    if fails:
        raise AssertionError(f"{len(fails)} sanity check(s) failed:\n" + "\n".join(fails))
    return notes


if __name__ == "__main__":
    run_checks()
