from core.services.snapshot_manager_service import SnapshotManagerService

service = SnapshotManagerService()
items = service.list_metadata()
summary = service.summary(items)

print("Snapshots:", summary["snapshots"])
print("Records:", summary["records"])
print("Exposure:", service.format_indian_compact(summary["exposure"]))
print("MTM:", service.format_indian_compact(summary["mtm"]))

if items:
    status, level = service.health_status(items[0])
    print("Latest status:", status, level)
    print("Search result count:", len(service.list_metadata(status)))

print("Sprint 3.2.2 service test passed.")
