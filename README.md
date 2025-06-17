# Falcoria CLI

**Falcoria CLI** is a unified command-line interface for managing the distributed scanning system — Falcoria. It streamlines every stage of the scanning workflow: from project creation to task dispatch and result retrieval. Built to simplify complex infrastructure scans, `falcli` brings full control to your terminal.

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

## How to Scan

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
./falcli.py scan start --targets-file ../hosts.txt 
[+] Scan initiated for project 26e73c7f-c1e3-4131-8ee5-99a01681af9f.

Scan Settings
  Import mode      : insert
  Nmap open ports  : -n --max-retries 1 --min-rate 300 -Pn -p 1-65535
  Nmap services    : -sV -Pn

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

### 4. Get Results

```bash
./falcli.py project ips get
```

---

## Documentation

Full documentation is available at: [https://falcoria.github.io/falcoria-docs/](https://falcoria.github.io/falcoria-docs/)

