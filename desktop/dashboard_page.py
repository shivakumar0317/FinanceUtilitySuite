from __future__ import annotations
from datetime import datetime
import customtkinter as ctk
from core.dashboard_service import DashboardService
from desktop.widgets.risk_alert_panel import RiskAlertPanel
from desktop.widgets.risk_metric_card import RiskMetricCard
from desktop.widgets.risk_table import RiskTable
class DashboardPage(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master); self.dashboard_service=DashboardService(); self.metric_cards={}; self._build(); self.load_dashboard()
    def _build(self):
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
        h=ctk.CTkFrame(self,fg_color='transparent'); h.grid(row=0,column=0,sticky='ew',padx=24,pady=(18,8)); h.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(h,text='Enterprise Risk Dashboard',font=('Segoe UI',28,'bold'),anchor='w').grid(row=0,column=0,sticky='w')
        self.header_status=ctk.CTkLabel(h,text='Risk Engine: Waiting',font=('Segoe UI',11,'bold'),text_color='#3B82F6'); self.header_status.grid(row=0,column=1,sticky='e',padx=(12,12))
        self.refresh_button=ctk.CTkButton(h,text='Refresh',width=105,command=self.load_dashboard); self.refresh_button.grid(row=0,column=2)
        ctk.CTkLabel(h,text='Centralized portfolio health, concentration and threshold monitoring',font=('Segoe UI',12),text_color=('#6B7280','#9CA3AF'),anchor='w').grid(row=1,column=0,columnspan=3,sticky='w',pady=(3,0))
        self.scroll=ctk.CTkScrollableFrame(self,corner_radius=0,fg_color='transparent'); self.scroll.grid(row=1,column=0,sticky='nsew',padx=16,pady=(0,14)); self.scroll.grid_columnconfigure((0,1),weight=1)
        cards=ctk.CTkFrame(self.scroll,fg_color='transparent'); cards.grid(row=0,column=0,columnspan=2,sticky='ew',padx=4,pady=(6,12))
        for c in range(3):cards.grid_columnconfigure(c,weight=1)
        defs=[('score','Executive Risk Score'),('health','Portfolio Health'),('exposure','Total Exposure'),('mtm','MTM Loss'),('margin','Margin Utilization'),('diversification','Diversification')]
        for i,(k,t) in enumerate(defs):
            card=RiskMetricCard(cards,title=t,value='--',subtitle='Import an MTF file',height=136); card.grid(row=i//3,column=i%3,sticky='ew',padx=8,pady=8); self.metric_cards[k]=card
        self.client_table=RiskTable(self.scroll,'Top Risky Clients'); self.client_table.grid(row=1,column=0,sticky='nsew',padx=(8,6),pady=8)
        self.symbol_table=RiskTable(self.scroll,'Top Risky Symbols'); self.symbol_table.grid(row=1,column=1,sticky='nsew',padx=(6,8),pady=8)
        self.alert_panel=RiskAlertPanel(self.scroll); self.alert_panel.grid(row=2,column=0,columnspan=2,sticky='ew',padx=8,pady=8)
        self.footer=ctk.CTkFrame(self.scroll,corner_radius=10,border_width=1,border_color=('#D1D5DB','#374151')); self.footer.grid(row=3,column=0,columnspan=2,sticky='ew',padx=8,pady=(8,16))
        for c in range(4):self.footer.grid_columnconfigure(c,weight=1)
        self.footer_labels={}
        for c,(k,t) in enumerate([('snapshot','Snapshot'),('refresh','Last Refresh'),('portfolio','Portfolio'),('engine','Risk Engine')]):
            f=ctk.CTkFrame(self.footer,fg_color='transparent'); f.grid(row=0,column=c,sticky='ew',padx=12,pady=10)
            ctk.CTkLabel(f,text=t,font=('Segoe UI',9),text_color=('#6B7280','#9CA3AF')).pack(anchor='w'); lab=ctk.CTkLabel(f,text='--',font=('Segoe UI',10,'bold')); lab.pack(anchor='w'); self.footer_labels[k]=lab
        self.empty_label=ctk.CTkLabel(self.scroll,text='',font=('Segoe UI',12),text_color=('#6B7280','#9CA3AF')); self.empty_label.grid(row=4,column=0,columnspan=2,sticky='ew',padx=10,pady=(0,8))
    def load_dashboard(self):
        self.refresh_button.configure(state='disabled',text='Loading...'); self.update_idletasks()
        try:
            data=self.dashboard_service.get_dashboard_data()
            if not data.available or data.summary is None:self._empty(data.message); return
            self._populate(data.summary); self.empty_label.configure(text='')
        finally:self.refresh_button.configure(state='normal',text='Refresh')
    def _empty(self,msg):
        for c in self.metric_cards.values():c.set_data('--','Import an MTF file to calculate risk','Neutral')
        self.client_table.load_items([]); self.symbol_table.load_items([]); self.alert_panel.load_alerts([]); self.header_status.configure(text='Risk Engine: Waiting',text_color='#3B82F6')
        for l in self.footer_labels.values():l.configure(text='--')
        self.empty_label.configure(text=msg)
    def _populate(self,s):
        color={'Healthy':'#22C55E','Warning':'#F59E0B','Critical':'#EF4444'}.get(s.health,'#3B82F6'); self.header_status.configure(text='Risk Engine: '+s.health.upper(),text_color=color)
        self.metric_cards['score'].set_data(f'{s.display_score:.0f} / 100',f'Calculated score: {s.calculated_score:.2f}',s.health)
        self.metric_cards['health'].set_data(s.health.upper(),{'Critical':'Immediate attention required','Warning':'Enhanced monitoring required','Healthy':'Within configured thresholds'}.get(s.health,'Risk status unavailable'),s.health)
        self.metric_cards['exposure'].set_data(self._money(s.total_exposure),f'{s.clients:,} clients • {s.symbols:,} symbols','Neutral')
        self.metric_cards['mtm'].set_data(self._money(s.total_mtm),f'{s.mtm_loss_percent:.2f}% loss of exposure',self._mtm_status(s.mtm_loss_percent))
        self.metric_cards['margin'].set_data(f'{s.margin_utilization_percent:.2f}%',f'Margin: {self._money(s.total_margin)}',self._margin_status(s.margin_utilization_percent))
        self.metric_cards['diversification'].set_data(f'{s.diversification_score:.2f} / 100',f'Client {s.top_client_concentration_percent:.2f}% • Symbol {s.top_symbol_concentration_percent:.2f}%',self._div_status(s.diversification_score))
        self.client_table.load_items(s.top_clients); self.symbol_table.load_items(s.top_symbols); self.alert_panel.load_alerts(s.alerts)
        self.footer_labels['snapshot'].configure(text=s.snapshot_id or 'Current Portfolio'); self.footer_labels['refresh'].configure(text=self._time(s.last_refresh)); self.footer_labels['portfolio'].configure(text=f'{s.records:,} positions'); self.footer_labels['engine'].configure(text=s.engine_status)
    @staticmethod
    def _money(v):
        a=abs(float(v)); sg='-' if v<0 else ''
        if a>=1e7:return f'{sg}₹{a/1e7:.2f} Cr'
        if a>=1e5:return f'{sg}₹{a/1e5:.2f} L'
        return f'{sg}₹{a:,.2f}'
    @staticmethod
    def _time(v):
        try:return datetime.fromisoformat(v).strftime('%d-%b-%Y %I:%M:%S %p')
        except:return v or '--'
    @staticmethod
    def _mtm_status(p):return 'Critical' if p>=8 else 'Warning' if p>=5 else 'Healthy'
    @staticmethod
    def _margin_status(p):return 'Critical' if p>=80 else 'Warning' if p>=60 else 'Healthy'
    @staticmethod
    def _div_status(s):return 'Critical' if s<40 else 'Warning' if s<65 else 'Healthy'
