import { Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";

import api from "../services/api";

export default function EnterpriseRMSPage() {
  const dashboard = useQuery({
    queryKey: ["enterprise-rms-dashboard"],
    queryFn: async () =>
      (await api.get("/dashboard/enterprise")).data,
    retry: false,
    refetchOnWindowFocus: false,
  });

  const data = dashboard.data;

  const healthSeverity = (health) => {
    if (health === "Critical") {
      return "error";
    }

    if (health === "High Risk") {
      return "error";
    }

    if (health === "Warning") {
      return "warning";
    }

    if (health === "Moderate") {
      return "warning";
    }

    if (health === "No Data") {
      return "info";
    }

    return "success";
  };

  const formatNumber = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    });

  const formatPercent = (value) =>
    `${Number(value ?? 0).toFixed(2)}%`;

  const formatCrores = (value) => {
    const amount = Number(value ?? 0);
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  };

  const MetricCard = ({ title, value, subtitle }) => (
    <Card
      sx={{
        height: "100%",
        minWidth: 0,
      }}
    >
      <CardContent
        sx={{
          p: { xs: 1.75, sm: 2 },
          "&:last-child": {
            pb: { xs: 1.75, sm: 2 },
          },
          minWidth: 0,
        }}
      >
        <Typography
          variant="body2"
          color="text.secondary"
          gutterBottom
          sx={{
            minHeight: { xs: "auto", sm: 22 },
            lineHeight: 1.25,
            overflowWrap: "anywhere",
          }}
        >
          {title}
        </Typography>

        <Typography
          variant="h5"
          fontWeight={800}
          sx={{
            fontSize: {
              xs: "1.25rem",
              sm: "1.35rem",
              md: "1.5rem",
              lg: "1.55rem",
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
          {value}
        </Typography>

        {subtitle && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: "block",
              mt: 0.5,
              lineHeight: 1.25,
              overflowWrap: "anywhere",
            }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  if (dashboard.isLoading) {
    return (
      <Stack
        alignItems="center"
        justifyContent="center"
        py={10}
      >
        <CircularProgress />
      </Stack>
    );
  }

  if (dashboard.isError) {
    return (
      <Stack spacing={3}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Enterprise RMS
          </Typography>

          <Typography color="text.secondary">
            Enterprise risk management dashboard.
          </Typography>
        </Box>

        <Alert severity="error">
          {dashboard.error?.response?.data?.error?.message ||
            dashboard.error?.response?.data?.detail ||
            "Unable to load Enterprise RMS dashboard."}
        </Alert>

        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={() => dashboard.refetch()}
        >
          Retry
        </Button>
      </Stack>
    );
  }

  if (!data) {
    return null;
  }

  const summary = data.summary ?? {};
  const snapshot = data.snapshot ?? {};
  const topClients = data.top_clients ?? [];
  const topSymbols = data.top_symbols ?? [];
  const alerts = data.alerts ?? [];

  return (
    <Stack spacing={3}>
      {/* Header */}
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ sm: "center" }}
        spacing={2}
      >
        <Box>
          <Typography
            variant="h4"
            fontWeight={800}
          >
            Enterprise RMS
          </Typography>

          <Typography color="text.secondary">
            Enterprise-level exposure, concentration and
            portfolio risk monitoring.
          </Typography>
        </Box>

        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={() => dashboard.refetch()}
          disabled={dashboard.isFetching}
        >
          Refresh
        </Button>
      </Stack>

      {/* Overall Risk */}
      <Alert severity={healthSeverity(summary.health)}>
        <strong>Overall Risk Health:</strong>{" "}
        {summary.health}{" "}
        <span>
          · Risk Score:{" "}
          {Number(summary.risk_score ?? 0).toFixed(1)}
        </span>
      </Alert>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ alignItems: "stretch" }}>
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Risk Score"
            value={Number(
              summary.risk_score ?? 0,
            ).toFixed(1)}
            subtitle="Enterprise risk score"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Total Exposure"
            value={formatCrores(summary.total_exposure)}
            subtitle="Current exposure"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Total MTM"
            value={formatCrores(summary.total_mtm)}
            subtitle="Mark-to-market"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Margin Utilization"
            value={formatPercent(
              summary.margin_utilization,
            )}
            subtitle="Margin utilization"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Diversification Score"
            value={Number(
              summary.diversification ?? 0,
            ).toFixed(1)}
            subtitle="Portfolio diversification score"
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}>
          <MetricCard
            title="Clients"
            value={snapshot.clients ?? 0}
            subtitle={`${snapshot.records ?? 0} records`}
          />
        </Grid>
      </Grid>

      {/* Snapshot */}
      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Typography
              variant="h6"
              fontWeight={700}
            >
              Risk Snapshot
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Snapshot ID:{" "}
              {snapshot.snapshot_id || "N/A"}
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Business Date:{" "}
              {snapshot.business_date || "N/A"}
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Records: {snapshot.records ?? 0} · Clients:{" "}
              {snapshot.clients ?? 0} · Symbols:{" "}
              {snapshot.symbols ?? 0}
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Stack spacing={1}>
          <Typography
            variant="h6"
            fontWeight={700}
          >
            Risk Alerts
          </Typography>

          {alerts.map((alert, index) => (
            <Alert
              key={`${alert.title}-${index}`}
              severity={healthSeverity(alert.level)}
            >
              <Typography fontWeight={700}>
                {alert.title}
              </Typography>

              <Typography variant="body2">
                {alert.message}
              </Typography>

              {alert.recommendation && (
                <Typography
                  variant="body2"
                  sx={{ mt: 0.5 }}
                >
                  Recommendation:{" "}
                  {alert.recommendation}
                </Typography>
              )}
            </Alert>
          ))}
        </Stack>
      )}

      {/* Top Clients */}
      <Card>
        <CardContent>
          <Typography
            variant="h6"
            fontWeight={700}
            gutterBottom
          >
            Top Risk Clients
          </Typography>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Client</TableCell>
                <TableCell align="right">
                  Exposure
                </TableCell>
                <TableCell align="right">
                  MTM
                </TableCell>
                <TableCell align="right">
                  Concentration
                </TableCell>
                <TableCell align="right">
                  Score
                </TableCell>
                <TableCell>Level</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {topClients.map((client) => (
                <TableRow key={client.name}>
                  <TableCell>
                    <Typography fontWeight={600}>
                      {client.name}
                    </Typography>
                  </TableCell>

                  <TableCell align="right">
                    ₹{formatNumber(client.exposure)}
                  </TableCell>

                  <TableCell align="right">
                    ₹{formatNumber(client.mtm)}
                  </TableCell>

                  <TableCell align="right">
                    {formatPercent(
                      client.concentration_percent,
                    )}
                  </TableCell>

                  <TableCell align="right">
                    {Number(
                      client.score ?? 0,
                    ).toFixed(1)}
                  </TableCell>

                  <TableCell>
                    <Chip
                      size="small"
                      label={client.level}
                      color={healthSeverity(
                        client.level,
                      )}
                    />
                  </TableCell>
                </TableRow>
              ))}

              {topClients.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    align="center"
                  >
                    No client risk data available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Top Symbols */}
      <Card>
        <CardContent>
          <Typography
            variant="h6"
            fontWeight={700}
            gutterBottom
          >
            Top Risk Symbols
          </Typography>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">
                  Exposure
                </TableCell>
                <TableCell align="right">
                  MTM
                </TableCell>
                <TableCell align="right">
                  Concentration
                </TableCell>
                <TableCell align="right">
                  Score
                </TableCell>
                <TableCell>Level</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {topSymbols.map((symbol) => (
                <TableRow key={symbol.name}>
                  <TableCell>
                    <Typography fontWeight={600}>
                      {symbol.name}
                    </Typography>
                  </TableCell>

                  <TableCell align="right">
                    ₹{formatNumber(symbol.exposure)}
                  </TableCell>

                  <TableCell align="right">
                    ₹{formatNumber(symbol.mtm)}
                  </TableCell>

                  <TableCell align="right">
                    {formatPercent(
                      symbol.concentration_percent,
                    )}
                  </TableCell>

                  <TableCell align="right">
                    {Number(
                      symbol.score ?? 0,
                    ).toFixed(1)}
                  </TableCell>

                  <TableCell>
                    <Chip
                      size="small"
                      label={symbol.level}
                      color={healthSeverity(
                        symbol.level,
                      )}
                    />
                  </TableCell>
                </TableRow>
              ))}

              {topSymbols.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    align="center"
                  >
                    No symbol risk data available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Stack>
  );
}