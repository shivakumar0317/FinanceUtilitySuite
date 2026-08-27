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
  "Large Cap": "#3b82f6",
  "Mid Cap": "#22c55e",
  "Small Cap": "#f59e0b",
  Unclassified: "#94a3b8",
};

function formatCrore(value, decimals = 2) {
  return `₹${(
    Number(value || 0) / 10000000
  ).toFixed(decimals)} Cr`;
}

function formatPercentage(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

export default function MTFSymbolExposureChart({
  data,
}) {
  /*
   * Market Cap split is based on NETVALUE.
   */
  const chartData = (
    Array.isArray(data) ? data : []
  )
    .map((item) => ({
      cap_category:
        item?.cap_category ||
        "Unclassified",

      net_value: Number(
        item?.net_value || 0,
      ),

      symbols: Number(
        item?.symbols || 0,
      ),
    }))
    .filter(
      (item) => item.net_value !== 0,
    );

  /*
   * Net Value can be negative.
   *
   * ABS(Net Value) is used only for
   * percentage contribution.
   */
  const totalAbsoluteNetValue =
    chartData.reduce(
      (sum, item) =>
        sum +
        Math.abs(item.net_value),
      0,
    );

  const finalChartData =
    chartData.map((item) => ({
      ...item,

      net_value_percentage:
        totalAbsoluteNetValue > 0
          ? (Math.abs(item.net_value) /
              totalAbsoluteNetValue) *
            100
          : 0,
    }));

  /*
   * Custom Net Value label.
   *
   * Creates the rounded label style
   * shown in the approved reference.
   */
  const renderNetValueLabel = ({
  x,
  y,
  width,
  height,
  index,
}) => {
  const item = finalChartData[index];

  if (!item) {
    return null;
  }

  const value = Number(item.net_value || 0);

  const percentage = Number(
    item.net_value_percentage || 0,
  );

  const label = `${formatCrore(
    value,
  )} (${formatPercentage(
    percentage,
  )})`;

  const labelHeight = 26;
  const paddingX = 8;

  const estimatedTextWidth = Math.max(
    105,
    label.length * 6.5,
  );

  /*
   * Recharts gives:
   *
   * positive bar:
   * x = left edge
   *
   * negative bar:
   * x = right edge
   * width = negative
   *
   * Therefore calculate the actual
   * left edge ourselves.
   */
  const barLeft =
    width < 0 ? x + width : x;

  const barWidth = Math.abs(width);

  /*
   * Large enough bar:
   * put the label inside the bar.
   */
  if (
    barWidth >=
    estimatedTextWidth + 20
  ) {
    return (
      <g>
        <rect
          x={barLeft + 6}
          y={
            y +
            height / 2 -
            labelHeight / 2
          }
          width={estimatedTextWidth}
          height={labelHeight}
          rx={6}
          ry={6}
          fill="rgba(15, 23, 42, 0.72)"
          stroke="rgba(255, 255, 255, 0.18)"
        />

        <text
          x={
            barLeft +
            6 +
            paddingX
          }
          y={
            y +
            height / 2
          }
          textAnchor="start"
          dominantBaseline="middle"
          fill="#ffffff"
          fontSize={12}
          fontWeight={600}
        >
          {label}
        </text>
      </g>
    );
  }

  /*
   * Small bars:
   * put label inside when possible.
   *
   * For negative bars, align from
   * the right side so it doesn't escape
   * the chart boundary.
   */
  if (width < 0) {
    return (
      <text
        x={barLeft - 8}
        y={y + height / 2}
        textAnchor="end"
        dominantBaseline="middle"
        fill="#ffffff"
        fontSize={11}
        fontWeight={600}
      >
        {label}
      </text>
    );
  }

  return (
    <text
      x={x + width + 8}
      y={y + height / 2}
      textAnchor="start"
      dominantBaseline="middle"
      fill="#ffffff"
      fontSize={11}
      fontWeight={600}
    >
      {label}
    </text>
  );
};

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography
          variant="h6"
          fontWeight={700}
          mb={2}
        >
          Market Cap
        </Typography>

        {finalChartData.length === 0 ? (
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
          <ResponsiveContainer
            width="100%"
            height={340}
          >
            <BarChart
              data={finalChartData}
              layout="vertical"
              margin={{
                top: 10,
                right: 35,
                left: 20,
                bottom: 25,
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
                label={{
                  value: "Net Value",
                  position: "insideBottom",
                  offset: -15,
                  fill: "#94a3b8",
                }}
              />

              <YAxis
                type="category"
                dataKey="cap_category"
                width={110}
              />

              <Tooltip
                contentStyle={{
                  backgroundColor:
                    "#0f172a",
                  border:
                    "1px solid #334155",
                  borderRadius: 8,
                  color: "#ffffff",
                }}
                labelStyle={{
                  color: "#ffffff",
                  fontWeight: 600,
                }}
                itemStyle={{
                  color: "#ffffff",
                }}
                formatter={(value, name) => {
                  if (
                    name === "Net Value"
                  ) {
                    return [
                      formatCrore(value),
                      "Net Value",
                    ];
                  }

                  return [
                    value,
                    name,
                  ];
                }}
                labelFormatter={(label) => {
                  const item =
                    finalChartData.find(
                      (row) =>
                        row.cap_category ===
                        label,
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
                radius={[
                  6,
                  6,
                  6,
                  6,
                ]}
                minPointSize={4}
              >
                {finalChartData.map(
                  (entry) => (
                    <Cell
                      key={`net-value-${entry.cap_category}`}
                      fill={
                        CATEGORY_COLORS[
                          entry.cap_category
                        ] ||
                        CATEGORY_COLORS.Unclassified
                      }
                    />
                  ),
                )}

                <LabelList
                  dataKey="net_value"
                  content={
                    renderNetValueLabel
                  }
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}