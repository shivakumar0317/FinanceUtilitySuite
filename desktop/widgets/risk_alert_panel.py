from __future__ import annotations
import customtkinter as ctk
class RiskAlertPanel(ctk.CTkFrame):
    COLORS={'Healthy':'#22C55E','Warning':'#F59E0B','Critical':'#EF4444'}
    def __init__(self,master):
        super().__init__(master,corner_radius=12,border_width=1,border_color=('#D1D5DB','#374151')); self.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(self,text='Enterprise Alert Center',font=('Segoe UI',17,'bold'),anchor='w').grid(row=0,column=0,sticky='ew',padx=16,pady=(14,8))
        self.box=ctk.CTkFrame(self,fg_color='transparent'); self.box.grid(row=1,column=0,sticky='ew',padx=12,pady=(0,12)); self.box.grid_columnconfigure(0,weight=1)
    def load_alerts(self,alerts):
        for w in self.box.winfo_children():w.destroy()
        for r,a in enumerate(alerts):
            color=self.COLORS.get(a.level,'#3B82F6'); card=ctk.CTkFrame(self.box,corner_radius=8,border_width=1,border_color=color); card.grid(row=r,column=0,sticky='ew',pady=5); card.grid_columnconfigure(1,weight=1)
            ctk.CTkLabel(card,text=a.level.upper(),font=('Segoe UI',10,'bold'),text_color=color,width=82).grid(row=0,column=0,rowspan=3,padx=10,pady=10)
            ctk.CTkLabel(card,text=a.title,font=('Segoe UI',12,'bold'),anchor='w').grid(row=0,column=1,sticky='ew',padx=(0,12),pady=(8,1))
            ctk.CTkLabel(card,text=a.message,font=('Segoe UI',10),anchor='w',justify='left',wraplength=760).grid(row=1,column=1,sticky='ew',padx=(0,12),pady=1)
            ctk.CTkLabel(card,text='Recommended action: '+a.recommendation,font=('Segoe UI',9,'italic'),text_color=('#6B7280','#9CA3AF'),anchor='w',justify='left',wraplength=760).grid(row=2,column=1,sticky='ew',padx=(0,12),pady=(1,8))
