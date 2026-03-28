"""Tool definitions for Claude to use in the agent loop."""

CLAUDE_TOOLS = [
    {
        "name": "analyze_stock",
        "description": (
            "Run a full technical, fundamental, and sentiment analysis on a single stock ticker. "
            "Returns a probability score (0-100%) of the stock going UP this week, a directional "
            "prediction (UP/DOWN/NEUTRAL), confidence level, score breakdown, and a trade setup."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol e.g. AAPL, NVDA, TSLA"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "compare_stocks",
        "description": (
            "Analyse and compare two or more stock tickers side by side. Returns a ranked list "
            "with probability scores and a recommendation on which is the stronger pick."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols e.g. ['AAPL', 'MSFT', 'GOOGL']"
                }
            },
            "required": ["tickers"]
        }
    },
    {
        "name": "scan_market",
        "description": (
            "Scan a predefined watchlist of top stocks and return a ranked summary by probability. "
            "Use this for a market overview without specifying individual tickers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "watchlist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tickers to scan. Uses default watchlist if empty.",
                    "default": []
                }
            },
            "required": []
        }
    },
    {
        "name": "get_market_regime",
        "description": (
            "Check the current macro market environment (BULL/BEAR/NEUTRAL) based on SPY. "
            "Use this when asked about overall market conditions or market direction."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_news_sentiment",
        "description": (
            "Fetch and analyze recent news headlines for a stock and return sentiment score. "
            "Use when asked about news, recent events, or sentiment for a ticker."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "scan_sp500",
        "description": (
            "Scan S&P 500 stocks and return only those with probability above threshold. "
            "Use when asked to scan the full market, find best stocks, or search for high-conviction picks."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "min_probability": {
                    "type": "number",
                    "description": "Minimum probability threshold (default 80).",
                    "default": 80
                },
                "max_stocks": {
                    "type": "integer",
                    "description": "Max number of S&P 500 stocks to scan (default 503).",
                    "default": 503
                }
            },
            "required": []
        }
    },
    {
        "name": "build_portfolio",
        "description": (
            "Analyze stocks and build a suggested portfolio allocation based on probability "
            "scores and risk tolerance. Returns position sizes and reasoning."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "number",
                    "description": "Total budget in USD"
                },
                "risk": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Risk tolerance"
                },
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Stocks to consider. Uses default if empty.",
                    "default": []
                }
            },
            "required": ["budget", "risk"]
        }
    }
]
