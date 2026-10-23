"""Nashville 2026: how much of the goal difference is repeatable chance quality,
and how much is finishing / goalkeeping that may regress?

Three pieces:
1. decompose()   - split Nashville's goal difference into xG difference + three "conversion" terms
2. persistence() - year-N vs year-N+1 correlations across MLS 2013-2025 for each term
3. project()     - shrink each Nashville term by its year-to-year r -> forward-looking rates
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.fetch import NSH, SEASON

LAST_FULL_SEASON = 2025  # N+1 in persistence pairs must be a complete season


# ---------------------------------------------------------------- helpers

def _names(t: dict) -> tuple[dict, dict]:
    teams = t["teams"].set_index("team_id")["team_abbreviation"].to_dict()
    players = t["players"].set_index("player_id")["player_name"].to_dict()
    return teams, players


def team_seasons(t: dict) -> pd.DataFrame:
    """One row per team-season with the four goal-difference components (season totals)."""
    team = pd.concat([
        t["team_xg_hist"][t["team_xg_hist"].season_name != SEASON],
        t["team_xg_2026"].assign(season_name=SEASON),
    ], ignore_index=True)
    gk = (t["keeper_xg_hist_by_team"]
          .groupby(["team_id", "season_name"], as_index=False)["xgoals_gk_faced"].sum())
    df = team.merge(gk, on=["team_id", "season_name"], how="left")
    df["season"] = df.season_name.astype(int)
    # GD = xGD + finishing + opponent shooting + goalkeeping   (exact identity)
    df["finishing"] = df.goals_for - df.xgoals_for                  # our shots: goals above xG
    df["opp_shooting"] = df.xgoals_against - df.xgoals_gk_faced     # opp. xG lost to misses / blocks / poor placement
    df["goalkeeping"] = df.xgoals_gk_faced - df.goals_against       # goals prevented by our keepers
    for c in ["goals_for", "xgoals_for", "goals_against", "xgoals_against", "goal_difference",
              "xgoal_difference", "finishing", "opp_shooting", "goalkeeping", "points", "xpoints"]:
        df[f"{c}_pg"] = df[c] / df.count_games
    return df


# ---------------------------------------------------------------- 1. decomposition

def decompose(t: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    teams, _ = _names(t)
    ts = team_seasons(t)
    cur = ts[ts.season_name == SEASON].copy()
    cur.insert(0, "team", cur.team_id.map(teams))
    cur["is_nashville"] = cur.team_id == NSH
    for c, asc in [("points", False), ("xpoints", False), ("xgoal_difference_pg", False),
                   ("goals_against", True), ("xgoals_against", True), ("xgoals_for", False),
                   ("goals_for", False)]:
        cur[f"rank_{c}"] = cur[c].rank(ascending=asc, method="min").astype(int)
    cur["points_minus_xpoints"] = cur.points - cur.xpoints
    cur["rank_points_minus_xpoints"] = cur.points_minus_xpoints.rank(ascending=False, method="min").astype(int)

    n = cur[cur.is_nashville].iloc[0]
    parts = pd.DataFrame([
        ("xG difference (chance creation - chance conceded)", n.xgoal_difference, "repeatable"),
        ("Finishing: goals scored above xG", n.finishing, "conversion"),
        ("Opponent shooting: opp. xG that never became on-target danger", n.opp_shooting, "conversion"),
        ("Goalkeeping: goals prevented on shots on target", n.goalkeeping, "conversion"),
    ], columns=["component", "goals", "type"])
    parts["per_game"] = parts.goals / n.count_games
    parts["share_of_gd"] = parts.goals / n.goal_difference
    team_cols = ["team", "team_id", "is_nashville", "count_games", "points", "xpoints", "points_minus_xpoints",
                 "goals_for", "xgoals_for", "goals_against", "xgoals_against", "xgoals_gk_faced",
                 "goal_difference", "xgoal_difference", "finishing", "opp_shooting", "goalkeeping",
                 "shots_for", "shots_against"] + [c for c in cur.columns if c.endswith("_pg") or c.startswith("rank_")]
    return cur[team_cols].sort_values("points", ascending=False).round(3), parts.round(3)


# ---------------------------------------------------------------- 2. persistence

def _pairs(df: pd.DataFrame, key: str, value: str, metric: str, level: str) -> pd.DataFrame:
    df = df[["season", key, value]].dropna()
    nxt = df.assign(season=df.season - 1).rename(columns={value: "next"})
    p = df.merge(nxt, on=["season", key]).rename(columns={value: "this", key: "entity_id"})
    p = p[p.season + 1 <= LAST_FULL_SEASON]
    return p.assign(metric=metric, level=level)[["level", "metric", "entity_id", "season", "this", "next"]]


def persistence(t: dict, min_minutes: int = 900, min_shots: int = 20, min_gk_minutes: int = 1500):
    ph = t["player_xg_hist"].assign(season=lambda d: d.season_name.astype(int))
    ph = ph[(ph.minutes_played >= min_minutes) & (ph.shots >= min_shots)].copy()
    ph["xg_p90"] = ph.xgoals / ph.minutes_played * 90
    ph["g_minus_xg"] = ph.goals - ph.xgoals

    kh = t["keeper_xg_hist"].assign(season=lambda d: d.season_name.astype(int))
    kh = kh[kh.minutes_played >= min_gk_minutes].copy()
    kh["gp_p90"] = (kh.xgoals_gk_faced - kh.goals_conceded) / kh.minutes_played * 90

    ts = team_seasons(t)
    pairs = pd.concat([
        _pairs(ph, "player_id", "xg_p90", "Player xG per 90 (control)", "player"),
        _pairs(ph, "player_id", "g_minus_xg", "Player finishing (goals - xG)", "player"),
        _pairs(kh, "player_id", "gp_p90", "Keeper goals prevented per 90", "keeper"),
        _pairs(ts, "team_id", "xgoal_difference_pg", "Team xG difference per game (control)", "team"),
        _pairs(ts, "team_id", "finishing_pg", "Team finishing per game", "team"),
        _pairs(ts, "team_id", "opp_shooting_pg", "Team opponent-shooting per game", "team"),
        _pairs(ts, "team_id", "goalkeeping_pg", "Team goalkeeping per game", "team"),
    ], ignore_index=True)

    rows = []
    for (level, metric), g in pairs.groupby(["level", "metric"], sort=False):
        r = g["this"].corr(g["next"])
        lo, hi = _fisher_ci(r, len(g))
        rows.append(dict(level=level, metric=metric, n_pairs=len(g), r=r, ci_low=lo, ci_high=hi,
                         seasons=f"{g.season.min()}-{g.season.max() + 1}"))
    return pairs.round(4), pd.DataFrame(rows).round(3)


def sensitivity(t: dict) -> pd.DataFrame:
    """Does the conclusion depend on the sample filters? Re-run r under stricter thresholds."""
    rows = []
    for ms in (20, 40, 60, 80):
        _, r = persistence(t, min_shots=ms)
        x = r.set_index("metric").loc["Player finishing (goals - xG)"]
        rows.append(dict(metric="Player finishing (goals - xG)", filter=f">= {ms} shots both seasons",
                         n_pairs=x.n_pairs, r=x.r))
    for mm in (1500, 2000, 2500):
        _, r = persistence(t, min_gk_minutes=mm)
        x = r.set_index("metric").loc["Keeper goals prevented per 90"]
        rows.append(dict(metric="Keeper goals prevented per 90", filter=f">= {mm} minutes both seasons",
                         n_pairs=x.n_pairs, r=x.r))
    return pd.DataFrame(rows)


def _fisher_ci(r: float, n: int, z: float = 1.96) -> tuple[float, float]:
    f, se = np.arctanh(r), 1 / math.sqrt(n - 3)
    return float(np.tanh(f - z * se)), float(np.tanh(f + z * se))


# ---------------------------------------------------------------- 3. projection

def project(team: pd.DataFrame, parts: pd.DataFrame, rtab: pd.DataFrame) -> pd.DataFrame:
    """Regression to the mean: keep r x (this year's over-performance) of each conversion term.

    Team finishing / opponent shooting use team-level r. Goalkeeping uses keeper-level r
    (same keeper, so roster turnover in the team-level number doesn't apply).
    """
    n = team[team.is_nashville].iloc[0]
    r = rtab.set_index("metric")["r"]
    keep = {
        "finishing": r["Team finishing per game"],
        "opp_shooting": r["Team opponent-shooting per game"],
        "goalkeeping": r["Keeper goals prevented per 90"],
    }
    gf_proj = n.xgoals_for_pg + max(keep["finishing"], 0) * n.finishing_pg
    ga_proj = n.xgoals_against_pg - max(keep["opp_shooting"], 0) * n.opp_shooting_pg \
        - max(keep["goalkeeping"], 0) * n.goalkeeping_pg
    scen = pd.DataFrame([
        ("Actual 2026 results", n.goals_for_pg, n.goals_against_pg),
        ("Pure xG (all conversion luck)", n.xgoals_for_pg, n.xgoals_against_pg),
        ("Projected (regressed by year-to-year r)", gf_proj, ga_proj),
    ], columns=["scenario", "gf_per_game", "ga_per_game"])
    scen["gd_per_game"] = scen.gf_per_game - scen.ga_per_game
    probs = scen.apply(lambda s: _poisson_wdl(s.gf_per_game, s.ga_per_game), axis=1, result_type="expand")
    scen[["p_win_90", "p_draw_90", "p_loss_90"]] = probs
    scen.attrs["kept_share"] = keep
    return scen.round(3)


def _poisson_wdl(lam_for: float, lam_against: float, max_goals: int = 12) -> tuple[float, float, float]:
    """Independent-Poisson W/D/L for one 90-minute game vs an average-strength opponent."""
    k = np.arange(max_goals + 1)
    pf = np.exp(-lam_for) * lam_for ** k / np.array([math.factorial(i) for i in k])
    pa = np.exp(-lam_against) * lam_against ** k / np.array([math.factorial(i) for i in k])
    m = np.outer(pf, pa)
    return float(np.tril(m, -1).sum()), float(np.trace(m)), float(np.triu(m, 1).sum())


# ---------------------------------------------------------------- player & keeper tables

def player_table(t: dict) -> pd.DataFrame:
    _, names = _names(t)
    ph = t["player_xg_hist"]
    cur = ph[(ph.season_name == SEASON) & ph.team_id.str.contains(NSH)].copy()
    pens = t["player_xg_2026_pens"].set_index("player_id")
    cur["pen_goals"] = cur.player_id.map(pens.goals).fillna(0)
    cur["pen_xg"] = cur.player_id.map(pens.xgoals).fillna(0)
    cur["np_goals"] = cur.goals - cur.pen_goals
    cur["np_xg"] = cur.xgoals - cur.pen_xg
    cur["g_minus_xg"] = cur.goals - cur.xgoals
    cur["np_g_minus_xg"] = cur.np_goals - cur.np_xg
    cur["xg_p90"] = cur.xgoals / cur.minutes_played * 90
    prior = ph[(ph.season_name.astype(int) < int(SEASON))].groupby("player_id").agg(
        prior_seasons=("season_name", "nunique"), prior_goals=("goals", "sum"),
        prior_xg=("xgoals", "sum"), prior_shots=("shots", "sum"))
    cur = cur.join(prior, on="player_id")
    cur["prior_g_minus_xg"] = cur.prior_goals - cur.prior_xg
    cur["prior_g_minus_xg_per_100_shots"] = cur.prior_g_minus_xg / cur.prior_shots * 100
    cur.insert(0, "player", cur.player_id.map(names))
    cols = ["player", "player_id", "general_position", "minutes_played", "shots", "goals", "xgoals",
            "g_minus_xg", "pen_goals", "pen_xg", "np_goals", "np_xg", "np_g_minus_xg", "xg_p90",
            "primary_assists", "xassists", "prior_seasons", "prior_goals", "prior_xg",
            "prior_g_minus_xg", "prior_g_minus_xg_per_100_shots"]
    return cur[cols].sort_values("goals", ascending=False).round(3)


def player_history(t: dict, player_ids: list[str]) -> pd.DataFrame:
    _, names = _names(t)
    ph = t["player_xg_hist"]
    h = ph[ph.player_id.isin(player_ids)].copy()
    h.insert(0, "player", h.player_id.map(names))
    h["g_minus_xg"] = h.goals - h.xgoals
    return h[["player", "season_name", "team_id", "minutes_played", "shots", "goals", "xgoals", "g_minus_xg"]] \
        .sort_values(["player", "season_name"]).round(3)


def keeper_table(t: dict, min_minutes: int = 900) -> pd.DataFrame:
    teams, names = _names(t)
    kh = t["keeper_xg_hist_by_team"]
    k = kh[(kh.season_name == SEASON)].copy()
    k["goals_prevented"] = k.xgoals_gk_faced - k.goals_conceded
    k["gp_p90"] = k.goals_prevented / k.minutes_played * 90
    k["save_pct"] = k.saves / k.shots_faced
    k.insert(0, "keeper", k.player_id.map(names))
    k.insert(1, "team", k.team_id.map(teams))
    k["is_nashville"] = k.team_id == NSH
    qual = k[k.minutes_played >= min_minutes].copy()
    qual["rank_goals_prevented"] = qual.goals_prevented.rank(ascending=False, method="min").astype(int)
    k = k.merge(qual[["player_id", "team_id", "rank_goals_prevented"]], on=["player_id", "team_id"], how="left")
    cols = ["keeper", "team", "player_id", "team_id", "is_nashville", "minutes_played", "shots_faced", "saves",
            "save_pct", "goals_conceded", "xgoals_gk_faced", "goals_prevented", "gp_p90", "rank_goals_prevented"]
    return k[cols].sort_values("goals_prevented", ascending=False).round(3)
