import {
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

export default function StockScoreCards({ analysis }) {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4 }}>
        <Card sx={{ height: "100%" }}>
          <CardContent>
            <Typography color="text.secondary">Investment Score</Typography>
            <Typography variant="h3" fontWeight={800} mt={1}>
              {analysis.investment_score}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={analysis.investment_score}
              sx={{ mt: 2, height: 9, borderRadius: 5 }}
            />
            <Typography mt={2}>{analysis.star_rating}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Card sx={{ height: "100%" }}>
          <CardContent>
            <Typography color="text.secondary">Risk Score</Typography>
            <Typography variant="h3" fontWeight={800} mt={1}>
              {analysis.risk_score}
            </Typography>
            <LinearProgress
              variant="determinate"
              color="error"
              value={analysis.risk_score}
              sx={{ mt: 2, height: 9, borderRadius: 5 }}
            />
            <Typography mt={2}>Risk Level: {analysis.risk_level}</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid size={{ xs: 12, md: 4 }}>
        <Card sx={{ height: "100%" }}>
          <CardContent>
            <Typography color="text.secondary">Recommendation</Typography>
            <Typography variant="h3" fontWeight={800} mt={1}>
              {analysis.recommendation}
            </Typography>
            <Stack spacing={0.75} mt={2}>
              {analysis.reasons.slice(0, 3).map((reason) => (
                <Typography
                  color="text.secondary"
                  variant="body2"
                  key={reason}
                >
                  • {reason}
                </Typography>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
