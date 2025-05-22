# Falcoria CLI

Falcoria CLI is the command-line interface for interacting with the Falcoria system. It allows users to configure, trigger, and control distributed scans across the infrastructure.

## Features

- Initiates scans via Tasker using HTTP APIs.
- Supports multiple import modes: `insert`, `append`, `replace`, `update`.
- Accepts YAML scan configurations and flexible input targets.
- Enables port sharding and phase-based scan control.
- Tracks scan progress and supports result download.
- Designed for fast, modular interactions with the scanning backend.

## Usage

Run scans and manage projects using:

```bash
python falcli.py <command> [options]
```

Available commands include:
- `scan`: Start a scan using provided config and targets.
- `status`: Check the scan status.
- `stop`: Stop a scan by project ID.
- `import`: Load external results using specific import mode.
- `download`: Retrieve scan reports from the backend.

## License

MIT
