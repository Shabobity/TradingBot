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
<title>Wall Street Alpha Terminal</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#0f172a;--primary2:#1e293b;--primary3:#334155;
  --accent:#3b82f6;--accent2:#2563eb;
  --bg:#020617;--bg2:#0f172a;--bg3:#1e293b;--border:#334155;
  --text:#f8fafc;--muted:#94a3b8;
  --up:#10b981; --down:#ef4444; --warn:#f59e0b;
}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}

/* ── Top banner ── */
.hdr{background:linear-gradient(180deg,#0f172a 0%,#020617 100%);border-bottom:2px solid var(--accent);padding:0;position:sticky;top:0;z-index:100}
.hdr-inner{max-width:1400px;margin:0 auto;padding:14px 28px;display:flex;align-items:center;gap:16px}
.star-left,.star-right{font-size:28px;color:var(--accent);text-shadow:0 0 12px rgba(59,130,246,.5);flex-shrink:0}
.hdr-title{flex:1;text-align:center}
.hdr-title h1{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;color:var(--text);letter-spacing:.05em;text-transform:uppercase;}
.hdr-title .sub{font-size:10px;color:var(--muted);letter-spacing:.15em;text-transform:uppercase;margin-top:4px}
.regime-area{font-size:12px;color:var(--muted);text-align:right;min-width:160px;font-family:'JetBrains Mono',monospace;}
.badge{display:inline-block;padding:3px 10px;font-family:'Inter',sans-serif;font-weight:600;letter-spacing:.05em;font-size:11px;border-radius:2px}
.bull{background:var(--up);color:#022c22}.bear{background:var(--down);color:#450a0a}.neutral{background:var(--primary3);color:var(--text)}

/* ── Ticker stripe ── */
.stripe{background:#000;border-bottom:1px solid var(--border);padding:8px 0;text-align:center;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--up);text-transform:uppercase;overflow:hidden}
.stripe-inner{white-space:nowrap;animation:marquee 25s linear infinite}
@keyframes marquee{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}

/* ── Layout ── */
.wrap{max-width:1400px;margin:0 auto;padding:24px 28px}

/* ── Stat cards ── */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:28px}
.scard{background:var(--bg2);border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:4px;padding:18px 20px;position:relative;overflow:hidden;box-shadow:0 4px 6px -1px rgba(0,0,0,.1)}
.scard::before{content:'$';position:absolute;right:16px;top:10px;font-size:40px;color:rgba(59,130,246,.05);font-family:'JetBrains Mono',monospace;font-weight:700}
.scard .lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}
.scard .val{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:700}
.gn{color:var(--up)}.rd{color:var(--down)}.bl{color:var(--accent)}.am{color:var(--warn)}

/* ── Toolbar ── */
.toolbar{display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.btn{padding:8px 20px;border-radius:4px;border:1px solid var(--border);background:var(--bg2);color:var(--text);font-family:'Inter',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;}
.btn:hover{background:var(--bg3);border-color:var(--accent)}
.btn-p{background:var(--accent);border-color:var(--accent2);color:#fff;}
.btn-p:hover{background:var(--accent2)}
.btn:disabled{opacity:.4;cursor:not-allowed}
input.srch, select.srch{padding:8px 14px;border-radius:4px;border:1px solid var(--border);background:var(--bg2);color:var(--text);font-family:'Inter',sans-serif;font-size:13px;width:220px;outline:none;}
select.srch{width:170px;}
input.srch:focus, select.srch:focus{border-color:var(--accent);}
input.srch::placeholder{color:var(--muted)}
.st{font-size:12px;color:var(--muted);padding:8px 0;font-family:'Inter',sans-serif;}

/* ── Table ── */
.twrap{background:var(--bg2);border:1px solid var(--border);border-radius:6px;overflow:hidden;box-shadow:0 10px 15px -3px rgba(0,0,0,.1)}
table{width:100%;border-collapse:collapse}
thead{background:var(--bg3)}
th{color:var(--text);font-family:'Inter',sans-serif;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;padding:12px 16px;text-align:left;border-bottom:1px solid var(--border)}
td{padding:13px 16px;border-bottom:1px solid var(--border);font-size:13px}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,0.02)}
.tkr{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:15px;color:var(--text);}
.coy{color:var(--muted);font-size:12px;margin-top:2px}
.pbg{flex:1;height:6px;background:var(--primary3);border-radius:3px;max-width:100px}
.pfg{height:6px;border-radius:3px}
.pcell{display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;}
.tag{display:inline-block;padding:3px 10px;border-radius:4px;font-family:'Inter',sans-serif;font-size:11px;font-weight:600;letter-spacing:.05em}
.tu{background:rgba(16,185,129,0.1);color:var(--up);border:1px solid rgba(16,185,129,0.2)}
.td{background:rgba(239,68,68,0.1);color:var(--down);border:1px solid rgba(239,68,68,0.2)}
.tn{background:var(--bg3);color:var(--muted)}
.ch{color:var(--up)}.cm{color:var(--warn)}.cl{color:var(--muted)}
.sc{display:flex;gap:5px;flex-wrap:wrap}
.sp{background:var(--bg3);border:1px solid var(--border);border-radius:4px;padding:2px 7px;font-size:11px;font-family:'JetBrains Mono',monospace;color:var(--muted)}
.nodata{text-align:center;padding:60px 20px;color:var(--muted)}
.nodata h3{font-family:'Inter',sans-serif;font-size:20px;margin-bottom:8px;color:var(--text);font-weight:600;}
.spin{animation:spin 1s linear infinite;display:inline-block;color:var(--accent)}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Chat ── */
.chat{position:fixed;bottom:24px;right:24px;width:380px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;box-shadow:0 25px 50px -12px rgba(0,0,0,.5);z-index:1000;overflow:hidden;}
.chdr{padding:14px 18px;background:var(--bg3);border-bottom:1px solid var(--border);font-family:'Inter',sans-serif;font-size:13px;font-weight:600;color:var(--text);display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none}
.dot{width:8px;height:8px;background:var(--up);border-radius:50%;box-shadow:0 0 8px var(--up)}
.cmsgs{height:280px;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:var(--bg)}
.cmsgs.hidden{display:none}
.msg{max-width:85%;padding:10px 14px;border-radius:6px;font-size:13px;line-height:1.5;font-family:'Inter',sans-serif;word-break:break-word}
.mu{background:var(--accent);color:#fff;align-self:flex-end;border-bottom-right-radius:2px;}
.ma{background:var(--bg3);color:var(--text);align-self:flex-start;border-bottom-left-radius:2px;border:1px solid var(--border);}
.cinrow{padding:12px;background:var(--bg2);border-top:1px solid var(--border);display:flex;gap:8px}
.cin{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);padding:10px 12px;font-size:13px;font-family:'Inter',sans-serif;outline:none}
.cin:focus{border-color:var(--accent)}
.csend{background:var(--accent);border:none;color:#fff;border-radius:4px;padding:0 16px;cursor:pointer;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;flex-shrink:0;transition:background .15s;}
.csend:hover{background:var(--accent2)}
.csend:disabled{opacity:.5;cursor:not-allowed}

/* ── Background watermark ── */
.watermark{position:fixed;bottom:100px;left:40px;font-size:180px;color:rgba(255,255,255,.01);pointer-events:none;user-select:none;z-index:0;font-family:serif;}
.enr{display:none;background:#05080f;border-top:1px solid var(--border)}
.enr.open{display:table-row}
.enr td{padding:16px 20px}
.enr-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px}
.enr-card{background:var(--bg2);border:1px solid var(--border);border-radius:4px;padding:10px 12px}
.enr-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px;font-weight:600;}
.enr-val{font-size:14px;font-family:'JetBrains Mono',monospace;font-weight:700}
.enr-warn{background:rgba(245,158,11,0.1);border:1px solid var(--warn);border-radius:4px;padding:8px 12px;font-size:12px;color:var(--warn);margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.enr-scores{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.enr-pill{font-size:11px;padding:3px 8px;border-radius:4px;background:var(--bg2);border:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-weight:600;}
.pos{color:var(--up);border-color:rgba(16,185,129,0.3)}.neg{color:var(--down);border-color:rgba(239,68,68,0.3)}.neu{color:var(--muted)}
.enr-patterns{font-size:12px;color:var(--muted);line-height:1.6;font-family:'Inter',sans-serif;}
.enr-patterns .bp{color:var(--up)}.enr-patterns .br{color:var(--down)}
.expand-btn{background:none;border:none;color:var(--muted);cursor:pointer;font-size:11px;padding:4px;border-radius:4px;}
.expand-btn:hover{color:var(--text);background:var(--bg3);}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-inner">
    <span class="star-left">🦅</span>
    <div class="hdr-title">
      <h1>Capital Edge Quant Terminal</h1>
      <div class="sub">Institutional Grade Alpha & Algorithmic Insights</div>
    </div>
    <div class="regime-area">
      <div id="lu" style="margin-bottom:4px"></div>
      <div id="rm">Loading Engine...</div>
    </div>
    <span class="star-right">📈</span>
  </div>
</div>

<div class="stripe">
  <div class="stripe-inner">
    $ &nbsp; GREED IS GOOD &nbsp; $ &nbsp; MAXIMIZE SHAREHOLDER VALUE &nbsp; $ &nbsp; INVISIBLE HAND AT WORK &nbsp; $ &nbsp; BUY LOW, SELL HIGH &nbsp; $ &nbsp; LIQUIDITY DEPLOYED &nbsp; $ &nbsp; GENERATING ALPHA &nbsp; $ &nbsp; COMPOUND INTEREST IS KING &nbsp; $
  </div>
</div>

<div class="watermark">$</div>

<div class="wrap">
  <div class="stats">
    <div class="scard"><div class="lbl">Equities Analyzed</div><div class="val bl" id="s0">—</div></div>
    <div class="scard"><div class="lbl">🚀 Bullish (Long)</div><div class="val gn" id="s1">—</div></div>
    <div class="scard"><div class="lbl">🩸 Bearish (Short)</div><div class="val rd" id="s2">—</div></div>
    <div class="scard"><div class="lbl">High Conviction</div><div class="val am" id="s3">—</div></div>
  </div>

  <div class="toolbar">
    <button class="btn btn-p" onclick="runScan()" id="sbtn">⚡ Initialize Scan</button>
    <button class="btn" onclick="load()">↻ Sync Data</button>
    <input class="srch" type="text" id="q" placeholder="Filter ticker / company..." oninput="filter()">
    <select class="srch" id="fp" onchange="filter()">
      <option value="">All Equities</option>
      <option value="UP">🚀 Long Only</option>
      <option value="DOWN">🩸 Short Only</option>
      <option value="NEUTRAL">◆ Hold / Neutral</option>
    </select>
    <span class="st" id="sm"></span>
  </div>

  <div class="twrap">
    <table>
      <thead><tr>
        <th></th><th>#</th><th>Asset</th><th>Action</th>
        <th>Win Probability</th><th>Conviction</th>
        <th>Quant Scores</th><th>Spot Price</th><th>VIX / Sector RS</th>
      </tr></thead>
      <tbody id="tb">
        <tr><td colspan="9" class="nodata"><h3>📉 Awaiting Market Data</h3><p>Click "Initialize Scan" to compute alpha generation.</p></td></tr>
      </tbody>
    </table>
  </div>
</div>

<div class="chat" id="chatbox">
  <div class="chdr" onclick="toggleChat()">
    <span class="dot"></span> 💼 Consult AI Broker
    <span style="margin-left:auto;font-size:16px" id="ctic">▼</span>
  </div>
  <div class="cmsgs" id="cmsgs">
    <div class="msg ma">Welcome, Investor. Ask me about any equity or sector, and let's maximize your portfolio's yield today.</div>
  </div>
  <div class="cinrow" id="cinrow">
    <input class="cin" id="cin" placeholder="Is NVDA a strong buy for Q3?" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send();}">
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
    document.getElementById('rm').innerHTML=`Macro: <span class="badge ${c}">${d.regime}</span>`;
  }
  if(d.timestamp) document.getElementById('lu').textContent='Last sync: '+d.timestamp;
}

function render(rs){
  const tb=document.getElementById('tb');
  if(!rs.length){tb.innerHTML='<tr><td colspan="9" class="nodata"><h3>📉 No Alpha Generated</h3><p>Run a quantitative scan to discover market inefficiencies.</p></td></tr>';return;}
  const srt=[...rs].sort((a,b)=>b.probability-a.probability);
  tb.innerHTML=srt.map((r,i)=>{
    const p=r.probability||0;
    const bc=p>=80?'#10b981':p>=60?'#f59e0b':p>=40?'#fbbf24':'#ef4444';
    const pc={UP:'tu',DOWN:'td',NEUTRAL:'tn'}[r.prediction]||'tn';
    const cc={HIGH:'ch',MEDIUM:'cm',LOW:'cl'}[r.confidence]||'cl';
    const s=r.scores||{};
    const pl=r.prediction==='UP'?'▲ LONG':r.prediction==='DOWN'?'▼ SHORT':'◆ HOLD';
    const enr=(r.reasoning||{}).enrichment||{};
    const vix=enr.vix||'—';
    const srs=enr.sector_rs||'—';
    const srsCol=srs.includes('+')?'#10b981':srs.includes('-')?'#ef4444':'var(--muted)';
    const ew=(r.reasoning||{}).earnings_warning;
    const earnFlag=ew?'<span style="color:var(--warn);margin-left:4px" title="Earnings Approaching">⚠</span>':'';

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
      ...pb.slice(0,3).map(x=>`<span class="bp">▲ ${x}</span>`),
      ...pbrr.slice(0,2).map(x=>`<span class="br">▼ ${x}</span>`)
    ].join('<br>') || '<span style="color:var(--muted)">No dominant patterns</span>';

    const warnHtml=ew?`<div class="enr-warn"><span>⚠</span> ${ew}</div>`:'';
    const mlNote=(r.reasoning||{}).ml||'';

    const detailRow=`<tr class="enr" id="enr${i}">
      <td colspan="9">
        ${warnHtml}
        <div class="enr-grid">
          <div class="enr-card"><div class="enr-lbl">VIX Level</div><div class="enr-val" style="color:${vix>25?'var(--down)':'var(--up)'}">${vix}</div></div>
          <div class="enr-card"><div class="enr-lbl">Sector vs SPY</div><div class="enr-val" style="color:${srsCol}">${srs}</div></div>
          <div class="enr-card"><div class="enr-lbl">Short Float</div><div class="enr-val">${si}</div></div>
          <div class="enr-card"><div class="enr-lbl">Insider Flows</div><div class="enr-val" style="color:${String(ins).includes('+')?'var(--up)':'var(--down)'}">${ins}</div></div>
          <div class="enr-card"><div class="enr-lbl">52W Position</div><div class="enr-val">${pos52}</div></div>
          <div class="enr-card"><div class="enr-lbl">Days to EPS</div><div class="enr-val" style="color:${dte<14?'var(--warn)':'var(--text)'}">${dteStr}</div></div>
          <div class="enr-card" style="grid-column:span 2"><div class="enr-lbl">AI Model Output</div><div class="enr-val" style="font-size:12px;font-weight:400;font-family:'Inter',sans-serif;">${mlNote}</div></div>
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
        <span class="sp">Q ${(s.ml||0)>=0?'+':''}${(s.ml||0).toFixed(2)}</span>
      </div></td>
      <td style="font-weight:600;font-family:'JetBrains Mono',monospace;">$${(r.price||0).toFixed(2)}</td>
      <td style="font-size:11px"><span style="color:${srsCol};font-weight:600">${srs}</span><br><span style="color:var(--muted)">VIX ${vix}</span></td>
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
  btn.disabled=true; btn.textContent='⚡ Processing...';
  document.getElementById('sm').innerHTML='<span class="spin">⟳</span> Quantitative Scan initiated — crunching variables. You can chat below during processing.';
  try{
    const d=await(await fetch('/api/scan',{method:'POST'})).json();
    if(d.status==='started'){
      document.getElementById('sm').textContent='Algorithms running in background — check the terminal for compute status. Auto-refreshing...';
      const poll=setInterval(async()=>{
        const r=await(await fetch('/api/results')).json();
        if((r.reports||[]).length>0){
          clearInterval(poll);
          await load();
          document.getElementById('sm').textContent='Scan complete — '+r.count+' equities processed.';
          btn.disabled=false; btn.textContent='⚡ Initialize Scan';
        }
      },10000);
      setTimeout(()=>{clearInterval(poll);btn.disabled=false;btn.textContent='⚡ Initialize Scan';},300000);
    } else if(d.status==='busy'){
      document.getElementById('sm').textContent='Compute engine currently occupied — please hold.';
      btn.disabled=false; btn.textContent='⚡ Initialize Scan';
    } else {
      document.getElementById('sm').textContent='Exception: '+(d.error||'unknown error');
      btn.disabled=false; btn.textContent='⚡ Initialize Scan';
    }
  }catch(e){
    document.getElementById('sm').textContent='Engine failure: '+e.message;
    btn.disabled=false; btn.textContent='⚡ Initialize Scan';
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
  const th=addMsg('📊 Consulting the Quants...','ma');
  try{
    const res=await fetch('/api/chat',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:msg})
    });
    if(!res.ok) throw new Error('Server exception '+res.status);
    const d=await res.json();
    const txt=(d.response||d.error||'Null output.');
    
    th.innerHTML=txt.split('\\n').join('<br>');
    
  }catch(e){
    th.textContent='System Error: '+e.message;
    th.style.color='var(--down)';
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
        return jsonify({"status": "busy", "error": "Scan already processing — check terminal for status."})

    def _run():
        global _scanning, _results
        _scanning = True
        try:
            print("[dashboard] Initializing quantitative scan...", flush=True)
            agent_module = _import_agent()
            _results = agent_module.scan_watchlist(agent_module.DEFAULT_WATCHLIST, detailed=False, export=True)
            print(f"[dashboard] Computation complete — {len(_results)} assets analyzed.", flush=True)
        except ImportError as e:
            print(f"[dashboard] IMPORT ERROR: {e}", flush=True)
        except Exception as e:
            print(f"[dashboard] Scan exception: {e}", flush=True)
        finally:
            _scanning = False

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started", "message": "Algorithms deployed — watch terminal for progress.", "count": 0})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    global _chat_history
    data = request.get_json(silent=True) or {}
    msg  = data.get("message", "").strip()
    print(f"[dashboard] Client inquiry received: {msg[:60]}", flush=True)
    if not msg:
        return jsonify({"response": "Please enter an inquiry, Investor."})
    try:
        agent_module = _import_agent()
        print("[dashboard] Querying AI Broker...", flush=True)
        resp = agent_module.run_agent(msg, _chat_history)
        print(f"[dashboard] Broker responded ({len(resp)} chars)", flush=True)
        _chat_history.append({"role": "user",      "content": msg})
        _chat_history.append({"role": "assistant", "content": resp})
        if len(_chat_history) > 40:
            _chat_history = _chat_history[-40:]
        return jsonify({"response": resp})
    except ImportError as e:
        msg_err = f"Failed to load AI Broker: {e}"
        print(f"[dashboard] {msg_err}", flush=True)
        return jsonify({"response": msg_err})
    except Exception as e:
        print(f"[dashboard] Broker exception: {e}", flush=True)
        return jsonify({"response": f"Broker exception: {str(e)}"})


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    _load_from_disk()
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         Wall Street Alpha Terminal                       ║")
    print(f"║  Access: http://localhost:{port:<32}║")
    print("║  Ctrl+C to terminate session                            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
