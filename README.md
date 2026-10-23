# Nashville playoff check: how much of 2026 will travel?

**The question:** Nashville have the best record and the fewest goals conceded in MLS. Before the knockout rounds, how much of that comes from chance creation and chance prevention we can rely on, and how much from finishing and goalkeeping that may cool off?

**Answer:** About a quarter (24%). Nashville's +41 goal difference rests on a +10.0 xG difference. The other +31.0 came from finishing (+11.2), opponents missing or misplacing their shots (+7.7) and goalkeeping (+12.1: Brian Schwake +10.9, Joe Willis +1.2). Across 13 MLS seasons, finishing over xG has not carried into the next year (r = 0.04) and shot-stopping only weakly (r = 0.23). Nashville should be planned for as a good team, 5th in MLS on xG difference per game, not the dominant one the table shows. On regressed rates, they win about 48% of 90-minute games against an average opponent, not the 69% their actual 2026 rates imply.

*Data through 2026-10-21: Nashville have played 30 of 34 regular-season games. Rerun after Decision Day (Nov 7) with `python -m src.run --refresh`.*

![Goal difference waterfall](output/01_goal_difference_waterfall.png)

## Key numbers

| | Nashville 2026 | MLS rank |
|---|---|---|
| Points / expected points (xPoints) | 67 / 46.6 (+20.4) | 1st / 8th |
| Goals for / xG for | 63 / 51.8 | 2nd / 12th |
| Goals against / xG against | 22 / 41.8 | 1st / 4th |
| xG difference per game | +0.33 | 5th (Vancouver +1.03) |
| Schwake goals prevented | 22 conceded on 32.9 keeper xG faced = +10.9 | 2nd (Turner, NE, +12.4) |
| Team goalkeeping (Schwake + Willis) | 22 conceded on 34.1 keeper xG faced = +12.1 | |

Goals here are ASA shot goals, which leave out own goals (1 for, 1 against). The scoreboard (64 GF, 23 GA) gives the same +41 goal difference.

## Does it repeat?

![Year-to-year persistence](output/02_does_it_repeat.png)

| Year N vs year N+1, MLS 2013-2025 | r | 95% CI | pairs |
|---|---|---|---|
| Player xG per 90 (control) | 0.80 | 0.78 to 0.82 | 1,045 |
| Player finishing (goals minus xG) | 0.04 | -0.03 to 0.10 | 1,045 |
| Keeper goals prevented per 90 | 0.23 | 0.09 to 0.37 | 179 |
| Team xG difference per game (control) | 0.40 | 0.30 to 0.49 | 285 |
| Team finishing per game | 0.04 | -0.08 to 0.16 | 285 |
| Team opponent-shooting per game | 0.08 | -0.04 to 0.19 | 285 |

The finishing result holds at stricter filters: r stays between -0.01 and 0.11 when the minimum rises from 20 to 80 shots in both seasons. Keeper r drops to 0.09 for keepers with 2,500+ minutes, so 0.23 is the generous figure for Schwake. Both are in `output/persistence_sensitivity.csv`.

### Three players to check

- **Sam Surridge:** 17 goals from 15.7 xG. Three of those goals are penalties, so his non-penalty line is 14 from 13.4. He is finishing about at expectation. His value is shot volume: 0.67 xG per 90, the highest on the team. That is the repeatable part. In his previous three MLS seasons he finished 1.0 goal *below* xG on 184 shots, including 24 goals from 26.8 xG in 2025.
- **Hany Mukhtar:** 16 goals from 12.7 xG, no penalties, so +3.3. This is the one case with a track record: +3.7 over six prior seasons on about 590 shots. That works out to roughly +0.6 goals per 100 shots, a small edge. It is not +3 a season (2024 was -4.1).
- **Brian Schwake:** +10.9 goals prevented, 2nd in MLS. This is his first season as Nashville's starter, and ASA has no prior MLS season for him. That leaves 102 shots on target as the whole sample. A keeper's season this far above average usually lands much closer to average the next year.

<!-- sofascore:start -->
## Second opinion: Sofascore

*Sofascore context, hand-entered from Sofascore's MLS 2026 pages on 2026-10-23 (`data/sofascore_manual.csv`). None of it enters any calculation above. This section is regenerated from that file on every run.*

- **Two models agree on Schwake.** ASA has him at +10.9 goals prevented; Sofascore at +8.96. Different models, same verdict: elite shot-stopping this season.
- **Penalties.** He saved 2 of 4. ASA values a penalty at 0.78 xG (3.13 xG on the 4 penalties Nashville faced), so 2 saves from 4 is worth about +1.1 goals against an average keeper (10% of his +10.9 ASA total). Penalty saves are the least repeatable part of a keeper's record: a handful of kicks, mostly decided by a guess.
- **Errors.** Nashville made 20 errors that led to a shot and 0 that led to a goal. That many errors without a goal conceded is not something to plan on repeating.
- **Surridge: 17 goals vs 16.79 xGOT.** xGOT (expected goals on target) adds shot placement to xG. His 13.76 xG becomes 16.79 once placement is counted, leaving only +0.2 unexplained. His goals come from where he puts the ball, not from keeper mistakes.
- **Mukhtar: 16 goals vs 13.78 xGOT,** about +2.2 beyond placement (his placement adds only +0.8 to 12.98 xG). Goals above xGOT are shots keepers should have saved, the part most likely to even out.
- **Schwake beyond shot-stopping:** 20 high claims, 0 crosses not claimed, 11/11 successful run-outs. That is value goals prevented doesn't capture: it only measures shots on target, not the shots that never happen because he took the cross.
- **Woodwork.** Nashville hit the post or bar 12 times. xG already counts those chances, and they went in the books as misses, so the finishing term (goals minus xG) already reflects them.

Where the two sources differ, it is definitional:

- **Goals conceded:** Sofascore has Schwake on 23; ASA on 22. Sofascore matches the scoreboard, which includes the one own goal; ASA's xG tables count shot goals only.
- **Minutes:** Sofascore 2610, exactly 90 x his 29 starts; ASA 2935, which includes stoppage time.
<!-- sofascore:end -->

## What this means for the playoffs

| Scenario (per game) | GF | GA | GD | Win in 90 vs average opponent |
|---|---|---|---|---|
| Actual 2026 | 2.10 | 0.73 | +1.37 | 69% |
| Pure xG | 1.73 | 1.39 | +0.33 | 45% |
| Projected (each conversion term kept at its r) | 1.74 | 1.28 | +0.46 | 48% |

- The defensive structure is real. Nashville are 4th in xG against. But 22 conceded is a goalkeeping and opponent-finishing number, not a structure number. Expect more like 1.2 to 1.3 goals against per game.
- Against Vancouver (+1.03 xG difference per game), Nashville would not be favourites on chance quality.
- Single-elimination games are short samples, and variance can still go Nashville's way. Planning should assume it won't.

![League context](output/03_league_context.png)

## Method

1. **Decomposition.** Goal difference = xG difference + finishing + opponent shooting + goalkeeping. This is an exact identity, built from two xG measures:
   - **Pre-shot xG (ASA `xgoals`)** values every shot by where it was taken and how it came about.
   - **Keeper xG faced (ASA `xgoals_gk_faced`)** values only shots on target, using where they were placed.

   Opponent xG minus keeper xG faced is chance quality the opponent lost to misses, blocks and poor placement. Keeper xG faced minus goals conceded is the keeper's contribution.
2. **Persistence.** Each metric is correlated between consecutive regular seasons, 2013 to 2025. The 2025 to 2026 pairs are excluded because 2026 is not finished. Player filters: 900+ minutes and 20+ shots in both seasons. Keeper filter: 1,500+ minutes. 95% CIs use the Fisher z-transform.
3. **Projection.** Each conversion term is multiplied by its r and added back to xG:
   - team r for finishing and opponent shooting
   - keeper r for goalkeeping, since the keeper is the same player

   The Poisson win/draw/loss line treats goals for and against as independent Poisson draws against an average-strength opponent. It ignores home advantage and extra time.

## Data

- **American Soccer Analysis**, through the [`itscalledsoccer`](https://github.com/American-Soccer-Analysis/itscalledsoccer-python) package (v2.3.0). Pulls are cached as parquet in `data/`, and `data/pull_log.json` records the time and row count of each pull.
- `get_players()` in v2.3.0 crashes when merging pages whose columns differ. The player-name lookup therefore calls the same ASA REST endpoint directly (`src/fetch.py`).
- **Sofascore** figures are used only as context. They come from a hand-entered file (`data/sofascore_manual.csv`, template in `data/sofascore_manual.template.csv`), never enter any calculation, and appear in the "Second opinion: Sofascore" section above (written by `src/sofascore.py` on every run) and in `output/summary.md`. Nothing is scraped.

## Sanity checks

`src/checks.py` runs before any output is built and stops the pipeline if a check fails. Current result: 17 pass, 0 fail.

- Nashville's record from ASA game results matches the public MLS standings: 30 games, 20W 7D 3L, 67 points, 64 GF, 23 GA.
- ASA team points (67) match points computed from the scoreboard.
- Scoreboard goals minus ASA shot goals = 1 own goal for and 1 against. Goal difference reconciles at +41.
- Nashville player goals sum to team goals (63).
- Player xG sums to 53.5 against team xG of 51.8 (+3.4%; ASA's team xG is not a plain sum of shot xG). The check allows up to 5%.
- Keeper goals conceded equal team goals against in all 346 MLS team-seasons from 2013 to 2026.
- Every player-season row has a name.

## Not verified / caveats

- **Cross-model note.** Sofascore lists Surridge at 13.76 xG and Mukhtar at 12.98; ASA has 15.7 and 12.7. Surridge's Sofascore figure is close to his ASA non-penalty xG (13.4). This analysis uses ASA throughout.
- **Public standings** come from a third-party standings table found by web search on 2026-10-23, not from mlssoccer.com directly. Surridge's and Mukhtar's goal totals were not checked against an official MLS page.
- **Opponent shooting includes blocked shots.** Part of the +7.7 may be Nashville defenders blocking shots, which is a skill. ASA's API does not separate blocks.
- **Roster turnover.** Year-to-year r mixes real decline with roster turnover, so it may understate persistence for a settled squad. Within-season split-half r would be a cleaner test (see below).
- **Incomplete season.** Four regular-season games remain. Figures will move slightly after the rerun.

## Worth adding (not built)

- **Even game state split** (ASA `even_game_state=True`): does Nashville's chance quality hold when level, or is it inflated by protecting leads?
- **Within-season split-half persistence:** odd vs even games for 2026 Nashville players. It removes roster turnover from the persistence estimate.
- **Opponent-specific preview** for the actual first-round opponent once seeding is set: both teams' xG for and against, set-piece share, and the same projection.
- **Game-by-game cross-model check:** ASA xG vs Sofascore xG and xGOT per match, to see where the two models disagree most.

## Rerun

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.run            # uses the cached data in data/
.venv/bin/python -m src.run --refresh  # re-pulls from ASA (needed after new matches)
```

Outputs in `output/`:

| File | Contents |
|---|---|
| `team_2026.csv` | all 30 teams: decomposition, per-game rates, ranks |
| `players_2026.csv` | Nashville players: penalty split, prior-season finishing |
| `keepers_2026.csv` | all MLS keepers |
| `persistence_pairs.csv`, `persistence_summary.csv`, `persistence_sensitivity.csv` | year N vs N+1 pairs and their correlations |
| `projection.csv` | the three scenarios above |
| `nashville_gd_decomposition.csv` | Nashville's goal difference split |
| `spotlight_player_history.csv` | Surridge and Mukhtar season by season |
| `key_numbers.json` | headline figures |
| `summary.md` | auto-generated summary, regenerated on every run |

After a refresh, update `PUBLIC` in `src/checks.py` to the new standings, or the checks will fail on purpose.
