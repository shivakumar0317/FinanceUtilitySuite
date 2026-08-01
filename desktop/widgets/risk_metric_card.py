from __future__ import annotations
import customtkinter as ctk
class RiskMetricCard(ctk.CTkFrame):
    COLORS={'Healthy':'#22C55E','Warning':'#F59E0B','Critical':'#EF4444','Neutral':'#3B82F6'}
    def __init__(self,master,title,value='--',subtitle='',status='Neutral',width=190,height=128):
        super().__init__(master,width=width,height=height,corner_radius=12,border_width=1,border_color=('#D1D5DB','#374151')); self.grid_propagate(False); self.configure(fg_color=('#FFFFFF','#111827'))
        self.accent=ctk.CTkFrame(self,width=5,corner_radius=8,fg_color=self.COLORS.get(status,self.COLORS['Neutral'])); self.accent.grid(row=0,column=0,rowspan=3,sticky='ns',padx=(0,12))
        self.title_label=ctk.CTkLabel(self,text=title,font=('Segoe UI',12,'bold'),text_color=('#4B5563','#9CA3AF'),anchor='w'); self.title_label.grid(row=0,column=1,sticky='ew',pady=(14,2))
        self.value_label=ctk.CTkLabel(self,text=value,font=('Segoe UI',23,'bold'),anchor='w'); self.value_label.grid(row=1,column=1,sticky='ew')
        self.subtitle_label=ctk.CTkLabel(self,text=subtitle,font=('Segoe UI',10),text_color=('#6B7280','#9CA3AF'),anchor='w',justify='left',wraplength=260); self.subtitle_label.grid(row=2,column=1,sticky='new',pady=(2,12)); self.grid_columnconfigure(1,weight=1)
    def set_data(self,value,subtitle='',status='Neutral'):
        self.value_label.configure(text=value); self.subtitle_label.configure(text=subtitle); self.accent.configure(fg_color=self.COLORS.get(status,self.COLORS['Neutral']))
