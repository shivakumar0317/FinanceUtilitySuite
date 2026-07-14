import { Refresh } from "@mui/icons-material";
import { Alert, Box, Button, CircularProgress, Grid, Stack, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import AnalyticsCards from "../components/AnalyticsCards";
import PortfolioAllocationChart from "../components/charts/PortfolioAllocationChart";
import PortfolioPerformanceChart from "../components/charts/PortfolioPerformanceChart";
import ProfitLossChart from "../components/charts/ProfitLossChart";
import TopHoldingsChart from "../components/charts/TopHoldingsChart";
import api from "../services/api";

export default function AnalyticsPage() {
  const analytics = useQuery({ queryKey:["analytics-dashboard"], queryFn:async()=> (await api.get("/api/analytics/dashboard")).data, refetchInterval:60000 });
  if (analytics.isLoading) return <Stack alignItems="center" py={10}><CircularProgress/></Stack>;
  return <Stack spacing={3}><Stack direction={{xs:"column",sm:"row"}} alignItems={{sm:"center"}} justifyContent="space-between" spacing={2}><Box><Typography variant="h4" fontWeight={800}>Analytics</Typography><Typography color="text.secondary">Live portfolio analytics refreshed every 60 seconds.</Typography></Box><Button variant="outlined" startIcon={<Refresh/>} onClick={()=>analytics.refetch()}>Refresh</Button></Stack>{analytics.isError&&<Alert severity="error">Unable to load analytics data.</Alert>}<AnalyticsCards summary={analytics.data?.summary}/><Grid container spacing={2}><Grid size={{xs:12,lg:6}}><PortfolioAllocationChart data={analytics.data?.allocation||[]}/></Grid><Grid size={{xs:12,lg:6}}><ProfitLossChart data={analytics.data?.profit_loss||[]}/></Grid><Grid size={{xs:12,lg:6}}><TopHoldingsChart data={analytics.data?.top_holdings||[]}/></Grid><Grid size={{xs:12,lg:6}}><PortfolioPerformanceChart data={analytics.data?.performance||[]}/></Grid></Grid></Stack>;
}
