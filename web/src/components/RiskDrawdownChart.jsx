import {
  Area,
  AreaChart,
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

export default function RiskDrawdownChart({ data }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Portfolio Drawdown
        </Typography>

        <ResponsiveContainer width="100%" height={360}>
          <AreaChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />
            <XAxis dataKey="date" minTickGap={35} />
            <YAxis domain={["auto", 0]} />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="drawdown"
              name="Drawdown %"
              stroke="#ef4444"
              fill="#ef4444"
              fillOpacity={0.22}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
