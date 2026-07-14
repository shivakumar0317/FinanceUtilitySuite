import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "./ChartCard";
export default function PortfolioPerformanceChart({ data }) {
  return <ChartCard title="Portfolio Performance"><ResponsiveContainer width="100%" height={340}><LineChart data={data}><CartesianGrid strokeDasharray="3 3" opacity={0.2}/><XAxis dataKey="date" minTickGap={35}/><YAxis/><Tooltip/><Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2.5} dot={false}/></LineChart></ResponsiveContainer></ChartCard>;
}
