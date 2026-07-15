import {
  AccountBalance,
  Assessment,
  Groups,
  Paid,
  ShowChart,
  WarningAmber,
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

export default function MTFSummaryCards({ summary }) {
  const cards = [
    {
      title: "Total Clients",
      value: summary.total_clients,
      subtitle: `${summary.total_symbols} symbols`,
      icon: <Groups />,
    },
    {
      title: "Total Buy Value",
      value: money(summary.total_buy_value),
      icon: <AccountBalance />,
    },
    {
      title: "Total Net Value",
      value: money(summary.total_net_value),
      icon: <Assessment />,
    },
    {
      title: "Total MTM",
      value: money(summary.total_mtm),
      subtitle: `${summary.positive_mtm_clients} gainers / ${summary.negative_mtm_clients} losers`,
      icon: <ShowChart />,
    },
    {
      title: "Total Margin",
      value: money(summary.total_margin),
      subtitle: `${Number(
        summary.average_margin_percent || 0,
      ).toFixed(2)}% average`,
      icon: <Paid />,
    },
    {
      title: "Risk Level",
      value: summary.risk_level,
      icon: <WarningAmber />,
    },
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card) => (
        <Grid
          size={{ xs: 12, sm: 6, lg: 4 }}
          key={card.title}
        >
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Stack
                direction="row"
                justifyContent="space-between"
                spacing={2}
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
