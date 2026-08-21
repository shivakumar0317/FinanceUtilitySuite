import {
  AccountBalance,
  Groups,
  PieChart,
  ShowChart,
  WarningAmber,
} from "@mui/icons-material";
import {
  Box,
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
  }).format(Number(value || 0));

const formatExposure = (value) => {
  const amount = Number(value || 0);

  if (Math.abs(amount) >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  }

  if (Math.abs(amount) >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} L`;
  }

  return money(amount);
};

export default function MTFConcentrationSummaryCards({
  summary,
}) {
  const cards = [
    {
      title: "Total Clients",
      value: summary.total_clients,
      icon: <Groups />,
      accent: "#42a5f5",
    },
    {
      title: "Single Stock",
      value: summary.single_stock_clients,
      subtitle: "100% concentration clients",
      icon: <ShowChart />,
      accent: "#ffb300",
    },
    {
      title: "Multiple Stocks",
      value: summary.multiple_stock_clients,
      subtitle: `${summary.three_to_five_stock_clients} with 3–5 stocks`,
      icon: <PieChart />,
      accent: "#a78bfa",
    },
    {
      title: "Critical Risk",
      value: summary.critical_clients,
      subtitle: `${summary.high_risk_clients} high-risk clients`,
      icon: <WarningAmber />,
      accent: "#ef4444",
    },
    {
      title: "Total Exposure",
      value: formatExposure(summary.total_exposure),
      subtitle: `MTM ${money(summary.total_mtm)}`,
      icon: <AccountBalance />,
      accent: "#22c55e",
    },
  ];

  return (
    <Grid
      container
      spacing={2}
      sx={{
        display: "grid",
        gridTemplateColumns: {
          xs: "1fr",
          sm: "repeat(2, minmax(0, 1fr))",
          md: "repeat(3, minmax(0, 1fr))",
          lg: "repeat(5, minmax(0, 1fr))",
        },
      }}
    >
      {cards.map((card) => (
        <Grid
          key={card.title}
          sx={{
            minWidth: 0,
          }}
        >
          <Card
            sx={{
              height: "100%",
              position: "relative",
              overflow: "hidden",

              // Rounded card
              borderRadius: "35px",

              // Colored top accent
              borderTop: `3px solid ${card.accent}`,

              // Keep the normal MUI border subtle
              borderLeft: "1px solid rgba(255,255,255,0.06)",
              borderRight: "1px solid rgba(255,255,255,0.06)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",

              // Smooth hover animation
              transition:
                "transform 180ms ease, box-shadow 180ms ease",

              // Normal state
              boxShadow:
                "0 2px 8px rgba(0, 0, 0, 0.18)",

              // Hover state
              "&:hover": {
                transform: "translateY(-4px)",
                boxShadow:
                  "0 8px 20px rgba(0, 0, 0, 0.30)",
              },
            }}
          >
            <CardContent
              sx={{
                height: "100%",
                p: { xs: 1.75, sm: 2 },
                "&:last-child": {
                  pb: { xs: 1.75, sm: 2 },
                },
              }}
            >
              <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={{ xs: 1.25, sm: 1.5 }}
                sx={{
                  height: "100%",
                  minWidth: 0,
                }}
              >
                <BoxContent card={card} />

                <Box
                  sx={{
                    width: { xs: 42, sm: 46, md: 48 },
                    height: { xs: 42, sm: 46, md: 48 },
                    minWidth: { xs: 42, sm: 46, md: 48 },
                    borderRadius: "50%",

                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",

                    backgroundColor: `${card.accent}20`,
                    color: card.accent,

                    flexShrink: 0,
                  }}
                >
                  {card.icon}
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

function BoxContent({ card }) {
  return (
    <Box
      sx={{
        minWidth: 0,
        flex: 1,
        width: 0,
      }}
    >
      <Typography
        color="text.secondary"
        sx={{
          fontSize: {
            xs: "0.82rem",
            sm: "0.88rem",
            md: "0.95rem",
          },
          fontWeight: 500,
          lineHeight: 1.25,
          overflowWrap: "anywhere",
        }}
      >
        {card.title}
      </Typography>

      <Typography
        variant="h5"
        fontWeight={800}
        mt={1}
        sx={{
          fontSize: {
            xs: "1.2rem",
            sm: "1.3rem",
            md: "1.4rem",
            lg: "1.45rem",
            xl: "1.5rem",
          },
          lineHeight: 1.15,
          whiteSpace: "normal",
          overflow: "visible",
          textOverflow: "clip",
          overflowWrap: "anywhere",
          wordBreak: "break-word",
          letterSpacing: "-0.02em",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {card.value}
      </Typography>

      {card.subtitle && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            display: "block",
            mt: 0.5,
            lineHeight: 1.3,
            overflowWrap: "anywhere",
            wordBreak: "break-word",
          }}
        >
          {card.subtitle}
        </Typography>
      )}
    </Box>
  );
}