"""
EMAIL BUILDER
Formats analysis exactly like our chart reading sessions
"""

def build_email(analysis):
    d         = analysis
    direction = d["direction"]
    emoji     = "🔴 SELL" if direction == "SELL" else "🟢 BUY"
    macro     = d["macro"]
    dxy       = macro.get("dxy", {})
    us10y     = macro.get("us10y", {})
    levels    = d["levels"]
    situation = d["situation"]
    killzone  = d["killzone"]
    disp      = d["displacement"]
    judas     = d["judas"]
    ote       = levels.get("ote")

    body = f"""
╔══════════════════════════════════╗
     🥇 XAUUSD SIGNAL ANALYSIS
╚══════════════════════════════════╝

⏰ {d['timestamp']}
📊 Timeframe: {d['timeframe'].upper()}
💰 Gold Price: ${d['price']}
Direction: {emoji}
Score: {d['score']}/10

══════════════════════════════════
📖 LEVEL 1 — NARRATIVE
══════════════════════════════════
DXY:    {dxy.get('price','N/A')} {dxy.get('arrow','')}  {'⚠️ Above 100 = bearish gold' if dxy.get('above_100') else '✅ Below 100 = gold supported'}
US10Y:  {us10y.get('yield','N/A')}% {us10y.get('arrow','')}  {'⚠️ Above 4% rising = bearish gold' if us10y.get('bearish_gold') else '✅ Yields supportive for gold'}
Macro Bias: {macro.get('macro_bias','N/A')}

══════════════════════════════════
📊 LEVEL 2 — MARKET SITUATION
══════════════════════════════════
Situation: {situation['emoji']} {situation['situation']}
{situation['description']}

Rules for this situation:
{chr(10).join('→ ' + r for r in situation['rules'])}

══════════════════════════════════
⏱️ KILLZONE ANALYSIS
══════════════════════════════════
{killzone['emoji']} Zone: {killzone['zone']}
Quality: {killzone['quality']}
{killzone['message']}

══════════════════════════════════
💧 LIQUIDITY & DISPLACEMENT
══════════════════════════════════
Displacement: {disp['message']}
{judas['message']}

══════════════════════════════════
✅ CONFIRMATIONS ({len(d['reasons'])})
══════════════════════════════════
{chr(10).join(d['reasons']) if d['reasons'] else 'None confirmed'}

══════════════════════════════════
⚠️ WARNINGS & FAILURE RISKS
══════════════════════════════════
{chr(10).join(d['failures']) if d['failures'] else '✅ No major warnings'}

══════════════════════════════════
🎯 OTE ENTRY ZONE (ICT Style)
══════════════════════════════════
{ote['explanation'] if ote else 'No swing data provided — using current price'}
Entry at 70.5% Fibonacci = Most precise ICT level

══════════════════════════════════
💰 TRADE LEVELS ($35 Account)
══════════════════════════════════
Entry:    ${levels['entry']}
Stop:     ${levels['sl']} ({levels['sl_pips']} pips)
Target 1: ${levels['tp1']} ({levels['sl_pips']*2} pips = 2R) → Take 50% here
Target 2: ${levels['tp2']} ({levels['sl_pips']*4} pips = 4R) → Move SL to BE
Target 3: ${levels['tp3']} ({levels['sl_pips']*7} pips = 7R) → Let run

Lot Size: {levels['lots']} lots
Risk:     ${levels['risk_dollar']} ({round(levels['risk_dollar']/35*100,1)}% of $35)

══════════════════════════════════
📈 FINAL VERDICT
══════════════════════════════════
{d['color']} {d['verdict']}
{d['trade_msg']}

══════════════════════════════════
📋 TRADE MANAGEMENT RULES
══════════════════════════════════
→ Hit TP1: Close 50%, move SL to breakeven
→ Hit TP2: Close 25%, let 25% run to TP3
→ If macro changes before entry: CANCEL
→ If spread widens > 30 pips: SKIP
→ If news in 30 mins: WAIT or CANCEL
→ Never move SL wider — ever
→ Max 2 trades open at same time
→ 3 losses today = stop trading

══════════════════════════════════
"""
    return body


def build_subject(analysis):
    direction = analysis["direction"]
    emoji     = "SELL 🔴" if direction == "SELL" else "BUY 🟢"
    score     = analysis["score"]
    verdict   = analysis["verdict"].split()[0]
    price     = analysis["price"]
    zone      = analysis["killzone"]["zone"]
    return f"🥇 XAUUSD {emoji} | Score {score}/10 | {verdict} | ${price} | {zone}"
