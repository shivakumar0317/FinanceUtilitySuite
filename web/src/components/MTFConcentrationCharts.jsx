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
  Grid,
  Typography,
} from "@mui/material";

const chartLabelStyle = {
  fontSize: 16,
  fontWeight: 700,
};

function ChartCard({
  title,
  subtitle,
  children,
}) {
  return (
    <Card
      sx={{
        height: "100%",
        borderRadius: 4,
        backgroundColor: "background.paper",
        border: "1px solid",
        borderColor: "divider",
        overflow: "hidden",
      }}
    >
      <CardContent
        sx={{
          p: 3,
          "&:last-child": {
            pb: 3,
          },
        }}
      >
        <Typography
          variant="h6"
          fontWeight={800}
          sx={{
            mb: 0.5,
          }}
        >
          {title}
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
          }}
        >
          {subtitle}
        </Typography>

        <ResponsiveContainer
          width="100%"
          height={330}
        >
          {children}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function ValueLabel(props) {
  const {
    x,
    y,
    width,
    value,
    fill = "#64b5f6",
  } = props;

  return (
    <text
      x={x + width / 2}
      y={y - 10}
      textAnchor="middle"
      fill={fill}
      style={chartLabelStyle}
    >
      {value}
    </text>
  );
}

function RiskValueLabel(props) {
  const {
    x,
    y,
    width,
    value,
    fill,
  } = props;

  return (
    <text
      x={x + width / 2}
      y={y - 10}
      textAnchor="middle"
      fill={fill}
      style={chartLabelStyle}
    >
      {value}
    </text>
  );
}

export default function MTFConcentrationCharts({
  distribution,
  riskDistribution,
}) {
  const concentrationData =
    distribution || [];

  const riskData =
    riskDistribution || [];

  return (
    <Grid
      container
      spacing={2}
    >
      {/* Client Concentration */}
      <Grid
        size={{
          xs: 12,
          lg: 6,
        }}
      >
        <ChartCard
          title="Client Concentration"
          subtitle="Clients grouped by number of stock holdings"
        >
          <BarChart
            data={concentrationData}
            margin={{
              top: 30,
              right: 10,
              left: 0,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              opacity={0.25}
            />

            <XAxis
              dataKey="category"
              tickLine={false}
              axisLine={{
                opacity: 0.35,
              }}
            />

            <YAxis
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              cursor={{
                fill: "rgba(255,255,255,0.04)",
              }}
              contentStyle={{
                backgroundColor: "#101827",
                border: "1px solid #334155",
                borderRadius: 10,
                color: "#fff",
              }}
            />

            <Bar
              dataKey="clients"
              name="Clients"
              fill="#64b5f6"
              radius={[
                8,
                8,
                0,
                0,
              ]}
              maxBarSize={110}
            >
              <LabelList
                dataKey="clients"
                content={
                  <ValueLabel
                    fill="#64b5f6"
                  />
                }
              />
            </Bar>
          </BarChart>
        </ChartCard>
      </Grid>

      {/* Risk Distribution */}
      <Grid
        size={{
          xs: 12,
          lg: 6,
        }}
      >
        <ChartCard
          title="Risk Distribution"
          subtitle="Clients grouped by concentration risk level"
        >
          <BarChart
            data={riskData}
            margin={{
              top: 30,
              right: 10,
              left: 0,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              opacity={0.25}
            />

            <XAxis
              dataKey="risk_level"
              tickLine={false}
              axisLine={{
                opacity: 0.35,
              }}
            />

            <YAxis
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              cursor={{
                fill: "rgba(255,255,255,0.04)",
              }}
              contentStyle={{
                backgroundColor: "#101827",
                border: "1px solid #334155",
                borderRadius: 10,
              }}
              labelStyle={{
                color: "#ffffff",
                fontWeight: 700,
              }}
              itemStyle={{
                color: "#ffffff",
                fontWeight: 600,
              }}
            />

            <Bar
              dataKey="clients"
              name="Clients"
              radius={[
                8,
                8,
                0,
                0,
              ]}
              maxBarSize={100}
            >
              {riskData.map(
                (entry, index) => {
                  const level =
                    String(
                      entry.risk_level ||
                        "",
                    ).toLowerCase();

                  let fill =
                    "#22c55e";

                  if (
                    level ===
                    "critical"
                  ) {
                    fill = "#ef4444";
                  } else if (
                    level === "high"
                  ) {
                    fill = "#f59e0b";
                  } else if (
                    level ===
                    "medium"
                  ) {
                    fill = "#eab308";
                  }

                  return (
                    <Cell
                      key={`risk-cell-${index}`}
                      fill={fill}
                    />
                  );
                },
              )}

              <LabelList
                dataKey="clients"
                content={(props) => {
                  const level =
                    String(
                      props?.payload
                        ?.risk_level ||
                        "",
                    ).toLowerCase();

                  let fill =
                    "#22c55e";

                  if (
                    level ===
                    "critical"
                  ) {
                    fill = "#ef4444";
                  } else if (
                    level === "high"
                  ) {
                    fill = "#f59e0b";
                  } else if (
                    level ===
                    "medium"
                  ) {
                    fill = "#eab308";
                  }

                  return (
                    <RiskValueLabel
                      {...props}
                      fill={fill}
                    />
                  );
                }}
              />
            </Bar>
          </BarChart>
        </ChartCard>
      </Grid>
    </Grid>
  );
}