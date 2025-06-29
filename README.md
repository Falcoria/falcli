# Falcoria CLI

**Falcoria CLI** is a unified command-line interface for managing the distributed scanning system — Falcoria. It streamlines every stage of the scanning workflow: from project creation to task dispatch and result retrieval. Built to simplify complex infrastructure scans, `falcli` brings full control to your terminal.

---

## Documentation

Full documentation is available at: [https://falcoria.github.io/falcoria-docs/](https://falcoria.github.io/falcoria-docs/)

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
./falcli.py --help
```

---

## Configuration

Before using the CLI, set up your connection to Falcoria services by editing:

```bash
./app/data/profiles/default.yaml
```

Fill in the following fields:

```yaml
backend_base_url: <scanledger_url>
tasker_base_url: <tasker_url>      # Optional if you don't use scan functionality
token: <your_access_token>
```

This enables communication with the backend and task dispatch system.

---

## Quick Start Example

```bash
./falcli.py project create test_project
./falcli.py scan start --targets-file hosts.txt
./falcli.py scan status
./falcli.py project ips get
./falcli.py workers ips
```

See detailed examples below.

---

## Typical Workflow

### 1. Create a Project

```bash
./falcli.py project create pentest_project
[+] Project 'pentest_project' created successfully (26e73c7f-c1e3-4131-8ee5-99a01681af9f).
  project_name  : pentest_project
  id            : 26e73c7f-c1e3-4131-8ee5-99a01681af9f
  users         : admin
First project saved.
```

### 2. Start a Scan

```bash
./falcli.py scan start --targets-file hosts.txt
[+] Scan initiated for project: 'test_project' (056e77ef-ed63-409a-82cd-a47693c2366a).

Scan Settings
  Import mode        : insert
  Nmap (open ports)  : -n --max-retries 1 --min-rate 300 -Pn -p 1-65535
  Nmap (services)    : -sV -Pn
  Scan config        : app/data/scan_configs/default.yaml

Scan Summary
  Targets provided         : 6
  Duplicates removed       : 1
  Skipped (already known)  : 0
  Rejected                 : 0
  Accepted and sent        : 5
```

### 3. Check Scan Status

```bash
./falcli.py scan status
[+] Scan status for project 26e73c7f-c1e3-4131-8ee5-99a01681af9f fetched successfully.

Scan Status Summary
  Tasks total    : 5
  Tasks running  : 4
  Tasks queued   : 1

Running Targets:
IP               HOSTNAMES  WORKER        STARTED_AT (UTC)     ELAPSED
142.93.156.194              a5ef4e44ca7b  2025-06-17 13:57:46  0:00:11
147.182.157.118             d2b5c09fe876  2025-06-17 13:57:46  0:00:11
143.110.223.7               c21da8b747db  2025-06-17 13:57:46  0:00:11
165.22.231.248              e323a82d28d3  2025-06-17 13:57:46  0:00:11
```

### 4. Get Scan Results

```bash
./falcli.py project ips get
```

### 5. Check Active Workers

```bash
./falcli.py workers ips
[+] Fetched external IP addresses of active workers.

HOSTNAME      IP               LAST_UPDATED         LAST_UPDATED_AGO
d2b5c09fe876  134.209.200.222  2025-06-26 15:44:02  25 min ago
c21da8b747db  146.190.27.214   2025-06-26 15:44:02  25 min ago
e323a82d28d3  159.223.225.154  2025-06-26 15:44:02  25 min ago
a5ef4e44ca7b  64.225.64.155    2025-06-26 15:44:02  25 min ago

4 workers online.
```

---

## Use Cases

| Use Case                  | Description                                      |
|---------------------------|--------------------------------------------------|
| [Import Mode: Insert](https://github.com/Falcoria/falcoria-use-cases/tree/main/import-mode-insert)  | Adds new scan data without affecting existing results. Ideal for incremental discovery. |
| [Import Mode: Replace](https://github.com/Falcoria/falcoria-use-cases/tree/main/import-mode-replace) | Clears existing results and replaces them entirely with the new scan. Useful for fresh scans. |

---
