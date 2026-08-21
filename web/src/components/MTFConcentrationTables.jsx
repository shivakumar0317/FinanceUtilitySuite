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

const concentration = (value) =>
  `${Number(value || 0).toFixed(2)}%`;

function RiskBadge({ level }) {
  const normalized = String(level || "").toLowerCase();

  let color = "success.main";

  if (normalized === "critical") {
    color = "error.main";
  } else if (normalized === "high") {
    color = "warning.main";
  } else if (normalized === "medium") {
    color = "#facc15";
  }

  return (
    <Typography
      component="span"
      variant="body2"
      sx={{
        color,
        fontWeight: 700,
        whiteSpace: "nowrap",
      }}
    >
      {level || "-"}
    </Typography>
  );
}

const headerCellSx = {
  backgroundColor: "rgba(8, 15, 30, 0.96)",
  color: "text.secondary",
  fontWeight: 700,
  fontSize: "0.78rem",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  borderBottom: "1px solid",
  borderColor: "divider",
  whiteSpace: "nowrap",
};

const bodyCellSx = {
  borderBottom: "1px solid",
  borderColor: "divider",
  py: 1.15,
  whiteSpace: "nowrap",
  fontVariantNumeric: "tabular-nums",
};

function ClientTable({
  title,
  rows,
}) {
  return (
    <Card
      sx={{
        height: "100%",
        borderRadius: 3,
        overflow: "hidden",
      }}
    >
      <CardContent
        sx={{
          p: 2,
          "&:last-child": {
            pb: 2,
          },
        }}
      >
        <Typography
          variant="h6"
          fontWeight={800}
          mb={0.5}
        >
          {title}
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          mb={2}
        >
          {rows?.length || 0} clients
        </Typography>

        <TableContainer
          sx={{
            maxHeight: 420,
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
            "&::-webkit-scrollbar": {
              width: 8,
              height: 8,
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: "rgba(148, 163, 184, 0.35)",
              borderRadius: 8,
            },
          }}
        >
          <Table
            size="small"
            stickyHeader
            sx={{
              width: "100%",
              minWidth: 0,
              tableLayout: "fixed",
              "& .MuiTableRow-root": {
                transition: "background-color 0.15s ease",
              },
              "& .MuiTableBody-root .MuiTableRow-root:hover": {
                backgroundColor: "rgba(96, 165, 250, 0.07)",
              },
            }}
          >
            <TableHead>
              <TableRow>
                <TableCell
                  sx={{ ...headerCellSx, width: "14%" }}
                >
                  Account
                </TableCell>

                <TableCell
                  align="center"
                  sx={{ ...headerCellSx, width: "8%" }}
                >
                  Holdings
                </TableCell>

                <TableCell
                  sx={{ ...headerCellSx, width: "20%" }}
                >
                  Largest Stock
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "16%" }}
                >
                  Concentration
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "16%" }}
                >
                  Exposure
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "16%" }}
                >
                  MTM
                </TableCell>

                <TableCell
                  sx={{ ...headerCellSx, width: "10%" }}
                >
                  Risk
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {(rows || []).map((row, index) => (
                <TableRow
                  key={`${row.AccountId}-${index}`}
                >
                  <TableCell
                    sx={{
                      ...bodyCellSx,
                      fontWeight: 700,
                    }}
                  >
                    {row.AccountId}
                  </TableCell>

                  <TableCell
                    align="center"
                    sx={bodyCellSx}
                  >
                    {row.Holdings}
                  </TableCell>

                  <TableCell sx={bodyCellSx}>
                    <Typography
                      variant="body2"
                      fontWeight={600}
                    >
                      {row["Largest Stock"] || "-"}
                    </Typography>
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      ...bodyCellSx,
                      fontWeight: 700,
                    }}
                  >
                    {concentration(
                      row["Largest Holding %"],
                    )}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      ...bodyCellSx,
                      fontWeight: 600,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {money(
                      row["Largest Exposure"] ||
                        row["Total Exposure"],
                    )}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      ...bodyCellSx,
                      color:
                        Number(row.MarkToMarket || 0) >= 0
                          ? "success.main"
                          : "error.main",
                      fontWeight: 700,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {money(row.MarkToMarket || 0)}
                  </TableCell>

                  <TableCell sx={bodyCellSx}>
                    <RiskBadge
                      level={row["Risk Level"]}
                    />
                  </TableCell>
                </TableRow>
              ))}

              {(!rows || rows.length === 0) && (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    align="center"
                    sx={{
                      py: 6,
                      color: "text.secondary",
                    }}
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

function SummaryTable({ rows }) {
  return (
    <Card
      sx={{
        borderRadius: 3,
        overflow: "hidden",
      }}
    >
      <CardContent
        sx={{
          p: 2,
          "&:last-child": {
            pb: 2,
          },
        }}
      >
        <Typography
          variant="h6"
          fontWeight={800}
          mb={0.5}
        >
          Client Concentration Summary
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          mb={2}
        >
          Complete client-level concentration and exposure
          overview
        </Typography>

        <TableContainer
          sx={{
            maxHeight: 600,
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
            "&::-webkit-scrollbar": {
              width: 8,
              height: 8,
            },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: "rgba(148, 163, 184, 0.35)",
              borderRadius: 8,
            },
          }}
        >
          <Table
            size="small"
            stickyHeader
            sx={{
              width: "100%",
              minWidth: 0,
              tableLayout: "fixed",
              "& .MuiTableRow-root": {
                transition: "background-color 0.15s ease",
              },
              "& .MuiTableBody-root .MuiTableRow-root:hover": {
                backgroundColor: "rgba(96, 165, 250, 0.07)",
              },
            }}
          >
            <TableHead>
              <TableRow>
                <TableCell
                  sx={{ ...headerCellSx, width: "11%" }}
                >
                  Account
                </TableCell>

                <TableCell
                  align="center"
                  sx={{ ...headerCellSx, width: "7%" }}
                >
                  Holdings
                </TableCell>

                <TableCell
                  sx={{ ...headerCellSx, width: "14%" }}
                >
                  Largest Stock
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "14%" }}
                >
                  Largest Exposure
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "12%" }}
                >
                  Concentration
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "14%" }}
                >
                  Total Exposure
                </TableCell>

                <TableCell
                  align="right"
                  sx={{ ...headerCellSx, width: "14%" }}
                >
                  MTM
                </TableCell>

                <TableCell
                  sx={{ ...headerCellSx, width: "8%" }}
                >
                  Risk
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {(rows || []).map((row, index) => {
                const mtm = Number(
                  row.MarkToMarket || 0,
                );

                return (
                  <TableRow
                    key={`${row.AccountId}-${index}`}
                  >
                    <TableCell
                      sx={{
                        ...bodyCellSx,
                        fontWeight: 700,
                      }}
                    >
                      {row.AccountId}
                    </TableCell>

                    <TableCell
                      align="center"
                      sx={bodyCellSx}
                    >
                      {row.Holdings}
                    </TableCell>

                    <TableCell sx={bodyCellSx}>
                      <Typography
                        variant="body2"
                        fontWeight={600}
                      >
                        {row["Largest Stock"] || "-"}
                      </Typography>
                    </TableCell>

                    <TableCell
                      align="right"
                      sx={{
                        ...bodyCellSx,
                        fontWeight: 600,
                        minWidth: 145,
                      }}
                    >
                      {money(
                        row["Largest Exposure"],
                      )}
                    </TableCell>

                    <TableCell
                      align="right"
                      sx={{
                        ...bodyCellSx,
                        fontWeight: 700,
                      }}
                    >
                      {concentration(
                        row["Largest Holding %"],
                      )}
                    </TableCell>

                    <TableCell
                      align="right"
                      sx={{
                        ...bodyCellSx,
                        fontWeight: 600,
                        minWidth: 145,
                      }}
                    >
                      {money(
                        row["Total Exposure"],
                      )}
                    </TableCell>

                    <TableCell
                      align="right"
                      sx={{
                        ...bodyCellSx,
                        minWidth: 145,
                        color:
                          mtm >= 0
                            ? "success.main"
                            : "error.main",
                        fontWeight: 700,
                      }}
                    >
                      {money(mtm)}
                    </TableCell>

                    <TableCell sx={bodyCellSx}>
                      <RiskBadge
                        level={row["Risk Level"]}
                      />
                    </TableCell>
                  </TableRow>
                );
              })}

              {(!rows || rows.length === 0) && (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    align="center"
                    sx={{
                      py: 6,
                      color: "text.secondary",
                    }}
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

export default function MTFConcentrationTables({
  singleStockClients,
  topConcentratedClients,
  multipleStockClients,
  clientSummary,
}) {
  return (
    <>
      <Grid container spacing={2}>
        {/* 1. Single Stock Clients */}
        <Grid size={{ xs: 12 }}>
          <ClientTable
            title="Single Stock Clients"
            rows={singleStockClients}
          />
        </Grid>

        {/* 2. Multiple Stock Clients */}
        <Grid size={{ xs: 12 }}>
          <ClientTable
            title="Multiple Stock Clients"
            rows={multipleStockClients}
          />
        </Grid>

        {/* 3. Top Concentrated Clients */}
        <Grid size={{ xs: 12 }}>
          <ClientTable
            title="Top Concentrated Clients"
            rows={topConcentratedClients}
          />
        </Grid>

        {/* 4. Client Concentration Summary */}
        <Grid size={{ xs: 12 }}>
          <SummaryTable rows={clientSummary} />
        </Grid>
      </Grid>
    </>
  );
}
