"""Advanced AI Stock Trading Agent combining technical, fundamental, sentiment, and pattern analysis."""

from typing import Dict, Any, Tuple
from datetime import datetime
import numpy as np
from sentiment import SentimentEngine
from market import MarketRegime, MarketScanner
from patterns import PatternDetector


class AdvancedTradingAgent:
    """Comprehensive stock analysis combining four pillars of analysis."""
    
    WEIGHTS = {
        "technical": 0.35,
        "fundamental": 0.30,
        "sentiment": 0.15,
        "pattern": 0.20
    }
    
    def __init__(self, ticker: str, skip_news: bool = False):
        self.ticker = ticker.upper()
        self.sentiment = SentimentEngine(skip_news=skip_news)
        self.regime = MarketRegime()
        self.scanner = MarketScanner()
        self.patterns = PatternDetector()
    
    def run(self) -> Dict[str, Any]:
        """Run full analysis and return comprehensive report."""
        data = self.scanner.fetch(self.ticker)
        tech = data["technicals"]
        fund = data["fundamentals"]
        df = data["df"]
        
        sent_score, sent_summary, headlines = self.sentiment.analyze(
            self.ticker, fund.get("company_name", ""))
        
        tech_score, tech_reasons = self._score_technicals(tech)
        fund_score, fund_reasons = self._score_fundamentals(fund)
        pat_score, pat_bullish, pat_bearish = self.patterns.detect(df)
        
        # Composite score
        raw_score = (
            tech_score * self.WEIGHTS["technical"] +
            fund_score * self.WEIGHTS["fundamental"] +
            sent_score * self.WEIGHTS["sentiment"] +
            pat_score * self.WEIGHTS["pattern"]
        )
        
        # Check for conflicting signals
        variance = float(np.var([tech_score, fund_score, sent_score, pat_score]))
        conflict = None
        if variance > 0.4:
            raw_score *= 0.75
            conflict = f"Conflicting signals (variance={variance:.2f}) — confidence reduced"
        
        # Apply market regime adjustment
        regime, regime_mult, regime_label = self.regime.detect()
        adj_score = raw_score * regime_mult
        probability = float(min(max((adj_score + 1) / 2 * 100, 0), 100))
        
        # Direction prediction
        if adj_score >= 0.25:
            prediction = "UP"
        elif adj_score <= -0.25:
            prediction = "DOWN"
        else:
            prediction = "NEUTRAL"
        
        # Confidence level
        if variance > 0.4 or 40 < probability < 60:
            confidence = "LOW"
        elif probability > 78 or probability < 22:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"
        
        # Conservative three-pillar gate
        PILLAR_MIN = {
            "technical": 0.20,
            "fundamental": 0.15,
            "sentiment": -0.10,
            "pattern": -0.15
        }
        pillar_failures = []
        if tech_score < PILLAR_MIN["technical"]:
            pillar_failures.append(f"Technical weak ({tech_score:+.2f})")
        if fund_score < PILLAR_MIN["fundamental"]:
            pillar_failures.append(f"Fundamentals weak ({fund_score:+.2f})")
        if sent_score < PILLAR_MIN["sentiment"]:
            pillar_failures.append(f"Sentiment negative ({sent_score:+.2f})")
        if pat_score < PILLAR_MIN["pattern"]:
            pillar_failures.append(f"Patterns bearish ({pat_score:+.2f})")
        
        conservative_veto = bool(pillar_failures)
        if conservative_veto:
            prediction = "NEUTRAL"
            confidence = "LOW"
            probability = min(probability, 49.9)
        
        # Build report
        report = {
            "ticker": self.ticker,
            "company": fund.get("company_name", self.ticker),
            "sector": fund.get("sector", "N/A"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": prediction,
            "probability": probability,
            "confidence": confidence,
            "market_regime": regime,
            "price": tech["current_price"],
            "atr": tech["atr"],
            "scores": {
                "technical": round(tech_score, 3),
                "fundamental": round(fund_score, 3),
                "sentiment": round(sent_score, 3),
                "pattern": round(pat_score, 3),
                "raw": round(raw_score, 3),
                "final": round(adj_score, 3),
            },
            "reasoning": {
                "trend": tech_reasons.get("trend", "N/A"),
                "momentum": tech_reasons.get("momentum", "N/A"),
                "volume": tech_reasons.get("volume", "N/A"),
                "volatility": tech_reasons.get("volatility", "N/A"),
                "strength": tech_reasons.get("strength", "N/A"),
                "fundamentals": fund_reasons,
                "sentiment": sent_summary,
                "regime": regime_label,
                "conflict": conflict or "Signals broadly aligned",
                "pillar_gate": ("FAILED — " + " | ".join(pillar_failures)) if conservative_veto else "PASSED",
                "patterns_bullish": pat_bullish,
                "patterns_bearish": pat_bearish,
            },
            "headlines": headlines,
        }
        
        # Trade setup if bullish
        if prediction == "UP" and confidence in ("MEDIUM", "HIGH"):
            p, a = tech["current_price"], tech["atr"]
            report["trade_setup"] = {
                "entry": f"${p * 0.995:.2f} - ${p * 1.005:.2f}",
                "stop": f"${p - (a * 1.5):.2f}",
                "target_1": f"${p + (a * 2.5):.2f}",
                "target_2": f"${p + (a * 4.0):.2f}",
                "target_3": f"${p + (a * 6.0):.2f}",
            }
        
        return report
    
    def _score_technicals(self, tech: Dict) -> Tuple[float, Dict]:
        """Score technical indicators."""
        score = 0.0
        r = {}
        
        ema20, sma50, sma200, price = tech["ema_20"], tech["sma_50"], tech["sma_200"], tech["current_price"]
        if ema20 > sma50 > sma200 and price > ema20:
            score += 0.35
            r["trend"] = "Strong bullish"
        elif ema20 > sma50 and price > ema20:
            score += 0.15
            r["trend"] = "Moderate bullish"
        elif ema20 < sma50 < sma200 and price < ema20:
            score -= 0.35
            r["trend"] = "Strong bearish"
        elif ema20 < sma50:
            score -= 0.15
            r["trend"] = "Bearish developing"
        else:
            r["trend"] = "Mixed/consolidating"
        
        rsi, macd_hist, stoch_k = tech["rsi"], tech["macd_hist"], tech["stoch_k"]
        mom, mnotes = 0.0, []
        if 45 <= rsi <= 65 and macd_hist > 0:
            mom += 0.25
            mnotes.append(f"RSI healthy ({rsi:.0f}), MACD bullish")
        elif rsi > 70:
            mom -= 0.15
            mnotes.append(f"RSI overbought ({rsi:.0f})")
        elif rsi < 30:
            mom += 0.10
            mnotes.append(f"RSI oversold ({rsi:.0f})")
        else:
            mnotes.append(f"RSI neutral ({rsi:.0f})")
        if stoch_k < 20:
            mom += 0.08
            mnotes.append(f"Stoch oversold ({stoch_k:.0f})")
        elif stoch_k > 80:
            mom -= 0.08
            mnotes.append(f"Stoch overbought ({stoch_k:.0f})")
        score += mom
        r["momentum"] = " | ".join(mnotes)
        
        adx = tech["adx"]
        if adx > 25:
            r["strength"] = f"Strong trend (ADX={adx:.0f})"
        elif adx < 15:
            score -= 0.05
            r["strength"] = f"Weak/ranging (ADX={adx:.0f})"
        else:
            r["strength"] = f"Moderate trend (ADX={adx:.0f})"
        
        vr, obv = tech["vol_ratio"], tech["obv_trend"]
        vnotes = []
        if vr > 1.5 and macd_hist > 0:
            score += 0.12
            vnotes.append(f"High vol bullish ({vr:.1f}x)")
        elif vr > 1.5 and macd_hist < 0:
            score -= 0.12
            vnotes.append(f"High vol bearish ({vr:.1f}x)")
        elif vr < 0.7:
            vnotes.append(f"Low vol ({vr:.1f}x)")
        else:
            vnotes.append(f"Normal vol ({vr:.1f}x)")
        if obv == "RISING":
            score += 0.08
            vnotes.append("OBV rising")
        else:
            score -= 0.05
            vnotes.append("OBV falling")
        r["volume"] = " | ".join(vnotes)
        
        bb_pct, sq = tech["bb_pct"], tech["bb_squeeze"]
        bnotes = []
        if sq:
            score += 0.08
            bnotes.append("Squeeze detected")
        if bb_pct > 0.85:
            score -= 0.05
            bnotes.append(f"Near upper band")
        elif bb_pct < 0.15:
            score += 0.05
            bnotes.append(f"Near lower band")
        else:
            bnotes.append(f"Mid-band position")
        r["volatility"] = " | ".join(bnotes) if bnotes else "Normal"
        
        return float(min(max(score, -1.0), 1.0)), r
    
    def _score_fundamentals(self, fund: Dict) -> Tuple[float, str]:
        """Score fundamental metrics."""
        score = 0.0
        notes = []
        
        eps = fund.get("eps_growth", 0) or 0
        rev = fund.get("revenue_growth", 0) or 0
        peg = fund.get("peg_ratio")
        dte = fund.get("debt_to_equity")
        mgn = fund.get("profit_margin", 0) or 0
        roe = fund.get("return_on_equity", 0) or 0
        curr = fund.get("current_ratio")
        
        if eps > 0.20:
            score += 0.30
            notes.append(f"EPS +{eps*100:.0f}%")
        elif eps > 0.05:
            score += 0.15
            notes.append(f"EPS +{eps*100:.0f}%")
        elif eps < 0:
            score -= 0.20
            notes.append(f"EPS {eps*100:.0f}%")
        else:
            notes.append(f"EPS flat")
        
        if rev > 0.10:
            score += 0.10
            notes.append(f"Revenue +{rev*100:.0f}%")
        elif rev < 0:
            score -= 0.10
            notes.append(f"Revenue {rev*100:.0f}%")
        
        if peg is not None:
            if peg < 1.0:
                score += 0.20
                notes.append(f"PEG undervalued")
            elif peg < 1.5:
                score += 0.10
                notes.append(f"PEG fair")
            elif peg > 3.0:
                score -= 0.15
                notes.append(f"PEG expensive")
        
        if dte is not None:
            if dte < 0.5:
                score += 0.15
                notes.append(f"Low debt")
            elif dte > 2.0:
                score -= 0.15
                notes.append(f"High debt")
        
        if mgn > 0.20:
            score += 0.10
            notes.append(f"Strong margin")
        elif mgn < 0:
            score -= 0.10
        if roe > 0.15:
            score += 0.10
            notes.append(f"High ROE")
        if curr is not None and curr < 1.0:
            score -= 0.10
            notes.append(f"Liquidity risk")
        
        return float(min(max(score, -1.0), 1.0)), " | ".join(notes) if notes else "Insufficient data"
