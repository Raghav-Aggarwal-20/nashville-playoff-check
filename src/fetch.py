"""Pull everything the analysis needs from American Soccer Analysis and cache it in data/.

Cached files are reused on later runs; pass --refresh (or refresh=True) to re-pull.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LEAGUE = "mls"
SEASON = "2026"
HISTORY = [str(y) for y in range(2013, 2027)]  # ASA's MLS xG starts in 2013
STAGE = "Regular Season"
API = "https://app.americansocceranalysis.com/api/v1"
NSH = "vzqoOgNqap"  # Nashville SC team_id in ASA


def _flatten(v):
    if isinstance(v, (list, tuple)) and all(isinstance(x, str) for x in v):
        return "|".join(v)
    if isinstance(v, (list, tuple, dict)):
        return json.dumps(v, default=str)
    return v


def _clean(df) -> pd.DataFrame:
    """polars -> pandas, flattening ASA's mixed 'object' columns.

    ASA returns some numeric columns as objects, and team_id as a list for players
    who moved clubs mid-season. Lists become 'id1|id2'; everything else is coerced
    to numeric where possible.
    """
    out = df.to_pandas()
    for col in out.columns:
        if out[col].dtype != object:
            continue
        nested = out[col].map(lambda v: isinstance(v, (list, tuple, dict))).any()
        if nested:
            out[col] = out[col].map(_flatten)
        else:
            converted = pd.to_numeric(out[col], errors="coerce")
            if converted.notna().sum() == out[col].notna().sum():
                out[col] = converted
    return out


def _base(**kw) -> dict:
    return dict(leagues=LEAGUE, stage_name=STAGE, **kw)


def _players_direct() -> pd.DataFrame:
    """Player id -> name lookup straight from the ASA REST API.

    itscalledsoccer 2.3.0's get_players() fails to vstack pages whose columns differ,
    so we call the same endpoint the package wraps and keep only what we need.
    """
    r = requests.get(f"{API}/{LEAGUE}/players", timeout=60)
    r.raise_for_status()
    return pd.DataFrame(r.json())[["player_id", "player_name", "primary_general_position"]]


# name -> function(asa client) returning a DataFrame (polars from the client, or pandas)
PULLS = {
    "teams": lambda asa: asa.get_teams(leagues=LEAGUE),
    "players": lambda asa: _players_direct(),
    "games_2026": lambda asa: asa.get_games(leagues=LEAGUE, season_name=SEASON),
    "team_xg_2026": lambda asa: asa.get_team_xgoals(**_base(season_name=SEASON)),
    "team_xg_2026_pens": lambda asa: asa.get_team_xgoals(**_base(season_name=SEASON, shot_pattern="Penalty")),
    "player_xg_2026_pens": lambda asa: asa.get_player_xgoals(
        **_base(season_name=SEASON, shot_pattern="Penalty", team_ids=NSH)),
    "team_xg_hist": lambda asa: asa.get_team_xgoals(**_base(season_name=HISTORY, split_by_seasons=True)),
    "player_xg_hist": lambda asa: asa.get_player_xgoals(**_base(season_name=HISTORY, split_by_seasons=True)),
    "keeper_xg_hist": lambda asa: asa.get_goalkeeper_xgoals(**_base(season_name=HISTORY, split_by_seasons=True)),
}


def fetch(refresh: bool = False) -> dict[str, pd.DataFrame]:
    DATA.mkdir(exist_ok=True)
    tables, asa = {}, None
    meta_path = DATA / "pull_log.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for name, pull in PULLS.items():
        path = DATA / f"{name}.parquet"
        if path.exists() and not refresh:
            tables[name] = pd.read_parquet(path)
            continue
        if asa is None:
            from itscalledsoccer.client import AmericanSoccerAnalysis
            asa = AmericanSoccerAnalysis()
        print(f"  pulling {name} from ASA ...")
        df = pull(asa)
        df = df if isinstance(df, pd.DataFrame) else _clean(df)
        df.to_parquet(path, index=False)
        meta[name] = {"pulled_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "rows": len(df)}
        tables[name] = df
    meta_path.write_text(json.dumps(meta, indent=2))
    return tables


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-pull from ASA instead of using data/ cache")
    t = fetch(refresh=ap.parse_args().refresh)
    for k, v in t.items():
        print(f"{k:22s} {len(v):>6} rows")
