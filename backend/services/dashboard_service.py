"""
Dashboard Service

Aggregates all dashboard data required by the
Enterprise Dashboard.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.services.persistent_upload_service import PersistentUploadService
from core.services.enterprise_risk_service import EnterpriseRiskService


class DashboardService:
    """
    Enterprise Dashboard Service.

    Reads the active persisted MTF dataset for the user
    and sends it through the shared Enterprise Risk Engine.
    """

    DATASET_TYPE = PersistentUploadService.MTF

    def __init__(self) -> None:
        self.risk_service = EnterpriseRiskService()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def get_dashboard(
        self,
        db: Session,
        *,
        user_id: int,
    ) -> dict[str, Any]:
        """
        Return the complete Enterprise Dashboard payload.

        The dashboard reads the user's active persisted MTF
        dataset. No new file upload is required.
        """

        record = PersistentUploadService.get_active(
            db,
            user_id=user_id,
            dataset_type=self.DATASET_TYPE,
        )

        if record is None:
            return self._empty_dashboard(
                message="No active MTF dataset is available."
            )

        dataframe = PersistentUploadService.restore_dataframe(
            db,
            user_id=user_id,
            dataset_type=self.DATASET_TYPE,
        )

        if dataframe is not None:
            dataframe = self._normalize_mtf_dataframe(dataframe)

        if dataframe is None or dataframe.empty:
            return self._empty_dashboard(
                message="The active MTF dataset contains no records."
            )

        dataframe = self._normalize_mtf_dataframe(dataframe)

        summary = self.risk_service.analyze(dataframe)

        return {
            "summary": self._summary_payload(summary),
            "snapshot": {
                "snapshot_id": str(record.id),
                "business_date": self._business_date(record),
                "records": int(len(dataframe)),
                "clients": int(summary.clients),
                "symbols": int(summary.symbols),
            },
            "top_clients": self._risk_items(summary.top_clients),
            "top_symbols": self._risk_items(summary.top_symbols),
            "alerts": self._alerts(summary.alerts),
        }

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    @staticmethod
    def _summary_payload(summary) -> dict[str, Any]:
        return {
            "risk_score": float(summary.display_score),
            "health": str(summary.health),
            "total_exposure": float(summary.total_exposure),
            "total_mtm": float(summary.total_mtm),
            "margin_utilization": float(
                summary.margin_utilization_percent
            ),
            "diversification": float(
                summary.diversification_score
            ),
        }

    # ---------------------------------------------------------
    # Risk Items
    # ---------------------------------------------------------

    @staticmethod
    def _risk_items(items) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        for item in items or []:
            result.append(
                {
                    "name": str(
                        getattr(item, "name", "")
                    ),
                    "exposure": float(
                        getattr(item, "exposure", 0.0)
                    ),
                    "mtm": float(
                        getattr(item, "mtm", 0.0)
                    ),
                    "concentration_percent": float(
                        getattr(
                            item,
                            "concentration_percent",
                            0.0,
                        )
                    ),
                    "score": float(
                        getattr(item, "score", 0.0)
                    ),
                    "level": str(
                        getattr(item, "level", "Healthy")
                    ),
                }
            )

        return result

    # ---------------------------------------------------------
    # Alerts
    # ---------------------------------------------------------

    @staticmethod
    def _alerts(alerts) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        for alert in alerts or []:
            result.append(
                {
                    "level": str(
                        getattr(alert, "level", "Info")
                    ),
                    "title": str(
                        getattr(alert, "title", "")
                    ),
                    "message": str(
                        getattr(alert, "message", "")
                    ),
                    "recommendation": str(
                        getattr(
                            alert,
                            "recommendation",
                            "",
                        )
                    ),
                }
            )

        return result

    # ---------------------------------------------------------
    # Snapshot
    # ---------------------------------------------------------

    @staticmethod
    def _business_date(record) -> str:
        """
        UploadedDataset currently does not expose a dedicated
        business_date field, so use the creation timestamp.
        """

        created_at = getattr(record, "created_at", None)

        if created_at is None:
            return ""

        return created_at.isoformat()

    # ---------------------------------------------------------
    # Empty State
    # ---------------------------------------------------------

    @staticmethod
    def _empty_dashboard(
        *,
        message: str,
    ) -> dict[str, Any]:
        return {
            "summary": {
                "risk_score": 0.0,
                "health": "No Data",
                "total_exposure": 0.0,
                "total_mtm": 0.0,
                "margin_utilization": 0.0,
                "diversification": 0.0,
            },
            "snapshot": {
                "snapshot_id": "",
                "business_date": "",
                "records": 0,
                "clients": 0,
                "symbols": 0,
            },
            "top_clients": [],
            "top_symbols": [],
            "alerts": [
                {
                    "level": "Info",
                    "title": "Dashboard Unavailable",
                    "message": message,
                    "recommendation": (
                        "Import an MTF dataset before "
                        "viewing the Enterprise Dashboard."
                    ),
                }
            ],
        }

    @staticmethod
    def _normalize_mtf_dataframe(dataframe):
        """
        Normalize persisted broker MTF column names into
        the canonical Finance Utility Suite column names.
        """

        column_map = {
            "ACCOUNTID": "AccountId",
            "EXCHG-SEG": "Exchg-Seg",
            "SYMBOL": "Symbol",
            "INSTRUMENT NAME": "Instrument Name",
            "NETVALUE": "NetValue",
            "PRODUCT TYPE": "Product Type",
            "SERIES/EXPIRY": "Series/Expiry",
            "NETBUYQTY": "NetBuyQty",
            "NETSELLQTY": "NetSellQty",
            "NETQTY": "NetQty",
            "BUYAVGPRICE": "BuyAvgPrice",
            "LASTTRADEDPRICE": "LastTradedPrice",
            "MARKTOMARKET": "MarkToMarket",
            "BUY VALUE": "BUY VALUE",
            "MTF VAR": "MTF VAR",
            "MTF MARGIN": "MTF MARGIN",
        }

        dataframe = dataframe.copy()

        dataframe.rename(
            columns={
                column: column_map[column]
                for column in dataframe.columns
                if column in column_map
            },
            inplace=True,
        )

        return dataframe    