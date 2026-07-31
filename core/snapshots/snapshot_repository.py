from __future__ import annotations
from pathlib import Path
import pandas as pd
from core.models.snapshot import SnapshotMetadata
from core.snapshots.metadata_repository import MetadataRepository

class SnapshotRepository:
    def __init__(self,root_dir:str|Path='data/snapshots')->None:
        self.root_dir=Path(root_dir); self.root_dir.mkdir(parents=True,exist_ok=True)
        self.metadata_repository=MetadataRepository(self.root_dir/'metadata.json')
    def save(self,dataframe:pd.DataFrame,metadata:SnapshotMetadata)->Path:
        if dataframe is None or dataframe.empty: raise ValueError('Cannot save an empty snapshot.')
        target=self.root_dir/metadata.relative_path; target.parent.mkdir(parents=True,exist_ok=True)
        try: dataframe.to_parquet(target,index=False,engine='pyarrow',compression='snappy')
        except ImportError as exc: raise RuntimeError('Parquet support requires pyarrow. Install it with: pip install pyarrow') from exc
        self.metadata_repository.upsert(metadata); return target
    def load(self,snapshot_id:str)->pd.DataFrame:
        meta=self.get_metadata(snapshot_id)
        if meta is None: raise FileNotFoundError(f'Snapshot not found: {snapshot_id}')
        path=self.root_dir/meta.relative_path
        if not path.exists(): raise FileNotFoundError(f'Snapshot data file is missing: {path}')
        return pd.read_parquet(path,engine='pyarrow')
    def list_snapshots(self)->list[SnapshotMetadata]: return self.metadata_repository.list_all()
    def latest(self)->SnapshotMetadata|None:
        items=self.list_snapshots(); return items[0] if items else None
    def get_metadata(self,snapshot_id:str)->SnapshotMetadata|None: return self.metadata_repository.get(snapshot_id)
    def delete(self,snapshot_id:str)->bool:
        meta=self.get_metadata(snapshot_id)
        if meta is None: return False
        path=self.root_dir/meta.relative_path
        if path.exists(): path.unlink()
        self.metadata_repository.remove(snapshot_id); return True
