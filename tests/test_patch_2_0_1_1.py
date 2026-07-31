from pathlib import Path
import sys

# -------------------------------------------------
# Add project root to Python path
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.services.master_import_service import MasterImportService

path = Path(r"D:\Test\MTF Test.xlsx")
result = MasterImportService.import_file(path)
df = result.dataframe

assert "Exposure" in df.columns
assert df["Exposure"].notna().all()

print("RMS v2.0.1 Patch 1 test passed successfully.")
print(f"Records imported : {len(df):,}")
print(f"Clients          : {result.summary.get('clients', 0):,}")
print(f"Symbols          : {result.summary.get('symbols', 0):,}")
print(f"Total exposure   : {result.summary.get('total_exposure', 0):,.2f}")
