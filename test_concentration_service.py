import pandas as pd

from core.concentration_service import ConcentrationService


def main() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "AccountId": "CLIENT001",
                "Symbol": "RELIANCE",
                "BUY VALUE": 500000,
                "NetValue": 550000,
                "MarkToMarket": 50000,
                "MTF VAR": 90000,
                "MTF MARGIN": 120000,
            },
            {
                "AccountId": "CLIENT002",
                "Symbol": "TCS",
                "BUY VALUE": 300000,
                "NetValue": 320000,
                "MarkToMarket": 20000,
                "MTF VAR": 50000,
                "MTF MARGIN": 70000,
            },
            {
                "AccountId": "CLIENT002",
                "Symbol": "INFY",
                "BUY VALUE": 100000,
                "NetValue": 80000,
                "MarkToMarket": -20000,
                "MTF VAR": 15000,
                "MTF MARGIN": 20000,
            },
            {
                "AccountId": "CLIENT003",
                "Symbol": "HDFCBANK",
                "BUY VALUE": 200000,
                "NetValue": 210000,
                "MarkToMarket": 10000,
                "MTF VAR": 30000,
                "MTF MARGIN": 40000,
            },
            {
                "AccountId": "CLIENT003",
                "Symbol": "ICICIBANK",
                "BUY VALUE": 180000,
                "NetValue": 175000,
                "MarkToMarket": -5000,
                "MTF VAR": 28000,
                "MTF MARGIN": 38000,
            },
            {
                "AccountId": "CLIENT003",
                "Symbol": "SBIN",
                "BUY VALUE": 100000,
                "NetValue": 95000,
                "MarkToMarket": -5000,
                "MTF VAR": 18000,
                "MTF MARGIN": 25000,
            },
        ]
    )

    service = ConcentrationService()
    service.load_dataframe(dataframe)

    print("\nCONCENTRATION SUMMARY")
    print(service.calculate_concentration().to_string(index=False))

    print("\nSINGLE STOCK CLIENTS")
    print(service.get_single_stock_clients().to_string(index=False))

    print("\nTWO STOCK CLIENTS")
    print(service.get_two_stock_clients().to_string(index=False))

    print("\nDASHBOARD SUMMARY")
    print(service.get_summary())

    print("\nDISTRIBUTION")
    print(service.get_distribution().to_string(index=False))

    print("\nCLIENT002 HOLDINGS")
    print(
        service.get_client_holdings(
            "CLIENT002"
        ).to_string(index=False)
    )


if __name__ == "__main__":
    main()