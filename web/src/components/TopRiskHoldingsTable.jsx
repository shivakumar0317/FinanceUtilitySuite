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

const numeric = (value) =>
  value === null || value === undefined
    ? "N/A"
    : Number(value).toFixed(2);

export default function TopRiskHoldingsTable({ rows }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Top Risk Holdings
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Sector</TableCell>
                <TableCell align="right">
                  Current Value
                </TableCell>
                <TableCell align="right">
                  Weight %
                </TableCell>
                <TableCell align="right">Beta</TableCell>
                <TableCell align="right">
                  Volatility %
                </TableCell>
                <TableCell align="right">
                  Risk Contribution
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.symbol}>
                  <TableCell>{row.symbol}</TableCell>
                  <TableCell>{row.sector}</TableCell>
                  <TableCell align="right">
                    {money(row.current_value)}
                  </TableCell>
                  <TableCell align="right">
                    {numeric(row.portfolio_weight)}%
                  </TableCell>
                  <TableCell align="right">
                    {numeric(row.beta)}
                  </TableCell>
                  <TableCell align="right">
                    {numeric(
                      row.annualized_volatility,
                    )}
                    %
                  </TableCell>
                  <TableCell align="right">
                    {numeric(row.risk_contribution)}
                  </TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No risk holdings data available.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
