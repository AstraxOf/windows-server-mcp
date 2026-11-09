# Security Model

This MCP server is a local Windows automation surface. It can be extremely useful, and it can also be dangerous if connected to an assistant or workflow you do not trust.

## Trust Boundary

The server runs with the privileges of the process that launches it. If you start it from an Administrator terminal, many tools can perform Administrator-level changes.

Do not expose this server over a network transport without authentication, authorization, logging, and a tool allowlist.

## Tool Risk Classes

Read-only tools inspect state and should be the default starting point:

- `disk_cleanup_report`
- `get_security_status`
- `get_windows_update_status`
- `list_scheduled_tasks`
- `get_process_details`
- `get_smart_disk_health`
- `list_problem_devices`

Safer mutation tools default to previews or reversible operations:

- `safe_delete_to_recycle_bin`
- `safe_delete_many_to_recycle_bin`
- `safe_delete_by_pattern` with `dry_run=true`
- `uninstall_software` with `dry_run=true`
- `install_windows_updates` with `dry_run=true`
- `clear_print_queue` with `dry_run=true`

Sharp tools can cause immediate system changes:

- `execute_powershell`
- `manage_registry` write/delete actions
- `delete_file`
- `delete_files_by_extension`
- `kill_process`
- `manage_service`
- `install_windows_updates` with `dry_run=false`
- `install_driver_updates` with `dry_run=false`
- `uninstall_software` with `dry_run=false`
- `empty_recycle_bin`

## Recommended Client Policy

- Require confirmation before invoking sharp tools.
- Prefer dry-run tools before mutation.
- Use a per-tool allowlist for untrusted or semi-trusted assistants.
- Avoid starting the server as Administrator unless the task needs it.
- Keep local logs of destructive actions when possible.
- Review paths carefully before any file deletion or archiving operation.

## Known Limitations

- Some Windows APIs require Administrator privileges.
- Some hardware data depends on vendor tools or optional Windows providers.
- File handle discovery may miss handles hidden from the current user.
- Windows Update and driver installation behavior depends on local policy.
