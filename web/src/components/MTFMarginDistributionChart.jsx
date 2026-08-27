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

const BAR_COLORS = [
  "#3b82f6",
  "#3b82f6",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
];

function CustomTooltip({ active, payload, totalClients }) {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const clients = Number(payload[0]?.value || 0);

  const percentage =
    totalClients > 0
      ? (clients / totalClients) * 100
      : 0;

  return (
    <div
      style={{
        background: "#000000",
        border: "1px solid #334155",
        borderRadius: "10px",
        padding: "12px 16px",
        boxShadow:
          "0 4px 16px rgba(0, 0, 0, 0.45)",
      }}
    >
      <div
        style={{
          color: "#3b82f6",
          fontSize: "14px",
          fontWeight: 700,
        }}
      >
        {percentage.toFixed(1)}% of clients
      </div>
    </div>
  );
}

export default function MTFMarginDistributionChart({
  data,
}) {
  const chartData = Array.isArray(data)
    ? data.map((item, index) => ({
        ...item,
        clients: Number(item?.clients || 0),
        bar_color:
          BAR_COLORS[index] || "#3b82f6",
      }))
    : [];

  const totalClients = chartData.reduce(
    (sum, item) => sum + item.clients,
    0,
  );

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography
          variant="h6"
          fontWeight={700}
          mb={2}
        >
          Margin Distribution
        </Typography>

        <ResponsiveContainer
          width="100%"
          height={340}
        >
          <BarChart
            data={chartData}
            margin={{
              top: 25,
              right: 20,
              left: 20,
              bottom: 10,
            }}
          >
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

            <Tooltip
              content={
                <CustomTooltip
                  totalClients={totalClients}
                />
              }
            />

            <Bar
              dataKey="clients"
              name="Clients"
              radius={[5, 5, 0, 0]}
              minPointSize={4}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`bar-${entry.range}`}
                  fill={BAR_COLORS[index] || "#3b82f6"}
                />
              ))}

              <LabelList
                dataKey="clients"
                position="top"
                formatter={(value) => {
                  const clients = Number(
                    value || 0,
                  );

                  return `${clients} ${
                    clients === 1
                      ? "Client"
                      : "Clients"
                  }`;
                }}
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  fill: "#ffffff",
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}