import { Download, Star } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import StockMetricsGrid from "../components/StockMetricsGrid";
import StockPriceChart from "../components/StockPriceChart";
import StockScoreCards from "../components/StockScoreCards";
import StockSearchBox from "../components/StockSearchBox";
import api from "../services/api";

export default function StockAnalyzerPage() {
  const [search, setSearch] = useState(null);

  const stock = useQuery({
    queryKey: ["stock-analysis", search?.symbol, search?.period],
    enabled: Boolean(search),
    queryFn: async () =>
      (
        await api.get(`/api/stocks/${search.symbol}`, {
          params: {
            period: search.period,
            interval: "1d",
          },
        })
      ).data,
  });

  const addToWatchlist = useMutation({
    mutationFn: async () =>
      (
        await api.post("/api/watchlist", {
          symbol: stock.data.details.symbol,
          exchange: "NSE",
        })
      ).data,
  });

  const downloadExcel = async () => {
    const response = await api.get(
      `/api/stocks/${search.symbol}/export`,
      {
        params: { period: search.period },
        responseType: "blob",
      },
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${search.symbol}_Stock_Analysis.xlsx`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={800}>
          Stock Analyzer
        </Typography>
        <Typography color="text.secondary">
          Analyze fundamentals, risk, valuation and price history.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <StockSearchBox
            loading={stock.isFetching}
            onSearch={(symbol, period) => setSearch({ symbol, period })}
          />
        </CardContent>
      </Card>

      {stock.isFetching && (
        <Stack alignItems="center" py={6}>
          <CircularProgress />
        </Stack>
      )}

      {stock.isError && (
        <Alert severity="error">
          {stock.error.response?.data?.detail ||
            "Unable to analyze this stock."}
        </Alert>
      )}

      {stock.data && (
        <>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            justifyContent="space-between"
            alignItems={{ sm: "center" }}
            spacing={2}
          >
            <Box>
              <Typography variant="h5" fontWeight={800}>
                {stock.data.details.company_name}
              </Typography>
              <Typography color="text.secondary">
                {stock.data.details.resolved_symbol} ·{" "}
                {stock.data.details.industry}
              </Typography>
              <Typography
                color={
                  stock.data.details.change_percent >= 0
                    ? "success.main"
                    : "error.main"
                }
                fontWeight={700}
              >
                {stock.data.details.change_percent >= 0 ? "+" : ""}
                {stock.data.details.change} (
                {stock.data.details.change_percent}%)
              </Typography>
            </Box>

            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                startIcon={<Star />}
                onClick={() => addToWatchlist.mutate()}
                disabled={addToWatchlist.isPending}
              >
                Add to Watchlist
              </Button>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={downloadExcel}
              >
                Export Excel
              </Button>
            </Stack>
          </Stack>

          {addToWatchlist.isSuccess && (
            <Alert severity="success">
              Stock added to your watchlist.
            </Alert>
          )}

          {addToWatchlist.isError && (
            <Alert severity="warning">
              {addToWatchlist.error.response?.data?.detail ||
                "Unable to add stock to watchlist."}
            </Alert>
          )}

          <StockMetricsGrid details={stock.data.details} />
          <StockScoreCards analysis={stock.data.analysis} />
          <StockPriceChart history={stock.data.history} />
        </>
      )}
    </Stack>
  );
}
