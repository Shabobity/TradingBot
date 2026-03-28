"""Export analysis results to CSV and JSON."""

import json
from typing import List, Dict, Any
import pandas as pd


def export_csv(reports: List[Dict], filename: str = "scan_results.csv") -> None:
    """Export reports to CSV file."""
    rows = [{
        "ticker": r["ticker"],
        "company": r["company"],
        "sector": r["sector"],
        "prediction": r["prediction"],
        "probability_%": round(r["probability"], 1),
        "confidence": r["confidence"],
        "regime": r["market_regime"],
        "tech_score": r["scores"]["technical"],
        "fund_score": r["scores"]["fundamental"],
        "sent_score": r["scores"]["sentiment"],
        "final_score": r["scores"]["final"],
        "price": r["price"],
        "timestamp": r["timestamp"],
    } for r in reports]
    
    pd.DataFrame(rows).sort_values("probability_%", ascending=False).to_csv(filename, index=False)
    print(f"CSV  → {filename}")


def export_json(reports: List[Dict], filename: str = "scan_results.json") -> None:
    """Export reports to JSON file."""
    with open(filename, "w") as f:
        json.dump(reports, f, indent=2, default=str)
    print(f"JSON → {filename}")
