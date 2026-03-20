"""
MACRO FETCHER
Gets live DXY, US10Y, gold price from Yahoo Finance
"""
import yfinance as yf

def get_gold_price():
    try:
        gc = yf.Ticker("GC=F")
        d  = gc.history(period="1d", interval="5m")
        if not d.empty:
            return round(float(d['Close'].iloc[-1]), 2)
    except Exception as e:
        print(f"Gold price error: {e}")
    return None

def get_dxy():
    try:
        dxy = yf.Ticker("DX-Y.NYB")
        d   = dxy.history(period="2d", interval="15m")
        if not d.empty:
            price  = round(float(d['Close'].iloc[-1]), 3)
            prev   = round(float(d['Close'].iloc[-2]), 3)
            rising = price > prev
            return {
                "price":        price,
                "change":       round(price - prev, 3),
                "arrow":        "⬆️" if rising else "⬇️",
                "above_100":    price > 100,
                "bearish_gold": price > 100 and rising
            }
    except Exception as e:
        print(f"DXY error: {e}")
    return None

def get_us10y():
    try:
        tnx = yf.Ticker("^TNX")
        d   = tnx.history(period="2d", interval="15m")
        if not d.empty:
            y      = round(float(d['Close'].iloc[-1]), 3)
            prev   = round(float(d['Close'].iloc[-2]), 3)
            rising = y > prev
            return {
                "yield":        y,
                "change":       round(y - prev, 3),
                "arrow":        "⬆️" if rising else "⬇️",
                "above_4":      y > 4.0,
                "bearish_gold": y > 4.0 and rising
            }
    except Exception as e:
        print(f"US10Y error: {e}")
    return None

def get_full_macro():
    gold  = get_gold_price()
    dxy   = get_dxy()
    us10y = get_us10y()

    # Determine macro bias
    bear = 0
    bull = 0
    if dxy:
        if dxy["bearish_gold"]: bear += 1
        else: bull += 1
    if us10y:
        if us10y["bearish_gold"]: bear += 1
        else: bull += 1

    bias = "BEARISH" if bear > bull else "BULLISH" if bull > bear else "NEUTRAL"

    return {
        "gold":       gold,
        "dxy":        dxy,
        "us10y":      us10y,
        "macro_bias": bias
    }
