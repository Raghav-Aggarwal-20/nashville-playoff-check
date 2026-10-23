"""Sofascore context section for the README, built from data/sofascore_manual.csv.

Context only: nothing here feeds the decomposition, persistence or projection. The section
is written between two markers in README.md on every run, so its numbers always come from
the CSV (and from ASA's cached data where an ASA figure is set beside a Sofascore one).
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.fetch import DATA, NSH, ROOT

CSV = DATA / "sofascore_manual.csv"
README = ROOT / "README.md"
START, END = "<!-- sofascore:start -->", "<!-- sofascore:end -->"


def _lookup(df: pd.DataFrame):
    vals = df.set_index(["entity", "metric"]).value

    def get(entity: str, metric: str) -> float:
        return float(vals.loc[(entity, metric)])
    return get


def _n(x: float, dp: int = 2) -> str:
    """Integers print without decimals; everything else to `dp` places."""
    return f"{x:.0f}" if float(x).is_integer() else f"{x:.{dp}f}"


def section(t: dict, keepers: pd.DataFrame) -> str:
    if not CSV.exists():
        return f"{START}\n_No `{CSV.name}` found: Sofascore context omitted._\n{END}"
    df = pd.read_csv(CSV)
    s = _lookup(df)
    captured = df.captured.max()

    sch = keepers[keepers.keeper == "Brian Schwake"].iloc[0]
    pens = t["team_xg_2026_pens"].set_index("team_id").loc[NSH]
    pen_xg_each = pens.xgoals_against / pens.shots_against
    faced, saved = s("Brian Schwake", "penalties_faced"), s("Brian Schwake", "penalties_saved")
    pen_value = pen_xg_each * faced - (faced - saved)

    sur_g, sur_xg, sur_xgot = s("Sam Surridge", "goals"), s("Sam Surridge", "xg"), s("Sam Surridge", "xgot")
    muk_g, muk_xg, muk_xgot = s("Hany Mukhtar", "goals"), s("Hany Mukhtar", "xg"), s("Hany Mukhtar", "xgot")
    starts = s("Brian Schwake", "matches_started")
    per_start = (f", exactly 90 x his {_n(starts)} starts"
                 if s("Brian Schwake", "minutes") == 90 * starts else "")
    run_outs = df[(df.entity == "Brian Schwake") & (df.metric == "successful_run_outs")].iloc[0]
    run_outs_of = re.search(r"of (\d+)", run_outs.unit)

    lines = [
        START,
        "## Second opinion: Sofascore",
        "",
        f"*Sofascore context, hand-entered from Sofascore's MLS 2026 pages on {captured} "
        f"(`data/{CSV.name}`). None of it enters any calculation above. This section is regenerated "
        "from that file on every run.*",
        "",
        f"- **Two models agree on Schwake.** ASA has him at +{sch.goals_prevented:.1f} goals prevented; "
        f"Sofascore at +{_n(s('Brian Schwake', 'goals_prevented'))}. Different models, same verdict: elite "
        "shot-stopping this season.",
        f"- **Penalties.** He saved {_n(saved)} of {_n(faced)}. ASA values a penalty at {pen_xg_each:.2f} xG "
        f"({pens.xgoals_against:.2f} xG on the {pens.shots_against:.0f} penalties Nashville faced), so "
        f"{_n(saved)} saves from {_n(faced)} is worth about +{pen_value:.1f} goals against an average keeper "
        f"({pen_value / sch.goals_prevented:.0%} of his +{sch.goals_prevented:.1f} ASA total). Penalty saves are the least repeatable part of a keeper's record: a handful of kicks, mostly decided "
        "by a guess.",
        f"- **Errors.** Nashville made {_n(s('Nashville SC', 'errors_leading_to_shot'))} errors that led to a "
        f"shot and {_n(s('Nashville SC', 'errors_leading_to_goal'))} that led to a goal. That many errors "
        "without a goal conceded is not something to plan on repeating.",
        f"- **Surridge: {_n(sur_g)} goals vs {_n(sur_xgot)} xGOT.** xGOT (expected goals on target) adds "
        f"shot placement to xG. His {_n(sur_xg)} xG becomes {_n(sur_xgot)} once placement is counted, "
        f"leaving only {sur_g - sur_xgot:+.1f} unexplained. His goals come from where he puts the ball, not "
        "from keeper mistakes.",
        f"- **Mukhtar: {_n(muk_g)} goals vs {_n(muk_xgot)} xGOT,** about {muk_g - muk_xgot:+.1f} beyond "
        f"placement (his placement adds only {muk_xgot - muk_xg:+.1f} to {_n(muk_xg)} xG). Goals above xGOT "
        "are shots keepers should have saved, the part most likely to even out.",
        f"- **Schwake beyond shot-stopping:** {_n(s('Brian Schwake', 'high_claims'))} high claims, "
        f"{_n(s('Brian Schwake', 'crosses_not_claimed'))} crosses not claimed, "
        f"{_n(s('Brian Schwake', 'successful_run_outs'))}/{run_outs_of.group(1) if run_outs_of else '?'} "
        "successful run-outs. That is value goals prevented doesn't capture: it only measures shots on "
        "target, not the shots that never happen because he took the cross.",
        f"- **Woodwork.** Nashville hit the post or bar {_n(s('Nashville SC', 'hit_woodwork'))} times. xG "
        "already counts those chances, and they went in the books as misses, so the finishing term "
        "(goals minus xG) already reflects them.",
        "",
        "Where the two sources differ, it is definitional:",
        "",
        f"- **Goals conceded:** Sofascore has Schwake on {_n(s('Brian Schwake', 'goals_conceded'))}; ASA on "
        f"{sch.goals_conceded:.0f}. Sofascore matches the scoreboard, which includes the one own goal; ASA's xG "
        "tables count shot goals only.",
        f"- **Minutes:** Sofascore {_n(s('Brian Schwake', 'minutes'))}{per_start}; "
        f"ASA {sch.minutes_played:.0f}, which includes stoppage time.",
        END,
    ]
    return "\n".join(lines)


def write_into_readme(text: str) -> None:
    readme = README.read_text()
    if START not in readme:
        raise ValueError(f"README.md is missing the {START} marker")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    README.write_text(pattern.sub(lambda _: text, readme))
