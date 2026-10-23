# Auto-generated summary (data through 2026-10-21, 30 games)

- Points 67 vs xPoints 46.6 (rank 8 on xPoints)
- Goal difference +41 vs xG difference +10.0; 76% of GD from conversion terms
  - xG difference (chance creation - chance conceded): +10.0
  - Finishing: goals scored above xG: +11.2
  - Opponent shooting: opp. xG that never became on-target danger: +7.7
  - Goalkeeping: goals prevented on shots on target: +12.1

## Persistence (year N vs N+1)

| level   | metric                                |   n_pairs |     r |   ci_low |   ci_high | seasons   |
|:--------|:--------------------------------------|----------:|------:|---------:|----------:|:----------|
| player  | Player xG per 90 (control)            |      1045 | 0.799 |    0.776 |     0.82  | 2013-2025 |
| player  | Player finishing (goals - xG)         |      1045 | 0.035 |   -0.025 |     0.096 | 2013-2025 |
| keeper  | Keeper goals prevented per 90         |       179 | 0.231 |    0.087 |     0.365 | 2013-2025 |
| team    | Team xG difference per game (control) |       285 | 0.401 |    0.299 |     0.494 | 2013-2025 |
| team    | Team finishing per game               |       285 | 0.04  |   -0.076 |     0.156 | 2013-2025 |
| team    | Team opponent-shooting per game       |       285 | 0.079 |   -0.037 |     0.193 | 2013-2025 |
| team    | Team goalkeeping per game             |       285 | 0.177 |    0.062 |     0.287 | 2013-2025 |

## Projection

| scenario                                |   gf_per_game |   ga_per_game |   gd_per_game |   p_win_90 |   p_draw_90 |   p_loss_90 |
|:----------------------------------------|--------------:|--------------:|--------------:|-----------:|------------:|------------:|
| Actual 2026 results                     |         2.1   |         0.733 |         1.367 |      0.691 |       0.191 |       0.118 |
| Pure xG (all conversion luck)           |         1.725 |         1.393 |         0.332 |      0.454 |       0.234 |       0.311 |
| Projected (regressed by year-to-year r) |         1.74  |         1.28  |         0.46  |      0.482 |       0.235 |       0.282 |

## Sanity checks

- PASS scoreboard games = 30 (public table: 30)
- PASS scoreboard wins = 20 (public table: 20)
- PASS scoreboard draws = 7 (public table: 7)
- PASS scoreboard losses = 3 (public table: 3)
- PASS scoreboard points = 67 (public table: 67)
- PASS scoreboard goals_for = 64 (public table: 64)
- PASS scoreboard goals_against = 23 (public table: 23)
- PASS ASA team points 67.0 = scoreboard points 67
- PASS ASA team games 30.0 = scoreboard games 30
- PASS own goals implied: 1.0 for, 1.0 against (scoreboard minus ASA shot goals)
- PASS ASA goal difference 41.0 reconciles with scoreboard after own goals
- PASS no Nashville 2026 player split across clubs (0 found)
- PASS sum of player goals 63 = team goals 63.0
- PASS sum of player xG 53.50 within 5% of team xG 51.76 (+3.4%)
- PASS keeper goals conceded = team goals against in all 346 team-seasons (0 mismatches)
- PASS 2026 row in multi-season pull matches single-season pull
- PASS all 9348 player-season rows have a name (0 missing)
- INFO Nashville have played 30 of 34; 4 regular-season games not yet in data

## Sofascore context (manual entry, not used in any calculation)

| entity        | metric                      |   value | unit                    | source                           | captured   |
|:--------------|:----------------------------|--------:|:------------------------|:---------------------------------|:-----------|
| Nashville SC  | matches                     |   30    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | avg_sofascore_rating        |    7.02 | rating                  | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goals_scored                |   64    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goals_conceded              |   23    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | xg_per_game                 |    1.67 | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | xgot_per_game               |    1.94 | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goal_conversion             |   16    | pct                     | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | penalty_goals               |    4    | count (4 of 4)          | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | free_kick_goals             |    2    | count (2 of 19)         | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goals_inside_box            |   54    | count (54 of 265 shots) | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goals_outside_box           |    9    | count (9 of 123 shots)  | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | big_chances_per_game        |    2.9  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | big_chances_missed_per_game |    1.6  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | shots_per_game              |   12.9  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | shots_on_target_per_game    |    5.3  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | shots_blocked_per_game      |    3.2  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | hit_woodwork                |   12    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | xa_per_game                 |    1.18 | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | possession                  |   53.9  | pct                     | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | pass_accuracy               |   87    | pct                     | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | clean_sheets                |   14    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | tackles_per_game            |   14.7  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | interceptions_per_game      |    7.7  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | clearances_per_game         |   21.4  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | errors_leading_to_shot      |   20    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | errors_leading_to_goal      |    0    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | penalties_committed         |    4    | count                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | goals_prevented             |    9.96 | goals                   | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | duels_won                   |   50.2  | pct                     | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | distance_per_game           |  101.7  | km                      | Sofascore team stats MLS 2026    | 2026-10-23 |
| Nashville SC  | sprints_per_game            |  117.5  | per_game                | Sofascore team stats MLS 2026    | 2026-10-23 |
| Brian Schwake | avg_sofascore_rating        |    7.39 | rating                  | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | matches_started             |   29    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | minutes                     | 2610    | minutes                 | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | clean_sheets                |   13    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | goals_conceded              |   23    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | xg_conceded                 |   36.16 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | goals_prevented             |    8.96 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | saves                       |   77    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | save_pct                    |   77    | pct                     | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | conceded_inside_box         |   19    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | conceded_outside_box        |    4    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | penalties_faced             |    4    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | penalties_saved             |    2    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | high_claims                 |   20    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | crosses_not_claimed         |    0    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | successful_run_outs         |   11    | count (11 of 11)        | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | pass_accuracy               |   73    | pct                     | Sofascore player season MLS 2026 | 2026-10-23 |
| Brian Schwake | long_ball_accuracy          |   40    | pct                     | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | goals                       |   17    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | xg                          |   13.76 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | xgot                        |   16.79 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | shots_on_target             |   35    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | assists                     |    1    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | xa                          |    1.92 | assists                 | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | offsides                    |   20    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Sam Surridge  | avg_sofascore_rating        |    7.07 | rating                  | Sofascore top players MLS 2026   | 2026-10-23 |
| Hany Mukhtar  | goals                       |   16    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | xg                          |   12.98 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | xgot                        |   13.78 | goals                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | shots_on_target             |   40    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | assists                     |    7    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | xa                          |    5.06 | assists                 | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | corners_taken               |   37    | count                   | Sofascore player season MLS 2026 | 2026-10-23 |
| Hany Mukhtar  | avg_sofascore_rating        |    7.35 | rating                  | Sofascore top players MLS 2026   | 2026-10-23 |
