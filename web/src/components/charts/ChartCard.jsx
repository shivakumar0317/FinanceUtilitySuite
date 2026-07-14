import { Card, CardContent, Typography } from "@mui/material";

export default function ChartCard({ title, children }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>{title}</Typography>
        {children}
      </CardContent>
    </Card>
  );
}
