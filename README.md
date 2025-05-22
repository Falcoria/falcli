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

## 📄 License

MIT

---

Falcoria is developed for real-world offensive security workflows.
