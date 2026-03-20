"""
BOT BRAIN — ICT/SMC Logic Engine
Handles all market situations intelligently
Based on real ICT concepts: OTE, Killzones, Liquidity, Displacement
"""

from datetime import datetime, timezone
import pytz

# ============================================
# KILLZONE CHECKER
# Based on ICT killzone research:
# London: 02:00-05:00 AM NY time (07:00-10:00 GMT)
# NY Open: 07:00-10:00 AM NY time (12:00-15:00 GMT)
# London Close: 10:00-12:00 AM NY time
# Asian: 08:00-10:00 PM NY time (avoid for gold)
# ============================================
def check_killzone(utc_hour, utc_minute):
    """
    Returns which killzone we are in right now
    All times converted to UTC for simplicity
    """
    time_decimal = utc_hour + utc_minute / 60

    # London Killzone: 07:00-10:00 UTC
    if 7.0 <= time_decimal < 10.0:
        return {
            "zone": "LONDON",
            "quality": "HIGH",
            "emoji": "🇬🇧",
            "message": "London Killzone — Highest probability for gold setups",
            "valid": True
        }

    # NY Open Killzone: 12:00-15:00 UTC
    elif 12.0 <= time_decimal < 15.0:
        return {
            "zone": "NEW_YORK",
            "quality": "HIGH",
            "emoji": "🇺🇸",
            "message": "NY Open Killzone — Second best for gold, watch US data",
            "valid": True
        }

    # London Close: 14:00-16:00 UTC
    elif 14.0 <= time_decimal < 16.0:
        return {
            "zone": "LONDON_CLOSE",
            "quality": "MEDIUM",
            "emoji": "🔔",
            "message": "London Close — Valid for scalps, momentum fading",
            "valid": True
        }

    # NY Silver Bullet: 15:00-16:00 UTC (10-11 AM NY)
    elif 15.0 <= time_decimal < 16.0:
        return {
            "zone": "SILVER_BULLET",
            "quality": "HIGH",
            "emoji": "🥈",
            "message": "ICT Silver Bullet window — High quality OTE setups",
            "valid": True
        }

    # Asian session: 00:00-06:00 UTC — avoid for gold
    elif 0.0 <= time_decimal < 6.0:
        return {
            "zone": "ASIAN",
            "quality": "LOW",
            "emoji": "🌏",
            "message": "Asian session — Low probability for gold, choppy and fake signals",
            "valid": False
        }

    # Dead zones
    else:
        return {
            "zone": "OFF_HOURS",
            "quality": "LOW",
            "emoji": "😴",
            "message": "Outside killzones — Lower probability setup",
            "valid": False
        }


# ============================================
# MARKET SITUATION DETECTOR
# ============================================
def detect_situation(signals, macro, htf_bias, killzone):
    """
    Detects which of 4 market situations we are in
    Each situation has different rules
    """

    has_sweep      = "liquidity_sweep" in signals
    has_choch      = "bos_choch" in signals
    has_ob_fvg     = "ob_fvg" in signals
    has_ribbon     = "ma_ribbon" in signals
    has_ema        = "ema_cross" in signals
    has_htf        = "htf_confirms" in signals
    has_volume     = "volume_spike" in signals
    has_vpvr       = "vpvr_level" in signals
    has_accum      = "accum_distrib" in signals

    macro_bias = macro.get("macro_bias", "NEUTRAL")
    dxy_bear   = macro.get("dxy", {}).get("bearish_gold", False)
    y_bear     = macro.get("us10y", {}).get("bearish_gold", False)

    # SITUATION 1: TRENDING MARKET
    # Ribbon aligned + HTF confirms + strong macro
    if has_ribbon and has_htf and (dxy_bear or y_bear):
        return {
            "situation": "TRENDING",
            "emoji": "📉📈",
            "description": "Market is in a clear trend",
            "rules": [
                "Trade WITH the trend only",
                "Wait for pullback to OB or FVG",
                "Liquidity sweep MUST happen first",
                "OTE entry at 61.8-78.6% fib",
                "Target: next HTF liquidity pool"
            ],
            "required_signals": ["liquidity_sweep", "ob_fvg", "htf_confirms"],
            "weight_multiplier": 1.3
        }

    # SITUATION 2: RANGING MARKET
    # No clear ribbon + no strong macro
    elif not has_ribbon and not has_htf:
        return {
            "situation": "RANGING",
            "emoji": "↔️",
            "description": "Market is ranging between levels",
            "rules": [
                "Sell at range HIGH after sweep",
                "Buy at range LOW after sweep",
                "VPVR POC = middle magnet, avoid",
                "Tight SL = range can break anytime",
                "Target = opposite range extreme"
            ],
            "required_signals": ["liquidity_sweep", "vpvr_level", "bos_choch"],
            "weight_multiplier": 0.9
        }

    # SITUATION 3: REVERSAL FORMING
    # CHoCH + sweep + accum/distrib signals
    elif has_choch and has_sweep:
        return {
            "situation": "REVERSAL",
            "emoji": "🔄",
            "description": "Potential reversal forming after trend exhaustion",
            "rules": [
                "Liquidity sweep of previous extreme = REQUIRED",
                "Strong displacement candle after sweep = REQUIRED",
                "CHoCH on 15M/1H = confirmation",
                "Enter at FVG created by displacement",
                "Smaller position = still risky"
            ],
            "required_signals": ["liquidity_sweep", "bos_choch", "ob_fvg"],
            "weight_multiplier": 1.1
        }

    # SITUATION 4: DEFAULT — STANDARD SETUP
    else:
        return {
            "situation": "STANDARD",
            "emoji": "📊",
            "description": "Standard ICT setup",
            "rules": [
                "Check HTF bias before entering",
                "Wait for killzone window",
                "Liquidity sweep improves probability",
                "OB or FVG = entry zone",
                "Displacement = confirmation"
            ],
            "required_signals": ["ob_fvg", "htf_confirms"],
            "weight_multiplier": 1.0
        }


# ============================================
# OTE CALCULATOR
# ICT Optimal Trade Entry: 61.8% - 78.6%
# Precise level: 70.5%
# ============================================
def calculate_ote(swing_high, swing_low, direction):
    """
    Calculate ICT OTE levels for entry
    For SELL: fib drawn from low to high, enter at 61.8-78.6% pullback
    For BUY:  fib drawn from high to low, enter at 61.8-78.6% pullback
    """
    full_range = abs(swing_high - swing_low)

    if direction == "SELL":
        # Price moved UP, now pulling back DOWN
        # Entry in premium zone (above 50%)
        ote_precise = round(swing_high - (full_range * 0.705), 2)
        ote_high    = round(swing_high - (full_range * 0.618), 2)
        ote_low     = round(swing_high - (full_range * 0.786), 2)
        sl_level    = round(swing_high + (full_range * 0.1), 2)   # above swing high
    else:
        # Price moved DOWN, now pulling back UP
        # Entry in discount zone (below 50%)
        ote_precise = round(swing_low + (full_range * 0.705), 2)
        ote_high    = round(swing_low + (full_range * 0.786), 2)
        ote_low     = round(swing_low + (full_range * 0.618), 2)
        sl_level    = round(swing_low - (full_range * 0.1), 2)    # below swing low

    return {
        "ote_precise": ote_precise,   # 70.5% — most accurate
        "ote_zone_high": ote_high,    # 61.8%
        "ote_zone_low": ote_low,      # 78.6%
        "sl_suggestion": sl_level,
        "explanation": f"OTE zone: ${ote_low} - ${ote_high} | Precise: ${ote_precise}"
    }


# ============================================
# DISPLACEMENT CHECKER
# Strong candle = real institutional move
# Weak candle = fake sweep
# ============================================
def check_displacement(signals):
    """
    Checks if there's evidence of displacement
    (strong candle after liquidity sweep)
    """
    has_sweep  = "liquidity_sweep" in signals
    has_volume = "volume_spike" in signals
    has_choch  = "bos_choch" in signals

    if has_sweep and has_volume and has_choch:
        return {
            "confirmed": True,
            "quality": "STRONG",
            "message": "✅ Strong displacement — Sweep + Volume + Structure shift"
        }
    elif has_sweep and (has_volume or has_choch):
        return {
            "confirmed": True,
            "quality": "MODERATE",
            "message": "⚠️ Moderate displacement — Missing one confirmation"
        }
    elif has_sweep and not has_volume and not has_choch:
        return {
            "confirmed": False,
            "quality": "WEAK",
            "message": "❌ Weak — Sweep WITHOUT displacement = possible fake!"
        }
    else:
        return {
            "confirmed": False,
            "quality": "NONE",
            "message": "❌ No sweep detected — Entry may be premature"
        }


# ============================================
# JUDAS SWING DETECTOR
# Fake move to trap retail before real move
# ============================================
def detect_judas_swing(direction, killzone, signals):
    """
    Judas swing = fake move opposite to daily bias
    Common in London and NY opens
    Look for this to get swept THEN enter real direction
    """
    in_killzone = killzone.get("valid", False)
    has_sweep   = "liquidity_sweep" in signals
    has_htf     = "htf_confirms" in signals

    if in_killzone and has_sweep and has_htf:
        return {
            "likely": True,
            "message": f"🎭 Judas Swing likely in {killzone['zone']} — Price swept stops, now expect real move {direction}"
        }
    elif in_killzone and has_sweep:
        return {
            "likely": True,
            "message": f"🎭 Possible Judas Swing — Sweep in killzone detected"
        }
    else:
        return {
            "likely": False,
            "message": "No Judas Swing pattern detected"
        }


# ============================================
# FAILURE REASON DETECTOR
# Why might this trade FAIL?
# ============================================
def detect_failure_reasons(signals, macro, direction, killzone, situation):
    """
    Based on real research on why ICT trades fail
    Returns list of warnings
    """
    warnings = []

    # FAILURE 1: No liquidity sweep
    if "liquidity_sweep" not in signals:
        warnings.append("🚨 NO SWEEP: Entering without liquidity sweep = premature entry, likely to get stopped")

    # FAILURE 2: No displacement
    if "liquidity_sweep" in signals and "volume_spike" not in signals:
        warnings.append("⚠️ NO DISPLACEMENT: Sweep without strong candle = possible fake, wait for confirmation")

    # FAILURE 3: Against HTF bias
    if "htf_confirms" not in signals:
        warnings.append("⚠️ HTF NOT CONFIRMED: Trading against higher timeframe = fighting smart money")

    # FAILURE 4: Outside killzone
    if not killzone.get("valid"):
        warnings.append(f"⚠️ OUTSIDE KILLZONE: {killzone['zone']} session = lower probability, more fake signals")

    # FAILURE 5: Macro conflict
    dxy_bear = macro.get("dxy", {}).get("bearish_gold", False)
    y_bear   = macro.get("us10y", {}).get("bearish_gold", False)

    if direction == "SELL" and not dxy_bear and not y_bear:
        warnings.append("⚠️ MACRO CONFLICT: DXY and yields not confirming sell — gold has macro support")
    elif direction == "BUY" and dxy_bear and y_bear:
        warnings.append("🚨 MACRO CONFLICT: DXY above 100 + yields rising = strong headwind for longs")

    # FAILURE 6: Ranging market trying to trend trade
    if situation["situation"] == "RANGING" and "ma_ribbon" in signals:
        warnings.append("⚠️ RANGING MARKET: MA Ribbon signals unreliable in range — use range extremes only")

    # FAILURE 7: No OB or FVG
    if "ob_fvg" not in signals:
        warnings.append("⚠️ NO OB/FVG: Missing institutional level = random entry, no edge")

    # FAILURE 8: No EMA confirmation
    if "ema_cross" not in signals and "ma_ribbon" not in signals:
        warnings.append("⚠️ NO MOMENTUM CONFIRMATION: EMA and ribbon both missing")

    return warnings


# ============================================
# SMART SCORER
# Scores differently based on situation
# ============================================
def smart_score(signals, macro, direction, killzone, situation, displacement):
    """
    Scores the setup intelligently based on situation
    Not just a simple checklist
    """
    score   = 0
    reasons = []

    # Base macro score (2 points)
    dxy_bear = macro.get("dxy", {}).get("bearish_gold", False)
    y_bear   = macro.get("us10y", {}).get("bearish_gold", False)

    if direction == "SELL":
        if dxy_bear:
            score += 1
            reasons.append("✅ DXY above 100 = bearish gold confirmed")
        if y_bear:
            score += 1
            reasons.append("✅ US10Y above 4% rising = bearish gold confirmed")
    else:
        if not dxy_bear:
            score += 1
            reasons.append("✅ DXY falling/below 100 = gold supported")
        if not y_bear:
            score += 1
            reasons.append("✅ Yields low/falling = gold supported")

    # Killzone score (1 point)
    if killzone.get("valid"):
        score += 1
        reasons.append(f"✅ In {killzone['zone']} killzone = high probability window")

    # Liquidity sweep (2 points — most important)
    if "liquidity_sweep" in signals:
        score += 2
        reasons.append("✅ Liquidity sweep confirmed = fuel collected, real move likely")

    # Displacement (1 point)
    if displacement["confirmed"]:
        score += 1
        reasons.append(f"✅ Displacement: {displacement['quality']} = institutional intent")

    # OB/FVG at entry (1 point)
    if "ob_fvg" in signals:
        score += 1
        reasons.append("✅ OB/FVG level = institutional order zone")

    # HTF confirmation (1 point)
    if "htf_confirms" in signals:
        score += 1
        reasons.append("✅ HTF structure confirms direction")

    # BOS/CHoCH (1 point)
    if "bos_choch" in signals:
        score += 1
        reasons.append("✅ BOS/CHoCH = structure shift confirmed")

    # Volume spike (1 point)
    if "volume_spike" in signals:
        score += 1
        reasons.append("✅ Volume spike = conviction behind move")

    # VPVR confluence (1 point)
    if "vpvr_level" in signals:
        score += 1
        reasons.append("✅ VPVR level = big orders sitting here")

    # MA Ribbon (1 point)
    if "ma_ribbon" in signals:
        score += 1
        reasons.append("✅ MA Ribbon aligned = multi-timeframe momentum")

    # EMA Cross (1 point)
    if "ema_cross" in signals:
        score += 1
        reasons.append("✅ EMA cross = entry momentum confirmed")

    # Apply situation multiplier
    raw_score     = score
    adjusted      = round(score * situation["weight_multiplier"])
    max_possible  = round(13 * situation["weight_multiplier"])

    # Normalize to /10
    normalized = min(10, round((adjusted / max_possible) * 10))

    return normalized, raw_score, reasons


# ============================================
# TRADE LEVEL CALCULATOR
# ICT style: SL above/below OTE level
# ============================================
def calculate_trade_levels(price, direction, score, swing_high=None, swing_low=None):
    """
    Calculate precise trade levels
    SL based on OTE + account size
    """
    # SL pips based on confidence
    if score >= 8:
        sl_pips = 15
    elif score >= 6:
        sl_pips = 18
    elif score >= 4:
        sl_pips = 22
    else:
        sl_pips = 25

    # OTE levels if swing data available
    ote = None
    if swing_high and swing_low:
        ote = calculate_ote(swing_high, swing_low, direction)
        entry = ote["ote_precise"]
    else:
        entry = price

    if direction == "SELL":
        sl  = round(entry + sl_pips, 2)
        tp1 = round(entry - sl_pips * 2, 2)   # 2R
        tp2 = round(entry - sl_pips * 4, 2)   # 4R
        tp3 = round(entry - sl_pips * 7, 2)   # 7R
    else:
        sl  = round(entry - sl_pips, 2)
        tp1 = round(entry + sl_pips * 2, 2)
        tp2 = round(entry + sl_pips * 4, 2)
        tp3 = round(entry + sl_pips * 7, 2)

    # $35 account, 2% risk
    risk_dollar    = round(35 * 0.02, 2)
    pip_value      = 0.10  # per 0.01 lot per pip
    lots           = round(min(risk_dollar / (sl_pips * pip_value) * 0.01, 0.03), 2)
    actual_risk    = round(lots * sl_pips * pip_value / 0.01, 2)

    return {
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "sl_pips": sl_pips,
        "lots": lots,
        "risk_dollar": actual_risk,
        "ote": ote
    }


# ============================================
# MASTER ANALYZER
# Puts everything together
# ============================================
def full_analysis(direction, timeframe, signals, macro, swing_high=None, swing_low=None):
    """
    Master function — runs complete ICT analysis
    Returns everything needed for the alert
    """
    now      = datetime.now(timezone.utc)
    killzone = check_killzone(now.hour, now.minute)
    situation = detect_situation(signals, macro, direction, killzone)
    displacement = check_displacement(signals)
    judas = detect_judas_swing(direction, killzone, signals)
    failures = detect_failure_reasons(signals, macro, direction, killzone, situation)
    score, raw_score, reasons = smart_score(
        signals, macro, direction, killzone, situation, displacement
    )
    price  = macro.get("gold", 0)
    levels = calculate_trade_levels(price, direction, score, swing_high, swing_low)

    # Final verdict
    if score >= 8:
        verdict   = "VERY STRONG ✅"
        trade_msg = "High confidence setup. Consider full position."
        color     = "🟢"
    elif score >= 6:
        verdict   = "GOOD SETUP ✅"
        trade_msg = "Solid setup. Normal position size."
        color     = "🟡"
    elif score >= 4:
        verdict   = "WEAK SETUP ⚠️"
        trade_msg = "Missing key signals. Half size or wait."
        color     = "🟠"
    else:
        verdict   = "SKIP ❌"
        trade_msg = "Too many missing pieces. Do not trade."
        color     = "🔴"

    return {
        "direction":    direction,
        "timeframe":    timeframe,
        "price":        price,
        "killzone":     killzone,
        "situation":    situation,
        "displacement": displacement,
        "judas":        judas,
        "score":        score,
        "raw_score":    raw_score,
        "reasons":      reasons,
        "failures":     failures,
        "levels":       levels,
        "verdict":      verdict,
        "trade_msg":    trade_msg,
        "color":        color,
        "macro":        macro,
        "timestamp":    now.strftime("%b %d %Y %H:%M UTC")
    }
