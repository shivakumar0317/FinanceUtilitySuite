import {
  AccountBalanceWallet,
  Inventory2,
  ShowChart,
  Today,
} from "@mui/icons-material";
import {
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
} from "@mui/material";

const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value || 0);

export default function PortfolioLiveSummaryCards({
  summary,
}) {
  const cards = [
    {
      title: "Invested Value",
      value: money(summary.invested_value),
      icon: <AccountBalanceWallet />,
    },
    {
      title: "Current Value",
      value: money(summary.current_value),
      icon: <Inventory2 />,
    },
    {
      title: "Total P/L",
      value: money(summary.profit_loss),
      subtitle: `${summary.profit_loss_percent}%`,
      icon: <ShowChart />,
    },
    {
      title: "Today's P/L",
      value: money(summary.today_profit_loss),
      subtitle: `${summary.total_holdings} holdings`,
      icon: <Today />,
    },
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card) => (
        <Grid
          size={{ xs: 12, sm: 6, lg: 3 }}
          key={card.title}
        >
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Stack
                direction="row"
                justifyContent="space-between"
              >
                <div>
                  <Typography color="text.secondary">
                    {card.title}
                  </Typography>
                  <Typography
                    variant="h5"
                    fontWeight={800}
                    mt={1}
                  >
                    {card.value}
                  </Typography>
                  {card.subtitle && (
                    <Typography color="text.secondary">
                      {card.subtitle}
                    </Typography>
                  )}
                </div>
                {card.icon}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
