import { Refresh } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import PortfolioLiveChart from "../components/PortfolioLiveChart";
import PortfolioLiveHoldingsTable from "../components/PortfolioLiveHoldingsTable";
import PortfolioLiveSummaryCards from "../components/PortfolioLiveSummaryCards";
import PortfolioLiveTables from "../components/PortfolioLiveTables";
import PortfolioUploadCard from "../components/PortfolioUploadCard";
import api from "../services/api";

export default function PortfolioLivePage() {
  const [dashboardData, setDashboardData] = useState(null);

  const upload = useMutation({
    mutationFn: async (file) => {
      const formData = new FormData();
      formData.append("file", file);

      return (
        await api.post(
          "/api/portfolio-live/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          },
        )
      ).data;
    },
    onSuccess: (data) => {
      setDashboardData(data);
    },
  });

  const refresh = useQuery({
    queryKey: ["portfolio-live-dashboard"],
    enabled: true,
    retry: false,
    queryFn: async () =>
      (
        await api.get(
          "/api/portfolio-live/dashboard",
        )
      ).data,
  });
    useEffect(() => {
      if (refresh.data) {
        setDashboardData(refresh.data);
      }
    }, [refresh.data]);

  const refreshDashboard = async () => {
    const result = await refresh.refetch();

    if (result.data) {
      setDashboardData(result.data);
    }
  };

  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ sm: "center" }}
        spacing={2}
      >
        <Box>
          <Typography variant="h4" fontWeight={800}>
            Portfolio Live
          </Typography>
          <Typography color="text.secondary">
            Upload holdings and calculate live portfolio values.
          </Typography>
        </Box>

        {dashboardData && (
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshDashboard}
            disabled={refresh.isFetching}
          >
            Refresh Prices
          </Button>
        )}
      </Stack>

      <PortfolioUploadCard
        onUpload={(file) => upload.mutate(file)}
        uploading={upload.isPending}
        error={
          upload.error?.response?.data?.detail
          || (upload.isError
            ? "Unable to upload portfolio."
            : "")
        }
      />

      {(upload.isPending || refresh.isFetching) && (
        <Stack alignItems="center" py={4}>
          <CircularProgress />
        </Stack>
      )}

      {refresh.isError && (
        <Alert severity="error">
          {refresh.error.response?.data?.detail
            || "Unable to refresh portfolio."}
        </Alert>
      )}

      {dashboardData && (
        <>
          <PortfolioLiveSummaryCards
            summary={dashboardData.summary}
          />

          <PortfolioLiveChart
            performance={dashboardData.performance}
          />

          <PortfolioLiveTables
            topHoldings={dashboardData.top_holdings}
            gainers={dashboardData.top_gainers}
            losers={dashboardData.top_losers}
          />

          <PortfolioLiveHoldingsTable
            holdings={dashboardData.holdings}
          />
        </>
      )}
    </Stack>
  );
}
