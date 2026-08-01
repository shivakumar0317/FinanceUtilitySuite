from __future__ import annotations
import pandas as pd
from core.services.risk_engine import RiskEngine

def main():
    df=pd.DataFrame({'AccountId':['A1','A1','A2','A3'],'Symbol':['AAA','BBB','AAA','CCC'],'NetValue':[400000,100000,250000,250000],'Exposure':[400000,100000,250000,250000],'MarkToMarket':[-80000,-5000,10000,-15000],'MTF VAR':[60000,15000,35000,35000],'MTF MARGIN':[280000,70000,175000,175000]})
    s=RiskEngine().analyze(df,snapshot_id='TEST_SNAPSHOT')
    assert s.calculated_score==s.overall_score and s.display_score>=80 and s.health=='Critical' and s.alerts and s.snapshot_id=='TEST_SNAPSHOT'
    print('RMS v2.1.2 Sprint 4.1 Patch 2 tests passed successfully.')
    print(f'Calculated score : {s.calculated_score:.2f}')
    print(f'Display score    : {s.display_score:.2f}')
    print(f'Health           : {s.health}')
    print(f'Alerts           : {len(s.alerts)}')
if __name__=='__main__':main()
