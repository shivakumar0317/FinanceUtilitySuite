import {
  AccountBalance,
  Assessment,
  Groups,
  Paid,
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
  }).format(value || 0);

const CARD_COLORS = {
  clients: {
    accent: "#3b82f6",
    iconBg: "rgba(59, 130, 246, 0.18)",
  },

  buyValue: {
    accent: "#06b6d4",
    iconBg: "rgba(6, 182, 212, 0.18)",
  },

  netValue: {
    positive: {
      accent: "#22c55e",
      iconBg: "rgba(34, 197, 94, 0.18)",
    },
    negative: {
      accent: "#ef4444",
      iconBg: "rgba(239, 68, 68, 0.18)",
    },
  },

  mtm: {
    accent: "#3b82f6",
    iconBg: "rgba(59, 130, 246, 0.18)",
  },

  margin: {
    accent: "#22c55e",
    iconBg: "rgba(34, 197, 94, 0.18)",
  },

  risk: {
    low: {
      accent: "#22c55e",
      iconBg: "rgba(34, 197, 94, 0.18)",
    },
    moderate: {
      accent: "#f59e0b",
      iconBg: "rgba(245, 158, 11, 0.18)",
    },
    high: {
      accent: "#ef4444",
      iconBg: "rgba(239, 68, 68, 0.18)",
    },
    default: {
      accent: "#94a3b8",
      iconBg: "rgba(148, 163, 184, 0.18)",
    },
  },
};

function getRiskColors(riskLevel) {
  const level = String(
    riskLevel || "",
  ).toLowerCase();

  if (level === "low") {
    return CARD_COLORS.risk.low;
  }

  if (level === "moderate") {
    return CARD_COLORS.risk.moderate;
  }

  if (level === "high") {
    return CARD_COLORS.risk.high;
  }

  return CARD_COLORS.risk.default;
}

function getNetValueColors(value) {
  return Number(value || 0) < 0
    ? CARD_COLORS.netValue.negative
    : CARD_COLORS.netValue.positive;
}

function SummaryCard({
  title,
  value,
  subtitle,
  icon,
  accent,
  iconBg,
  valueColor,
}) {
  return (
    <Card
      sx={{
        height: "100%",
        borderTop: `3px solid ${accent}`,
        background:
          "linear-gradient(145deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96))",
        boxShadow:
          "0 8px 24px rgba(0, 0, 0, 0.18)",
        transition:
          "transform 0.2s ease, box-shadow 0.2s ease",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow:
            "0 12px 30px rgba(0, 0, 0, 0.28)",
        },
      }}
    >
      <CardContent
        sx={{
          p: 2.5,
          "&:last-child": {
            pb: 2.5,
          },
        }}
      >
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="flex-start"
          spacing={2}
        >
          <Box sx={{ minWidth: 0 }}>
            <Typography
              sx={{
                color: accent,
                fontWeight: 600,
                fontSize: "0.95rem",
                letterSpacing: "0.01em",
              }}
            >
              {title}
            </Typography>

            <Typography
              variant="h5"
              fontWeight={800}
              mt={1}
              sx={{
                color:
                  valueColor || "#ffffff",
                lineHeight: 1.2,
                wordBreak: "break-word",
              }}
            >
              {value}
            </Typography>

            {subtitle && (
              <Typography
                sx={{
                  mt: 0.75,
                  color: "rgba(226, 232, 240, 0.78)",
                  fontSize: "0.92rem",
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>

          <Box
            sx={{
              flexShrink: 0,
              width: 42,
              height: 42,
              borderRadius: "35px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: iconBg,
              color: accent,
              "& svg": {
                fontSize: 25,
              },
            }}
          >
            {icon}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default function MTFSummaryCards({
  summary,
}) {
  const netValueColors = getNetValueColors(
    summary.total_net_value,
  );

  const riskColors = getRiskColors(
    summary.risk_level,
  );

  const cards = [
    {
      title: "Total Clients",
      value: summary.total_clients,
      subtitle: `${summary.total_symbols} symbols`,
      icon: <Groups />,
      ...CARD_COLORS.clients,
    },

    {
      title: "Total Buy Value",
      value: money(summary.total_buy_value),
      icon: <AccountBalance />,
      ...CARD_COLORS.buyValue,
    },

    {
      title: "Total Net Value",
      value: money(summary.total_net_value),
      icon: <Assessment />,
      ...netValueColors,
      valueColor: netValueColors.accent,
    },

    {
      title: "Total MTM",
      value: money(summary.total_mtm),
      subtitle: (
        <>
          <Box
            component="span"
            sx={{
              color: "#22c55e",
              fontWeight: 600,
            }}
          >
            {summary.positive_mtm_clients} gainers
          </Box>

          {" / "}

          <Box
            component="span"
            sx={{
              color: "#ef4444",
              fontWeight: 600,
            }}
          >
            {summary.negative_mtm_clients} losers
          </Box>
        </>
      ),
      icon: <ShowChart />,
      ...CARD_COLORS.mtm,
    },

    {
      title: "Total Margin",
      value: money(summary.total_margin),
      subtitle: `${Number(
        summary.average_margin_percent || 0,
      ).toFixed(2)}% average`,
      icon: <Paid />,
      ...CARD_COLORS.margin,
    },

    {
      title: "Risk Level",
      value: summary.risk_level,
      icon: <WarningAmber />,
      ...riskColors,
      valueColor: riskColors.accent,
    },
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card) => (
        <Grid
          size={{ xs: 12, sm: 6, lg: 4 }}
          key={card.title}
        >
          <SummaryCard {...card} />
        </Grid>
      ))}
    </Grid>
  );
}