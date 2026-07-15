import {
  Bar,
  BarChart,
  CartesianGrid,
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

export default function MTFSymbolExposureChart({ data }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Symbol Exposure
        </Typography>

        <ResponsiveContainer width="100%" height={340}>
          <BarChart
            data={(data || []).slice(0, 12)}
            layout="vertical"
          >
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />
            <XAxis type="number" />
            <YAxis
              dataKey="symbol"
              type="category"
              width={95}
            />
            <Tooltip />
            <Bar
              dataKey="buy_value"
              name="Buy Value"
              fill="#22c55e"
              radius={[0, 5, 5, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
