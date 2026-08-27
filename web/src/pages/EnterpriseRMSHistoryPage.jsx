import { useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import RemoveIcon from "@mui/icons-material/Remove";
import HistoricalRiskTrendCharts from "../components/HistoricalRiskTrendCharts";
import AssessmentIcon from "@mui/icons-material/Assessment";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import GroupsIcon from "@mui/icons-material/Groups";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

import api from "../services/api";

function healthColor(health) {
  switch (health) {
    case "Critical":
      return "error";
    case "Warning":
      return "warning";
    case "Healthy":
      return "success";
    default:
      return "default";
  }
}

function formatNumber(value, decimals = 2) {
  return Number(value ?? 0).toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatCurrency(value) {
  return `INR ${formatNumber(value)}`;
}

function formatChange(value, decimals = 2) {
  const number = Number(value ?? 0);

  if (number > 0) {
    return `+${formatNumber(number, decimals)}`;
  }

  return formatNumber(number, decimals);
}

function changeColor(value, inverse = false) {
  const number = Number(value ?? 0);

  if (number === 0) {
    return "text.secondary";
  }

  const positive = number > 0;

  if (inverse) {
    return positive ? "error.main" : "success.main";
  }

  return positive ? "success.main" : "error.main";
}

function RiskTrend({ trend }) {
  if (trend === "Improved") {
    return (
      <Chip
        icon={<TrendingDownIcon />}
        label="Improved"
        color="success"
        sx={{ fontWeight: 700 }}
      />
    );
  }

  if (trend === "Deteriorated") {
    return (
      <Chip
        icon={<TrendingUpIcon />}
        label="Deteriorated"
        color="error"
        sx={{ fontWeight: 700 }}
      />
    );
  }

  return (
    <Chip
      icon={<RemoveIcon />}
      label="Stable"
      color="default"
      sx={{ fontWeight: 700 }}
    />
  );
}

function ComparisonMetric({
  label,
  first,
  second,
  change,
  suffix = "",
  currency = false,
  inverse = false,
}) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        borderRadius: 2,
        height: "100%",
      }}
    >
      <Typography
        variant="caption"
        color="text.secondary"
        fontWeight={700}
      >
        {label}
      </Typography>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          mt: 1,
          flexWrap: "wrap",
        }}
      >
        <Typography variant="body2" fontWeight={700}>
          {currency ? formatCurrency(first) : formatNumber(first)}
          {suffix}
        </Typography>

        <Typography color="text.secondary">
          →
        </Typography>

        <Typography variant="body2" fontWeight={800}>
          {currency ? formatCurrency(second) : formatNumber(second)}
          {suffix}
        </Typography>
      </Box>

      <Typography
        variant="body2"
        fontWeight={800}
        sx={{
          mt: 1,
          color: changeColor(change, inverse),
        }}
      >
        Change: {currency ? formatCurrency(change) : formatChange(change)}
        {!currency ? suffix : ""}
      </Typography>
    </Paper>
  );
}

function RiskInsightCard({
  title,
  value,
  subtitle,
  icon,
  valueColor = "text.primary",
}) {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2.5,
        borderRadius: 2,
        height: "100%",
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          mb: 1,
        }}
      >
        {icon}
        <Typography
          variant="caption"
          color="text.secondary"
          fontWeight={700}
        >
          {title}
        </Typography>
      </Box>

      <Typography
        variant="h6"
        fontWeight={800}
        sx={{ color: valueColor }}
      >
        {value}
      </Typography>

      {subtitle && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 0.5 }}
        >
          {subtitle}
        </Typography>
      )}
    </Paper>
  );
}

export default function EnterpriseRMSHistoryPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef(null);

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  const {
    data: snapshots = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["enterprise-rms-snapshots"],
    queryFn: async () => {
      const response = await api.get("/snapshots");
      return response.data;
    },
  });

  // ---------------------------------------------------------
  // MTF Upload
  // ---------------------------------------------------------

  async function handleMtfUpload(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploadError("");
    setUploadSuccess("");
    setUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post(
        "/api/mtf/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );

      const snapshot = response.data?.snapshot;

      await queryClient.invalidateQueries({
        queryKey: ["enterprise-rms-snapshots"],
      });

      setUploadSuccess(
        snapshot?.snapshot_id
          ? `MTF uploaded successfully. Snapshot ${snapshot.snapshot_id} created.`
          : "MTF uploaded successfully and historical analytics updated.",
      );
    } catch (uploadException) {
      setUploadError(
        uploadException?.response?.data?.detail ||
          uploadException?.response?.data?.error?.message ||
          uploadException?.message ||
          "Unable to upload the MTF file.",
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  const [selectedFirst, setSelectedFirst] = useState(null);
  const [selectedSecond, setSelectedSecond] = useState(null);

  const comparisonQuery = useQuery({
    queryKey: [
      "enterprise-rms-comparison",
      selectedFirst,
      selectedSecond,
    ],
    queryFn: async () => {
      const response = await api.get(
        `/snapshots/compare/${selectedFirst}/${selectedSecond}`,
      );

      return response.data;
    },
    enabled: Boolean(selectedFirst && selectedSecond),
  });

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          py: 8,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box>
        <Typography variant="h4" fontWeight={800} gutterBottom>
          Historical Risk Analytics
        </Typography>

        <Alert severity="error">
          {error?.response?.data?.detail ||
            error?.message ||
            "Unable to load snapshot history."}
        </Alert>
      </Box>
    );
  }

  const orderedSnapshots = [...snapshots].sort((a, b) => {
    return (
      new Date(b.business_date || b.timestamp) -
      new Date(a.business_date || a.timestamp)
    );
  });

  function handleSnapshotClick(snapshot) {
    if (!selectedFirst) {
      setSelectedFirst(snapshot.snapshot_id);
      return;
    }

    if (
      selectedFirst === snapshot.snapshot_id &&
      !selectedSecond
    ) {
      return;
    }

    setSelectedSecond(snapshot.snapshot_id);
  }

  function clearComparison() {
    setSelectedFirst(null);
    setSelectedSecond(null);
  }

  const comparison = comparisonQuery.data;

  const firstSnapshot = orderedSnapshots.find(
    (snapshot) => snapshot.snapshot_id === selectedFirst,
  );

  const secondSnapshot = orderedSnapshots.find(
    (snapshot) => snapshot.snapshot_id === selectedSecond,
  );

  // ---------------------------------------------------------
  // Historical Risk Insights
  // ---------------------------------------------------------

  const chronologicalSnapshots = [...orderedSnapshots].sort(
    (a, b) =>
      new Date(a.business_date || a.timestamp) -
      new Date(b.business_date || b.timestamp),
  );

  const oldestSnapshot = chronologicalSnapshots[0];
  const latestSnapshot =
    chronologicalSnapshots[chronologicalSnapshots.length - 1];

  const bestRiskSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((best, snapshot) =>
          Number(snapshot.risk_score ?? Infinity) <
          Number(best.risk_score ?? Infinity)
            ? snapshot
            : best,
        )
      : null;

  const worstRiskSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((worst, snapshot) =>
          Number(snapshot.risk_score ?? -Infinity) >
          Number(worst.risk_score ?? -Infinity)
            ? snapshot
            : worst,
        )
      : null;

  const highestExposureSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((highest, snapshot) =>
          Number(snapshot.total_exposure ?? 0) >
          Number(highest.total_exposure ?? 0)
            ? snapshot
            : highest,
        )
      : null;

  const lowestExposureSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((lowest, snapshot) =>
          Number(snapshot.total_exposure ?? Infinity) <
          Number(lowest.total_exposure ?? Infinity)
            ? snapshot
            : lowest,
        )
      : null;

  const bestMTMSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((best, snapshot) =>
          Number(snapshot.total_mtm ?? -Infinity) >
          Number(best.total_mtm ?? -Infinity)
            ? snapshot
            : best,
        )
      : null;

  const worstMTMSnapshot =
    chronologicalSnapshots.length > 0
      ? chronologicalSnapshots.reduce((worst, snapshot) =>
          Number(snapshot.total_mtm ?? Infinity) <
          Number(worst.total_mtm ?? Infinity)
            ? snapshot
            : worst,
        )
      : null;

  const historicalRiskChange =
    oldestSnapshot && latestSnapshot
      ? Number(latestSnapshot.risk_score ?? 0) -
        Number(oldestSnapshot.risk_score ?? 0)
      : 0;

  const historicalExposureChange =
    oldestSnapshot && latestSnapshot
      ? Number(latestSnapshot.total_exposure ?? 0) -
        Number(oldestSnapshot.total_exposure ?? 0)
      : 0;

  const historicalMTMChange =
    oldestSnapshot && latestSnapshot
      ? Number(latestSnapshot.total_mtm ?? 0) -
        Number(oldestSnapshot.total_mtm ?? 0)
      : 0;

  const historicalDiversificationChange =
    oldestSnapshot && latestSnapshot
      ? Number(latestSnapshot.diversification_score ?? 0) -
        Number(oldestSnapshot.diversification_score ?? 0)
      : 0;

  const historicalTrend =
    historicalRiskChange < 0
      ? "Improved"
      : historicalRiskChange > 0
        ? "Deteriorated"
        : "Stable";

  return (
    <Box>
      <Typography variant="h4" fontWeight={800} gutterBottom>
        Historical Risk Analytics
      </Typography>

      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ mb: 3 }}
      >
        Review historical Enterprise RMS snapshots and compare
        portfolio risk across business dates.
      </Typography>

            <Paper
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Box>
            <Typography variant="h6" fontWeight={800}>
              MTF Risk Data
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 0.5 }}
            >
              Upload the latest MTF file to update the MTF Dashboard,
              Concentration Risk and Historical Risk Analytics.
            </Typography>
          </Box>

          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            hidden
            onChange={handleMtfUpload}
          />

          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload MTF File"}
          </Button>
        </Box>

        {uploading && (
          <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
            <CircularProgress size={20} sx={{ mr: 1.5 }} />

            <Typography variant="body2" color="text.secondary">
              Uploading MTF data and creating RMS snapshot...
            </Typography>
          </Box>
        )}

        {uploadSuccess && (
          <Alert
            severity="success"
            icon={<CheckCircleIcon />}
            sx={{ mt: 2 }}
          >
            {uploadSuccess}
          </Alert>
        )}

        {uploadError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {uploadError}
          </Alert>
        )}
      </Paper>

      <Paper
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
        }}
      >
        <Typography variant="h6" fontWeight={700}>
          Snapshot History
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {orderedSnapshots.length} historical snapshots available.
          Select two snapshots to compare their risk position.
        </Typography>

        {(selectedFirst || selectedSecond) && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2,
              mt: 2,
              flexWrap: "wrap",
            }}
          >
            <Chip
              label={
                selectedFirst
                  ? `First: ${selectedFirst}`
                  : "First snapshot"
              }
              color={selectedFirst ? "primary" : "default"}
              variant={selectedFirst ? "filled" : "outlined"}
            />

            <CompareArrowsIcon />

            <Chip
              label={
                selectedSecond
                  ? `Second: ${selectedSecond}`
                  : "Second snapshot"
              }
              color={selectedSecond ? "primary" : "default"}
              variant={selectedSecond ? "filled" : "outlined"}
            />

            <Button
              variant="outlined"
              size="small"
              onClick={clearComparison}
            >
              Clear
            </Button>
          </Box>
        )}
      </Paper>

      <Paper
        sx={{
          borderRadius: 3,
          overflow: "hidden",
          mb: 3,
        }}
      >
        <TableContainer>
          <Table
            stickyHeader
            size="small"
            sx={{
              minWidth: 1200,
            }}
          >
            <TableHead>
              <TableRow>
                <TableCell>
                  <strong>Business Date</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Risk Score</strong>
                </TableCell>

                <TableCell>
                  <strong>Health</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Total Exposure</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Total MTM</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Margin Util.</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Diversification</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Clients</strong>
                </TableCell>

                <TableCell align="right">
                  <strong>Symbols</strong>
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {orderedSnapshots.map((snapshot) => {
                const isFirst =
                  selectedFirst === snapshot.snapshot_id;

                const isSecond =
                  selectedSecond === snapshot.snapshot_id;

                return (
                  <TableRow
                    key={snapshot.snapshot_id}
                    hover
                    selected={isFirst || isSecond}
                    onClick={() =>
                      handleSnapshotClick(snapshot)
                    }
                    sx={{
                      cursor: "pointer",
                    }}
                  >
                    <TableCell>
                      <Typography
                        variant="body2"
                        fontWeight={700}
                      >
                        {snapshot.business_date}
                      </Typography>

                      <Typography
                        variant="caption"
                        color="text.secondary"
                      >
                        Snapshot #{snapshot.snapshot_id}
                      </Typography>

                      {isFirst && (
                        <Chip
                          label="First"
                          size="small"
                          color="primary"
                          sx={{ ml: 1 }}
                        />
                      )}

                      {isSecond && (
                        <Chip
                          label="Second"
                          size="small"
                          color="secondary"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </TableCell>

                    <TableCell align="right">
                      <Typography fontWeight={800}>
                        {formatNumber(
                          snapshot.risk_score,
                          2,
                        )}
                      </Typography>
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={snapshot.health || "Unknown"}
                        color={healthColor(snapshot.health)}
                        size="small"
                      />
                    </TableCell>

                    <TableCell align="right">
                      {formatCurrency(
                        snapshot.total_exposure,
                      )}
                    </TableCell>

                    <TableCell align="right">
                      {formatCurrency(snapshot.total_mtm)}
                    </TableCell>

                    <TableCell align="right">
                      {formatNumber(
                        snapshot.margin_utilization,
                        2,
                      )}
                      %
                    </TableCell>

                    <TableCell align="right">
                      {formatNumber(
                        snapshot.diversification_score,
                        2,
                      )}
                    </TableCell>

                    <TableCell align="right">
                      {snapshot.clients}
                    </TableCell>

                    <TableCell align="right">
                      {snapshot.symbols}
                    </TableCell>
                  </TableRow>
                );
              })}

              {orderedSnapshots.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={9}
                    align="center"
                    sx={{ py: 6 }}
                  >
                    <Typography color="text.secondary">
                      No historical snapshots available.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {selectedFirst && selectedSecond && (
        <Paper
          sx={{
            p: 3,
            borderRadius: 3,
          }}
        >
          <Typography
            variant="h5"
            fontWeight={800}
            gutterBottom
          >
            Snapshot Comparison
          </Typography>

          {comparisonQuery.isLoading && (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                py: 5,
              }}
            >
              <CircularProgress />
            </Box>
          )}

          {comparisonQuery.isError && (
            <Alert severity="error">
              {comparisonQuery.error?.response?.data?.detail ||
                comparisonQuery.error?.message ||
                "Unable to compare snapshots."}
            </Alert>
          )}

          {comparison && (
            <Box>
              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  flexWrap: "wrap",
                  alignItems: "center",
                  mb: 3,
                }}
              >
                <Typography fontWeight={700}>
                  {comparison.first_business_date}
                </Typography>

                <CompareArrowsIcon color="action" />

                <Typography fontWeight={700}>
                  {comparison.second_business_date}
                </Typography>

                <RiskTrend
                  trend={comparison.risk_trend}
                />
              </Box>

              <Divider sx={{ mb: 3 }} />

              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: {
                    xs: "1fr",
                    sm: "repeat(2, 1fr)",
                    lg: "repeat(3, 1fr)",
                  },
                  gap: 2,
                }}
              >
                <ComparisonMetric
                  label="Risk Score"
                  first={firstSnapshot?.risk_score ?? 0}
                  second={secondSnapshot?.risk_score ?? 0}
                  change={comparison.risk_score_change}
                  inverse
                />

                <ComparisonMetric
                  label="Portfolio Value"
                  first={firstSnapshot?.portfolio_value ?? 0}
                  second={secondSnapshot?.portfolio_value ?? 0}
                  change={comparison.portfolio_value_change}
                  currency
                />

                <ComparisonMetric
                  label="Exposure"
                  first={firstSnapshot?.total_exposure ?? 0}
                  second={secondSnapshot?.total_exposure ?? 0}
                  change={comparison.exposure_change}
                  currency
                  inverse
                />

                <ComparisonMetric
                  label="MTM"
                  first={firstSnapshot?.total_mtm ?? 0}
                  second={secondSnapshot?.total_mtm ?? 0}
                  change={comparison.mtm_change}
                  currency
                />

                <ComparisonMetric
                  label="Margin Utilization"
                  first={firstSnapshot?.margin_utilization ?? 0}
                  second={secondSnapshot?.margin_utilization ?? 0}
                  change={comparison.margin_utilization_change}
                  suffix="%"
                  inverse
                />

                <ComparisonMetric
                  label="Diversification"
                  first={firstSnapshot?.diversification_score ?? 0}
                  second={secondSnapshot?.diversification_score ?? 0}
                  change={comparison.diversification_change}
                />

                <ComparisonMetric
                  label="Clients"
                  first={firstSnapshot?.clients ?? 0}
                  second={secondSnapshot?.clients ?? 0}
                  change={comparison.client_change}
                />

                <ComparisonMetric
                  label="Symbols"
                  first={firstSnapshot?.symbols ?? 0}
                  second={secondSnapshot?.symbols ?? 0}
                  change={comparison.symbol_change}
                />

                <ComparisonMetric
                  label="Records"
                  first={firstSnapshot?.records ?? 0}
                  second={secondSnapshot?.records ?? 0}
                  change={comparison.record_change}
                />
              </Box>

              <HistoricalRiskTrendCharts snapshots={snapshots} />

              {/* ---------------------------------------------------------
                  Risk Trend Insights
              --------------------------------------------------------- */}

              {chronologicalSnapshots.length > 0 && (
                <Box sx={{ mt: 4 }}>
                  <Typography
                    variant="h5"
                    fontWeight={800}
                    gutterBottom
                  >
                    Risk Trend Insights
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2.5 }}
                  >
                      Key observations from the historical Enterprise RMS
                      snapshots.
                    </Typography>

                    <Box
                      sx={{
                        display: "grid",
                        gridTemplateColumns: {
                          xs: "1fr",
                          sm: "repeat(2, 1fr)",
                          lg: "repeat(3, 1fr)",
                        },
                        gap: 2,
                      }}
                    >
                      <RiskInsightCard
                        title="Overall Risk Trend"
                        value={historicalTrend}
                        subtitle={
                          oldestSnapshot && latestSnapshot
                            ? `${formatNumber(
                                oldestSnapshot.risk_score,
                              )} → ${formatNumber(latestSnapshot.risk_score)}`
                            : "Insufficient data"
                        }
                        icon={
                          historicalTrend === "Improved" ? (
                            <TrendingDownIcon color="success" />
                          ) : historicalTrend === "Deteriorated" ? (
                            <TrendingUpIcon color="error" />
                          ) : (
                            <RemoveIcon color="action" />
                          )
                        }
                        valueColor={
                          historicalTrend === "Improved"
                            ? "success.main"
                            : historicalTrend === "Deteriorated"
                              ? "error.main"
                              : "text.primary"
                        }
                      />

                      <RiskInsightCard
                        title="Best Risk Day"
                        value={
                          bestRiskSnapshot
                            ? formatNumber(bestRiskSnapshot.risk_score)
                            : "â€”"
                        }
                        subtitle={
                          bestRiskSnapshot
                            ? bestRiskSnapshot.business_date
                            : "No data"
                        }
                        icon={<AssessmentIcon color="success" />}
                        valueColor="success.main"
                      />

                      <RiskInsightCard
                        title="Worst Risk Day"
                        value={
                          worstRiskSnapshot
                            ? formatNumber(worstRiskSnapshot.risk_score)
                            : "â€”"
                        }
                        subtitle={
                          worstRiskSnapshot
                            ? worstRiskSnapshot.business_date
                            : "No data"
                        }
                        icon={<WarningAmberIcon color="error" />}
                        valueColor="error.main"
                      />

                      <RiskInsightCard
                        title="Highest Exposure"
                        value={
                          highestExposureSnapshot
                            ? formatCurrency(
                                highestExposureSnapshot.total_exposure,
                              )
                            : "â€”"
                        }
                        subtitle={
                          highestExposureSnapshot
                            ? highestExposureSnapshot.business_date
                            : "No data"
                        }
                        icon={<AccountBalanceIcon color="warning" />}
                      />

                      <RiskInsightCard
                        title="Lowest Exposure"
                        value={
                          lowestExposureSnapshot
                            ? formatCurrency(
                                lowestExposureSnapshot.total_exposure,
                              )
                            : "â€”"
                        }
                        subtitle={
                          lowestExposureSnapshot
                            ? lowestExposureSnapshot.business_date
                            : "No data"
                        }
                        icon={<AccountBalanceIcon color="success" />}
                        valueColor="success.main"
                      />

                      <RiskInsightCard
                        title="Best MTM"
                        value={
                          bestMTMSnapshot
                            ? formatCurrency(bestMTMSnapshot.total_mtm)
                            : "â€”"
                        }
                        subtitle={
                          bestMTMSnapshot
                            ? bestMTMSnapshot.business_date
                            : "No data"
                        }
                        icon={<ShowChartIcon color="success" />}
                        valueColor="success.main"
                      />

                      <RiskInsightCard
                        title="Worst MTM"
                        value={
                          worstMTMSnapshot
                            ? formatCurrency(worstMTMSnapshot.total_mtm)
                            : "â€”"
                        }
                        subtitle={
                          worstMTMSnapshot
                            ? worstMTMSnapshot.business_date
                            : "No data"
                        }
                        icon={<ShowChartIcon color="error" />}
                        valueColor="error.main"
                      />

                      <RiskInsightCard
                        title="Exposure Movement"
                        value={formatCurrency(historicalExposureChange)}
                        subtitle="Oldest snapshot → latest snapshot"
                        icon={
                          historicalExposureChange <= 0 ? (
                            <TrendingDownIcon color="success" />
                          ) : (
                            <TrendingUpIcon color="error" />
                          )
                        }
                        valueColor={
                          historicalExposureChange <= 0
                            ? "success.main"
                            : "error.main"
                        }
                      />

                      <RiskInsightCard
                        title="Diversification Movement"
                        value={formatChange(
                          historicalDiversificationChange,
                        )}
                        subtitle="Change across historical period"
                        icon={<AssessmentIcon color="info" />}
                        valueColor={changeColor(
                          historicalDiversificationChange,
                        )}
                      />
                    </Box>

                    <Box sx={{ mt: 3 }}>
                      <Alert
                        severity={
                          historicalTrend === "Improved"
                            ? "success"
                            : historicalTrend === "Deteriorated"
                              ? "warning"
                              : "info"
                        }
                      >
                        Historical risk trend is{" "}
                        <strong>{historicalTrend}</strong>. Risk score moved from{" "}
                        <strong>
                          {formatNumber(oldestSnapshot?.risk_score)}
                        </strong>{" "}
                        on{" "}
                        <strong>{oldestSnapshot?.business_date}</strong> to{" "}
                        <strong>
                          {formatNumber(latestSnapshot?.risk_score)}
                        </strong>{" "}
                        on{" "}
                        <strong>{latestSnapshot?.business_date}</strong>.
                        {" "}
                        Exposure changed by{" "}
                        <strong>
                          {formatCurrency(historicalExposureChange)}
                        </strong>
                        {" "}
                        and MTM changed by{" "}
                        <strong>
                          {formatCurrency(historicalMTMChange)}
                        </strong>.
                      </Alert>
                    </Box>
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        )}
      </Box>
    );
}
