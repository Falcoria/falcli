
# Falcoria CLI

**Falcoria CLI** is the command-line interface for interacting with the Falcoria system — a high-performance, distributed network scanning platform. It enables users to configure, trigger, and manage scans across infrastructure with power, precision, and flexibility.

---

## Features

- Initiates scans via Tasker using HTTP APIs
- Supports import modes: `insert`, `append`, `replace`, `update`
- Accepts YAML-based scan configurations and flexible target sources
- Enables port sharding and phase-based scan control
- Tracks scan progress with live status output
- Allows structured result download and CLI-based introspection
- Designed for fast, modular, and scalable integration

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Falcoria/falcli.git
cd falcli

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt
```

You're now ready to run the CLI using:

```bash
python falcli.py --help
```

---

## Configuration

Before running scans or importing data, you need to configure your local settings.

Edit the file:

```bash
./data/user_config.yaml
```

Set the following values:

```yaml
backend_base_url: <scanledger_url>
tasker_base_url: <tasker_url>      # Optional if you don't use scan functionality
token: <your_access_token>
```

This configuration allows the CLI to communicate with the Falcoria backend and (optionally) the Tasker API.

---

## Usage

Run scans and manage projects using:

```bash
python falcli.py <command> [options]
```

### Key Commands

- `project`: Create, list, and manage scanning projects and associated target IPs.
- `scan`: Launch scans, preview Nmap commands, check status, or stop ongoing scans.
- `import`: Import external scan results using one of the supported import modes (`insert`, `append`, `replace`, `update`).
- `config`: Set or view CLI settings and backend connection details.
- `workers`: View active worker nodes and their external IP addresses.
- `memory`: View or reset internal memory (e.g., last used project ID).

---

## Quick Start

### Fast Scan (One-liner)

Run your first scan in one command using a file of target hosts:

```bash
python3 falcli.py fast-scan --targets-file hosts.txt
[+] Project 'autoproj-bf470a30' created successfully (d9173423-5e02-47ee-922b-e88bc6223d27).
...
Saved to: scan_reports/d9173423-5e02-47ee-922b-e88bc6223d27_ips.xml
```

---

### Guided Workflow (Step-by-Step Control)

#### 1. Create a Project

```bash
python3 falcli.py project create example_project
[+] Project 'example_project' created successfully (271c56d6-7317-4013-a182-9def30881d21).
```

#### 2. Start a Scan

```bash
python3 falcli.py scan start --targets-file hosts.txt
[+] Scan started successfully for project 271c56d6-7317-4013-a182-9def30881d21
```

#### 3. Check Scan Status

```bash
python3 falcli.py scan status
[+] Scan status for project 271c56d6-7317-4013-a182-9def30881d21: 4
```

For interactive live status:

```bash
python3 falcli.py scan status -i
```

#### 4. Retrieve Scanned IPs

```bash
python3 falcli.py project ips get
```

#### 5. Download XML Report

```bash
python3 falcli.py project ips download
[+] Downloaded IPs report for project '271c56d6-7317-4013-a182-9def30881d21'.
Saved to: scan_reports/271c56d6-7317-4013-a182-9def30881d21_ips.xml
```

---

## Documentation

Full documentation is available at: [https://falcoria.github.io/falcoria-docs/](https://falcoria.github.io/falcoria-docs/)

---

## License

MIT

---

Falcoria is developed for real-world offensive security workflows.
