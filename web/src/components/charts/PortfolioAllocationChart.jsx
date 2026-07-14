import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import ChartCard from "./ChartCard";
const colors=["#3b82f6","#22c55e","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#ec4899","#84cc16"];
export default function PortfolioAllocationChart({ data }) {
  return <ChartCard title="Portfolio Allocation"><ResponsiveContainer width="100%" height={320}><PieChart><Pie data={data} dataKey="value" nameKey="name" outerRadius={105} label>{data.map((entry,index)=><Cell key={`${entry.name}-${index}`} fill={colors[index%colors.length]} />)}</Pie><Tooltip/><Legend/></PieChart></ResponsiveContainer></ChartCard>;
}
