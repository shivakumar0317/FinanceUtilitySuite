from core.services.snapshot_manager_service import SnapshotManagerService

service = SnapshotManagerService()
items = service.list_metadata()
summary = service.summary(items)
print(f"Snapshots: {summary['snapshots']}")
if items:
    print("Latest:", items[0].snapshot_id)
    print("Health:", service.health_status(items[0])[0])
    data = service.load_snapshot(items[0].snapshot_id)
    print("Rows:", len(data))
print("Professional Snapshot Manager service test passed.")
