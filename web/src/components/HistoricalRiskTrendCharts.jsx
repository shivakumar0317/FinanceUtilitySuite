import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const formatINR = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "INR 0.00";
  }

  return `INR ${Number(value).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const formatNumber = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "0.00";
  }

  return Number(value).toFixed(2);
};

const ChartCard = ({ title, subtitle, children }) => {
  return (
    <div
      style={{
        background: "#111827",
        border: "1px solid #273244",
        borderRadius: "20px",
        padding: "20px",
        minHeight: "390px",
      }}
    >
      <div style={{ marginBottom: "18px" }}>
        <h3
          style={{
            margin: 0,
            fontSize: "18px",
            fontWeight: 700,
            color: "#f8fafc",
          }}
        >
          {title}
        </h3>

        <p
          style={{
            margin: "6px 0 0",
            color: "#94a3b8",
            fontSize: "13px",
          }}
        >
          {subtitle}
        </p>
      </div>

      <div style={{ width: "100%", height: "300px" }}>
        {children}
      </div>
    </div>
  );
};

const HistoricalRiskTrendCharts = ({ snapshots = [] }) => {
  const chartData = useMemo(() => {
    return [...snapshots]
      .sort(
        (a, b) =>
          new Date(a.business_date) - new Date(b.business_date)
      )
      .map((snapshot) => ({
        date: snapshot.business_date,

        riskScore: Number(snapshot.risk_score ?? 0),

        exposure: Number(snapshot.total_exposure ?? 0),

        mtm: Number(snapshot.total_mtm ?? 0),

        marginUtilization: Number(
          snapshot.margin_utilization ?? 0
        ),

        diversification: Number(
          snapshot.diversification_score ?? 0
        ),

        health: snapshot.health ?? "Unknown",
      }));
  }, [snapshots]);

  if (!chartData.length) {
    return (
      <div
        style={{
          background: "#111827",
          border: "1px solid #273244",
          borderRadius: "20px",
          padding: "30px",
          color: "#94a3b8",
          textAlign: "center",
        }}
      >
        No historical snapshot data available for charts.
      </div>
    );
  }

  return (
    <section style={{ marginTop: "28px" }}>
      <div style={{ marginBottom: "20px" }}>
        <h2
          style={{
            margin: 0,
            color: "#f8fafc",
            fontSize: "24px",
            fontWeight: 800,
          }}
        >
          Historical Risk Trends
        </h2>

        <p
          style={{
            marginTop: "6px",
            color: "#94a3b8",
            fontSize: "14px",
          }}
        >
          Portfolio risk, exposure, margin utilization and
          diversification across historical snapshots.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
          gap: "20px",
        }}
      >
        {/* ------------------------------------------------ */}
        {/* Risk Score */}
        {/* ------------------------------------------------ */}

        <ChartCard
          title="Risk Score Trend"
          subtitle="Lower risk score indicates improving portfolio risk."
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#273244"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "10px",
                  color: "#f8fafc",
                }}
                formatter={(value) => [
                  formatNumber(value),
                  "Risk Score",
                ]}
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="riskScore"
                name="Risk Score"
                stroke="#f59e0b"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ------------------------------------------------ */}
        {/* Exposure + MTM */}
        {/* ------------------------------------------------ */}

        <ChartCard
          title="Exposure & MTM Trend"
          subtitle="Historical portfolio exposure and mark-to-market."
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#273244"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) =>
                  `${(value / 10000000).toFixed(1)}Cr`
                }
              />

              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "10px",
                  color: "#f8fafc",
                }}
                formatter={(value, name) => [
                  formatINR(value),
                  name,
                ]}
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="exposure"
                name="Total Exposure"
                stroke="#38bdf8"
                strokeWidth={3}
                dot={{ r: 3 }}
              />

              <Line
                type="monotone"
                dataKey="mtm"
                name="Total MTM"
                stroke="#ef4444"
                strokeWidth={3}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* ------------------------------------------------ */}
        {/* Margin + Diversification */}
        {/* ------------------------------------------------ */}

        <ChartCard
          title="Margin Utilization & Diversification"
          subtitle="Portfolio leverage and diversification quality."
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#273244"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <YAxis
                stroke="#94a3b8"
                tick={{ fontSize: 11 }}
              />

              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "10px",
                  color: "#f8fafc",
                }}
                formatter={(value, name) => [
                  `${formatNumber(value)}${
                    name === "Margin Utilization" ? "%" : ""
                  }`,
                  name,
                ]}
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="marginUtilization"
                name="Margin Utilization"
                stroke="#a855f7"
                strokeWidth={3}
                dot={{ r: 3 }}
              />

              <Line
                type="monotone"
                dataKey="diversification"
                name="Diversification"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </section>
  );
};

export default HistoricalRiskTrendCharts;