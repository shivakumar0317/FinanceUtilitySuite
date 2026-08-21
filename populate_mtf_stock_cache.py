from backend.database import SessionLocal
from backend.services.persistent_upload_service import PersistentUploadService
from core.services.stock_master_service import StockMasterService


def main():
    db = SessionLocal()

    try:
        dataframe = PersistentUploadService.restore_dataframe(
            db,
            user_id=2,
            dataset_type=PersistentUploadService.MTF,
        )

        if dataframe is None or dataframe.empty:
            print("ERROR: No saved MTF dataset found.")
            return

        if "SYMBOL" not in dataframe.columns:
            print("ERROR: Saved MTF dataset has no SYMBOL column.")
            return

        symbols = (
            dataframe["SYMBOL"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
            .tolist()
        )

        symbols = sorted(symbols)

        print(f"MTF symbols found: {len(symbols)}")

        service = StockMasterService(
            cache_ttl_days=7,
            max_workers=4,
        )

        def progress(completed, total, symbol):
            print(f"[{completed}/{total}] {symbol}")

        result = service.get_many(
            symbols,
            force_refresh=False,
            progress_callback=progress,
        )

        print()
        print("Stock Master cache population completed.")
        print(f"Cache hits      : {result.cache_hits}")
        print(f"Live fetches    : {result.live_fetches}")
        print(f"Stale fallbacks : {result.stale_fallbacks}")
        print(f"Failures        : {len(result.failures)}")

        if result.failures:
            print()
            print("Failures:")
            for symbol, error in result.failures.items():
                print(f"  {symbol}: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
