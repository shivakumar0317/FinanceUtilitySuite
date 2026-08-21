import { useState } from "react";

import {
  Box,
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

const getSortValue = (row, key) => {
  if (
    key === "AccountId" ||
    key === "Largest Stock" ||
    key === "Risk Level"
  ) {
    return String(row[key] || "").toLowerCase();
  }

  const value = Number(row[key] ?? 0);
  return Number.isNaN(value) ? 0 : value;
};

const sortRows = (rows, sortKey, sortDirection) => {
  if (!sortKey) {
    return rows || [];
  }

  return [...(rows || [])].sort((a, b) => {
    const aValue = getSortValue(a, sortKey);
    const bValue = getSortValue(b, sortKey);

    if (typeof aValue === "string") {
      const comparison = aValue.localeCompare(
        bValue,
        undefined,
        { numeric: true, sensitivity: "base" },
      );
      return sortDirection === "asc" ? comparison : -comparison;
    }

    if (aValue === bValue) {
      return 0;
    }

    const comparison = aValue < bValue ? -1 : 1;
    return sortDirection === "asc" ? comparison : -comparison;
  });
};

function SortableHeaderCell({
  label,
  sortKey,
  sortBy,
  sortDirection,
  onSort,
  align = "left",
  sx,
}) {
  const active = sortBy === sortKey;
  const arrow = active
    ? sortDirection === "asc"
      ? "▲"
      : "▼"
    : "↕";

  return (
    <TableCell
      align={align}
      sx={{
        ...headerCellSx,
        ...sx,
        p: 0,
      }}
    >
      <Box
        component="button"
        type="button"
        onClick={() => onSort(sortKey)}
        aria-label={`Sort ${label}`}
        sx={{
          width: "100%",
          minHeight: 40,
          display: "flex",
          alignItems: "center",
          justifyContent:
            align === "right"
              ? "flex-end"
              : align === "center"
                ? "center"
                : "flex-start",
          gap: 0.7,
          px: 1,
          py: 0.75,
          border: 0,
          background: "transparent",
          color: active
            ? "text.primary"
            : "text.secondary",
          font: "inherit",
          fontWeight: 700,
          fontSize: "inherit",
          textTransform: "uppercase",
          letterSpacing: "inherit",
          cursor: "pointer",
          userSelect: "none",
          textAlign: align,
          "&:hover": {
            color: "text.primary",
            backgroundColor:
              "rgba(96, 165, 250, 0.10)",
          },
          "&:focus-visible": {
            outline: "2px solid",
            outlineColor: "primary.main",
            outlineOffset: "-2px",
          },
        }}
      >
        <Box component="span">{label}</Box>
        <Box
          component="span"
          sx={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            minWidth: 12,
            fontSize: active ? "0.72rem" : "0.68rem",
            lineHeight: 1,
            opacity: active ? 1 : 0.55,
            color: active
              ? "primary.main"
              : "text.secondary",
          }}
        >
          {arrow}
        </Box>
      </Box>
    </TableCell>
  );
}

function ClientTable({
  title,
  rows,
}) {
  const [sortBy, setSortBy] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDirection((current) =>
        current === "asc" ? "desc" : "asc",
      );
      return;
    }

    setSortBy(key);
    setSortDirection("asc");
  };

  const sortedRows = sortRows(
    rows,
    sortBy,
    sortDirection,
  );

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
                <SortableHeaderCell
                  label="Account"
                  sortKey="AccountId"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "14%" }}
                />
                <SortableHeaderCell
                  label="Holdings"
                  sortKey="Holdings"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="center"
                  sx={{ width: "8%" }}
                />
                <SortableHeaderCell
                  label="Largest Stock"
                  sortKey="Largest Stock"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "20%" }}
                />
                <SortableHeaderCell
                  label="Concentration"
                  sortKey="Largest Holding %"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "16%" }}
                />
                <SortableHeaderCell
                  label="Exposure"
                  sortKey="Largest Exposure"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "16%" }}
                />
                <SortableHeaderCell
                  label="MTM"
                  sortKey="MarkToMarket"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "16%" }}
                />
                <SortableHeaderCell
                  label="Risk"
                  sortKey="Risk Level"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "10%" }}
                />
              </TableRow>
            </TableHead>

            <TableBody>
              {sortedRows.map((row, index) => (
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
  const [sortBy, setSortBy] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDirection((current) =>
        current === "asc" ? "desc" : "asc",
      );
      return;
    }

    setSortBy(key);
    setSortDirection("asc");
  };

  const sortedRows = sortRows(
    rows,
    sortBy,
    sortDirection,
  );

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
                <SortableHeaderCell
                  label="Account"
                  sortKey="AccountId"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "11%" }}
                />
                <SortableHeaderCell
                  label="Holdings"
                  sortKey="Holdings"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="center"
                  sx={{ width: "7%" }}
                />
                <SortableHeaderCell
                  label="Largest Stock"
                  sortKey="Largest Stock"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "14%" }}
                />
                <SortableHeaderCell
                  label="Largest Exposure"
                  sortKey="Largest Exposure"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "14%" }}
                />
                <SortableHeaderCell
                  label="Concentration"
                  sortKey="Largest Holding %"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "12%" }}
                />
                <SortableHeaderCell
                  label="Total Exposure"
                  sortKey="Total Exposure"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "14%" }}
                />
                <SortableHeaderCell
                  label="MTM"
                  sortKey="MarkToMarket"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  align="right"
                  sx={{ width: "14%" }}
                />
                <SortableHeaderCell
                  label="Risk"
                  sortKey="Risk Level"
                  sortBy={sortBy}
                  sortDirection={sortDirection}
                  onSort={handleSort}
                  sx={{ width: "8%" }}
                />
              </TableRow>
            </TableHead>

            <TableBody>
              {sortedRows.map((row, index) => {
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
