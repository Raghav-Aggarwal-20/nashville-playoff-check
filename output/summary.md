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

_sofascore_manual.csv not found: copy data/sofascore_manual.template.csv and fill it in._
