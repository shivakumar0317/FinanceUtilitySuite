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

function StandardTable({
  title,
  columns,
  rows,
  rowKey,
}) {
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
                {columns.map((column) => (
                  <TableCell
                    key={column.key}
                    align={column.align || "left"}
                  >
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, index) => (
                <TableRow
                  key={
                    typeof rowKey === "function"
                      ? rowKey(row, index)
                      : row[rowKey] ?? index
                  }
                >
                  {columns.map((column) => (
                    <TableCell
                      key={column.key}
                      align={column.align || "left"}
                      sx={column.sx?.(row)}
                    >
                      {column.render
                        ? column.render(row)
                        : row[column.key]}
                    </TableCell>
                  ))}
                </TableRow>
              ))}

              {rows.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    align="center"
                  >
                    No data available.
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

const clientColumns = [
  { key: "account_id", label: "Account" },
  {
    key: "margin",
    label: "Margin",
    align: "right",
    render: (row) => money(row.margin),
  },
  {
    key: "buy_value",
    label: "Buy Value",
    align: "right",
    render: (row) => money(row.buy_value),
  },
  {
    key: "mtm",
    label: "MTM",
    align: "right",
    render: (row) => money(row.mtm),
  },
  {
    key: "symbols",
    label: "Symbols",
    align: "right",
  },
];

const symbolColumns = [
  { key: "symbol", label: "Symbol" },
  {
    key: "margin",
    label: "Margin",
    align: "right",
    render: (row) => money(row.margin),
  },
  {
    key: "buy_value",
    label: "Buy Value",
    align: "right",
    render: (row) => money(row.buy_value),
  },
  {
    key: "mtm",
    label: "MTM",
    align: "right",
    render: (row) => money(row.mtm),
  },
  {
    key: "clients",
    label: "Clients",
    align: "right",
  },
];

const mtmColumns = [
  { key: "account_id", label: "Account" },
  { key: "symbol", label: "Symbol" },
  {
    key: "mtm",
    label: "MTM",
    align: "right",
    render: (row) => money(row.mtm),
    sx: (row) => ({
      color:
        row.mtm >= 0
          ? "success.main"
          : "error.main",
      fontWeight: 700,
    }),
  },
  {
    key: "buy_value",
    label: "Buy Value",
    align: "right",
    render: (row) => money(row.buy_value),
  },
  {
    key: "margin",
    label: "Margin",
    align: "right",
    render: (row) => money(row.margin),
  },
];

export default function MTFDataTables({
  topMarginClients,
  topMarginSymbols,
  topMtmGainers,
  topMtmLosers,
}) {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, lg: 6 }}>
        <StandardTable
          title="Top Margin Clients"
          columns={clientColumns}
          rows={topMarginClients}
          rowKey="account_id"
        />
      </Grid>

      <Grid size={{ xs: 12, lg: 6 }}>
        <StandardTable
          title="Top Margin Symbols"
          columns={symbolColumns}
          rows={topMarginSymbols}
          rowKey="symbol"
        />
      </Grid>

      <Grid size={{ xs: 12, lg: 6 }}>
        <StandardTable
          title="Top MTM Gainers"
          columns={mtmColumns}
          rows={topMtmGainers}
          rowKey={(row, index) =>
            `${row.account_id}-${row.symbol}-${index}`
          }
        />
      </Grid>

      <Grid size={{ xs: 12, lg: 6 }}>
        <StandardTable
          title="Top MTM Losers"
          columns={mtmColumns}
          rows={topMtmLosers}
          rowKey={(row, index) =>
            `${row.account_id}-${row.symbol}-${index}`
          }
        />
      </Grid>
    </Grid>
  );
}
