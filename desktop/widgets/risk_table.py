from __future__ import annotations
from tkinter import ttk
import customtkinter as ctk
class RiskTable(ctk.CTkFrame):
    COLS=(('name','Name',145,'w'),('exposure','Exposure',130,'e'),('mtm','MTM',120,'e'),('concentration','Conc. %',85,'e'),('level','Level',90,'center'))
    def __init__(self,master,title):
        super().__init__(master,corner_radius=12,border_width=1,border_color=('#D1D5DB','#374151')); self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
        ctk.CTkLabel(self,text=title,font=('Segoe UI',17,'bold'),anchor='w').grid(row=0,column=0,sticky='ew',padx=16,pady=(14,8))
        style=ttk.Style(); style.configure('Risk.Treeview',background='#111827',fieldbackground='#111827',foreground='#E5E7EB',rowheight=28,font=('Segoe UI',9)); style.configure('Risk.Treeview.Heading',background='#1F2937',foreground='#F9FAFB',font=('Segoe UI',9,'bold')); style.map('Risk.Treeview',background=[('selected','#1D4ED8')],foreground=[('selected','#FFFFFF')])
        self.tree=ttk.Treeview(self,columns=[c[0] for c in self.COLS],show='headings',style='Risk.Treeview',height=7)
        for k,h,w,a in self.COLS: self.tree.heading(k,text=h); self.tree.column(k,width=w,minwidth=70,anchor=a,stretch=True)
        sb=ttk.Scrollbar(self,orient='vertical',command=self.tree.yview); self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=1,column=0,sticky='nsew',padx=(12,0),pady=(0,12)); sb.grid(row=1,column=1,sticky='ns',padx=(0,12),pady=(0,12))
        self.tree.tag_configure('Healthy',foreground='#22C55E'); self.tree.tag_configure('Warning',foreground='#F59E0B'); self.tree.tag_configure('Critical',foreground='#EF4444')
    def load_items(self,items,limit=10):
        self.tree.delete(*self.tree.get_children())
        for item in list(items)[:limit]: self.tree.insert('', 'end', values=(item.name,self._money(item.exposure),self._money(item.mtm),f'{item.concentration_percent:.2f}%',item.level), tags=(item.level,))
    @staticmethod
    def _money(v):
        a=abs(float(v)); s='-' if v<0 else ''
        if a>=1e7:return f'{s}₹{a/1e7:.2f} Cr'
        if a>=1e5:return f'{s}₹{a/1e5:.2f} L'
        return f'{s}₹{a:,.2f}'
