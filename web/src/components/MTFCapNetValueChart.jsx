import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Card,
  CardContent,
  Typography,
} from "@mui/material";

const CATEGORY_COLORS = {
  "Large Cap": "#22c55e",
  "Mid Cap": "#22c55e",
  "Small Cap": "#22c55e",
  Unclassified: "#22c55e",
};

function formatCrore(value, decimals = 2) {
  return `₹${(Number(value || 0) / 10000000).toFixed(decimals)} Cr`;
}

function formatPercentage(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

export default function MTFCapNetValueChart({ data }) {
  const chartData = (Array.isArray(data) ? data : [])
    .map((item) => ({
      cap_category: item?.cap_category || "Unclassified",
      net_value: Number(item?.net_value || 0),
      symbols: Number(item?.symbols || 0),
    }))
    .filter((item) => item.net_value !== 0);

  /*
   * Net Value can be negative.
   *
   * For the percentage split we use ABS(Net Value), so:
   *
   * Large Cap     -₹26.18 Cr  -> 69.7%
   * Mid Cap        -₹8.43 Cr  -> 22.5%
   * Small Cap      -₹2.20 Cr  ->  5.9%
   * Unclassified   -₹0.73 Cr  ->  1.9%
   *
   * This represents each category's contribution to
   * the total Net Value exposure regardless of sign.
   */
  const totalAbsoluteNetValue = chartData.reduce(
    (sum, item) => sum + Math.abs(item.net_value),
    0,
  );

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Market Cap
        </Typography>

        {chartData.length === 0 ? (
          <Typography
            variant="body2"
            sx={{
              height: 340,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "text.secondary",
            }}
          >
            No net value data available.
          </Typography>
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{
                top: 10,
                right: 110,
                left: 20,
                bottom: 10,
              }}
              barCategoryGap="22%"
            >
              <CartesianGrid
                strokeDasharray="3 3"
                opacity={0.2}
              />

              <XAxis
                type="number"
                tickFormatter={(value) =>
                  formatCrore(value, 1)
                }
              />

              <YAxis
                type="category"
                dataKey="cap_category"
                width={110}
              />

              <Tooltip
                formatter={(value, name) => {
                  if (name === "Net Value") {
                    return [
                      formatCrore(value),
                      "Net Value",
                    ];
                  }

                  return [value, name];
                }}
                labelFormatter={(label) => {
                  const item = chartData.find(
                    (row) =>
                      row.cap_category === label,
                  );

                  if (!item) {
                    return label;
                  }

                  return `${label} — ${item.symbols} Symbols`;
                }}
              />

              <Bar
                dataKey="net_value"
                name="Net Value"
                radius={[0, 6, 6, 0]}
                minPointSize={4}
              >
                {chartData.map((entry) => (
                  <Cell
                    key={`net-value-${entry.cap_category}`}
                    fill={
                      CATEGORY_COLORS[
                        entry.cap_category
                      ] ||
                      CATEGORY_COLORS.Unclassified
                    }
                  />
                ))}

                <LabelList
                  dataKey="net_value"
                  position="insideRight"
                  formatter={(value) => {
                    const absoluteValue =
                      Math.abs(Number(value || 0));

                    const percentage =
                      totalAbsoluteNetValue > 0
                        ? (absoluteValue /
                            totalAbsoluteNetValue) *
                          100
                        : 0;

                    return `${formatCrore(
                      value,
                    )} (${formatPercentage(
                      percentage,
                    )})`;
                  }}
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}