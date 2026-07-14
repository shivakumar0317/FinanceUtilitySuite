import {
  Card,
  CardContent,
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

export default function PortfolioLiveHoldingsTable({
  holdings,
}) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Live Holdings
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">Qty</TableCell>
                <TableCell align="right">Avg Price</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">Invested</TableCell>
                <TableCell align="right">Current Value</TableCell>
                <TableCell align="right">P/L</TableCell>
                <TableCell align="right">P/L %</TableCell>
                <TableCell align="right">Today's P/L</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {holdings.map((row) => (
                <TableRow key={row.symbol}>
                  <TableCell>{row.symbol}</TableCell>
                  <TableCell align="right">
                    {row.quantity}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.average_price)}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.current_price)}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.invested_value)}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.current_value)}
                  </TableCell>
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
                  <TableCell align="right">
                    {money(row.day_change)}
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
