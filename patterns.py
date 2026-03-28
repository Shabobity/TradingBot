"""Chart pattern detection for technical analysis."""

from typing import Tuple, List
import numpy as np
import pandas as pd


class PatternDetector:
    """Detects technical chart patterns in price history."""
    
    def detect(self, df: pd.DataFrame) -> Tuple[float, List[str], List[str]]:
        """
        Detect chart patterns in price data.
        Returns: (score, bullish_patterns, bearish_patterns)
        """
        if len(df) < 30:
            return 0.0, [], ["Insufficient history for pattern detection"]
        
        score = 0.0
        bullish = []
        bearish = []
        
        close = df["Close"].values
        volume = df["Volume"].values
        high = df["High"].values
        low = df["Low"].values
        
        rsi_col = [c for c in df.columns if c.startswith("RSI")]
        macd_col = [c for c in df.columns if c.startswith("MACDh")]
        obv_col = "OBV" if "OBV" in df.columns else None
        
        rsi = df[rsi_col[0]].values if rsi_col else None
        macd = df[macd_col[0]].values if macd_col else None
        
        # 1. RSI Bullish Divergence
        try:
            if rsi is not None and len(close) >= 20:
                window = 20
                p = close[-window:]
                r = rsi[-window:]
                valid = ~np.isnan(r)
                if valid.sum() >= 10:
                    p_min1_idx = np.argmin(p[:-5])
                    p_min2_idx = np.argmin(p[-5:]) + (window - 5)
                    r_at_min1 = r[p_min1_idx]
                    r_at_min2 = r[p_min2_idx]
                    if (p[p_min2_idx] < p[p_min1_idx] and
                            not np.isnan(r_at_min1) and not np.isnan(r_at_min2) and
                            r_at_min2 > r_at_min1 + 3):
                        score += 0.25
                        bullish.append(f"Bullish RSI divergence (+{r_at_min2 - r_at_min1:.0f} pts)")
        except:
            pass
        
        # 2. RSI Bearish Divergence
        try:
            if rsi is not None and len(close) >= 20:
                window = 20
                p = close[-window:]
                r = rsi[-window:]
                valid = ~np.isnan(r)
                if valid.sum() >= 10:
                    p_max1_idx = np.argmax(p[:-5])
                    p_max2_idx = np.argmax(p[-5:]) + (window - 5)
                    r_at_max1 = r[p_max1_idx]
                    r_at_max2 = r[p_max2_idx]
                    if (p[p_max2_idx] > p[p_max1_idx] and
                            not np.isnan(r_at_max1) and not np.isnan(r_at_max2) and
                            r_at_max2 < r_at_max1 - 3):
                        score -= 0.20
                        bearish.append(f"Bearish RSI divergence (-{r_at_max1 - r_at_max2:.0f} pts)")
        except:
            pass
        
        # 3. Double Bottom
        try:
            if len(low) >= 40:
                seg = low[-40:]
                mid = len(seg) // 2
                min1 = np.min(seg[:mid])
                min2 = np.min(seg[mid:])
                peak = np.max(seg[mid // 2: mid + mid // 2])
                depth = (peak - min(min1, min2)) / peak if peak > 0 else 0
                if (abs(min1 - min2) / max(min1, min2) < 0.03 and
                        depth > 0.04 and
                        close[-1] > peak * 0.98):
                    score += 0.30
                    bullish.append(f"Double bottom at ${min1:.2f} and ${min2:.2f}")
        except:
            pass
        
        # 4. Head & Shoulders
        try:
            if len(high) >= 60:
                seg = high[-60:]
                n = len(seg)
                q = n // 4
                ls = np.max(seg[:q])
                head = np.max(seg[q:3*q])
                rs = np.max(seg[3*q:])
                if (head > ls * 1.03 and head > rs * 1.03 and
                        abs(ls - rs) / head < 0.05 and
                        close[-1] < head * 0.97):
                    score -= 0.25
                    bearish.append(f"Head & shoulders pattern detected")
        except:
            pass
        
        # 5. Momentum Shift
        try:
            if rsi is not None and len(rsi) >= 15:
                r = rsi[-15:]
                valid = r[~np.isnan(r)]
                if len(valid) >= 10:
                    r_start = float(np.nanmean(valid[:5]))
                    r_end = float(np.nanmean(valid[-5:]))
                    swing = r_end - r_start
                    if r_start < 45 and swing > 12:
                        score += 0.20
                        bullish.append(f"Bullish momentum shift (RSI +{swing:.0f})")
                    elif r_start > 55 and swing < -12:
                        score -= 0.15
                        bearish.append(f"Bearish momentum shift (RSI -{abs(swing):.0f})")
        except:
            pass
        
        # 6. Cup & Handle
        try:
            if len(close) >= 50:
                cup = close[-50:-10]
                handle = close[-10:]
                cup_low = np.min(cup)
                cup_high = np.max([cup[0], cup[-1]])
                handle_low = np.min(handle)
                handle_high = np.max(handle)
                
                cup_mid_low = np.min(cup[len(cup)//4 : 3*len(cup)//4])
                is_rounded = cup_mid_low < cup_low * 1.05
                
                handle_tight = (handle_high - handle_low) / handle_high < 0.06
                handle_high_ok = handle_low > cup_high * 0.90
                breakout_near = close[-1] > handle_high * 0.98
                
                if is_rounded and handle_tight and handle_high_ok and breakout_near:
                    score += 0.28
                    bullish.append(f"Cup & handle pattern forming")
        except:
            pass
        
        # 7. Volume Accumulation Trend
        try:
            if obv_col and len(df) >= 20:
                obv_series = df[obv_col].dropna().values
                if len(obv_series) >= 20:
                    obv_20 = obv_series[-20:]
                    x = np.arange(len(obv_20), dtype=float)
                    slope = np.polyfit(x, obv_20, 1)[0]
                    avg_obv = np.mean(np.abs(obv_20))
                    norm_slope = slope / avg_obv if avg_obv > 0 else 0
                    
                    if norm_slope > 0.005:
                        score += 0.15
                        bullish.append(f"OBV accumulation trend detected")
                    elif norm_slope < -0.005:
                        score -= 0.12
                        bearish.append(f"OBV distribution trend detected")
        except:
            pass
        
        # 8. Support Breakout
        try:
            if len(close) >= 25 and len(volume) >= 25:
                recent_high = np.max(close[-25:-2])
                avg_vol_20 = np.mean(volume[-22:-2])
                today_vol = volume[-1]
                if close[-1] > recent_high * 1.005 and today_vol > avg_vol_20 * 1.3:
                    score += 0.20
                    bullish.append(f"Breakout on volume above 20-day resistance")
        except:
            pass
        
        score = float(min(max(score, -1.0), 1.0))
        return score, bullish, bearish
