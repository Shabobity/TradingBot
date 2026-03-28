"""Market regime detection and technical data scanning."""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from cache import cache_get, cache_set


class MarketRegime:
    """Detects overall market conditions (BULL/BEAR/NEUTRAL)."""
    
    def detect(self) -> Tuple[str, float, str]:
        """
        Analyze SPY to determine market regime.
        Returns: (regime, confidence_multiplier, description)
        """
        cached = cache_get("market_regime")
        if cached:
            return cached
        
        try:
            df = yf.Ticker("SPY").history(period="6mo")
            df.ta.sma(length=50, append=True)
            df.ta.sma(length=200, append=True)
            df.ta.rsi(length=14, append=True)
            
            latest = df.iloc[-1]
            price = latest["Close"]
            sma50 = latest.get("SMA_50", price)
            sma200 = latest.get("SMA_200", price)
            rsi = latest.get("RSI_14", 50)
            vol_20 = float(df["Close"].pct_change().dropna()[-20:].std() * np.sqrt(252) * 100)
            
            if price > sma50 > sma200 and rsi > 50:
                regime, mult, label = "BULL", 1.0, "Bull market — signals carry full weight"
            elif price < sma50 < sma200 and rsi < 50:
                regime, mult, label = "BEAR", 0.75, "Bear market — confidence discounted 25%"
            else:
                regime, mult, label = "NEUTRAL", 0.88, "Neutral market — confidence discounted 12%"
            
            if vol_20 > 25:
                label += f" | High volatility ({vol_20:.0f}% ann.)"
                mult *= 0.90
            
            result = (regime, mult, label)
            cache_set("market_regime", result)
            return result
        except:
            return ("NEUTRAL", 1.0, "Regime detection unavailable")


class MarketScanner:
    """Fetches and calculates technical indicators for a stock."""
    
    def fetch(self, symbol: str) -> Dict[str, Any]:
        """Get full technical and fundamental data for a stock."""
        cached = cache_get(f"market_{symbol}")
        if cached:
            return cached
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty:
            raise ValueError(f"No data for {symbol}")
        
        # Calculate all indicators
        df.ta.ema(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.obv(append=True)
        df.ta.stoch(append=True)
        df.ta.adx(append=True)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Bollinger Bands analysis
        bb_upper = latest.get("BBU_20_2.0", 0) or 0
        bb_lower = latest.get("BBL_20_2.0", 0) or 0
        bb_width = (bb_upper - bb_lower) / latest["Close"] if latest["Close"] else 0
        bb_pct = (latest["Close"] - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        # Volume analysis
        avg_vol = df["Volume"][-20:].mean()
        vol_ratio = latest["Volume"] / avg_vol if avg_vol > 0 else 1.0
        obv_trend = "RISING" if df["OBV"].iloc[-1] > df["OBV"].iloc[-10] else "FALLING"
        
        tech = {
            "current_price": float(latest["Close"]),
            "prev_close": float(prev["Close"]),
            "ema_20": float(latest.get("EMA_20", 0) or 0),
            "sma_50": float(latest.get("SMA_50", 0) or 0),
            "sma_200": float(latest.get("SMA_200", 0) or 0),
            "rsi": float(latest.get("RSI_14", 50) or 50),
            "macd_hist": float(latest.get("MACDh_12_26_9", 0) or 0),
            "stoch_k": float(latest.get("STOCHk_14_3_3", 50) or 50),
            "adx": float(latest.get("ADX_14", 20) or 20),
            "atr": float(latest.get("ATRr_14", 1) or 1),
            "vol_ratio": round(float(vol_ratio), 2),
            "obv_trend": obv_trend,
            "bb_squeeze": bb_width < 0.05,
            "bb_pct": float(bb_pct),
            "bb_upper": float(bb_upper),
            "bb_lower": float(bb_lower),
        }
        
        info = ticker.info
        raw_dte = info.get("debtToEquity")
        fund = {
            "company_name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "eps_growth": info.get("earningsGrowth", 0) or 0,
            "revenue_growth": info.get("revenueGrowth", 0) or 0,
            "peg_ratio": info.get("pegRatio", None),
            "debt_to_equity": (raw_dte / 100) if raw_dte is not None else None,
            "profit_margin": info.get("profitMargins", 0) or 0,
            "return_on_equity": info.get("returnOnEquity", 0) or 0,
            "current_ratio": info.get("currentRatio", None),
        }
        
        result = {"technicals": tech, "fundamentals": fund, "df": df}
        cache_set(f"market_{symbol}", result)
        return result
