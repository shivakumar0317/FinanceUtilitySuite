import {
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

const money = (value) =>
  `₹${Number(value || 0).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  })}`;

function MoversTable({ title, rows }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          {title}
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">P/L</TableCell>
                <TableCell align="right">P/L %</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.symbol}>
                  <TableCell>{row.symbol}</TableCell>
                  <TableCell align="right">
                    {money(row.profit_loss)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color:
                        row.profit_loss_percent >= 0
                          ? "success.main"
                          : "error.main",
                      fontWeight: 700,
                    }}
                  >
                    {row.profit_loss_percent}%
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}

export default function PortfolioLiveTables({
  topHoldings,
  gainers,
  losers,
}) {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, lg: 4 }}>
        <Card sx={{ height: "100%" }}>
          <CardContent>
            <Typography
              variant="h6"
              fontWeight={700}
              mb={2}
            >
              Top Holdings
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="right">
                      Current Value
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topHoldings.map((row) => (
                    <TableRow key={row.symbol}>
                      <TableCell>{row.symbol}</TableCell>
                      <TableCell align="right">
                        {money(row.current_value)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, lg: 4 }}>
        <MoversTable
          title="Top Gainers"
          rows={gainers}
        />
      </Grid>

      <Grid size={{ xs: 12, lg: 4 }}>
        <MoversTable
          title="Top Losers"
          rows={losers}
        />
      </Grid>
    </Grid>
  );
}
