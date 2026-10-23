"""Three memo charts. Style: gray context, one accent (blue = repeatable, orange = conversion)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, CONTEXT = "#2a78d6", "#eb6834", "#c3c2b7"

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10, "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": AXIS,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _title(fig, title: str, subtitle: str, source: str):
    fig.text(0.0, 1.05, title, fontsize=14, fontweight="bold", ha="left", transform=fig.transFigure)
    fig.text(0.0, 1.01, subtitle, fontsize=10, color=INK2, ha="left", transform=fig.transFigure)
    fig.text(0.0, -0.06, source, fontsize=8, color=MUTED, ha="left", transform=fig.transFigure)


def waterfall(parts: pd.DataFrame, team_row: pd.Series, path: Path, as_of: str):
    labels = ["xG difference", "Finishing", "Opponent\nshooting", "Goalkeeping", "Actual goal\ndifference"]
    vals = parts.goals.tolist()
    bottoms = np.r_[0, np.cumsum(vals)[:-1]]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for i, (b, v, kind) in enumerate(zip(bottoms, vals, parts.type)):
        ax.bar(i, v, bottom=b, width=0.62, color=BLUE if kind == "repeatable" else ORANGE, zorder=3)
        ax.text(i, b + v + 0.8, f"+{v:.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.text(i, b + v / 2, f"{v / team_row.goal_difference:.0%}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        if i < len(vals) - 1:
            ax.plot([i + 0.31, i + 0.69], [b + v, b + v], color=AXIS, lw=0.8, zorder=2)
    total = team_row.goal_difference
    ax.bar(4, total, width=0.62, color=INK2, zorder=3)
    ax.text(4, total + 0.8, f"+{total:.0f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_xticks(range(5), labels)
    ax.tick_params(axis="x", colors=INK2, length=0)
    ax.set_ylabel("Goals (2026, through %d games)" % team_row.count_games)
    ax.set_ylim(0, total * 1.12)
    ax.grid(axis="x", visible=False)
    ax.text(0.0, total * 1.08, "■ repeatable (chance quality)", color=BLUE, fontsize=9, ha="left")
    ax.text(1.9, total * 1.08, "■ conversion (repeats weakly at best year to year)", color=ORANGE, fontsize=9, ha="left")
    _title(fig, f"Only about a quarter of Nashville's +{total:.0f} goal difference comes from chance quality",
           f"Goal difference split into xG difference plus three conversion terms (through {as_of})",
           "Source: American Soccer Analysis (itscalledsoccer). Own goals (1 for, 1 against) excluded by ASA. "
           "Opponent shooting = opp. xG - keeper xG faced; goalkeeping = keeper xG faced - goals conceded.")
    fig.savefig(path)
    plt.close(fig)


def persistence_panels(pairs: pd.DataFrame, rtab: pd.DataFrame, marks: dict, path: Path):
    """marks: metric -> list of (label, 2026 value) to show as vertical reference lines."""
    metrics = [("Player xG per 90 (control)", "xG per 90, year N", "xG per 90, year N+1"),
               ("Player finishing (goals - xG)", "Goals minus xG, year N", "Goals minus xG, year N+1"),
               ("Keeper goals prevented per 90", "Goals prevented per 90, year N", "Goals prevented per 90, year N+1")]
    r = rtab.set_index("metric")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
    for ax, (m, xl, yl) in zip(axes, metrics):
        p = pairs[pairs.metric == m]
        ax.scatter(p["this"], p["next"], s=9, color=CONTEXT, alpha=0.55, lw=0, zorder=2)
        slope, icpt = np.polyfit(p["this"], p["next"], 1)
        xs = np.linspace(p["this"].quantile(0.005), p["this"].quantile(0.995), 50)
        color = BLUE if "control" in m else ORANGE
        ax.plot(xs, icpt + slope * xs, color=color, lw=2, zorder=4)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        row = r.loc[m]
        ax.set_title(f"{m.replace(' (control)', '')}\nr = {row.r:.2f}  (n = {row.n_pairs:,} pairs)",
                     loc="left", fontsize=10.5, fontweight="bold", color=color)
        lo, hi = ax.get_ylim()
        for j, (lab, v) in enumerate(marks.get(m, [])):
            ax.axvline(v, color=INK2, lw=0.8, zorder=3)
            ax.text(v, hi - (hi - lo) * (0.06 + 0.08 * j), f" {lab} 2026", fontsize=8.5, color=INK, ha="left")
    _title(fig, "Creating chances repeats year to year. Finishing doesn't, and shot-stopping only a little",
           "Each dot is a player or keeper in consecutive MLS seasons, 2013-2025 (players: 900+ min and 20+ shots "
           "both seasons; keepers: 1,500+ min)",
           "Source: American Soccer Analysis. Line = least-squares fit. Vertical lines mark Nashville players' 2026 values.")
    fig.subplots_adjust(wspace=0.28)
    fig.savefig(path)
    plt.close(fig)


def league_context(team: pd.DataFrame, path: Path, as_of: str):
    fig, ax = plt.subplots(figsize=(7.5, 5.6))
    other = team[~team.is_nashville]
    n = team[team.is_nashville].iloc[0]
    ax.scatter(other.xpoints, other.points, s=40, color=CONTEXT, lw=0, zorder=3)
    ax.scatter(n.xpoints, n.points, s=90, color=BLUE, edgecolor=SURFACE, lw=2, zorder=4)
    lo = min(team.xpoints.min(), team.points.min()) - 3
    hi = max(team.xpoints.max(), team.points.max()) + 3
    ax.plot([lo, hi], [lo, hi], color=AXIS, lw=1, zorder=2)
    ax.text(hi - 1, hi - 3.5, "points = xPoints", color=MUTED, fontsize=8.5, ha="right", rotation=0)
    rk = int(n.rank_points_minus_xpoints)
    most = "most in MLS" if rk == 1 else f"{_ordinal(rk)}-most in MLS"
    ax.annotate(f"Nashville\n{n.points:.0f} pts from {n.xpoints:.1f} xPts\n(+{n.points_minus_xpoints:.1f}, {most})",
                (n.xpoints, n.points), xytext=(n.xpoints - 17, n.points - 4), fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    for _, row in team.nlargest(4, "xpoints").iterrows():
        if not row.is_nashville:
            ax.text(row.xpoints + 0.6, row.points - 0.4, row.team, fontsize=8, color=INK2, va="top")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Expected points (xPoints, from shot xG)")
    ax.set_ylabel("Actual points")
    _title(fig, f"{_ordinal(int(n.rank_points))} on points, {_ordinal(int(n.rank_xpoints))} on expected points",
           f"MLS 2026 regular season, all 30 teams (through {as_of})",
           "Source: American Soccer Analysis xPoints: each match simulated from both teams' shot xG.")
    fig.savefig(path)
    plt.close(fig)
