from __future__ import annotations
from datetime import datetime
import pandas as pd
from core.models.risk_summary import RiskAlert, RiskSummary
from core.services.exposure_service import ExposureService
from core.services.health_service import HealthService
from core.services.margin_service import MarginService
from core.services.mtm_risk_service import MTMRiskService
from core.services.risk_concentration_service import RiskConcentrationService
from core.services.risk_config import RiskConfig
from core.services.score_service import ScoreService

class RiskEngine:
    REQUIRED_COLUMNS={'AccountId','Symbol','MarkToMarket','MTF VAR','MTF MARGIN'}
    def __init__(self, config: RiskConfig|None=None):
        self.config=config or RiskConfig(); self.config.validate()
    def analyze(self, dataframe: pd.DataFrame, *, snapshot_id: str='')->RiskSummary:
        self._validate_dataframe(dataframe); frame=dataframe.copy(); t=self.config.thresholds
        exposure=ExposureService.total_exposure(frame); portfolio_value=ExposureService.portfolio_value(frame)
        total_mtm=MTMRiskService.total_mtm(frame); total_margin=MarginService.total_margin(frame); total_var=MarginService.total_var(frame)
        mtm_loss_percent=MTMRiskService.mtm_loss_percent(frame, exposure)
        margin_utilization=MarginService.utilization_percent(frame, exposure)
        top_client_percent=RiskConcentrationService.top_concentration_percent(frame,'AccountId')
        top_symbol_percent=RiskConcentrationService.top_concentration_percent(frame,'Symbol')
        exposure_score=ExposureService.score(frame); mtm_score=MTMRiskService.score(frame, exposure, t); margin_score=MarginService.score(frame, exposure, t)
        client_score=RiskConcentrationService.score(frame,'AccountId',t.client_concentration_warning_percent,t.client_concentration_critical_percent)
        symbol_score=RiskConcentrationService.score(frame,'Symbol',t.symbol_concentration_warning_percent,t.symbol_concentration_critical_percent)
        calculated_score=ScoreService.calculate(exposure_score=exposure_score,mtm_score=mtm_score,margin_score=margin_score,client_concentration_score=client_score,symbol_concentration_score=symbol_score,weights=self.config.weights)
        diversification_score=ScoreService.diversification_score(client_score,symbol_score)
        health,reason=HealthService.evaluate(overall_score=calculated_score,mtm_loss_percent=mtm_loss_percent,margin_utilization_percent=margin_utilization,thresholds=t)
        display_score=max(calculated_score,80.0) if health=='Critical' else max(calculated_score,60.0) if health=='Warning' else calculated_score
        warnings=self._build_warnings(mtm_loss_percent,margin_utilization,top_client_percent,top_symbol_percent)
        alerts=self._build_alerts(mtm_loss_percent,margin_utilization,top_client_percent,top_symbol_percent)
        return RiskSummary(overall_score=round(calculated_score,2),calculated_score=round(calculated_score,2),display_score=round(display_score,2),health=health,health_reason=reason,records=len(frame),clients=self._nunique(frame,'AccountId'),symbols=self._nunique(frame,'Symbol'),portfolio_value=round(portfolio_value,2),total_exposure=round(exposure,2),total_mtm=round(total_mtm,2),total_var=round(total_var,2),total_margin=round(total_margin,2),mtm_loss_percent=round(mtm_loss_percent,2),margin_utilization_percent=round(margin_utilization,2),top_client_concentration_percent=round(top_client_percent,2),top_symbol_concentration_percent=round(top_symbol_percent,2),exposure_score=round(exposure_score,2),mtm_score=round(mtm_score,2),margin_score=round(margin_score,2),client_concentration_score=round(client_score,2),symbol_concentration_score=round(symbol_score,2),diversification_score=round(diversification_score,2),top_clients=RiskConcentrationService.top_items(frame,'AccountId',t,self.config.top_n),top_symbols=RiskConcentrationService.top_items(frame,'Symbol',t,self.config.top_n),warnings=warnings,alerts=alerts,snapshot_id=snapshot_id,last_refresh=datetime.now().isoformat(timespec='seconds'),engine_status='Ready')
    @classmethod
    def analyze_current_portfolio(cls)->RiskSummary:
        from core.state.application_state import ApplicationState
        df=ApplicationState.get_master_portfolio()
        if df is None or df.empty: raise ValueError('No master portfolio is loaded. Import an MTF file before running the Risk Engine.')
        sid=''
        try:
            from core.services.snapshot_service import SnapshotService
            latest=SnapshotService().latest_snapshot(); sid=latest.snapshot_id if latest else ''
        except Exception: pass
        return cls().analyze(df,snapshot_id=sid)
    def _build_warnings(self,mtm,margin,client,symbol):
        t=self.config.thresholds; out=[]
        if mtm>=t.mtm_critical_percent: out.append('MTM loss has crossed the critical threshold.')
        elif mtm>=t.mtm_warning_percent: out.append('MTM loss has crossed the warning threshold.')
        if margin>=t.margin_critical_percent: out.append('Margin utilization has crossed the critical threshold.')
        elif margin>=t.margin_warning_percent: out.append('Margin utilization has crossed the warning threshold.')
        if client>=t.client_concentration_critical_percent: out.append('Largest client concentration is critical.')
        elif client>=t.client_concentration_warning_percent: out.append('Largest client concentration requires attention.')
        if symbol>=t.symbol_concentration_critical_percent: out.append('Largest symbol concentration is critical.')
        elif symbol>=t.symbol_concentration_warning_percent: out.append('Largest symbol concentration requires attention.')
        return out
    def _build_alerts(self,mtm,margin,client,symbol):
        t=self.config.thresholds; alerts=[]
        if mtm>=t.mtm_critical_percent: alerts.append(RiskAlert('Critical','MTM Threshold Breach',f'MTM loss is {mtm:.2f}% of total exposure.','Review the largest losing positions and initiate the approved risk-control process.'))
        elif mtm>=t.mtm_warning_percent: alerts.append(RiskAlert('Warning','MTM Loss Warning',f'MTM loss is {mtm:.2f}% of total exposure.','Monitor high-loss clients and symbols closely.'))
        if margin>=t.margin_critical_percent: alerts.append(RiskAlert('Critical','Margin Utilization Breach',f'Margin utilization is {margin:.2f}%.','Review additional margin requirements and reduce exposure where required.'))
        elif margin>=t.margin_warning_percent: alerts.append(RiskAlert('Warning','Margin Utilization Warning',f'Margin utilization is {margin:.2f}%.','Monitor margin availability and exposure growth.'))
        if client>=t.client_concentration_critical_percent: alerts.append(RiskAlert('Critical','Client Concentration Breach',f'The largest client contributes {client:.2f}% of total exposure.','Review the largest client positions and limits.'))
        elif client>=t.client_concentration_warning_percent: alerts.append(RiskAlert('Warning','Client Concentration Warning',f'The largest client contributes {client:.2f}% of total exposure.','Monitor concentration in the largest client.'))
        if symbol>=t.symbol_concentration_critical_percent: alerts.append(RiskAlert('Critical','Symbol Concentration Breach',f'The largest symbol contributes {symbol:.2f}% of total exposure.','Review the largest symbol exposure and liquidity.'))
        elif symbol>=t.symbol_concentration_warning_percent: alerts.append(RiskAlert('Warning','Symbol Concentration Warning',f'The largest symbol contributes {symbol:.2f}% of total exposure.','Monitor concentration in the largest symbol.'))
        return alerts or [RiskAlert('Healthy','No Active Breach','No configured risk threshold is currently breached.','Continue routine monitoring.')]
    @classmethod
    def _validate_dataframe(cls, dataframe):
        if not isinstance(dataframe,pd.DataFrame): raise TypeError('RiskEngine expects a pandas DataFrame.')
        if dataframe.empty: raise ValueError('RiskEngine cannot analyze an empty dataframe.')
        missing=sorted(cls.REQUIRED_COLUMNS-set(dataframe.columns))
        if 'Exposure' not in dataframe.columns and 'NetValue' not in dataframe.columns: missing.append('Exposure or NetValue')
        if missing: raise ValueError('RiskEngine missing required columns: '+', '.join(missing))
    @staticmethod
    def _nunique(dataframe,column):
        if column not in dataframe.columns: return 0
        values=dataframe[column].fillna('').astype(str).str.strip(); return int(values[values!=''].nunique())
