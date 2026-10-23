"""Self-contained interactive dashboard -> docs/index.html (served by GitHub Pages).

Reads only output/*.csv, output/key_numbers.json and data/sofascore_manual.csv. Plotly.js is
inlined, so the page makes no external requests. Text and tables are filled in here in Python;
charts are drawn in the browser from the embedded JSON so they can follow light/dark mode.
"""
from __future__ import annotations

import html
import re
import json

import pandas as pd
import plotly.offline

from src.fetch import DATA, ROOT

OUT = ROOT / "output"
DOCS = ROOT / "docs"
SOFASCORE = DATA / "sofascore_manual.csv"
REPO = "https://github.com/Raghav-Aggarwal-20/nashville-playoff-check"


def _pct(x: float) -> str:
    return f"{x:.0%}"


def _signed(x: float, dp: int = 1) -> str:
    return f"{x:+.{dp}f}"


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _load() -> dict:
    return {
        "key": json.loads((OUT / "key_numbers.json").read_text()),
        "team": pd.read_csv(OUT / "team_2026.csv"),
        "parts": pd.read_csv(OUT / "nashville_gd_decomposition.csv"),
        "rtab": pd.read_csv(OUT / "persistence_summary.csv"),
        "sens": pd.read_csv(OUT / "persistence_sensitivity.csv"),
        "proj": pd.read_csv(OUT / "projection.csv"),
        "players": pd.read_csv(OUT / "players_2026.csv"),
        "hist": pd.read_csv(OUT / "spotlight_player_history.csv"),
        "keepers": pd.read_csv(OUT / "keepers_2026.csv"),
        "sofa": pd.read_csv(SOFASCORE) if SOFASCORE.exists() else None,
    }


# ------------------------------------------------------------------ chart payload

SHORT = {
    "Player xG per 90 (control)": "Player xG per 90",
    "Player finishing (goals - xG)": "Player finishing (G − xG)",
    "Keeper goals prevented per 90": "Keeper goals prevented /90",
    "Team xG difference per game (control)": "Team xG difference /game",
    "Team finishing per game": "Team finishing /game",
    "Team opponent-shooting per game": "Team opponent shooting /game",
    "Team goalkeeping per game": "Team goalkeeping /game",
}


def _payload(d: dict) -> dict:
    team, parts, players, keepers = d["team"], d["parts"], d["players"], d["keepers"]
    n = team[team.is_nashville].iloc[0]
    p = players[(players.goals > 0) | (players.xgoals >= 1)].sort_values("goals")
    k = keepers[keepers.minutes_played >= 900]
    return {
        "waterfall": {
            "labels": ["xG difference", "Finishing", "Opponent shooting", "Goalkeeping", "Goal difference"],
            "values": parts.goals.round(1).tolist() + [float(n.goal_difference)],
            "types": parts.type.tolist() + ["total"],
            "shares": parts.share_of_gd.tolist() + [1.0],
        },
        "league": {c: team[c].tolist() for c in
                   ["team", "is_nashville", "xgoal_difference_pg", "goal_difference_pg", "points", "xpoints",
                    "goals_for", "xgoals_for", "goals_against", "xgoals_against"]},
        "persistence": {
            "metric": [SHORT.get(m, m) for m in d["rtab"].metric],
            "control": d["rtab"].metric.str.contains("control").tolist(),
            **{c: d["rtab"][c].tolist() for c in ["r", "ci_low", "ci_high", "n_pairs"]},
        },
        "sensitivity": {c: d["sens"][c].tolist() for c in ["metric", "filter", "n_pairs", "r"]},
        "players": {c: p[c].tolist() for c in
                    ["player", "minutes_played", "shots", "goals", "pen_goals", "np_goals", "xgoals", "np_xg",
                     "g_minus_xg", "prior_seasons", "prior_g_minus_xg"]},
        "history": {name: {c: g[c].tolist() for c in ["season_name", "goals", "xgoals", "g_minus_xg", "shots"]}
                    for name, g in d["hist"].groupby("player")},
        "keepers": {c: k[c].tolist() for c in
                    ["keeper", "team", "is_nashville", "minutes_played", "shots_faced", "goals_conceded",
                     "xgoals_gk_faced", "goals_prevented", "gp_p90"]},
    }


def _clean_nan(x):
    """NaN is not valid JSON; send it to the browser as null."""
    if isinstance(x, dict):
        return {k: _clean_nan(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_clean_nan(v) for v in x]
    if isinstance(x, float) and x != x:
        return None
    return x


# ------------------------------------------------------------------ HTML pieces

def _kpis(d: dict) -> str:
    k = d["key"]
    sch = d["keepers"][d["keepers"].keeper == k["keeper"]["name"]].iloc[0]
    n = d["team"][d["team"].is_nashville].iloc[0]
    tiles = [
        (f"+{k['goal_difference']}", "goal difference",
         f"xG difference only {_signed(k['xg_difference'])}"),
        (_pct(1 - k["conversion_share"]), "of it from chance quality",
         f"{_pct(k['conversion_share'])} from finishing, misses and saves"),
        (f"{k['points']}", f"points, {_ordinal(int(n.rank_points))} in MLS",
         f"{k['xpoints']} expected points, {_ordinal(k['rank_xpoints'])}"),
        (f"{_signed(sch.goals_prevented)}", f"{k['keeper']['name']} goals prevented",
         f"{_ordinal(k['keeper']['rank'])} among MLS keepers"),
        (f"{_pct(k['p_win_90_actual'])} → {_pct(k['p_win_90_projected'])}", "win in 90 minutes",
         "actual 2026 rates vs regressed rates"),
    ]
    return "\n".join(
        f'<div class="kpi"><div class="kpi-v">{html.escape(v)}</div><div class="kpi-l">{html.escape(l)}</div>'
        f'<div class="kpi-s">{html.escape(s)}</div></div>' for v, l, s in tiles)


def _answer(d: dict) -> str:
    k, parts = d["key"], d["parts"]
    g = parts.set_index(parts.component.str.split(":").str[0]).goals
    xgd_rank = _ordinal(k["rank_xgd_pg"])
    return (
        f"<p>About a quarter. Nashville's <b>+{k['goal_difference']}</b> goal difference rests on a "
        f"<b>{_signed(g['xG difference (chance creation - chance conceded)'])}</b> xG difference. The other "
        f"<b>{_signed(k['conversion_goals'])}</b> came from finishing ({_signed(g['Finishing'])}), opponents "
        f"missing or misplacing shots ({_signed(g['Opponent shooting'])}) and goalkeeping "
        f"({_signed(g['Goalkeeping'])}, of which {k['keeper']['name'].split()[-1]} "
        f"{_signed(k['keeper']['goals_prevented'])}).</p>"
        f"<p>Across MLS 2013–2025, finishing above xG has not carried into the next season "
        f"(r = {k['r_player_finishing']:.2f}) and shot-stopping only weakly (r = {k['r_keeper_gp90']:.2f}). "
        f"On chance quality Nashville are a good team, {xgd_rank} in xG difference per game, rather than the "
        f"dominant one the table shows.</p>")


def _projection_table(d: dict) -> str:
    rows = []
    label = {"Actual 2026 results": "Actual 2026", "Pure xG (all conversion luck)": "Pure xG",
             "Projected (regressed by year-to-year r)": "Projected (regressed)"}
    for _, r in d["proj"].iterrows():
        cls = ' class="hl"' if r.scenario.startswith("Projected") else ""
        rows.append(f"<tr{cls}><th>{label.get(r.scenario, r.scenario)}</th><td>{r.gf_per_game:.2f}</td>"
                    f"<td>{r.ga_per_game:.2f}</td><td>{r.gd_per_game:+.2f}</td><td>{_pct(r.p_win_90)}</td>"
                    f"<td>{_pct(r.p_draw_90)}</td><td>{_pct(r.p_loss_90)}</td></tr>")
    return ("<table><thead><tr><th>Per game</th><th>GF</th><th>GA</th><th>GD</th><th>Win</th><th>Draw</th>"
            "<th>Loss</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def _sofascore(d: dict) -> str:
    s = d["sofa"]
    if s is None:
        return "<p class='muted'>No Sofascore file provided.</p>"
    v = s.set_index(["entity", "metric"]).value
    k, pl, team = d["key"], d["players"].set_index("player"), d["team"]
    n = team[team.is_nashville].iloc[0]
    sch = k["keeper"]

    def f(x, dp=2):
        return f"{x:.0f}" if float(x).is_integer() else f"{x:.{dp}f}"

    rows = [
        ("Schwake goals prevented", f"+{sch['goals_prevented']:.1f}", "+" + f(v["Brian Schwake", "goals_prevented"])),
        ("Surridge xG", f"{pl.loc['Sam Surridge', 'xgoals']:.1f}", f(v["Sam Surridge", "xg"])),
        ("Surridge xGOT (xG + placement)", "–", f(v["Sam Surridge", "xgot"])),
        ("Mukhtar xG", f"{pl.loc['Hany Mukhtar', 'xgoals']:.1f}", f(v["Hany Mukhtar", "xg"])),
        ("Mukhtar xGOT (xG + placement)", "–", f(v["Hany Mukhtar", "xgot"])),
        ("Nashville xG per game", f"{n.xgoals_for_pg:.2f}", f(v["Nashville SC", "xg_per_game"])),
        ("Schwake goals conceded", f"{sch['goals_conceded']}", f(v["Brian Schwake", "goals_conceded"])),
    ]
    unit = s[(s.entity == "Brian Schwake") & (s.metric == "successful_run_outs")].unit.iloc[0]
    m = re.search(r"of (\d+)", str(unit))
    runouts_of = f"/{m.group(1)}" if m else ""
    extra = [
        ("Penalties saved", f"{f(v['Brian Schwake', 'penalties_saved'])} of {f(v['Brian Schwake', 'penalties_faced'])}"),
        ("High claims / crosses not claimed",
         f"{f(v['Brian Schwake', 'high_claims'])} / {f(v['Brian Schwake', 'crosses_not_claimed'])}"),
        ("Successful run-outs", f"{f(v['Brian Schwake', 'successful_run_outs'])}{runouts_of}"),
        ("Errors leading to shot / goal",
         f"{f(v['Nashville SC', 'errors_leading_to_shot'])} / {f(v['Nashville SC', 'errors_leading_to_goal'])}"),
        ("Woodwork hit", f(v["Nashville SC", "hit_woodwork"])),
    ]
    cmp_rows = "".join(f"<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    ext = "".join(f"<div class='mini'><div class='mini-v'>{b}</div><div class='mini-l'>{a}</div></div>"
                  for a, b in extra)
    return (f"<table class='cmp'><thead><tr><th></th><th>ASA</th><th>Sofascore</th></tr></thead>"
            f"<tbody>{cmp_rows}</tbody></table><div class='minis'>{ext}</div>"
            f"<p class='muted'>Hand-entered from Sofascore on {html.escape(str(s.captured.max()))}. Context only: "
            "none of these figures enters any calculation. Goals conceded differ because Sofascore counts the "
            "own goal and ASA's xG tables count shot goals only.</p>")


# ------------------------------------------------------------------ page

CSS = """
:root{color-scheme:light;--bg:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,.10);--blue:#2a78d6;--orange:#eb6834;--context:#c3c2b7;
--hl:rgba(42,120,214,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#0d0d0d;
--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;
--border:rgba(255,255,255,.10);--blue:#3987e5;--orange:#d95926;--context:#52514e;--hl:rgba(57,135,229,.14)}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--blue:#3987e5;--orange:#d95926;
--context:#52514e;--hl:rgba(57,135,229,.14)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 48px}
header h1{font-size:28px;line-height:1.2;margin:0 0 6px}
.sub{color:var(--ink2);margin:0 0 18px}
.q{color:var(--ink2);font-style:italic;margin:0 0 10px}
.answer p{margin:0 0 10px;max-width:780px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:22px 0 8px}
.kpi,.card{background:var(--surface);border:1px solid var(--border);border-radius:12px}
.kpi{padding:14px 14px 12px}
.kpi-v{font-size:26px;font-weight:700;line-height:1.15}
.kpi-l{font-size:13px;font-weight:600;margin-top:4px}
.kpi-s{font-size:12px;color:var(--muted);margin-top:2px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{padding:18px 18px 10px;margin-top:16px;min-width:0}
.card h2{font-size:17px;margin:0 0 2px}
.card .lede{color:var(--ink2);font-size:13.5px;margin:0 0 8px}
.chart{width:100%;height:380px}
.seg{display:inline-flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;margin:4px 0 6px}
.seg button{background:none;border:0;padding:5px 12px;font:inherit;font-size:13px;color:var(--ink2);cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--hl);color:var(--ink);font-weight:600}
table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums;margin:6px 0 10px}
th,td{text-align:right;padding:7px 8px;border-bottom:1px solid var(--grid)}
th:first-child{text-align:left;font-weight:500}
thead th{color:var(--muted);font-weight:600;font-size:12.5px}
tr.hl{background:var(--hl)}
.ctx{border-left:3px solid var(--muted)}
.tag{display:inline-block;font-size:11.5px;font-weight:600;letter-spacing:.02em;color:var(--muted);
border:1px solid var(--border);border-radius:999px;padding:1px 9px;margin-left:8px;vertical-align:2px}
.minis{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px;margin:6px 0 10px}
.mini{border:1px solid var(--border);border-radius:10px;padding:10px}
.mini-v{font-size:19px;font-weight:700}.mini-l{font-size:12px;color:var(--muted)}
.muted{color:var(--muted);font-size:13px}
.notes{color:var(--ink2);font-size:13.5px}
.notes li{margin:0 0 6px}
footer{margin-top:28px;color:var(--muted);font-size:13px;border-top:1px solid var(--grid);padding-top:14px}
a{color:var(--blue)}
@media (max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}.kpi:last-child{grid-column:span 2}}
@media (max-width:520px){header h1{font-size:23px}.chart{height:340px}th,td{padding:6px 4px;font-size:13px}}
"""

JS = r"""
const D = JSON.parse(document.getElementById('data').textContent);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const CFG = {displayModeBar:false, responsive:true};
const f1 = x => (x>=0?'+':'') + x.toFixed(1), f2 = x => (x>=0?'+':'') + x.toFixed(2);
const state = {persist:'r', keep:'total'};

function base(extra){
  const ink=css('--ink2'), grid=css('--grid'), axis=css('--axis');
  const ax = {gridcolor:grid, linecolor:axis, zerolinecolor:axis, tickfont:{color:css('--muted'),size:11},
              title:{font:{color:ink,size:12}}, automargin:true};
  return Object.assign({paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
    font:{family:'system-ui,-apple-system,Segoe UI,sans-serif', color:css('--ink'), size:12},
    margin:{l:10,r:10,t:10,b:10}, showlegend:false,
    hoverlabel:{bgcolor:css('--surface'), bordercolor:css('--axis'), font:{color:css('--ink')}},
    xaxis:Object.assign({},ax), yaxis:Object.assign({},ax)}, extra||{});
}

function waterfall(){
  const w=D.waterfall, blue=css('--blue'), orange=css('--orange'), ink=css('--ink2');
  let run=0; const bases=[], ys=[];
  w.values.forEach((v,i)=>{ if(w.types[i]==='total'){bases.push(0);ys.push(v);} else {bases.push(run);ys.push(v);run+=v;} });
  const colors=w.types.map(t=>t==='repeatable'?blue:t==='conversion'?orange:ink);
  const text=w.values.map((v,i)=> (w.types[i]==='total'?'+'+v.toFixed(0):f1(v)));
  Plotly.react('c-waterfall',[{type:'bar',x:w.labels,y:ys,base:bases,marker:{color:colors},
    text:text,textposition:'outside',textfont:{color:css('--ink'),size:13},cliponaxis:false,
    customdata:w.shares.map(s=>Math.round(s*100)+'%'),
    hovertemplate:'<b>%{x}</b><br>%{text} goals<br>%{customdata} of goal difference<extra></extra>'}],
    base({yaxis:Object.assign(base().yaxis,{title:{text:'Goals'},range:[0,Math.max(...w.values)*1.15]}),
          xaxis:Object.assign(base().xaxis,{tickfont:{color:css('--ink2'),size:12}}), bargap:.35}),CFG);
}

function league(){
  const L=D.league, n=L.team.length, idx=[...Array(n).keys()];
  const nsh=idx.filter(i=>L.is_nashville[i]), oth=idx.filter(i=>!L.is_nashville[i]);
  const pick=(ids,k)=>ids.map(i=>L[k][i]);
  const cd=ids=>ids.map(i=>[L.team[i],L.points[i],L.xpoints[i].toFixed(1),L.goals_for[i],L.xgoals_for[i].toFixed(1),
                             L.goals_against[i],L.xgoals_against[i].toFixed(1)]);
  const ht='<b>%{customdata[0]}</b><br>GD/game %{y:+.2f} · xGD/game %{x:+.2f}<br>Points %{customdata[1]} · xPts %{customdata[2]}'+
           '<br>GF %{customdata[3]} (xG %{customdata[4]}) · GA %{customdata[5]} (xGA %{customdata[6]})<extra></extra>';
  const byX=oth.slice().sort((a,b)=>L.xgoal_difference_pg[b]-L.xgoal_difference_pg[a]);
  const byY=oth.slice().sort((a,b)=>L.goal_difference_pg[b]-L.goal_difference_pg[a]);
  const labelled=new Set([...byX.slice(0,2),...byX.slice(-1),...byY.slice(-1)]);
  const all=L.xgoal_difference_pg.concat(L.goal_difference_pg), lo=Math.min(...all)-.15, hi=Math.max(...all)+.15;
  Plotly.react('c-league',[
    {x:[lo,hi],y:[lo,hi],mode:'lines',line:{color:css('--axis'),width:1},hoverinfo:'skip'},
    {x:pick(oth,'xgoal_difference_pg'),y:pick(oth,'goal_difference_pg'),mode:'markers+text',
     text:oth.map(i=>labelled.has(i)?L.team[i]:''),
     textposition:'top center',textfont:{size:11,color:css('--ink2')},
     marker:{size:10,color:css('--context')},customdata:cd(oth),hovertemplate:ht},
    {x:pick(nsh,'xgoal_difference_pg'),y:pick(nsh,'goal_difference_pg'),mode:'markers+text',text:['Nashville'],
     textposition:'middle left',textfont:{size:12,color:css('--ink')},
     marker:{size:15,color:css('--blue'),line:{color:css('--surface'),width:2}},customdata:cd(nsh),hovertemplate:ht}],
    base({xaxis:Object.assign(base().xaxis,{title:{text:'Expected goal difference per game (xG)'},range:[lo,hi]}),
          yaxis:Object.assign(base().yaxis,{title:{text:'Actual goal difference per game'},range:[lo,hi]}),
          annotations:[{x:hi,y:hi,xanchor:'right',yanchor:'top',text:'actual = expected',showarrow:false,
                        font:{size:10,color:css('--muted')}}]}),CFG);
}

function persistence(){
  const el='c-persist';
  if(state.persist==='r'){
    const P=D.persistence, m=P.metric.slice().reverse(), r=P.r.slice().reverse(), lo=P.ci_low.slice().reverse(),
          hi=P.ci_high.slice().reverse(), ctl=P.control.slice().reverse(), np=P.n_pairs.slice().reverse();
    const col=ctl.map(c=>c?css('--blue'):css('--orange'));
    Plotly.react(el,[{x:r,y:m,mode:'markers',marker:{size:11,color:col},
      error_x:{type:'data',symmetric:false,array:hi.map((h,i)=>h-r[i]),arrayminus:lo.map((l,i)=>r[i]-l),
               color:css('--ink2'),thickness:1.5,width:0},
      customdata:m.map((_,i)=>[lo[i].toFixed(2),hi[i].toFixed(2),np[i]]),
      hovertemplate:'<b>%{y}</b><br>r = %{x:.2f} (95% CI %{customdata[0]} to %{customdata[1]})<br>%{customdata[2]} season pairs<extra></extra>'}],
      base({xaxis:Object.assign(base().xaxis,{title:{text:'Correlation, season N vs N+1'},range:[-.15,1],zeroline:true}),
            yaxis:Object.assign(base().yaxis,{tickfont:{color:css('--ink2'),size:12}})}),CFG);
  } else {
    const S=D.sensitivity, groups=[...new Set(S.metric)], traces=groups.map((g,gi)=>{
      const ids=S.metric.map((m,i)=>m===g?i:-1).filter(i=>i>=0);
      return {x:ids.map(i=>S.filter[i].replace(' both seasons','').replace('>= ','').replace(' shots','+ shots').replace(' minutes','+ min')),y:ids.map(i=>S.r[i]),type:'bar',
        name:g,marker:{color:gi?css('--orange'):css('--context')},customdata:ids.map(i=>S.n_pairs[i]),
        hovertemplate:'<b>'+g+'</b><br>%{x}: r = %{y:.2f} (%{customdata} pairs)<extra></extra>'};});
    Plotly.react(el,traces,base({margin:{l:10,r:10,t:40,b:10},showlegend:true,legend:{orientation:'h',x:0,y:1.0,yanchor:'bottom',font:{color:css('--ink2')}},
      yaxis:Object.assign(base().yaxis,{title:{text:'r, season N vs N+1'},range:[-.1,.4]}),
      xaxis:Object.assign(base().xaxis,{tickfont:{color:css('--ink2'),size:11}}),bargap:.3}),CFG);
  }
}

function players(){
  const P=D.players, cd=P.player.map((_,i)=>[P.minutes_played[i],P.shots[i],P.goals[i],P.xgoals[i].toFixed(1),
    f1(P.g_minus_xg[i]),P.pen_goals[i],P.np_xg[i].toFixed(1),
    P.prior_seasons[i]?(f1(P.prior_g_minus_xg[i])+' over '+P.prior_seasons[i]+' prior MLS seasons'):'no prior MLS seasons']);
  const ht='<b>%{y}</b><br>%{customdata[2]} goals from %{customdata[3]} xG (%{customdata[4]})<br>'+
           'Penalty goals %{customdata[5]} · non-penalty xG %{customdata[6]}<br>%{customdata[0]} min · %{customdata[1]} shots'+
           '<br>Career finishing: %{customdata[7]}<extra></extra>';
  Plotly.react('c-players',[
    {type:'bar',orientation:'h',y:P.player,x:P.np_goals,name:'Non-penalty goals',marker:{color:css('--blue')},customdata:cd,hovertemplate:ht},
    {type:'bar',orientation:'h',y:P.player,x:P.pen_goals,name:'Penalty goals',marker:{color:css('--context')},customdata:cd,hovertemplate:ht},
    {type:'scatter',mode:'markers',y:P.player,x:P.xgoals,name:'xG',marker:{symbol:'line-ns',size:16,
      line:{width:3,color:css('--ink')}},customdata:cd,hovertemplate:ht}],
    base({barmode:'stack',margin:{l:10,r:10,t:40,b:10},showlegend:true,legend:{orientation:'h',x:0,y:1.0,yanchor:'bottom',font:{color:css('--ink2')}},bargap:.35,
          height:Math.max(340,P.player.length*28+80),
          xaxis:Object.assign(base().xaxis,{title:{text:'Goals (bar) and xG (tick)'}}),
          yaxis:Object.assign(base().yaxis,{tickfont:{color:css('--ink2'),size:12}})}),CFG);
}

function history(){
  const H=D.history, names=Object.keys(H), cols=[css('--blue'),css('--orange')];
  const traces=names.map((nm,i)=>({x:H[nm].season_name,y:H[nm].g_minus_xg,mode:'lines+markers',name:nm,
    line:{color:cols[i%2],width:2},marker:{size:9,color:cols[i%2],line:{color:css('--surface'),width:2}},
    customdata:H[nm].goals.map((g,j)=>[g,H[nm].xgoals[j].toFixed(1),H[nm].shots[j]]),
    hovertemplate:'<b>'+nm+' %{x}</b><br>%{customdata[0]} goals from %{customdata[1]} xG (%{y:+.1f})<br>%{customdata[2]} shots<extra></extra>'}));
  Plotly.react('c-history',traces,base({margin:{l:10,r:10,t:40,b:10},showlegend:true,legend:{orientation:'h',x:0,y:1.0,yanchor:'bottom',font:{color:css('--ink2')}},
    xaxis:Object.assign(base().xaxis,{dtick:1,title:{text:'Season'}}),
    yaxis:Object.assign(base().yaxis,{title:{text:'Goals minus xG'},zeroline:true,zerolinewidth:1.5})}),CFG);
}

function keepers(){
  const K=D.keepers, per=state.keep==='p90', v=per?K.gp_p90:K.goals_prevented;
  const ids=[...v.keys()].sort((a,b)=>v[a]-v[b]);
  const y=ids.map(i=>K.keeper[i]+' ('+K.team[i]+')'), x=ids.map(i=>v[i]);
  const col=ids.map(i=>K.is_nashville[i]?css('--blue'):css('--context'));
  const cd=ids.map(i=>[K.minutes_played[i],K.shots_faced[i],K.goals_conceded[i],K.xgoals_gk_faced[i].toFixed(1),
                       f1(K.goals_prevented[i]),f2(K.gp_p90[i])]);
  Plotly.react('c-keepers',[{type:'bar',orientation:'h',y:y,x:x,marker:{color:col},customdata:cd,
    hovertemplate:'<b>%{y}</b><br>%{customdata[2]} conceded on %{customdata[3]} keeper xG faced<br>'+
      'Goals prevented %{customdata[4]} (%{customdata[5]} per 90)<br>%{customdata[0]} min · %{customdata[1]} shots on target faced<extra></extra>'}],
    base({height:Math.max(420,ids.length*19+70),bargap:.25,
      xaxis:Object.assign(base().xaxis,{title:{text:per?'Goals prevented per 90':'Goals prevented'},zeroline:true}),
      yaxis:Object.assign(base().yaxis,{tickfont:{size:10.5,color:css('--ink2')}})}),CFG);
}

function drawAll(){waterfall();league();persistence();players();history();keepers();}
document.querySelectorAll('.seg').forEach(seg=>seg.addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  seg.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  state[seg.dataset.key]=b.dataset.val; ({persist:persistence,keep:keepers})[seg.dataset.key]();
}));
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',drawAll);
drawAll();
"""


def build() -> None:
    d = _load()
    k = d["key"]
    payload = json.dumps(_clean_nan(_payload(d)), separators=(",", ":"), allow_nan=False)
    plotly_js = plotly.offline.get_plotlyjs()
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nashville Playoff Check</title>
<meta name="description" content="How much of Nashville SC's 2026 MLS season is repeatable chance quality, and how much is finishing and goalkeeping that may cool off.">
<style>{CSS}</style>
<script>{plotly_js}</script>
</head><body><div class="wrap">
<header>
<h1>Nashville playoff check: how much of 2026 will travel?</h1>
<p class="sub">MLS 2026 regular season, data through {k['as_of']} ({k['games']} of 34 games). Source: American Soccer Analysis.</p>
<p class="q">The question: how much of Nashville's results come from chance creation and prevention that will hold up in the playoffs, and how much from finishing and goalkeeping that may cool off?</p>
<div class="answer">{_answer(d)}</div>
</header>
<section class="kpis">{_kpis(d)}</section>

<div class="card"><h2>Where the +{k['goal_difference']} goal difference comes from</h2>
<p class="lede"><span style="color:var(--blue);font-weight:600">Blue</span> is chance quality (xG difference). <span style="color:var(--orange);font-weight:600">Orange</span> is conversion: what happened to those chances. Hover for detail.</p>
<div id="c-waterfall" class="chart"></div></div>

<div class="grid2">
<div class="card"><h2>Does it repeat?</h2>
<p class="lede">Correlation between one season and the next, MLS 2013–2025, with 95% confidence intervals. Blue rows are controls that measure chance quality.</p>
<div class="seg" data-key="persist" role="group" aria-label="Persistence view"><button data-val="r" aria-pressed="true">All metrics</button><button data-val="sens" aria-pressed="false">Sensitivity to filters</button></div>
<div id="c-persist" class="chart"></div></div>
<div class="card"><h2>League context</h2>
<p class="lede">Every MLS team: actual vs expected goal difference per game. Teams above the line are outscoring their chances.</p>
<div id="c-league" class="chart"></div></div>
</div>

<div class="grid2">
<div class="card"><h2>Nashville scorers: goals vs xG</h2>
<p class="lede">Bars are goals (penalties in gray), the tick is xG. Hover for career finishing.</p>
<div id="c-players" class="chart" style="height:auto"></div></div>
<div class="card"><h2>Finishing by season: Surridge and Mukhtar</h2>
<p class="lede">Goals minus xG each MLS season. Above zero one year rarely predicts above zero the next.</p>
<div id="c-history" class="chart"></div></div>
</div>

<div class="card"><h2>Goalkeepers: goals prevented, MLS 2026</h2>
<p class="lede">Keeper xG faced (shots on target, by placement) minus goals conceded. Keepers with 900+ minutes.</p>
<div class="seg" data-key="keep" role="group" aria-label="Keeper measure"><button data-val="total" aria-pressed="true">Season total</button><button data-val="p90" aria-pressed="false">Per 90 minutes</button></div>
<div id="c-keepers" class="chart" style="height:auto"></div></div>

<div class="grid2">
<div class="card"><h2>What this means for a playoff game</h2>
<p class="lede">Per-game rates and the chance of winning a 90-minute game against an average opponent (independent Poisson).</p>
{_projection_table(d)}
<p class="muted">Projected keeps each conversion term only in proportion to its year-to-year r. Excludes home advantage and extra time.</p></div>
<div class="card ctx"><h2>Second opinion: Sofascore <span class="tag">CONTEXT ONLY</span></h2>
<p class="lede">A second data provider, to check the main figures.</p>
{_sofascore(d)}</div>
</div>

<div class="card"><h2>Method and caveats</h2><ul class="notes">
<li><b>Decomposition:</b> goal difference = xG difference + finishing (goals − xG) + opponent shooting (opponent xG − keeper xG faced) + goalkeeping (keeper xG faced − goals conceded). Own goals are excluded by ASA (1 for, 1 against).</li>
<li><b>Persistence:</b> season N vs N+1, MLS 2013–2025. Players 900+ minutes and 20+ shots in both seasons; keepers 1,500+ minutes. Year-to-year r includes roster turnover.</li>
<li><b>Opponent shooting</b> includes blocked shots, so part of it may be Nashville defending.</li>
<li>The season is {k['games']} of 34 games complete; figures will move slightly after Decision Day.</li>
</ul></div>

<footer>Analysis by Raghav Aggarwal · <a href="https://github.com/Raghav-Aggarwal-20">GitHub</a> ·
<a href="https://www.linkedin.com/in/raghav-aggarwal-a4b5721bb">LinkedIn</a> · <a href="{REPO}">Code and data</a></footer>
</div>
<script id="data" type="application/json">{payload}</script>
<script>{JS}</script>
</body></html>"""
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page)
    (DOCS / ".nojekyll").write_text("")


if __name__ == "__main__":
    build()
