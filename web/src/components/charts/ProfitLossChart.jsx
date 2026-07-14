import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "./ChartCard";
export default function ProfitLossChart({ data }) {
  return <ChartCard title="P/L by Stock"><ResponsiveContainer width="100%" height={320}><BarChart data={data.slice(0,12)}><CartesianGrid strokeDasharray="3 3" opacity={0.2}/><XAxis dataKey="symbol" angle={-35} textAnchor="end" height={70}/><YAxis/><Tooltip/><Bar dataKey="profit_loss" fill="#3b82f6" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></ChartCard>;
}
