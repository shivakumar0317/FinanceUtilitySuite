import {
  Clear,
  Download,
  Refresh,
  Search,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import MTFConcentrationCharts from "../components/MTFConcentrationCharts";
import MTFConcentrationSummaryCards from "../components/MTFConcentrationSummaryCards";
import MTFConcentrationTables from "../components/MTFConcentrationTables";
import api from "../services/api";

export default function MTFConcentrationPage() {
  const [search, setSearch] = useState("");

  const concentration = useQuery({
    queryKey: ["mtf-concentration"],
    queryFn: async () =>
      (await api.get("/api/mtf/concentration")).data,
    retry: false,
  });

  const data = concentration.data;

  const filteredClients = useMemo(() => {
    if (!data?.client_summary) {
      return [];
    }

    const term = search.trim().toUpperCase();

    if (!term) {
      return data.client_summary;
    }

    return data.client_summary.filter((row) => {
      const account = String(row.AccountId ?? "").toUpperCase();
      const stock = String(
        row["Largest Stock"] ?? "",
      ).toUpperCase();

      const risk = String(
        row["Risk Level"] ?? "",
      ).toUpperCase();

      return (
        account.includes(term) ||
        stock.includes(term) ||
        risk.includes(term)
      );
    });
  }, [data, search]);

  const exportCsv = () => {
    if (!filteredClients.length) {
      return;
    }

    const columns = [
      "AccountId",
      "Holdings",
      "Largest Stock",
      "Largest Exposure",
      "Largest Holding %",
      "Total Exposure",
      "BUY VALUE",
      "NetValue",
      "MarkToMarket",
      "MTF VAR",
      "MTF MARGIN",
      "Risk Level",
    ];

    const escapeCsv = (value) => {
      const text = String(value ?? "");

      if (
        text.includes(",") ||
        text.includes('"') ||
        text.includes("\n")
      ) {
        return `"${text.replaceAll('"', '""')}"`;
      }

      return text;
    };

    const rows = [
      columns.join(","),
      ...filteredClients.map((row) =>
        columns
          .map((column) => escapeCsv(row[column]))
          .join(","),
      ),
    ];

    const blob = new Blob(
      [rows.join("\n")],
      { type: "text/csv;charset=utf-8;" },
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "mtf_concentration_risk.csv";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);
  };

  if (concentration.isLoading) {
    return (
      <Stack
        alignItems="center"
        justifyContent="center"
        minHeight="60vh"
      >
        <CircularProgress />
      </Stack>
    );
  }

  if (concentration.isError) {
    return (
      <Stack spacing={3}>
        <Box>
          <Typography variant="h4" fontWeight={800}>
            MTF Concentration Risk Dashboard
          </Typography>

          <Typography color="text.secondary">
            Client-level concentration and single-stock
            MTF risk analysis.
          </Typography>
        </Box>

        <Alert severity="error">
          {concentration.error?.response?.data?.detail ||
            "Unable to load MTF concentration dashboard."}
        </Alert>

        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => concentration.refetch()}
        >
          Retry
        </Button>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        justifyContent="space-between"
        alignItems={{ md: "center" }}
        spacing={2}
      >
        <Box>
          <Typography
            variant="h4"
            fontWeight={800}
          >
            MTF Concentration Risk Dashboard
          </Typography>

          <Typography color="text.secondary">
            Client-level concentration and single-stock
            MTF risk analysis.
          </Typography>
        </Box>

        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={() => concentration.refetch()}
          disabled={concentration.isFetching}
        >
          Refresh
        </Button>
      </Stack>

      <MTFConcentrationSummaryCards
        summary={data.summary}
      />

      <Stack
        direction={{
          xs: "column",
          md: "row",
        }}
        spacing={2}
      >
        <TextField
          fullWidth
          label="Search Client / Stock / Risk"
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />

        <Button
          variant="outlined"
          startIcon={<Clear />}
          onClick={() => setSearch("")}
          sx={{ minWidth: 120 }}
        >
          Clear
        </Button>

        <Button
          variant="contained"
          startIcon={<Download />}
          onClick={exportCsv}
          disabled={!filteredClients.length}
          sx={{ minWidth: 140 }}
        >
          Export CSV
        </Button>
      </Stack>

      <MTFConcentrationCharts
        distribution={data.distribution}
        riskDistribution={data.risk_distribution}
      />

      <MTFConcentrationTables
        singleStockClients={data.single_stock_clients}
        topConcentratedClients={
          data.top_concentrated_clients
        }
        multipleStockClients={
          data.multiple_stock_clients
        }
        clientSummary={filteredClients}
      />
    </Stack>
  );
}