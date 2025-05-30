# Falcoria CLI

**Falcoria CLI** is the command-line interface for interacting with the Falcoria system — a high-performance, distributed network scanning platform. It enables users to configure, trigger, and manage scans across infrastructure with power, precision, and flexibility.

---

## 🚀 Features

- ⚡ Initiates scans via Tasker using HTTP APIs
- 📥 Supports import modes: `insert`, `append`, `replace`, `update`
- 🛠 Accepts YAML-based scan configurations and flexible target sources
- 🔀 Enables port sharding and phase-based scan control
- 📊 Tracks scan progress with live status output
- 📦 Allows structured result download and CLI-based introspection
- 🧱 Designed for fast, modular, and scalable integration

---

## 📦 Installation

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

## 🧪 Usage

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


## ⚡ Quick Start

Run your first scan with a single command using a file of target hosts:

```bash
python3 falcli.py fast-scan --targets-file hosts.txt
```

**Example output:**

```
[+] Project 'autoproj-bf470a30' created successfully (d9173423-5e02-47ee-922b-e88bc6223d27).
[+] Scan started successfully for project d9173423-5e02-47ee-922b-e88bc6223d27
[\] Scanning: 1/4 remaining | elapsed: 105s
Total scan time: 105 seconds

Scanned IPs:
IP: 128.199.62.51
Status   : up
OS       : -
Hostnames: -

PORT   PROTO  STATE  SERVICE  BANNER                                                                                                
22     tcp    open   ssh      product: OpenSSH version: 8.9p1 Ubuntu 3ubuntu0.13 extrainfo: Ubuntu Linux; protocol 2.0 ostype: Linux
33060  tcp    open   mysql    product: MySQL version: 8.4.5                                                                         
                                                                                                                     
...

Total scan time: 105 seconds

[+] Downloaded IPs report for project 'd9173423-5e02-47ee-922b-e88bc6223d27'.
Saved to: scan_reports/d9173423-5e02-47ee-922b-e88bc6223d27_ips.xml
```

---

## ⚡ Quick Start

### 🔹 Fast Scan (One-liner)

Run your first scan in one command using a file of target hosts:

```bash
$ python3 falcli.py fast-scan --targets-file hosts.txt
[+] Project 'autoproj-bf470a30' created successfully (d9173423-5e02-47ee-922b-e88bc6223d27).
...
Saved to: scan_reports/d9173423-5e02-47ee-922b-e88bc6223d27_ips.xml
```

---

### 🔸 Guided Workflow (Step-by-Step Control)

Use this method if you want more control over each stage of scanning.

#### 1. Create a Project

```bash
$ python3 falcli.py project create example_project
[+] Project 'example_project' created successfully (271c56d6-7317-4013-a182-9def30881d21).
  project_name  : example_project
  id            : 271c56d6-7317-4013-a182-9def30881d21
  ...
A project is already saved in memory: jet, (9bdcfa1a-72cf-4ff4-a581-0fce9b19cb21)
Do you want to replace it with the new project? [y/N]: y
Memory updated with the new project.
```

#### 2. Start a Scan

```bash
$ python3 falcli.py scan start --targets-file hosts.txt
[+] Scan started successfully for project 271c56d6-7317-4013-a182-9def30881d21
```

#### 3. Check Scan Status

```bash
$ python3 falcli.py scan status
[+] Scan status for project 271c56d6-7317-4013-a182-9def30881d21: 4
```

For interactive live status:

```bash
$ python3 falcli.py scan status -i
```

#### 4. Retrieve Scanned IPs

```bash
$ python3 falcli.py project ips get
```

#### 5. Download XML Report

```bash
$ python3 falcli.py project ips download
[+] Downloaded IPs report for project '271c56d6-7317-4013-a182-9def30881d21'.
Saved to: scan_reports/271c56d6-7317-4013-a182-9def30881d21_ips.xml
```

## 📄 License

MIT

---

Falcoria is developed for real-world offensive security workflows.
