import {
  AccountBalance,
  Assessment,
  Dashboard,
  History,
  InfoOutlined,
  Insights,
  Security,
  ShowChart,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Stack,
  Typography,
} from "@mui/material";

const modules = [
  {
    title: "Dashboard",
    description: "Central overview of the Finance Utility Suite.",
    icon: <Dashboard />,
  },
  {
    title: "Portfolio Analytics",
    description: "Portfolio monitoring, performance and analysis.",
    icon: <AccountBalance />,
  },
  {
    title: "Market & Stock Analysis",
    description: "Market monitoring, watchlists and stock analysis.",
    icon: <ShowChart />,
  },
  {
    title: "Risk Analytics",
    description: "Portfolio-level risk analysis and monitoring.",
    icon: <Security />,
  },
  {
    title: "MTF Analytics",
    description: "MTF exposure, margin and concentration analysis.",
    icon: <Assessment />,
  },
  {
    title: "Historical Risk Analytics",
    description:
      "Historical Enterprise RMS snapshots, comparisons and risk trends.",
    icon: <History />,
  },
  {
    title: "Enterprise RMS",
    description:
      "Enterprise-level exposure, concentration and portfolio risk monitoring.",
    icon: <Insights />,
  },
];

function ModuleCard({ title, description, icon }) {
  return (
    <Card
      variant="outlined"
      sx={{
        height: "100%",
        borderRadius: 2,
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: 42,
              height: 42,
              borderRadius: 2,
              bgcolor: "action.hover",
              color: "primary.main",
            }}
          >
            {icon}
          </Box>

          <Typography
            variant="h6"
            fontWeight={800}
          >
            {title}
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
          >
            {description}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default function AboutPage() {
  return (
    <Stack spacing={3}>
      {/* Header */}
      <Box>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1.5}
          alignItems={{ sm: "center" }}
        >
          <Typography
            variant="h4"
            fontWeight={800}
          >
            About Finance Utility Suite
          </Typography>

          <Chip
            icon={<InfoOutlined />}
            label="About"
            color="primary"
            variant="outlined"
          />
        </Stack>

        <Typography
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          A unified platform for financial analysis, portfolio
          monitoring, market intelligence and enterprise risk
          management.
        </Typography>
      </Box>

      {/* Product Overview */}
      <Card>
        <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
          <Stack spacing={2}>
            <Typography
              variant="h5"
              fontWeight={800}
            >
              Finance Utility Suite
            </Typography>

            <Typography
              color="text.secondary"
              sx={{ maxWidth: 900 }}
            >
              Finance Utility Suite brings portfolio analytics,
              market monitoring, MTF analysis and enterprise risk
              management into a single application. The platform is
              designed to provide a clear and practical view of
              financial exposure, risk and portfolio activity.
            </Typography>

            <Divider />

            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
            >
              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Platform
                </Typography>

                <Typography fontWeight={700}>
                  Finance Utility Suite
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Risk Management
                </Typography>

                <Typography fontWeight={700}>
                  Enterprise RMS
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  MTF
                </Typography>

                <Typography fontWeight={700}>
                  Exposure & Concentration Analytics
                </Typography>
              </Box>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {/* Modules */}
      <Box>
        <Typography
          variant="h5"
          fontWeight={800}
          gutterBottom
        >
          Platform Modules
        </Typography>

        <Typography
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Major capabilities currently available in the suite.
        </Typography>

        <Grid container spacing={2}>
          {modules.map((module) => (
            <Grid
              item
              xs={12}
              sm={6}
              md={4}
              key={module.title}
            >
              <ModuleCard {...module} />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* RMS */}
      <Card>
        <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
          <Stack spacing={2}>
            <Typography
              variant="h5"
              fontWeight={800}
            >
              Enterprise Risk Management
            </Typography>

            <Typography color="text.secondary">
              The Enterprise RMS layer provides an enterprise-level
              view of portfolio exposure and risk, including MTF
              concentration analysis and historical risk monitoring.
            </Typography>

            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={1}
              flexWrap="wrap"
              useFlexGap
            >
              <Chip label="Exposure Monitoring" />
              <Chip label="MTM Monitoring" />
              <Chip label="Concentration Risk" />
              <Chip label="Historical Risk" />
              <Chip label="Risk Trends" />
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {/* Footer */}
      <Box
        sx={{
          textAlign: "center",
          py: 2,
        }}
      >
        <Typography
          variant="body2"
          color="text.secondary"
        >
          Finance Utility Suite
        </Typography>

        <Typography
          variant="caption"
          color="text.secondary"
        >
          Financial analytics • Portfolio monitoring • Risk management
        </Typography>
      </Box>
    </Stack>
  );
}