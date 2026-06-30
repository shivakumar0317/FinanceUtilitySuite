import pandas as pd
import yfinance as yf


class StockAnalyzer:

    def __init__(self):
        pass

    def get_risk_category(self, beta):

        if beta is None:
            return "Unknown"

        if beta < 0.8:
            return "Low"

        elif beta <= 1.2:
            return "Moderate"

        else:
            return "High"

    def get_stock_data(self, symbol):

        symbol = str(symbol).strip().upper()

        exchanges = [
            symbol + ".NS",
            symbol + ".BO"
        ]

        for ticker_name in exchanges:

            try:

                ticker = yf.Ticker(ticker_name)

                info = ticker.info

                if len(info) == 0:
                    continue

                return {
                    "Symbol": symbol,
                    "Exchange": ticker_name,
                    "Company": info.get("longName", ""),
                    "CMP": info.get("currentPrice"),
                    "Beta": info.get("beta"),
                    "Risk": self.get_risk_category(info.get("beta")),
                    "Market Cap": info.get("marketCap"),
                    "PE": info.get("trailingPE"),
                    "EPS": info.get("trailingEps"),
                    "Sector": info.get("sector"),
                    "Industry": info.get("industry")
                }

            except Exception:
                continue

        return {
            "Symbol": symbol,
            "Exchange": "",
            "Company": "",
            "Beta": None,
            "CMP": None,
            "Market Cap": None,
            "PE": None,
            "EPS": None,
            "Sector": "",
            "Industry": ""
        }

    def analyze_file(self, filename):

        if filename.lower().endswith(".csv"):
            df = pd.read_csv(filename)
        else:
            df = pd.read_excel(filename)

        if "SYMBOL" not in df.columns:
            raise Exception("SYMBOL column not found.")

        results = []

        total = len(df)

        for index, symbol in enumerate(df["SYMBOL"], start=1):

            print(f"{index}/{total}  {symbol}")

            stock = self.get_stock_data(symbol)

            results.append(stock)

        return pd.DataFrame(results)