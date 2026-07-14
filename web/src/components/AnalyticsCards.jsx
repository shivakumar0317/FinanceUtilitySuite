import { AccountBalanceWallet, Inventory2, ShowChart, TrendingUp } from "@mui/icons-material";
import { Card, CardContent, Grid, Stack, Typography } from "@mui/material";

const money = (value) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value || 0);

export default function AnalyticsCards({ summary }) {
  const cards = [
    ["Total Investment", money(summary?.total_investment), <AccountBalanceWallet />],
    ["Current Value", money(summary?.current_value), <Inventory2 />],
    ["Profit / Loss", money(summary?.profit_loss), <TrendingUp />],
    ["Holdings", summary?.total_holdings ?? 0, <ShowChart />],
  ];
  return (
    <Grid container spacing={2}>
      {cards.map(([title, value, icon]) => (
        <Grid size={{ xs: 12, sm: 6, lg: 3 }} key={title}>
          <Card><CardContent><Stack direction="row" justifyContent="space-between"><div><Typography color="text.secondary">{title}</Typography><Typography variant="h5" fontWeight={800} mt={1}>{value}</Typography></div>{icon}</Stack></CardContent></Card>
        </Grid>
      ))}
    </Grid>
  );
}
