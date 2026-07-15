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

export default function MTFUploadCard({
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
              Upload MTF File
            </Typography>
            <Typography color="text.secondary">
              Upload Excel or CSV containing AccountId, Symbol,
              NetValue, MarkToMarket, BUY VALUE, MTF VAR and
              MTF MARGIN.
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
              : "Choose MTF Excel / CSV"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
