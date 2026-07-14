import { Search } from "@mui/icons-material";
import { Button, MenuItem, Stack, TextField } from "@mui/material";
import { useState } from "react";

export default function StockSearchBox({ onSearch, loading }) {
  const [symbol, setSymbol] = useState("");
  const [period, setPeriod] = useState("1y");

  const submit = (event) => {
    event.preventDefault();
    if (symbol.trim()) {
      onSearch(symbol.trim().toUpperCase(), period);
    }
  };

  return (
    <Stack
      component="form"
      direction={{ xs: "column", sm: "row" }}
      spacing={2}
      onSubmit={submit}
    >
      <TextField
        label="Stock symbol"
        placeholder="RELIANCE, TCS, INFY"
        required
        fullWidth
        value={symbol}
        onChange={(event) => setSymbol(event.target.value)}
      />
      <TextField
        select
        label="History"
        value={period}
        onChange={(event) => setPeriod(event.target.value)}
        sx={{ minWidth: 130 }}
      >
        <MenuItem value="1mo">1 Month</MenuItem>
        <MenuItem value="3mo">3 Months</MenuItem>
        <MenuItem value="6mo">6 Months</MenuItem>
        <MenuItem value="1y">1 Year</MenuItem>
        <MenuItem value="2y">2 Years</MenuItem>
        <MenuItem value="5y">5 Years</MenuItem>
      </TextField>
      <Button
        type="submit"
        variant="contained"
        startIcon={<Search />}
        disabled={loading}
        sx={{ minWidth: 140 }}
      >
        Analyze
      </Button>
    </Stack>
  );
}
