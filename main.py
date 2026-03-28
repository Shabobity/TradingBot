"""Main entry point for the trading bot."""

import sys
from agent import AdvancedTradingAgent
from display import print_stock_card, print_master_summary
from exports import export_csv, export_json
from config import DEFAULT_WATCHLIST


def quick_scan():
    """Quick scan of the default watchlist."""
    print(f"\nScanning {len(DEFAULT_WATCHLIST)} stocks...\n")
    
    reports = []
    for ticker in DEFAULT_WATCHLIST:
        print(f"  {ticker:<6}", end=" ", flush=True)
        try:
            report = AdvancedTradingAgent(ticker).run()
            reports.append(report)
            print(f"{report['prediction']:<8} {report['probability']:5.1f}%")
        except Exception as e:
            print(f"ERROR: {e}")
    
    if reports:
        print_master_summary(reports)
        ranked = sorted(reports, key=lambda r: r["probability"], reverse=True)
        for r in ranked[:3]:
            print_stock_card(r)
        export_csv(reports)
        export_json(reports)


def analyze_single(ticker: str):
    """Analyze a single stock."""
    try:
        report = AdvancedTradingAgent(ticker.upper()).run()
        print_stock_card(report)
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        
        if arg == "SCAN":
            quick_scan()
        else:
            # Treat as ticker
            analyze_single(arg)
    else:
        # Launch interactive chat
        from chat import chat
        chat()


if __name__ == "__main__":
    main()
