import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "./ChartCard";
export default function TopHoldingsChart({ data }) {
  return <ChartCard title="Top Holdings"><ResponsiveContainer width="100%" height={340}><BarChart data={data} layout="vertical"><CartesianGrid strokeDasharray="3 3" opacity={0.2}/><XAxis type="number"/><YAxis dataKey="symbol" type="category" width={90}/><Tooltip/><Bar dataKey="value" fill="#22c55e" radius={[0,5,5,0]}/></BarChart></ResponsiveContainer></ChartCard>;
}
