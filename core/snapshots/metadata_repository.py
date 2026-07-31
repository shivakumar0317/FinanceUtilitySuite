from __future__ import annotations
import json
from pathlib import Path
from threading import RLock
from core.models.snapshot import SnapshotMetadata

class MetadataRepository:
    def __init__(self, metadata_file: str|Path) -> None:
        self.metadata_file=Path(metadata_file); self.metadata_file.parent.mkdir(parents=True,exist_ok=True); self._lock=RLock()
    def list_all(self)->list[SnapshotMetadata]:
        with self._lock: payload=self._read_payload()
        return sorted([SnapshotMetadata.from_dict(x) for x in payload.get("snapshots",[])],key=lambda x:x.timestamp,reverse=True)
    def get(self,snapshot_id:str)->SnapshotMetadata|None:
        return next((x for x in self.list_all() if x.snapshot_id==snapshot_id),None)
    def upsert(self,metadata:SnapshotMetadata)->None:
        with self._lock:
            payload=self._read_payload(); rows=payload.get("snapshots",[]); found=False
            for i,item in enumerate(rows):
                if str(item.get("snapshot_id"))==metadata.snapshot_id: rows[i]=metadata.to_dict(); found=True; break
            if not found: rows.append(metadata.to_dict())
            rows.sort(key=lambda x:str(x.get("timestamp","")),reverse=True); payload["snapshots"]=rows; self._write_payload(payload)
    def remove(self,snapshot_id:str)->bool:
        with self._lock:
            payload=self._read_payload(); rows=payload.get("snapshots",[]); kept=[x for x in rows if str(x.get("snapshot_id"))!=snapshot_id]
            if len(kept)==len(rows): return False
            payload["snapshots"]=kept; self._write_payload(payload); return True
    def _read_payload(self)->dict:
        if not self.metadata_file.exists(): return {"version":1,"snapshots":[]}
        try:
            with self.metadata_file.open('r',encoding='utf-8') as h: data=json.load(h)
        except (json.JSONDecodeError,OSError): return {"version":1,"snapshots":[]}
        if not isinstance(data,dict): return {"version":1,"snapshots":[]}
        data.setdefault("version",1); data.setdefault("snapshots",[]); return data
    def _write_payload(self,payload:dict)->None:
        temp=self.metadata_file.with_suffix('.tmp')
        with temp.open('w',encoding='utf-8') as h: json.dump(payload,h,indent=2,ensure_ascii=False)
        temp.replace(self.metadata_file)
