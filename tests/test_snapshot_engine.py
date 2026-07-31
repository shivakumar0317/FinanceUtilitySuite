from __future__ import annotations
from datetime import datetime,timedelta
from pathlib import Path
import shutil,sys,pandas as pd
PROJECT_ROOT=Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0,str(PROJECT_ROOT))
from core.services.history_service import HistoryService
from core.services.snapshot_service import SnapshotService
from core.snapshots.snapshot_repository import SnapshotRepository

def sample(mult=1.0):
    return pd.DataFrame({'AccountId':['C001','C002','C003'],'Symbol':['RELIANCE','TCS','INFY'],'NetQty':[10,5,8],'NetValue':[25000*mult,18000*mult,14000*mult],'Exposure':[25000*mult,18000*mult,14000*mult],'MarkToMarket':[1200*mult,-400*mult,650*mult],'Current Value':[25000*mult,18000*mult,14000*mult]})

def main():
    test_root=PROJECT_ROOT/'data/test_snapshots'; shutil.rmtree(test_root,ignore_errors=True)
    repo=SnapshotRepository(test_root); service=SnapshotService(repo); history=HistoryService(repo)
    t=datetime(2026,7,31,10,30)
    first=service.create_snapshot(sample(),source_file='MTF Test.xlsx',timestamp=t)
    second=service.create_snapshot(sample(1.1),source_file='MTF Test.xlsx',timestamp=t+timedelta(hours=1))
    assert len(service.list_snapshots())==2
    assert service.latest_snapshot().snapshot_id==second.snapshot_id
    assert len(service.load_snapshot(first.snapshot_id))==3
    comparison=service.compare_snapshots(first.snapshot_id,second.snapshot_id)
    assert comparison['portfolio_value_change']>0
    assert len(history.get_portfolio_history())==2
    changes=history.get_symbol_changes(first.snapshot_id,second.snapshot_id)
    assert changes['added']==[] and changes['removed']==[]
    print('RMS v2.0.2 Sprint 3 snapshot tests passed successfully.')
    print(f'Snapshots created : {len(service.list_snapshots())}')
    print(f'Portfolio change  : {comparison["portfolio_value_change"]:,.2f}')
    print(f'Exposure change   : {comparison["exposure_change"]:,.2f}')
    print(f'MTM change        : {comparison["mtm_change"]:,.2f}')
    shutil.rmtree(test_root,ignore_errors=True)
if __name__=='__main__': main()
