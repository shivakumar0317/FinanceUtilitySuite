import {
  Card,
  CardContent,
  Chip,
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

const riskColor = (level) => {
  if (level === "High") {
    return "error";
  }

  if (level === "Moderate") {
    return "warning";
  }

  return "success";
};

export default function MTFClientRiskTable({ rows }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Client Risk Analysis
        </Typography>

        <TableContainer sx={{ maxHeight: 520 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Account</TableCell>
                <TableCell align="right">
                  Buy Value
                </TableCell>
                <TableCell align="right">
                  Net Value
                </TableCell>
                <TableCell align="right">MTM</TableCell>
                <TableCell align="right">
                  Margin
                </TableCell>
                <TableCell align="right">
                  Margin %
                </TableCell>
                <TableCell align="right">
                  MTM %
                </TableCell>
                <TableCell align="right">
                  Symbols
                </TableCell>
                <TableCell align="right">
                  Risk Score
                </TableCell>
                <TableCell align="center">
                  Risk Level
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.account_id}>
                  <TableCell>{row.account_id}</TableCell>
                  <TableCell align="right">
                    {money(row.buy_value)}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.net_value)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color:
                        row.mtm >= 0
                          ? "success.main"
                          : "error.main",
                      fontWeight: 700,
                    }}
                  >
                    {money(row.mtm)}
                  </TableCell>
                  <TableCell align="right">
                    {money(row.margin)}
                  </TableCell>
                  <TableCell align="right">
                    {Number(
                      row.margin_percent || 0,
                    ).toFixed(2)}
                    %
                  </TableCell>
                  <TableCell align="right">
                    {Number(
                      row.mtm_percent || 0,
                    ).toFixed(2)}
                    %
                  </TableCell>
                  <TableCell align="right">
                    {row.symbols}
                  </TableCell>
                  <TableCell align="right">
                    {Number(
                      row.risk_score || 0,
                    ).toFixed(2)}
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      size="small"
                      label={row.risk_level}
                      color={riskColor(row.risk_level)}
                    />
                  </TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    No client risk data available.
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
