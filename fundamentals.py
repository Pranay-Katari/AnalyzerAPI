import yfinance as yf
import requests
import datetime as dt
from functools import lru_cache
import logging

# Optional: silence yfinance's noisy warnings in production
logging.getLogger("yfinance").setLevel(logging.ERROR)

# Small cache speeds up repeated lookups
try:
    import requests_cache
    _SESSION = requests_cache.CachedSession('yfin.cache', expire_after=dt.timedelta(minutes=5))
    _SESSION.headers['User-Agent'] = 'my-flask-app/1.0'
except Exception:
    _SESSION = None

@lru_cache(maxsize=1024)
def resolve_symbol(query: str, country="United States") -> str:
    """Turn a name like 'JOHNSON & JOHNSON' or '$apple' into a ticker like 'JNJ' or 'AAPL'."""
    s = (query or "").strip().lstrip("$")
    # If it already looks like a ticker, return it
    if s and s.upper() == s and 1 <= len(s) <= 6 and " " not in s and "&" not in s:
        return s
    # Use Yahoo's public search endpoint
    try:
        r = requests.get(
            "https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": s, "quotesCount": 10, "newsCount": 0},
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        j = r.json()
        # Prefer US equities/ETFs with best name match
        candidates = [
            q for q in j.get("quotes", [])
            if q.get("symbol") and q.get("quoteType") in {"EQUITY", "ETF"}
        ]
        if country:
            # Prefer the requested country when available
            for q in candidates:
                if q.get("longname") and country.lower() in (q.get("country") or "").lower():
                    return q["symbol"]
        if candidates:
            # fallback: first candidate
            return candidates[0]["symbol"]
    except Exception:
        pass
    return s  # last resort: return as-is (may still fail)

def _safe_history(t: yf.Ticker, period="3mo", interval="1d"):
    try:
        return t.history(period=period, interval=interval, auto_adjust=False, prepost=False)
    except Exception:
        # yfinance throws on unknown/invalid ticker → return empty frame
        import pandas as pd
        return pd.DataFrame()

def get_fundamentals(symbol_or_name: str, include_slow=False):
    symbol = resolve_symbol(symbol_or_name)
    t = yf.Ticker(symbol, session=_SESSION)

    # fast_info fields (quick, but may be None for some tickers)
    try:
        fi = t.fast_info or {}
    except Exception:
        fi = {}

    def _fi_get(*keys):
        for k in keys:
            v = (fi.get(k) if isinstance(fi, dict) else getattr(fi, k, None))
            if v is not None:
                return v
        return None

    today_low  = _fi_get("day_low", "dayLow")
    today_high = _fi_get("day_high", "dayHigh")
    today_open = _fi_get("open", "regular_market_open", "regularMarketOpen")

    # 20-day average volume from market data (robust, avoids .info)
    avg_vol_20d = None
    hist = _safe_history(t, period="3mo", interval="1d")
    if not hist.empty and "Volume" in hist:
        avg_vol_20d = float(hist["Volume"].tail(20).mean())

    # Dividends & splits in one call
    last_div = last_split = None
    try:
        actions = t.actions
        if "Dividends" in actions and (actions["Dividends"] > 0).any():
            last_div = float(actions["Dividends"][actions["Dividends"] > 0].iloc[-1])
        if "Stock Splits" in actions and (actions["Stock Splits"] > 0).any():
            last_split = float(actions["Stock Splits"][actions["Stock Splits"] > 0].iloc[-1])
    except Exception:
        pass

    fpe = teps = None
    if include_slow:
        # Only fetch .get_info() when absolutely necessary (can hang / rate-limit)
        try:
            info = t.get_info()
            fpe = info.get("forwardPE")
            teps = info.get("trailingEps")
        except Exception:
            pass

    return {
        "Resolved_Symbol": symbol,
        "Today_Low": today_low,
        "Today_High": today_high,
        "Today_Open": today_open,
        "Average_Volume_20d": avg_vol_20d,
        "Last Dividend": last_div,
        "Last Split": last_split,
        "Forward P/E": fpe,
        "Trailing EPS": teps,
    }
