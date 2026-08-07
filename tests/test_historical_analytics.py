from core.services.historical_analytics_service import HistoricalAnalyticsService


def main():

    service = HistoricalAnalyticsService()

    history = service.load_history()

    print()
    print("RMS Historical Analytics Test")
    print("=" * 40)

    print(f"Snapshots Loaded : {len(history)}")

    if history:
        print("History          : PASS")
    else:
        print("History          : EMPTY")

    print()

    # ---- Exposure ----
    trend = service.exposure_trend()

    print(f"Exposure Points : {len(trend['values'])}")

    if len(trend["values"]) == len(history):
        print("Exposure Trend : PASS")
    else:
        print("Exposure Trend : FAIL")

    # ---- MTM ----
    mtm = service.mtm_trend()

    print(f"MTM Points      : {len(mtm['values'])}")

    if len(mtm["values"]) == len(history):
        print("MTM Trend       : PASS")
    else:
        print("MTM Trend       : FAIL")

    # ---- RISK ----
    risk = service.risk_score_trend()

    print(f"Risk Points     : {len(risk['values'])}")

    if len(risk["values"]) == 0:
        print("Risk Trend      : SKIPPED (No historical risk data)")

    elif len(risk["values"]) == len(history):
        print("Risk Trend      : PASS")

    else:
        print(f"Risk Trend      : PARTIAL ({len(risk['values'])}/{len(history)})")

    # ---- CLIENT TREND ----
    clients = service.client_trend()

    print(f"Client Points   : {len(clients['values'])}")

    if len(clients["values"]) == len(history):
        print("Client Trend    : PASS")
    else:
        print("Client Trend    : FAIL")

    # ---- SYMBOL TREND ----
    symbols = service.symbol_trend()

    print(f"Symbol Points   : {len(symbols['values'])}")

    if len(symbols["values"]) == len(history):
        print("Symbol Trend    : PASS")
    else:
        print("Symbol Trend    : FAIL")

    # ---- SUMMARY ----
    summary = service.summary()

    print()
    print("Historical Summary")
    print("-----------------------------")
    print(f"Snapshots : {summary['snapshots']}")
    print(f"Clients   : {summary['clients']}")
    print(f"Symbols   : {summary['symbols']}")
    print(f"Exposure  : ₹{summary['exposure']:,.2f}")
    print(f"MTM       : ₹{summary['mtm']:,.2f}")

    # ---- compare_snapshots ----
    comparison = service.compare_snapshots(0, len(history) - 1)

    print()
    print("Snapshot Comparison")
    print("-----------------------------")

    print("From :", comparison["snapshot_1"])
    print("To   :", comparison["snapshot_2"])

    print(f"Clients Δ  : {comparison['clients_diff']}")
    print(f"Symbols Δ  : {comparison['symbols_diff']}")
    print(f"Exposure Δ : ₹{comparison['exposure_diff']:,.2f}")
    print(f"MTM Δ      : ₹{comparison['mtm_diff']:,.2f}")

if __name__ == "__main__":
    main()