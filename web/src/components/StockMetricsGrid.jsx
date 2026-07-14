import { Card, CardContent, Grid, Typography } from "@mui/material";

const money = (value, currency = "INR") =>
  value == null
    ? "N/A"
    : new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency,
        maximumFractionDigits: 2,
      }).format(value);

const compact = (value) =>
  value == null
    ? "N/A"
    : new Intl.NumberFormat("en-IN", {
        notation: "compact",
        maximumFractionDigits: 2,
      }).format(value);

const numeric = (value, suffix = "") =>
  value == null ? "N/A" : `${Number(value).toFixed(2)}${suffix}`;

export default function StockMetricsGrid({ details }) {
  const metrics = [
    ["Current Price", money(details.current_price, details.currency)],
    ["Market Cap", compact(details.market_cap)],
    ["P/E Ratio", numeric(details.pe_ratio)],
    ["Price / Book", numeric(details.price_to_book)],
    ["Dividend Yield", numeric(details.dividend_yield, "%")],
    ["Beta", numeric(details.beta)],
    ["ROE", numeric(details.roe, "%")],
    ["Debt / Equity", numeric(details.debt_to_equity)],
    ["Profit Margin", numeric(details.profit_margin, "%")],
    ["52 Week High", money(details.fifty_two_week_high, details.currency)],
    ["52 Week Low", money(details.fifty_two_week_low, details.currency)],
    ["Sector", details.sector || "Unknown"],
  ];

  return (
    <Grid container spacing={2}>
      {metrics.map(([label, value]) => (
        <Grid size={{ xs: 12, sm: 6, lg: 3 }} key={label}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography color="text.secondary">{label}</Typography>
              <Typography variant="h6" fontWeight={700} mt={1}>
                {value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
