import {
  CartesianGrid,
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

export default function PortfolioLiveChart({
  performance,
}) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Portfolio Performance
        </Typography>
        <ResponsiveContainer width="100%" height={380}>
          <LineChart data={performance}>
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />
            <XAxis dataKey="date" minTickGap={35} />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
