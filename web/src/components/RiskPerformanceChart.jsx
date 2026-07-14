import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
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

export default function RiskPerformanceChart({ data }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Portfolio vs NIFTY 50
        </Typography>

        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />
            <XAxis dataKey="date" minTickGap={35} />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="portfolio"
              name="Portfolio"
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="benchmark"
              name="NIFTY 50"
              stroke="#22c55e"
              strokeWidth={2.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
