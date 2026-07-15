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

export default function MTFMarginDistributionChart({ data }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Margin Distribution
        </Typography>

        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              opacity={0.2}
            />
            <XAxis
              dataKey="range"
              angle={-20}
              textAnchor="end"
              height={65}
            />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="clients"
              name="Clients"
              fill="#3b82f6"
              radius={[5, 5, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
