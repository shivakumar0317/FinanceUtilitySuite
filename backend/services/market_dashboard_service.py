from __future__ import annotations
import pandas as pd
import yfinance as yf
class MarketDashboardService:
    INDEX_SYMBOLS={"NIFTY 50":"^NSEI","BANK NIFTY":"^NSEBANK","SENSEX":"^BSESN"}
    MARKET_UNIVERSE=["RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","AXISBANK.NS","KOTAKBANK.NS","HINDUNILVR.NS","MARUTI.NS","SUNPHARMA.NS","TATAMOTORS.NS","NTPC.NS","POWERGRID.NS","BAJFINANCE.NS","ASIANPAINT.NS","WIPRO.NS"]
    @classmethod
    def quote(cls,symbol:str,exchange:str="NSE"):
        for candidate in cls._candidates(symbol,exchange):
            try:
                h=yf.Ticker(candidate).history(period="5d",interval="1d",auto_adjust=False)
                if h is None or h.empty: continue
                close=pd.to_numeric(h["Close"],errors="coerce").dropna()
                if close.empty: continue
                price=float(close.iloc[-1]); prev=float(close.iloc[-2]) if len(close)>1 else price
                change=price-prev; pct=(change/prev*100) if prev else 0.0
                return {"resolved_symbol":candidate,"price":round(price,2),"change":round(change,2),"change_percent":round(pct,2)}
            except Exception: continue
        return {"resolved_symbol":symbol,"price":0.0,"change":0.0,"change_percent":0.0}
    @classmethod
    def indices(cls):
        return [{"name":name,"symbol":symbol,**cls.quote(symbol)} for name,symbol in cls.INDEX_SYMBOLS.items()]
    @classmethod
    def top_movers(cls,limit:int=5):
        rows=[]
        for s in cls.MARKET_UNIVERSE:
            q=cls.quote(s)
            if q["price"]>0: rows.append({"symbol":s.replace(".NS",""),**q})
        return {"gainers":sorted(rows,key=lambda x:x["change_percent"],reverse=True)[:limit],"losers":sorted(rows,key=lambda x:x["change_percent"])[:limit]}
    @staticmethod
    def _candidates(symbol,exchange):
        s=symbol.strip().upper()
        if s.startswith("^") or s.endswith((".NS",".BO")): return [s]
        return [f"{s}.BO",f"{s}.NS",s] if exchange.strip().upper()=="BSE" else [f"{s}.NS",f"{s}.BO",s]
