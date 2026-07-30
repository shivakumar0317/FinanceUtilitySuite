"""Report Center export orchestration.

The service accepts the same compact portfolio input used by Portfolio Analyzer::

    Symbol | Qty | Buy Price

Before portfolio or analytics export, the data is normalised and enriched with
live current prices through the application's existing ``MarketDataService``.
No Tkinter code is used here, keeping the workflow independently testable.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Callable, Final

import pandas as pd

from desktop.reports.report_controller import ReportController
from desktop.reports.report_registry import ReportDefinition


class ReportExportError(ValueError):
    """Raised when Report Center inputs cannot be exported safely."""


@dataclass(frozen=True, slots=True)
class ReportExportRequest:
    """Validated values required for one Report Center export."""

    report_id: str
    source_path: Path
    output_path: Path
    portfolio_name: str = "Portfolio"
    account_id: str = "CLIENT"
    history_path: Path | None = None

    def __post_init__(self) -> None:
        report_id = self.report_id.strip().lower()
        source = Path(self.source_path).expanduser()
        output = Path(self.output_path).expanduser()
        history = Path(self.history_path).expanduser() if self.history_path else None

        if report_id not in {"portfolio", "analytics", "client_holdings"}:
            raise ReportExportError(f"Unsupported report: {self.report_id}")
        if not source.exists() or not source.is_file():
            raise ReportExportError(f"Source data file was not found: {source}")
        if source.suffix.lower() not in {".xlsx", ".xls", ".csv"}:
            raise ReportExportError("Source data must be an Excel or CSV file.")
        if output.suffix.lower() != ".xlsx":
            output = output.with_suffix(".xlsx")
        if history is not None:
            if not history.exists() or not history.is_file():
                raise ReportExportError(f"History data file was not found: {history}")
            if history.suffix.lower() not in {".xlsx", ".xls", ".csv"}:
                raise ReportExportError("History data must be an Excel or CSV file.")

        object.__setattr__(self, "report_id", report_id)
        object.__setattr__(self, "source_path", source)
        object.__setattr__(self, "output_path", output)
        object.__setattr__(self, "history_path", history)
        object.__setattr__(self, "portfolio_name", self.portfolio_name.strip() or "Portfolio")
        object.__setattr__(self, "account_id", self.account_id.strip() or "CLIENT")


ProgressCallback = Callable[[int, str], None]


class ReportExportService:
    """Load, normalise and enrich source data, then dispatch the export."""

    PORTFOLIO_ALIASES: Final[dict[str, tuple[str, ...]]] = {
        "Symbol": ("Symbol", "Stock", "Scrip", "Ticker", "Security"),
        "Quantity": ("Quantity", "Qty", "QTY", "Net Qty", "NetQty"),
        "Average Price": (
            "Average Price", "Avg Price", "AVG PRICE", "Buy Price",
            "Purchase Price", "Cost Price",
        ),
        "Current Price": (
            "Current Price", "LTP", "Market Price", "Last Price", "CMP",
        ),
    }

    MARKET_SERVICE_MODULES: Final[tuple[str, ...]] = (
        "core.services.market_data_service",
        "core.market_data_service",
        "services.market_data_service",
    )

    @staticmethod
    def load_dataframe(path: str | Path) -> pd.DataFrame:
        source = Path(path)
        try:
            dataframe = pd.read_csv(source) if source.suffix.lower() == ".csv" else pd.read_excel(source)
        except Exception as exc:
            raise ReportExportError(f"Unable to read data file '{source.name}': {exc}") from exc

        if dataframe.empty:
            raise ReportExportError(f"Data file '{source.name}' contains no rows.")
        dataframe.columns = [str(column).strip() for column in dataframe.columns]
        return dataframe

    @classmethod
    def _normalise_portfolio_columns(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        frame = dataframe.copy()
        lower_lookup = {str(column).strip().casefold(): column for column in frame.columns}
        rename_map: dict[object, str] = {}

        for canonical, aliases in cls.PORTFOLIO_ALIASES.items():
            for alias in aliases:
                original = lower_lookup.get(alias.casefold())
                if original is not None:
                    rename_map[original] = canonical
                    break

        frame = frame.rename(columns=rename_map)
        required_input = ("Symbol", "Quantity", "Average Price")
        missing = [column for column in required_input if column not in frame.columns]
        if missing:
            raise ReportExportError(
                "Missing required portfolio columns: " + ", ".join(missing)
                + ". Supported compact format: Symbol, Qty, Buy Price."
            )

        frame["Symbol"] = frame["Symbol"].astype(str).str.strip().str.upper()
        frame = frame[frame["Symbol"].ne("") & frame["Symbol"].ne("NAN")].copy()
        if frame.empty:
            raise ReportExportError("The portfolio contains no valid symbols.")

        for column in ("Quantity", "Average Price"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        invalid = frame[["Quantity", "Average Price"]].isna().any(axis=1)
        if invalid.any():
            rows = ", ".join(str(index + 2) for index in frame.index[invalid][:10])
            raise ReportExportError(f"Invalid Qty or Buy Price in Excel row(s): {rows}.")

        return frame

    @classmethod
    def _market_data_service(cls):
        errors: list[str] = []
        for module_name in cls.MARKET_SERVICE_MODULES:
            try:
                module = import_module(module_name)
                service = getattr(module, "MarketDataService")
                return service
            except (ImportError, AttributeError) as exc:
                errors.append(f"{module_name}: {exc}")
        raise ReportExportError(
            "MarketDataService could not be loaded. Expected "
            "core/services/market_data_service.py with MarketDataService.get_current_price()."
        )

    @classmethod
    def _get_current_price(cls, symbol: str) -> float:
        service = cls._market_data_service()
        try:
            price = service.get_current_price(symbol)
        except Exception as exc:
            raise ReportExportError(f"Unable to fetch current price for {symbol}: {exc}") from exc
        try:
            numeric_price = float(price)
        except (TypeError, ValueError) as exc:
            raise ReportExportError(f"Invalid current price returned for {symbol}: {price!r}") from exc
        if numeric_price <= 0:
            raise ReportExportError(f"No valid current price was found for {symbol}.")
        return numeric_price

    @classmethod
    def prepare_portfolio_dataframe(
        cls,
        dataframe: pd.DataFrame,
        *,
        progress: ProgressCallback | None = None,
    ) -> pd.DataFrame:
        """Normalise compact portfolio columns and add missing current prices."""
        notify = progress or (lambda _value, _message: None)
        frame = cls._normalise_portfolio_columns(dataframe)

        if "Current Price" in frame.columns:
            frame["Current Price"] = pd.to_numeric(frame["Current Price"], errors="coerce")
        else:
            frame["Current Price"] = pd.NA

        symbols = list(dict.fromkeys(frame["Symbol"].tolist()))
        price_map: dict[str, float] = {}
        missing_symbols = [
            symbol for symbol in symbols
            if frame.loc[frame["Symbol"].eq(symbol), "Current Price"].isna().all()
        ]

        total = max(len(missing_symbols), 1)
        for position, symbol in enumerate(missing_symbols, start=1):
            percent = 20 + int((position / total) * 18)
            notify(percent, f"Fetching current price: {symbol} ({position}/{len(missing_symbols)})")
            price_map[symbol] = cls._get_current_price(symbol)

        if price_map:
            missing_mask = frame["Current Price"].isna()
            frame.loc[missing_mask, "Current Price"] = frame.loc[missing_mask, "Symbol"].map(price_map)

        frame["Current Price"] = pd.to_numeric(frame["Current Price"], errors="coerce")
        if frame["Current Price"].isna().any() or (frame["Current Price"] <= 0).any():
            symbols_failed = frame.loc[
                frame["Current Price"].isna() | (frame["Current Price"] <= 0), "Symbol"
            ].drop_duplicates().tolist()
            raise ReportExportError(
                "Current price is unavailable for: " + ", ".join(symbols_failed)
            )

        return frame

    @classmethod
    def export(
        cls,
        request: ReportExportRequest,
        *,
        progress: ProgressCallback | None = None,
    ) -> Path:
        if not isinstance(request, ReportExportRequest):
            raise TypeError("request must be a ReportExportRequest")

        notify = progress or (lambda _value, _message: None)
        notify(10, "Loading source data...")
        dataframe = cls.load_dataframe(request.source_path)

        if request.report_id in {"portfolio", "analytics"}:
            notify(18, "Preparing portfolio data...")
            dataframe = cls.prepare_portfolio_dataframe(dataframe, progress=notify)

        history_df: pd.DataFrame | None = None
        if request.history_path is not None:
            notify(39, "Loading historical portfolio values...")
            history_df = cls.load_dataframe(request.history_path)

        request.output_path.parent.mkdir(parents=True, exist_ok=True)
        notify(45, "Preparing report workbook...")

        if request.report_id == "portfolio":
            output = ReportController.generate_portfolio(
                request.output_path,
                portfolio_df=dataframe,
                portfolio_name=request.portfolio_name,
            )
        elif request.report_id == "analytics":
            output = ReportController.generate_analytics(
                request.output_path,
                portfolio_df=dataframe,
                portfolio_name=request.portfolio_name,
                history_df=history_df,
            )
        else:
            output = ReportController.generate_client_holdings(
                request.output_path,
                account_id=request.account_id,
                holdings_df=dataframe,
            )

        notify(90, "Saving Excel workbook...")
        output_path = Path(output)
        if not output_path.exists():
            raise ReportExportError("The report generator did not create the output file.")
        notify(100, "Report generated successfully.")
        return output_path

    @staticmethod
    def default_filename(report: ReportDefinition, subject_name: str) -> str:
        safe_subject = "".join(
            character if character.isalnum() or character in "-_" else "_"
            for character in subject_name.strip()
        ).strip("_") or "Report"
        suffixes = {
            "portfolio": "Portfolio_Report",
            "analytics": "Analytics_Report",
            "client_holdings": "Client_Holdings_Report",
        }
        return f"{safe_subject}_{suffixes.get(report.report_id, 'Report')}.xlsx"
