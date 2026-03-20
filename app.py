from flask import Flask, request, jsonify, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from brain import full_analysis
from macro import get_full_macro
from email_builder import build_email, build_subject

app = Flask(__name__)

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
ALERT_EMAIL   = os.environ.get("ALERT_EMAIL")

# ============================================
# MOBILE UI
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>XAUUSD Bot</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#080808;color:#fff;padding:16px;max-width:480px;margin:0 auto}
h1{color:#FFD700;font-size:22px;text-align:center;padding:16px 0 4px}
.sub{color:#666;font-size:11px;text-align:center;margin-bottom:16px}
.live{background:#111;border:1px solid #222;border-radius:12px;padding:14px;margin-bottom:12px}
.live h3{color:#FFD700;font-size:12px;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}
.row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;font-size:13px;border-bottom:1px solid #1a1a1a}
.row:last-child{border:none}
.up{color:#ff4444}.down{color:#00ff88}.neutral{color:#FFD700}
.card{background:#111;border:1px solid #222;border-radius:12px;padding:14px;margin-bottom:12px}
.card h3{color:#FFD700;font-size:12px;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px}
.dir-btns{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{padding:14px;border:none;border-radius:10px;font-size:15px;font-weight:bold;cursor:pointer;transition:all 0.15s;width:100%}
.sell-btn{background:#1a0000;color:#ff4444;border:2px solid #ff4444}
.sell-btn.on{background:#ff4444;color:#fff}
.buy-btn{background:#001a00;color:#00ff88;border:2px solid #00ff88}
.buy-btn.on{background:#00ff88;color:#000}
.tf-btns{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.tf-btn{padding:10px 0;background:#1a1a1a;color:#666;border:2px solid #2a2a2a;border-radius:8px;font-size:13px;font-weight:bold;cursor:pointer}
.tf-btn.on{background:#FFD700;color:#000;border-color:#FFD700}
.signals{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.sig{display:flex;align-items:center;gap:8px;background:#141414;padding:11px 10px;border-radius:9px;cursor:pointer;font-size:12px;border:1px solid #2a2a2a;transition:all 0.15s;user-select:none}
.sig.on{background:#0d1f0d;border-color:#00ff88;color:#00ff88}
.sig input{display:none}
.swing{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.input-wrap label{display:block;color:#666;font-size:11px;margin-bottom:5px}
.input-wrap input{width:100%;background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:10px;color:#fff;font-size:14px}
.analyze{width:100%;padding:18px;background:linear-gradient(135deg,#FFD700,#FF8C00);color:#000;font-size:17px;font-weight:bold;border:none;border-radius:12px;cursor:pointer;margin-top:4px;letter-spacing:0.5px}
.analyze:disabled{opacity:0.4;cursor:not-allowed}
.status{text-align:center;padding:14px;border-radius:10px;margin-top:12px;font-size:13px;line-height:1.6;display:none;white-space:pre-line}
.ok{background:#001a00;border:1px solid #00ff88;color:#00ff88;display:block}
.err{background:#1a0000;border:1px solid #ff4444;color:#ff4444;display:block}
.loading{background:#1a1500;border:1px solid #FFD700;color:#FFD700;display:block}
.killzone{text-align:center;padding:8px;border-radius:8px;font-size:12px;margin-bottom:12px}
.kz-high{background:#002200;border:1px solid #00ff88;color:#00ff88}
.kz-med{background:#1a1500;border:1px solid #FFD700;color:#FFD700}
.kz-low{background:#1a0000;border:1px solid #ff4444;color:#ff4444}
</style>
</head>
<body>
<h1>🥇 XAUUSD Bot</h1>
<p class="sub" id="time">Loading...</p>

<div id="killzone-bar" class="killzone kz-low">Checking killzone...</div>

<!-- LIVE MACRO -->
<div class="live">
  <h3>📡 Live Macro</h3>
  <div class="row"><span>Gold</span><span id="gold" class="neutral">...</span></div>
  <div class="row"><span>DXY</span><span id="dxy" class="neutral">...</span></div>
  <div class="row"><span>US10Y</span><span id="us10y" class="neutral">...</span></div>
  <div class="row"><span>Macro Bias</span><span id="bias" class="neutral">...</span></div>
</div>

<!-- DIRECTION -->
<div class="card">
  <h3>📊 Direction</h3>
  <div class="dir-btns">
    <button class="btn sell-btn" onclick="setDir('SELL')" id="s">🔴 SELL</button>
    <button class="btn buy-btn" onclick="setDir('BUY')" id="b">🟢 BUY</button>
  </div>
</div>

<!-- TIMEFRAME -->
<div class="card">
  <h3>⏱️ Timeframe</h3>
  <div class="tf-btns">
    <button class="tf-btn" onclick="setTF('1m')" id="t1">1M</button>
    <button class="tf-btn" onclick="setTF('5m')" id="t5">5M</button>
    <button class="tf-btn" onclick="setTF('15m')" id="t15">15M</button>
    <button class="tf-btn" onclick="setTF('1h')" id="t1h">1H</button>
  </div>
</div>

<!-- WHAT YOU SEE -->
<div class="card">
  <h3>👁️ What You See</h3>
  <div class="signals">
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="liquidity_sweep">💧 Liq. Sweep</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="ob_fvg">📦 OB / FVG</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="ema_cross">📈 EMA Cross</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="ma_ribbon">🎀 MA Ribbon</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="htf_confirms">🏛️ HTF Confirms</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="bos_choch">🔄 BOS/CHoCH</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="volume_spike">📊 Volume Spike</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="vpvr_level">🎯 VPVR Level</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="accum_distrib">🔁 Accum/Dist</label>
    <label class="sig" onclick="tog(this)"><input type="checkbox" value="displacement">⚡ Displacement</label>
  </div>
</div>

<!-- SWING LEVELS (optional) -->
<div class="card">
  <h3>📐 Swing Levels (Optional — for OTE)</h3>
  <div class="swing">
    <div class="input-wrap">
      <label>Swing High</label>
      <input type="number" id="sh" placeholder="e.g. 4895" step="0.1">
    </div>
    <div class="input-wrap">
      <label>Swing Low</label>
      <input type="number" id="sl" placeholder="e.g. 4712" step="0.1">
    </div>
  </div>
</div>

<button class="analyze" onclick="analyze()" id="go">🔍 ANALYZE NOW</button>
<div class="status" id="st"></div>

<script>
let dir=null, tf=null;

function updateTime(){
  const n=new Date();
  document.getElementById('time').textContent=n.toUTCString().slice(0,25)+' UTC';
}
updateTime(); setInterval(updateTime,1000);

function loadMacro(){
  fetch('/macro').then(r=>r.json()).then(d=>{
    if(d.gold) document.getElementById('gold').textContent='$'+d.gold;
    if(d.dxy){
      const el=document.getElementById('dxy');
      el.textContent=d.dxy.price+' '+d.dxy.arrow;
      el.className=d.dxy.bearish_gold?'up':'down';
    }
    if(d.us10y){
      const el=document.getElementById('us10y');
      el.textContent=d.us10y.yield+'% '+d.us10y.arrow;
      el.className=d.us10y.bearish_gold?'up':'down';
    }
    if(d.macro_bias){
      const el=document.getElementById('bias');
      el.textContent=d.macro_bias;
      el.className=d.macro_bias==='BEARISH'?'up':d.macro_bias==='BULLISH'?'down':'neutral';
    }
    if(d.killzone){
      const kz=document.getElementById('killzone-bar');
      kz.textContent=d.killzone.emoji+' '+d.killzone.zone+' — '+d.killzone.message;
      kz.className='killzone '+(d.killzone.quality==='HIGH'?'kz-high':d.killzone.quality==='MEDIUM'?'kz-med':'kz-low');
    }
  }).catch(e=>console.log(e));
}
loadMacro(); setInterval(loadMacro,60000);

function setDir(d){
  dir=d;
  document.getElementById('s').classList.toggle('on',d==='SELL');
  document.getElementById('b').classList.toggle('on',d==='BUY');
}

function setTF(t){
  tf=t;
  ['1m','5m','15m','1h'].forEach(x=>{
    document.getElementById('t'+x.replace('m','').replace('h','h')).classList.toggle('on',x===t);
  });
  // fix id mapping
  document.getElementById('t1').classList.toggle('on',t==='1m');
  document.getElementById('t5').classList.toggle('on',t==='5m');
  document.getElementById('t15').classList.toggle('on',t==='15m');
  document.getElementById('t1h').classList.toggle('on',t==='1h');
}

function tog(label){
  label.classList.toggle('on');
  const cb=label.querySelector('input');
  cb.checked=!cb.checked;
}

function getSigs(){
  return Array.from(document.querySelectorAll('input[type=checkbox]:checked')).map(c=>c.value);
}

function status(msg,type){
  const el=document.getElementById('st');
  el.textContent=msg; el.className='status '+type;
}

function analyze(){
  if(!dir){status('❌ Select SELL or BUY first','err');return}
  if(!tf){status('❌ Select a timeframe','err');return}
  const sigs=getSigs();
  if(!sigs.length){status('❌ Select at least one signal','err');return}

  const sh=document.getElementById('sh').value;
  const sl=document.getElementById('sl').value;

  status('🔍 Fetching live data & analyzing...','loading');
  document.getElementById('go').disabled=true;

  fetch('/analyze',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      direction:dir, timeframe:tf, signals:sigs,
      swing_high:sh?parseFloat(sh):null,
      swing_low:sl?parseFloat(sl):null
    })
  }).then(r=>r.json()).then(d=>{
    document.getElementById('go').disabled=false;
    if(d.success){
      status(
        '✅ Analysis sent to Gmail!\n\n'+
        'Score: '+d.score+'/10\n'+
        'Verdict: '+d.verdict+'\n'+
        'Entry: $'+d.entry+'\n'+
        'Stop: $'+d.sl+'\n'+
        'TP1: $'+d.tp1,
        'ok'
      );
    } else {
      status('❌ Error: '+(d.error||'Unknown'),'err');
    }
  }).catch(e=>{
    document.getElementById('go').disabled=false;
    status('❌ Connection error','err');
  });
}
</script>
</body>
</html>
"""

# ============================================
# SEND EMAIL
# ============================================
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = ALERT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        s.sendmail(GMAIL_ADDRESS, ALERT_EMAIL, msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ============================================
# ROUTES
# ============================================
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/macro")
def macro_route():
    from brain import check_killzone
    from datetime import datetime, timezone
    data = get_full_macro()
    now  = datetime.now(timezone.utc)
    data["killzone"] = check_killzone(now.hour, now.minute)
    return jsonify(data)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        d          = request.get_json()
        direction  = d.get("direction")
        timeframe  = d.get("timeframe")
        signals    = d.get("signals", [])
        swing_high = d.get("swing_high")
        swing_low  = d.get("swing_low")

        macro    = get_full_macro()
        analysis = full_analysis(
            direction, timeframe, signals,
            macro, swing_high, swing_low
        )

        subject = build_subject(analysis)
        body    = build_email(analysis)
        sent    = send_email(subject, body)

        levels = analysis["levels"]
        return jsonify({
            "success": sent,
            "score":   analysis["score"],
            "verdict": analysis["verdict"],
            "entry":   levels["entry"],
            "sl":      levels["sl"],
            "tp1":     levels["tp1"]
        })
    except Exception as e:
        print(f"Analyze error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "running ✅"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
