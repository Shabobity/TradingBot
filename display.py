"""Clean display formatting for reports and cards."""

from typing import List, Dict, Any
from datetime import datetime


def print_master_summary(reports: List[Dict[str, Any]]) -> None:
    """Print a clean summary table of all reports."""
    if not reports:
        return
    
    ranked = sorted(reports, key=lambda r: r["probability"], reverse=True)
    regime = reports[0]["market_regime"] if reports else "N/A"
    now_str = datetime.now().strftime("%A %d %B %Y  %H:%M")
    
    print()
    print("=" * 100)
    print(f"WEEKLY STOCK PROBABILITY REPORT  |  {now_str}")
    print(f"Market regime: {regime}  |  {len(reports)} stocks analysed")
    print("=" * 100)
    print(f"{'#':<3} {'TICKER':<8} {'COMPANY':<25} {'DIRECTION':<10} {'PROBABILITY':<15} {'CONFIDENCE':<12}")
    print("-" * 100)
    
    DIRS = {"UP": "UP", "DOWN": "DOWN", "NEUTRAL": "HOLD"}
    CONFS = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
    
    for i, r in enumerate(ranked, 1):
        direction = DIRS.get(r["prediction"], "?")
        confidence = CONFS.get(r["confidence"], "?")
        company = r["company"][:24] if len(r["company"]) > 24 else r["company"]
        
        row = f"{i:<3} {r['ticker']:<8} {company:<25} {direction:<10} {r['probability']:>6.1f}%{'':<8} {confidence:<12}"
        print(row)
    
    print("=" * 100)
    
    best = [r for r in ranked if r["prediction"] == "UP" and r["confidence"] in ("HIGH", "MEDIUM")]
    worst = [r for r in ranked if r["prediction"] == "DOWN"]
    
    if best:
        picks = ", ".join([f"{r['ticker']} {r['probability']:.0f}%" for r in best[:4]])
        print(f"Best opportunities: {picks}")
    if worst:
        avoid = ", ".join([f"{r['ticker']} {r['probability']:.0f}%" for r in worst[:4]])
        print(f"Avoid/caution: {avoid}")
    
    print("\nDISCLAIMER: For educational purposes only. Not financial advice.")
    print("=" * 100)
    print()


def print_stock_card(report: Dict[str, Any]) -> None:
    """Print a detailed analysis card for a single stock."""
    p = report["probability"]
    s = report["scores"]
    r = report["reasoning"]
    ts = report.get("trade_setup")
    
    print()
    print("=" * 80)
    print(f"{report['ticker']:<10} {report['company']:<30} Price: ${report['price']:>9.2f}")
    print(f"Sector: {report['sector']}")
    print("-" * 80)
    
    # Prediction
    direction_map = {"UP": "UP", "DOWN": "DOWN", "NEUTRAL": "NEUTRAL"}
    direction = direction_map.get(report["prediction"], "?")
    conf_map = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
    confidence = conf_map.get(report["confidence"], "?")
    
    print(f"Prediction: {direction:<10} Confidence: {confidence:<10} Probability: {p:5.1f}%")
    print(f"Regime: {report['market_regime']}")
    print()
    
    # Scores
    print("SCORES (range: -1.0 to +1.0)")
    print(f"  Technical   (35%): {s['technical']:+.3f}")
    print(f"  Fundamental (30%): {s['fundamental']:+.3f}")
    print(f"  Sentiment   (15%): {s['sentiment']:+.3f}")
    print(f"  Patterns    (20%): {s['pattern']:+.3f}")
    print(f"  Final (adj):       {s['final']:+.3f}")
    print()
    
    # Reasoning
    print("ANALYSIS")
    print(f"  Trend:          {r['trend']}")
    print(f"  Momentum:       {r['momentum']}")
    print(f"  Volume:         {r['volume']}")
    print(f"  Fundamentals:   {r['fundamentals']}")
    print(f"  Sentiment:      {r['sentiment']}")
    print(f"  Market regime:  {r['regime']}")
    print(f"  Signal conflict: {r['conflict']}")
    print(f"  3-Pillar check:  {r.get('pillar_gate', 'N/A')}")
    print()
    
    # Patterns
    if r.get("patterns_bullish") or r.get("patterns_bearish"):
        print("PATTERNS DETECTED")
        for pattern in r.get("patterns_bullish", []):
            print(f"  + {pattern}")
        for pattern in r.get("patterns_bearish", []):
            print(f"  - {pattern}")
        print()
    
    # Headlines
    if report.get("headlines"):
        print("RECENT HEADLINES")
        for headline in report["headlines"][:3]:
            print(f"  • {headline[:70]}")
        print()
    
    # Trade setup
    if ts:
        print("TRADE SETUP (if bullish)")
        print(f"  Entry:    {ts['entry']}")
        print(f"  Stop:     {ts['stop']}")
        print(f"  Target 1: {ts['target_1']}")
        print(f"  Target 2: {ts['target_2']}")
        print(f"  Target 3: {ts['target_3']}")
    
    print("=" * 80)
    print()


def print_comparison(reports: List[Dict[str, Any]]) -> None:
    """Print a side-by-side comparison of stocks."""
    if not reports:
        return
    
    ranked = sorted(
        [r for r in reports if "error" not in r],
        key=lambda r: r["probability"],
        reverse=True
    )
    
    print()
    print("=" * 90)
    print("STOCK COMPARISON")
    print("=" * 90)
    print(f"{'Rank':<5} {'Ticker':<8} {'Company':<25} {'Prediction':<12} {'Probability':<15}")
    print("-" * 90)
    
    for i, r in enumerate(ranked, 1):
        company = r["company"][:24] if len(r["company"]) > 24 else r["company"]
        print(f"{i:<5} {r['ticker']:<8} {company:<25} {r['prediction']:<12} {r['probability']:>6.1f}%")
    
    if ranked:
        print()
        print(f"TOP PICK: {ranked[0]['ticker']} ({ranked[0]['probability']:.1f}%)")
    
    print("=" * 90)
    print()
