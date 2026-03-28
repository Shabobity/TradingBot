"""Execute Claude's tool calls and return results."""

import json
from typing import Dict, Any
import logging
from agent import AdvancedTradingAgent
from display import print_stock_card, print_master_summary, print_comparison
from exports import export_csv, export_json
from market import MarketRegime, MarketScanner
from sentiment import SentimentEngine
from config import DEFAULT_WATCHLIST, SP500_TICKERS

log = logging.getLogger(__name__)


def execute_tool(name: str, inputs: Dict) -> str:
    """Execute a tool and return JSON result."""
    try:
        if name == "analyze_stock":
            ticker = inputs["ticker"].upper()
            print(f"\nAnalysing {ticker}...")
            report = AdvancedTradingAgent(ticker).run()
            print_stock_card(report)
            return json.dumps({
                "ticker": report["ticker"],
                "company": report["company"],
                "prediction": report["prediction"],
                "probability": f"{report['probability']:.1f}%",
                "confidence": report["confidence"],
                "scores": report["scores"],
                "reasoning": report["reasoning"],
                "trade_setup": report.get("trade_setup"),
            }, indent=2)
        
        elif name == "compare_stocks":
            tickers = [t.upper() for t in inputs["tickers"]]
            print(f"\nComparing {', '.join(tickers)}...")
            reports = []
            for t in tickers:
                try:
                    r = AdvancedTradingAgent(t).run()
                    reports.append(r)
                    print_stock_card(r)
                except Exception as e:
                    reports.append({"ticker": t, "error": str(e)})
            
            ranked = sorted(
                [r for r in reports if "error" not in r],
                key=lambda r: r["probability"],
                reverse=True
            )
            print_comparison(ranked)
            
            comparison = [{
                "rank": i + 1,
                "ticker": r["ticker"],
                "prediction": r["prediction"],
                "probability": f"{r['probability']:.1f}%",
                "confidence": r["confidence"],
            } for i, r in enumerate(ranked)]
            
            return json.dumps({
                "comparison": comparison,
                "top_pick": ranked[0]["ticker"] if ranked else "N/A"
            }, indent=2)
        
        elif name == "scan_market":
            watchlist = [t.upper() for t in (inputs.get("watchlist") or DEFAULT_WATCHLIST)]
            print(f"\nScanning {len(watchlist)} stocks...")
            
            reports = []
            for ticker in watchlist:
                try:
                    report = AdvancedTradingAgent(ticker).run()
                    reports.append(report)
                except Exception as e:
                    log.error(f"{ticker}: {e}")
            
            if reports:
                print_master_summary(reports)
                ranked = sorted(reports, key=lambda r: r["probability"], reverse=True)
                for r in ranked[:3]:
                    print_stock_card(r)
            
            return json.dumps([{
                "ticker": r["ticker"],
                "prediction": r["prediction"],
                "probability": f"{r['probability']:.1f}%",
                "confidence": r["confidence"],
            } for r in sorted(reports, key=lambda r: r["probability"], reverse=True)], indent=2)
        
        elif name == "get_market_regime":
            regime, mult, label = MarketRegime().detect()
            return json.dumps({
                "regime": regime,
                "confidence_multiplier": mult,
                "description": label
            })
        
        elif name == "get_news_sentiment":
            ticker = inputs["ticker"].upper()
            data = MarketScanner().fetch(ticker)
            company = data["fundamentals"].get("company_name", ticker)
            score, summary, headlines = SentimentEngine().analyze(ticker, company)
            return json.dumps({
                "ticker": ticker,
                "score": round(score, 3),
                "summary": summary,
                "headlines": headlines[:5],
            }, indent=2)
        
        elif name == "scan_sp500":
            min_prob = float(inputs.get("min_probability", 80))
            max_stocks = int(inputs.get("max_stocks", 503))
            tickers = SP500_TICKERS[:max_stocks]
            
            print(f"\nScanning {len(tickers)} S&P 500 stocks (threshold: {min_prob:.0f}%)...")
            hot_picks = []
            
            for i, t in enumerate(tickers, 1):
                if i % 25 == 0:
                    print(f"  [{i}/{len(tickers)}] ... {len(hot_picks)} found so far")
                try:
                    agent = AdvancedTradingAgent(t, skip_news=True)
                    report = agent.run()
                    if report["probability"] >= min_prob:
                        hot_picks.append(report)
                except:
                    pass
            
            hot_picks.sort(key=lambda r: r["probability"], reverse=True)
            
            if hot_picks:
                print_master_summary(hot_picks)
                for r in hot_picks[:5]:
                    print_stock_card(r)
                export_csv(hot_picks, "sp500_hot_picks.csv")
                export_json(hot_picks, "sp500_hot_picks.json")
            
            return json.dumps({
                "scanned": len(tickers),
                "found": len(hot_picks),
                "threshold": f"{min_prob:.0f}%",
                "top_picks": [{
                    "ticker": r["ticker"],
                    "company": r["company"],
                    "probability": f"{r['probability']:.1f}%",
                } for r in hot_picks[:10]]
            }, indent=2)
        
        elif name == "build_portfolio":
            budget = float(inputs["budget"])
            risk = inputs["risk"]
            tickers = [t.upper() for t in (inputs.get("tickers") or DEFAULT_WATCHLIST)]
            
            print(f"\nBuilding {risk}-risk portfolio from {len(tickers)} stocks...")
            reports = []
            for t in tickers:
                try:
                    reports.append(AdvancedTradingAgent(t).run())
                except:
                    pass
            
            # Filter by risk
            if risk == "low":
                candidates = [r for r in reports if r["confidence"] == "HIGH" and r["prediction"] == "UP"]
            elif risk == "medium":
                candidates = [r for r in reports if r["prediction"] == "UP"]
            else:
                candidates = [r for r in reports if r["probability"] > 50]
            
            if not candidates:
                return json.dumps({"error": "No suitable stocks found"})
            
            candidates = sorted(candidates, key=lambda r: r["probability"], reverse=True)[:6]
            total_score = sum(r["probability"] for r in candidates)
            allocations = []
            
            for r in candidates:
                weight = r["probability"] / total_score
                amount = budget * weight
                allocations.append({
                    "ticker": r["ticker"],
                    "company": r["company"],
                    "probability": f"{r['probability']:.1f}%",
                    "weight": f"{weight*100:.1f}%",
                    "amount": f"${amount:,.2f}",
                    "shares": f"~{amount / r['price']:.1f}",
                })
            
            print("\nPORTFOLIO ALLOCATION")
            print("=" * 80)
            for alloc in allocations:
                print(f"{alloc['ticker']:<8} {alloc['company']:<20} {alloc['weight']:>8} {alloc['amount']:>12} (~{alloc['shares']} shares)")
            print("=" * 80)
            
            return json.dumps({
                "budget": f"${budget:,.2f}",
                "risk": risk,
                "allocations": allocations,
            }, indent=2)
        
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})
