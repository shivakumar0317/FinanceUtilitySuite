import { CheckCircle, Delete, Restore } from "@mui/icons-material";
import {
  Card,
  CardContent,
  Chip,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";

const dateTime = (value) =>
  value ? new Date(value).toLocaleString("en-IN") : "N/A";

export default function UploadHistoryTable({
  title = "Upload History",
  rows,
  onActivate,
  onDelete,
  busy,
}) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>
          {title}
        </Typography>

        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>File</TableCell>
                <TableCell align="right">Rows</TableCell>
                <TableCell>Uploaded</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.filename}</TableCell>
                  <TableCell align="right">{row.row_count}</TableCell>
                  <TableCell>{dateTime(row.created_at)}</TableCell>
                  <TableCell align="center">
                    {row.is_active ? (
                      <Chip
                        size="small"
                        color="success"
                        icon={<CheckCircle />}
                        label="Active"
                      />
                    ) : (
                      <Chip size="small" label="Archived" />
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      {!row.is_active && (
                        <Tooltip title="Activate this upload">
                          <span>
                            <IconButton
                              disabled={busy}
                              onClick={() => onActivate(row.id)}
                            >
                              <Restore />
                            </IconButton>
                          </span>
                        </Tooltip>
                      )}

                      <Tooltip title="Delete upload">
                        <span>
                          <IconButton
                            color="error"
                            disabled={busy}
                            onClick={() => onDelete(row.id)}
                          >
                            <Delete />
                          </IconButton>
                        </span>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No saved uploads.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
