# Optional upload-history UI integration

The backend persistence works without frontend changes. Existing Portfolio Live
and MTF pages will automatically restore the latest active upload after FastAPI
restarts.

To display upload history, import:

```jsx
import UploadHistoryTable from "../components/UploadHistoryTable";
```

## Portfolio Live endpoints

```text
GET    /api/portfolio-live/uploads
POST   /api/portfolio-live/uploads/{upload_id}/activate
DELETE /api/portfolio-live/uploads/{upload_id}
```

## MTF endpoints

```text
GET    /api/mtf/uploads
POST   /api/mtf/uploads/{upload_id}/activate
DELETE /api/mtf/uploads/{upload_id}
```

After upload, activate, or delete, invalidate the corresponding upload-history
query and refresh the dashboard query.
