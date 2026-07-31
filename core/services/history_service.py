from __future__ import annotations
import pandas as pd
from core.snapshots.snapshot_repository import SnapshotRepository

class HistoryService:
    def __init__(self,repository:SnapshotRepository|None=None)->None: self.repository=repository or SnapshotRepository()
    def get_portfolio_history(self)->pd.DataFrame:
        rows=[x.to_dict() for x in reversed(self.repository.list_snapshots())]
        cols=['snapshot_id','timestamp','records','clients','symbols','portfolio_value','total_exposure','total_mtm','source_file','notes']
        if not rows: return pd.DataFrame(columns=cols)
        f=pd.DataFrame(rows); f['timestamp']=pd.to_datetime(f['timestamp'],errors='coerce'); return f[cols].sort_values('timestamp').reset_index(drop=True)
    def get_mtm_history(self): return self.get_portfolio_history()[['timestamp','total_mtm']].copy()
    def get_exposure_history(self): return self.get_portfolio_history()[['timestamp','total_exposure']].copy()
    def get_client_history(self): return self.get_portfolio_history()[['timestamp','clients']].copy()
    def get_symbol_changes(self,older_snapshot_id:str,newer_snapshot_id:str)->dict:
        old=self.repository.load(older_snapshot_id); new=self.repository.load(newer_snapshot_id)
        a={str(x).strip().upper() for x in old.get('Symbol',pd.Series(dtype=str)).dropna() if str(x).strip()}; b={str(x).strip().upper() for x in new.get('Symbol',pd.Series(dtype=str)).dropna() if str(x).strip()}
        return {'added':sorted(b-a),'removed':sorted(a-b),'unchanged':sorted(a&b)}
