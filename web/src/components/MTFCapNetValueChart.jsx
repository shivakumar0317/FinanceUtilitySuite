import {
  Bar,
  BarChart,
  CartesianGrid,
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

export default function MTFCapNetValueChart({ data }) {
  const chartData = (data || []).map((item) => ({
    cap_category: item.cap_category,
    net_value: Number(item.net_value || 0),
    symbols: Number(item.symbols || 0),
  }));

  const totalNetValue = chartData.reduce(
    (sum, item) => sum + item.net_value,
    0,
  );

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Market Cap
        </Typography>

        <ResponsiveContainer width="100%" height={340}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{
              top: 5,
              right: 90,
              left: 10,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />

            <XAxis
              type="number"
              tickFormatter={(value) =>
                `₹${(value / 10000000).toFixed(1)} Cr`
              }
            />

            <YAxis
              dataKey="cap_category"
              type="category"
              width={130}
            />

            <Tooltip
              formatter={(value) => [
                `₹${(Number(value) / 10000000).toFixed(2)} Cr`,
                "Net Value",
              ]}
              labelFormatter={(label) => {
                const item = chartData.find(
                  (row) => row.cap_category === label,
                );

                return item
                  ? `${label} — ${item.symbols} Symbols`
                  : label;
              }}
            />

            <Bar
              dataKey="net_value"
              name="Net Value"
              fill="#22c55e"
              radius={[0, 5, 5, 0]}
            >
              <LabelList
                dataKey="net_value"
                position="insideLeft"
                formatter={(value) => {
                  const crore = Number(value) / 10000000;
                  const percent =
                    totalNetValue !== 0
                      ? (Number(value) / totalNetValue) * 100
                      : 0;

                  return `₹${crore.toFixed(2)} Cr (${percent.toFixed(1)}%)`;
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}