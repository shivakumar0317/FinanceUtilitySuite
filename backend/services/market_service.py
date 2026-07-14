import pandas as pd
import yfinance as yf

class MarketService:
    @staticmethod
    def candidates(symbol:str)->list[str]:
        s=symbol.strip().upper()
        return [s] if s.endswith(('.NS','.BO')) or s.startswith('^') else [f'{s}.NS',f'{s}.BO',s]

    @classmethod
    def quote(cls,symbol:str)->dict:
        for candidate in cls.candidates(symbol):
            try:
                hist=yf.Ticker(candidate).history(period='5d',auto_adjust=False)
                if not hist.empty:
                    return {'symbol':symbol.upper(),'resolved_symbol':candidate,'price':float(hist['Close'].dropna().iloc[-1])}
            except Exception: pass
        raise ValueError(f'Unable to retrieve quote for {symbol}.')

    @classmethod
    def history(cls,symbol:str,period:str='1mo',interval:str='1d')->dict:
        for candidate in cls.candidates(symbol):
            try:
                df=yf.download(candidate,period=period,interval=interval,auto_adjust=False,progress=False,threads=False)
                if df is None or df.empty: continue
                if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
                rows=[]
                for idx,row in df.dropna(subset=['Close']).iterrows():
                    rows.append({'date':pd.Timestamp(idx).date().isoformat(),'open':float(row['Open']),'high':float(row['High']),'low':float(row['Low']),'close':float(row['Close']),'volume':int(row['Volume'] or 0)})
                return {'symbol':symbol.upper(),'resolved_symbol':candidate,'period':period,'interval':interval,'data':rows}
            except Exception: pass
        raise ValueError(f'Unable to retrieve history for {symbol}.')
