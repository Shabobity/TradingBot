"""
Stock Agent Dashboard
======================
Web dashboard: view scan results, run new scans, chat with the agent.

Usage:
    python DashBoard.py          → http://localhost:5000
    python DashBoard.py 8080     → custom port

Requirements:
    pip install flask
"""

import os, sys, json, glob, threading
from flask import Flask, render_template_string, jsonify, request

app         = Flask(__name__)
app.secret_key = "trading-agent-2024"
RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── HTML ──────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>☭ Peoples Market Dashboard ☭</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Special+Elite&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --red:#cc0000;--red2:#990000;--red3:#660000;--red4:#3d0000;
  --gold:#f5c518;--gold2:#d4a017;--cream:#f0e6cc;
  --bg:#1a0000;--bg2:#240000;--bg3:#300000;--border:#660000;
  --text:#f0e6cc;--muted:#b08060;
}
body{font-family:'Special Elite',serif;background:var(--bg);color:var(--text);min-height:100vh;background-image:repeating-linear-gradient(45deg,transparent,transparent 40px,rgba(150,0,0,.03) 40px,rgba(150,0,0,.03) 80px)}

/* ── Top banner ── */
.hdr{background:linear-gradient(180deg,#8b0000 0%,#cc0000 40%,#8b0000 100%);border-bottom:4px solid var(--gold);padding:0;position:sticky;top:0;z-index:100}
.hdr-inner{max-width:1400px;margin:0 auto;padding:14px 28px;display:flex;align-items:center;gap:16px}
.star-left,.star-right{font-size:28px;color:var(--gold);text-shadow:0 0 12px rgba(245,197,24,.5);flex-shrink:0}
.hdr-title{flex:1;text-align:center}
.hdr-title h1{font-family:'Oswald',sans-serif;font-size:22px;font-weight:700;color:var(--gold);letter-spacing:.15em;text-transform:uppercase;text-shadow:1px 1px 3px #000}
.hdr-title .sub{font-size:10px;color:#ffcdd2;letter-spacing:.25em;text-transform:uppercase;margin-top:2px}
.regime-area{font-size:12px;color:#ffcdd2;text-align:right;min-width:160px}
.badge{display:inline-block;padding:3px 10px;font-family:'Oswald',sans-serif;font-weight:600;letter-spacing:.05em;font-size:11px;border-radius:2px}
.bull{background:var(--gold);color:#3d0000}.bear{background:#1a1a1a;color:#f87171}.neutral{background:#4a3000;color:var(--gold2)}

/* ── Propaganda stripe ── */
.stripe{background:var(--red3);border-top:2px solid var(--gold);border-bottom:2px solid var(--gold);padding:6px 0;text-align:center;font-family:'Oswald',sans-serif;font-size:11px;letter-spacing:.3em;color:var(--gold);text-transform:uppercase;overflow:hidden}
.stripe-inner{white-space:nowrap;animation:marquee 30s linear infinite}
@keyframes marquee{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}

/* ── Layout ── */
.wrap{max-width:1400px;margin:0 auto;padding:24px 28px}

/* ── Stat cards ── */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px}
.scard{background:var(--bg2);border:1px solid var(--border);border-top:3px solid var(--gold);border-radius:2px;padding:18px 20px;position:relative;overflow:hidden}
.scard::before{content:'★';position:absolute;right:12px;top:8px;font-size:32px;color:rgba(245,197,24,.08)}
.scard .lbl{font-family:'Oswald',sans-serif;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px}
.scard .val{font-family:'Oswald',sans-serif;font-size:32px;font-weight:700}
.gn{color:#ff6b6b}.rd{color:#ff6b6b}.bl{color:var(--gold)}.am{color:var(--gold2)}

/* ── Toolbar ── */
.toolbar{display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.btn{padding:8px 20px;border-radius:2px;border:1px solid var(--border);background:var(--bg2);color:var(--cream);font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:.05em;cursor:pointer;transition:all .15s;text-transform:uppercase}
.btn:hover{background:var(--red3);border-color:var(--gold)}
.btn-p{background:var(--red);border-color:var(--gold2);color:var(--gold);font-weight:600}
.btn-p:hover{background:var(--red2)}
.btn:disabled{opacity:.4;cursor:not-allowed}
input.srch{padding:8px 14px;border-radius:2px;border:1px solid var(--border);background:var(--bg2);color:var(--cream);font-family:'Special Elite',serif;font-size:13px;width:220px}
input.srch::placeholder{color:var(--muted)}
select.srch{padding:8px 14px;border-radius:2px;border:1px solid var(--border);background:var(--bg2);color:var(--cream);font-family:'Special Elite',serif;font-size:13px;width:170px}
.st{font-size:12px;color:var(--muted);padding:8px 0;font-family:'Oswald',sans-serif;letter-spacing:.05em}

/* ── Table ── */
.twrap{background:var(--bg2);border:1px solid var(--border);border-top:3px solid var(--red);border-radius:2px;overflow:hidden}
table{width:100%;border-collapse:collapse}
thead{background:var(--red3)}
th{color:var(--gold);font-family:'Oswald',sans-serif;font-size:11px;text-transform:uppercase;letter-spacing:.1em;padding:12px 16px;text-align:left;border-bottom:2px solid var(--gold)}
td{padding:13px 16px;border-bottom:1px solid var(--red4);font-size:13px}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--bg3)}
.tkr{font-family:'Oswald',sans-serif;font-weight:700;font-size:15px;color:var(--gold);letter-spacing:.05em}
.coy{color:var(--muted);font-size:12px;margin-top:2px}
.pbg{flex:1;height:6px;background:var(--red4);border-radius:1px;max-width:100px}
.pfg{height:6px;border-radius:1px}
.pcell{display:flex;align-items:center;gap:10px}
.tag{display:inline-block;padding:2px 10px;border-radius:2px;font-family:'Oswald',sans-serif;font-size:11px;font-weight:600;letter-spacing:.08em}
.tu{background:var(--gold);color:#3d0000}.td{background:#2d0000;color:#ff6b6b;border:1px solid #660000}.tn{background:var(--bg3);color:var(--muted)}
.ch{background:#3d2000;color:var(--gold);border:1px solid var(--gold2)}.cm{background:#3d2000;color:var(--gold2)}.cl{background:var(--bg3);color:var(--muted)}
.sc{display:flex;gap:5px;flex-wrap:wrap}
.sp{background:var(--bg3);border:1px solid var(--border);border-radius:2px;padding:2px 7px;font-size:11px;font-family:monospace;color:var(--muted)}
.nodata{text-align:center;padding:60px 20px;color:var(--muted)}
.nodata h3{font-family:'Oswald',sans-serif;font-size:20px;margin-bottom:8px;color:var(--gold);letter-spacing:.1em}
.spin{animation:spin 1s linear infinite;display:inline-block;color:var(--gold)}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Chat ── */
.chat{position:fixed;bottom:24px;right:24px;width:380px;background:var(--bg2);border:1px solid var(--border);border-top:3px solid var(--gold);border-radius:2px;box-shadow:0 20px 40px rgba(0,0,0,.8);z-index:1000}
.chdr{padding:12px 18px;border-bottom:1px solid var(--border);font-family:'Oswald',sans-serif;font-size:14px;font-weight:600;letter-spacing:.08em;color:var(--gold);display:flex;align-items:center;gap:8px;cursor:pointer;text-transform:uppercase;background:var(--red3);user-select:none}
.dot{width:8px;height:8px;background:var(--gold);border-radius:50%;box-shadow:0 0 6px var(--gold)}
.cmsgs{height:260px;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.cmsgs.hidden{display:none}
.msg{max-width:85%;padding:8px 12px;border-radius:2px;font-size:13px;line-height:1.5;font-family:'Special Elite',serif;word-break:break-word}
.mu{background:var(--red);color:var(--cream);align-self:flex-end;border-left:2px solid var(--gold)}
.ma{background:var(--bg3);color:var(--cream);align-self:flex-start;border-left:2px solid var(--muted)}
.cinrow{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px}
.cin{flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:2px;color:var(--cream);padding:8px 12px;font-size:13px;font-family:'Special Elite',serif;outline:none}
.cin:focus{border-color:var(--gold)}
.csend{background:var(--red);border:1px solid var(--gold2);color:var(--gold);border-radius:2px;padding:8px 14px;cursor:pointer;font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:.05em;text-transform:uppercase;flex-shrink:0}
.csend:hover{background:var(--red2)}
.csend:disabled{opacity:.5;cursor:not-allowed}

/* ── Hammer & sickle watermark ── */
.watermark{position:fixed;bottom:120px;left:30px;font-size:120px;color:rgba(204,0,0,.04);pointer-events:none;user-select:none;z-index:0}
.enr{display:none;background:var(--bg3);border-top:1px solid var(--border)}
.enr.open{display:table-row}
.enr td{padding:14px 20px}
.enr-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px}
.enr-card{background:var(--bg2);border:1px solid var(--border);border-radius:2px;padding:8px 10px}
.enr-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:3px;font-family:'Oswald',sans-serif}
.enr-val{font-size:13px;font-weight:600}
.enr-warn{background:var(--abg,#2d1f00);border:1px solid var(--amber,#f59e0b);border-radius:2px;padding:6px 10px;font-size:12px;color:var(--amber,#f59e0b);margin-bottom:8px}
.enr-scores{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
.enr-pill{font-size:11px;padding:2px 8px;border-radius:2px;background:var(--bg2);border:1px solid var(--border);font-family:monospace}
.pos{color:#4ade80;border-color:#14532d}.neg{color:#f87171;border-color:#450a0a}.neu{color:var(--muted)}
.enr-patterns{font-size:11px;color:var(--muted);line-height:1.6}
.enr-patterns .bp{color:#4ade80}.enr-patterns .br{color:#f87171}
.expand-btn{background:none;border:none;color:var(--muted);cursor:pointer;font-size:11px;padding:2px 6px;font-family:'Oswald',sans-serif;letter-spacing:.05em}
.expand-btn:hover{color:var(--gold)}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-inner">
    <span class="star-left">★</span>
    <div class="hdr-title">
      <h1>☭ &nbsp; Peoples Market Komitet &nbsp; ☭</h1>
      <div class="sub">Central Bureau of Weekly Stock Intelligence — Est. 2024</div>
    </div>
    <div class="regime-area">
      <div id="lu" style="margin-bottom:4px"></div>
      <div id="rm">Loading...</div>
    </div>
    <span class="star-right">★</span>
  </div>
</div>

<div class="stripe">
  <div class="stripe-inner">
    ★ &nbsp; Workers of the Market, Unite! &nbsp; ★ &nbsp; Seize the Means of Production of Alpha &nbsp; ★ &nbsp; Glory to the Five-Pillar Plan &nbsp; ★ &nbsp; No Stock Left Behind &nbsp; ★ &nbsp; The Proletariat Demands Liquidity &nbsp; ★ &nbsp; Forward to the Weekly Scan! &nbsp; ★ &nbsp; Death to Bearish Signals &nbsp; ★
  </div>
</div>

<div class="watermark">☭</div>

<div class="wrap">
  <div class="stats">
    <div class="scard"><div class="lbl">Stocks Analysed</div><div class="val bl" id="s0">—</div></div>
    <div class="scard"><div class="lbl">★ Bullish UP</div><div class="val gn" id="s1">—</div></div>
    <div class="scard"><div class="lbl">✗ Bearish DOWN</div><div class="val rd" id="s2">—</div></div>
    <div class="scard"><div class="lbl">High Confidence</div><div class="val am" id="s3">—</div></div>
  </div>

  <div class="toolbar">
    <button class="btn btn-p" onclick="runScan()" id="sbtn">★ Run Scan Now</button>
    <button class="btn" onclick="load()">↻ Refresh</button>
    <input class="srch" type="text" id="q" placeholder="Search ticker / company..." oninput="filter()">
    <select class="srch" id="fp" onchange="filter()">
      <option value="">All Directions</option>
      <option value="UP">★ Bullish Only</option>
      <option value="DOWN">✗ Bearish Only</option>
      <option value="NEUTRAL">◆ Neutral Only</option>
    </select>
    <span class="st" id="sm"></span>
  </div>

  <div class="twrap">
    <table>
      <thead><tr>
        <th></th><th>#</th><th>Stock</th><th>Direction</th>
        <th>Weekly Probability</th><th>Confidence</th>
        <th>Scores</th><th>Price</th><th>VIX / Sector</th>
      </tr></thead>
      <tbody id="tb">
        <tr><td colspan="9" class="nodata"><h3>☭ No Results Yet, Comrade ☭</h3><p>Click "Run Scan Now" to begin the Five-Year Plan.</p></td></tr>
      </tbody>
    </table>
  </div>
</div>

<div class="chat" id="chatbox">
  <div class="chdr" onclick="toggleChat()">
    <span class="dot"></span> ☭ Consult The Agent
    <span style="margin-left:auto;font-size:16px" id="ctic">▼</span>
  </div>
  <div class="cmsgs" id="cmsgs">
    <div class="msg ma">Greetings, Comrade. Ask me about any stock, sector, or I shall build you a portfolio worthy of the Motherland.</div>
  </div>
  <div class="cinrow" id="cinrow">
    <input class="cin" id="cin" placeholder="Is NVDA worthy of the people?" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send();}">
    <button class="csend" id="sendbtn" onclick="send()">Send</button>
  </div>
</div>

<script>
let all=[];

async function load(){
  const d=await(await fetch('/api/results')).json();
  all=d.reports||[];
  render(all);
  document.getElementById('s0').textContent=all.length;
  document.getElementById('s1').textContent=all.filter(r=>r.prediction==='UP').length;
  document.getElementById('s2').textContent=all.filter(r=>r.prediction==='DOWN').length;
  document.getElementById('s3').textContent=all.filter(r=>r.confidence==='HIGH').length;
  if(d.regime){
    const c={BULL:'bull',BEAR:'bear',NEUTRAL:'neutral'}[d.regime]||'neutral';
    document.getElementById('rm').innerHTML=`Market: <span class="badge ${c}">${d.regime}</span>`;
  }
  if(d.timestamp) document.getElementById('lu').textContent='Last scan: '+d.timestamp;
}

function render(rs){
  const tb=document.getElementById('tb');
  if(!rs.length){tb.innerHTML='<tr><td colspan="9" class="nodata"><h3>☭ No Results, Comrade ☭</h3><p>Run a scan to serve the Motherland.</p></td></tr>';return;}
  const srt=[...rs].sort((a,b)=>b.probability-a.probability);
  tb.innerHTML=srt.map((r,i)=>{
    const p=r.probability||0;
    const bc=p>=80?'#4ade80':p>=60?'#f5c518':p>=40?'#fbbf24':'#f87171';
    const pc={UP:'tu',DOWN:'td',NEUTRAL:'tn'}[r.prediction]||'tn';
    const cc={HIGH:'ch',MEDIUM:'cm',LOW:'cl'}[r.confidence]||'cl';
    const s=r.scores||{};
    const pl=r.prediction==='UP'?'▲ UP':r.prediction==='DOWN'?'▼ DOWN':'◆ HOLD';
    const enr=(r.reasoning||{}).enrichment||{};
    const vix=enr.vix||'—';
    const srs=enr.sector_rs||'—';
    const srsCol=srs.includes('+')?'#4ade80':srs.includes('-')?'#f87171':'var(--muted)';
    const ew=(r.reasoning||{}).earnings_warning;
    const earnFlag=ew?'<span style="color:#f59e0b;margin-left:4px">⚠</span>':'';

    // Build enrichment detail panel
    const si=enr.short_interest||'—';
    const ins=enr.insider_net||'—';
    const pos52=enr.pos_52w||'—';
    const dte=enr.days_to_earnings;
    const dteStr=(dte&&dte<999)?dte+' days':'N/A';

    const allScores=[
      ['Tech',s.technical||0],['Fund',s.fundamental||0],
      ['Sent',s.sentiment||0],['Pat',s.pattern||0],['ML',s.ml||0]
    ];
    const pillHtml=allScores.map(([l,v])=>{
      const cls=v>0.05?'pos':v<-0.05?'neg':'neu';
      return `<span class="enr-pill ${cls}">${l} ${v>=0?'+':''}${v.toFixed(2)}</span>`;
    }).join('');

    const pb=(r.reasoning||{}).patterns_bullish||[];
    const pbrr=(r.reasoning||{}).patterns_bearish||[];
    const patHtml=[
      ...pb.slice(0,3).map(x=>`<span class="bp">+ ${x}</span>`),
      ...pbrr.slice(0,2).map(x=>`<span class="br">- ${x}</span>`)
    ].join('<br>') || '<span style="color:var(--muted)">No patterns detected</span>';

    const warnHtml=ew?`<div class="enr-warn">⚠ ${ew}</div>`:'';
    const mlNote=(r.reasoning||{}).ml||'';

    const detailRow=`<tr class="enr" id="enr${i}">
      <td colspan="9">
        ${warnHtml}
        <div class="enr-grid">
          <div class="enr-card"><div class="enr-lbl">VIX</div><div class="enr-val" style="color:${vix>25?'#f87171':'#4ade80'}">${vix}</div></div>
          <div class="enr-card"><div class="enr-lbl">Sector RS vs SPY</div><div class="enr-val" style="color:${srsCol}">${srs}</div></div>
          <div class="enr-card"><div class="enr-lbl">Short Interest</div><div class="enr-val">${si}</div></div>
          <div class="enr-card"><div class="enr-lbl">Insider Net</div><div class="enr-val" style="color:${String(ins).includes('+')?'#4ade80':'#f87171'}">${ins}</div></div>
          <div class="enr-card"><div class="enr-lbl">52w Position</div><div class="enr-val">${pos52}</div></div>
          <div class="enr-card"><div class="enr-lbl">Days to Earnings</div><div class="enr-val" style="color:${dte<14?'#f59e0b':'var(--text)'}">${dteStr}</div></div>
          <div class="enr-card" style="grid-column:span 2"><div class="enr-lbl">ML Model</div><div class="enr-val" style="font-size:11px;font-weight:400">${mlNote}</div></div>
        </div>
        <div class="enr-scores">${pillHtml}</div>
        <div class="enr-patterns">${patHtml}</div>
      </td>
    </tr>`;

    const mainRow=`<tr onclick="toggleEnr(${i})" style="cursor:pointer">
      <td><button class="expand-btn" id="ebtn${i}">▶</button></td>
      <td style="color:var(--muted)">${i+1}</td>
      <td><div class="tkr">${r.ticker}${earnFlag}</div><div class="coy">${(r.company||'').slice(0,26)}</div></td>
      <td><span class="tag ${pc}">${pl}</span></td>
      <td><div class="pcell"><div class="pbg"><div class="pfg" style="width:${p}%;background:${bc}"></div></div><span style="font-weight:700;min-width:42px;color:${bc}">${p.toFixed(1)}%</span></div></td>
      <td><span class="tag ${cc}">${r.confidence}</span></td>
      <td><div class="sc">
        <span class="sp">T ${(s.technical||0)>=0?'+':''}${(s.technical||0).toFixed(2)}</span>
        <span class="sp">F ${(s.fundamental||0)>=0?'+':''}${(s.fundamental||0).toFixed(2)}</span>
        <span class="sp">ML ${(s.ml||0)>=0?'+':''}${(s.ml||0).toFixed(2)}</span>
      </div></td>
      <td style="font-weight:600">$${(r.price||0).toFixed(2)}</td>
      <td style="font-size:11px"><span style="color:${srsCol}">${srs}</span><br><span style="color:var(--muted)">VIX ${vix}</span></td>
    </tr>${detailRow}`;

    return mainRow;
  }).join('');
}

function toggleEnr(i){
  const row=document.getElementById('enr'+i);
  const btn=document.getElementById('ebtn'+i);
  if(!row)return;
  row.classList.toggle('open');
  btn.textContent=row.classList.contains('open')?'▼':'▶';
}

function filter(){
  const q=document.getElementById('q').value.toLowerCase();
  const p=document.getElementById('fp').value;
  render(all.filter(r=>(!q||r.ticker.toLowerCase().includes(q)||(r.company||'').toLowerCase().includes(q))&&(!p||r.prediction===p)));}

async function runScan(){
  const btn=document.getElementById('sbtn');
  btn.disabled=true; btn.textContent='★ Scanning...';
  document.getElementById('sm').innerHTML='<span class="spin">★</span> Peoples Scan has begun — results will appear when complete. You can still chat below.';
  try{
    const d=await(await fetch('/api/scan',{method:'POST'})).json();
    if(d.status==='started'){
      document.getElementById('sm').textContent='Scan running in background — check the terminal for progress. Page refreshes automatically.';
      // Poll every 10s for results
      const poll=setInterval(async()=>{
        const r=await(await fetch('/api/results')).json();
        if((r.reports||[]).length>0){
          clearInterval(poll);
          await load();
          document.getElementById('sm').textContent='Scan complete — '+r.count+' stocks loaded.';
          btn.disabled=false; btn.textContent='★ Run Scan Now';
        }
      },10000);
      // Safety: re-enable button after 5 min
      setTimeout(()=>{clearInterval(poll);btn.disabled=false;btn.textContent='★ Run Scan Now';},300000);
    } else if(d.status==='busy'){
      document.getElementById('sm').textContent='Scan already running — please wait.';
      btn.disabled=false; btn.textContent='★ Run Scan Now';
    } else {
      document.getElementById('sm').textContent='Error: '+(d.error||'unknown');
      btn.disabled=false; btn.textContent='★ Run Scan Now';
    }
  }catch(e){
    document.getElementById('sm').textContent='Failed to start scan: '+e.message;
    btn.disabled=false; btn.textContent='★ Run Scan Now';
  }
}

async function send(){
  const inp=document.getElementById('cin');
  const btn=document.getElementById('sendbtn');
  const msg=inp.value.trim();
  if(!msg)return;
  inp.value='';
  inp.disabled=true;
  btn.disabled=true;
  btn.textContent='...';
  addMsg(msg,'mu');
  const th=addMsg('☭ Consulting the Politburo...','ma');
  try{
    const res=await fetch('/api/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:msg})
    });
    if(!res.ok) throw new Error('Server returned '+res.status);
    const d=await res.json();
    const txt=(d.response||d.error||'Empty response.');
    
    // IMPORTANT: Note the double backslash here to escape for JavaScript
    th.innerHTML=txt.split('\\n').join('<br>');
    
  }catch(e){
    th.textContent='Error: '+e.message;
    th.style.color='#ff6b6b';
  }finally{
    inp.disabled=false;
    btn.disabled=false;
    btn.textContent='Send';
    inp.focus();
  }
}

function addMsg(t,cls){
  const b=document.getElementById('cmsgs'), el=document.createElement('div');
  el.className='msg '+cls; el.textContent=t;
  b.appendChild(el); b.scrollTop=b.scrollHeight; return el;
}

function toggleChat(){
  const msgs=document.getElementById('cmsgs');
  const row=document.getElementById('cinrow');
  const ico=document.getElementById('ctic');
  const hidden=msgs.classList.toggle('hidden');
  row.style.display=hidden?'none':'flex';
  ico.textContent=hidden?'▲':'▼';
}

load(); setInterval(load,60000);
</script>
</body>
</html>"""

# ─── State ─────────────────────────────────────────────────────────────────────

_results      = []
_chat_history = []
_scanning     = False


def _import_agent():
    """Try all possible names for the main trading agent module."""
    for name in ["main", "tradingbot", "trading_agent", "TradingBot", "Main"]:
        try:
            import importlib
            return importlib.import_module(name)
        except ImportError:
            continue
    raise ImportError(
        "Could not find the trading agent. Make sure one of these files is in the same folder as Dashboard.py: "
        "main.py, tradingbot.py, or trading_agent.py"
    )


def _load_from_disk():
    global _results
    path = os.path.join(RESULTS_DIR, "scan_results.json")
    if os.path.exists(path):
        try:
            with open(path) as f:
                _results = json.load(f)
            return
        except Exception:
            pass
    snaps = sorted(glob.glob(os.path.join(RESULTS_DIR, "weekly_*.json")), reverse=True)
    if snaps:
        try:
            with open(snaps[0]) as f:
                _results = json.load(f)
        except Exception:
            pass


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/results")
def api_results():
    _load_from_disk()
    regime    = _results[0].get("market_regime", "N/A") if _results else "N/A"
    timestamp = _results[0].get("timestamp", "")         if _results else ""
    return jsonify({"reports": _results, "regime": regime, "timestamp": timestamp, "count": len(_results)})

@app.route("/api/scan", methods=["POST"])
def api_scan():
    global _scanning, _results
    if _scanning:
        return jsonify({"status": "busy", "error": "Scan already running — check the terminal for progress."})

    def _run():
        global _scanning, _results
        _scanning = True
        try:
            print("[dashboard] Starting scan...", flush=True)
            agent_module = _import_agent()
            _results = agent_module.scan_watchlist(agent_module.DEFAULT_WATCHLIST, detailed=False, export=True)
            print(f"[dashboard] Scan complete — {len(_results)} stocks.", flush=True)
        except ImportError as e:
            print(f"[dashboard] IMPORT ERROR: {e}", flush=True)
        except Exception as e:
            print(f"[dashboard] Scan error: {e}", flush=True)
        finally:
            _scanning = False

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started", "message": "Scan started — watch the terminal for progress.", "count": 0})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    global _chat_history
    data = request.get_json(silent=True) or {}
    msg  = data.get("message", "").strip()
    print(f"[dashboard] Chat message received: {msg[:60]}", flush=True)
    if not msg:
        return jsonify({"response": "Please enter a message, Comrade."})
    try:
        agent_module = _import_agent()
        print("[dashboard] Calling run_agent...", flush=True)
        resp = agent_module.run_agent(msg, _chat_history)
        print(f"[dashboard] Agent responded ({len(resp)} chars)", flush=True)
        _chat_history.append({"role": "user",      "content": msg})
        _chat_history.append({"role": "assistant", "content": resp})
        if len(_chat_history) > 40:
            _chat_history = _chat_history[-40:]
        return jsonify({"response": resp})
    except ImportError as e:
        msg_err = f"Could not load trading agent: {e}"
        print(f"[dashboard] {msg_err}", flush=True)
        return jsonify({"response": msg_err})
    except Exception as e:
        print(f"[dashboard] Agent error: {e}", flush=True)
        return jsonify({"response": f"Agent error: {str(e)}"})


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    _load_from_disk()
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         Stock Agent Dashboard                            ║")
    print(f"║  Open: http://localhost:{port:<33}║")
    print("║  Ctrl+C to stop                                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)