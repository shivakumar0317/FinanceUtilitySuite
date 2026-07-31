from __future__ import annotations
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import pandas as pd
from core.models.snapshot import SnapshotMetadata
from core.snapshots.snapshot_repository import SnapshotRepository

class SnapshotService:
    def __init__(self,repository:SnapshotRepository|None=None)->None: self.repository=repository or SnapshotRepository()
    def create_snapshot(self,dataframe:pd.DataFrame,*,source_file:str|Path='',notes:str='',timestamp:datetime|None=None)->SnapshotMetadata:
        if dataframe is None or dataframe.empty: raise ValueError('Cannot create a snapshot from empty portfolio data.')
        created=timestamp or datetime.now(); sid=created.strftime('%Y%m%d_%H%M%S_%f')+'_'+uuid4().hex[:6]
        filename=f'{sid}.parquet'; rel=str(Path(created.strftime('%Y-%m'))/filename)
        meta=SnapshotMetadata(sid,created.isoformat(timespec='seconds'),filename,rel,len(dataframe),self._unique(dataframe,'AccountId'),self._unique(dataframe,'Symbol'),self._sum(dataframe,('Current Value','NetValue','BUY VALUE'),True),self._sum(dataframe,('Exposure','NetValue'),True),self._sum(dataframe,('MarkToMarket','Profit/Loss'),False),str(source_file),notes)
        self.repository.save(dataframe,meta); return meta
    def load_snapshot(self,snapshot_id:str)->pd.DataFrame: return self.repository.load(snapshot_id)
    def list_snapshots(self): return self.repository.list_snapshots()
    def latest_snapshot(self): return self.repository.latest()
    def delete_snapshot(self,snapshot_id:str)->bool: return self.repository.delete(snapshot_id)
    def compare_snapshots(self,older_snapshot_id:str,newer_snapshot_id:str)->dict:
        old=self.repository.get_metadata(older_snapshot_id); new=self.repository.get_metadata(newer_snapshot_id)
        if old is None or new is None: raise FileNotFoundError('One or both snapshots were not found.')
        return {'older_snapshot_id':old.snapshot_id,'newer_snapshot_id':new.snapshot_id,'portfolio_value_change':new.portfolio_value-old.portfolio_value,'exposure_change':new.total_exposure-old.total_exposure,'mtm_change':new.total_mtm-old.total_mtm,'client_change':new.clients-old.clients,'symbol_change':new.symbols-old.symbols,'record_change':new.records-old.records}
    @staticmethod
    def _unique(df,column): return int(df[column].dropna().nunique()) if column in df.columns else 0
    @staticmethod
    def _sum(df,columns,absolute):
        for c in columns:
            if c in df.columns:
                s=pd.to_numeric(df[c],errors='coerce').fillna(0.0); s=s.abs() if absolute else s; return float(s.sum())
        return 0.0
