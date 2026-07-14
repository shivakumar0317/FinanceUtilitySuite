import {
  Assessment,
  DonutLarge,
  Security,
  ShowChart,
  TrendingDown,
  TrendingUp,
  WarningAmber,
} from "@mui/icons-material";
import {
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
} from "@mui/material";

const numeric = (value, suffix = "") =>
  value === null || value === undefined
    ? "N/A"
    : `${Number(value).toFixed(2)}${suffix}`;

export default function RiskSummaryCards({ summary }) {
  const cards = [
    {
      title: "Portfolio Beta",
      value: numeric(summary.portfolio_beta),
      icon: <ShowChart />,
    },
    {
      title: "Volatility",
      value: numeric(summary.volatility, "%"),
      icon: <Assessment />,
    },
    {
      title: "Alpha",
      value: numeric(summary.alpha, "%"),
      icon: <TrendingUp />,
    },
    {
      title: "Sharpe Ratio",
      value: numeric(summary.sharpe_ratio),
      icon: <Security />,
    },
    {
      title: "Max Drawdown",
      value: numeric(summary.max_drawdown, "%"),
      icon: <TrendingDown />,
    },
    {
      title: "Concentration Risk",
      value: numeric(summary.concentration_risk, "%"),
      icon: <WarningAmber />,
    },
    {
      title: "Diversification Score",
      value: numeric(summary.diversification_score, "%"),
      icon: <DonutLarge />,
    },
    {
      title: "Risk Level",
      value: summary.risk_level || "Unknown",
      icon: <Security />,
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
