from pathlib import Path
import pandas as pd

from config import OUTPUT_FOLDER


class DashboardService:

    def get_statistics(self):

        reports = list(Path(OUTPUT_FOLDER).glob("Stock_Report_*.xlsx"))

        total_reports = len(reports)

        if total_reports == 0:

            return {"stocks": 0, "reports": 0, "avg_beta": 0, "high_risk": 0}

        latest = max(reports, key=lambda f: f.stat().st_mtime)

        df = pd.read_excel(latest)

        stats = {
            "stocks": len(df),
            "reports": total_reports,
            "avg_beta": round(df["Beta"].mean(), 2) if "Beta" in df else 0,
            "high_risk": len(df[df["Risk"] == "High"]) if "Risk" in df else 0,
        }

        return stats
