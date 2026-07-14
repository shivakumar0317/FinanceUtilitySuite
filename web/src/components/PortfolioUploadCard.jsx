import { CloudUpload } from "@mui/icons-material";
import {
  Alert,
  Button,
  Card,
  CardContent,
  Stack,
  Typography,
} from "@mui/material";
import { useRef, useState } from "react";

export default function PortfolioUploadCard({
  onUpload,
  uploading,
  error,
}) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState("");

  const selectFile = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setFileName(file.name);
    onUpload(file);
  };

  return (
    <Card>
      <CardContent>
        <Stack spacing={2} alignItems="flex-start">
          <div>
            <Typography variant="h6" fontWeight={700}>
              Upload Portfolio
            </Typography>
            <Typography color="text.secondary">
              Required columns: SYMBOL, QTY, AVG_PRICE
            </Typography>
          </div>

          {error && (
            <Alert severity="error" sx={{ width: "100%" }}>
              {error}
            </Alert>
          )}

          {fileName && (
            <Typography color="text.secondary">
              Selected: {fileName}
            </Typography>
          )}

          <input
            ref={inputRef}
            hidden
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={selectFile}
          />

          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            disabled={uploading}
            onClick={() => inputRef.current?.click()}
          >
            {uploading
              ? "Uploading and calculating..."
              : "Choose Excel / CSV"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
