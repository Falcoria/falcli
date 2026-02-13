# falcli

falcli is the command-line interface for the [Falcoria](https://github.com/Falcoria/falcoria) distributed scanning system. It covers the full workflow: creating projects, submitting scans, importing reports, viewing results, checking history, and exporting data.

## Installation

```bash
git clone https://github.com/Falcoria/falcli.git
cd falcli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Edit the profile at `app/data/profiles/default.yaml`:

```yaml
backend_base_url: https://<scanledger_host>
tasker_base_url: https://<tasker_host>       # not needed for data aggregation only
token: <YOUR_ADMIN_TOKEN>
```

For a single-node setup (everything on localhost), both URLs point to `localhost` with ports `443` (ScanLedger) and `8443` (Tasker).

falcli remembers the active project — no need to specify it on every command. Switch projects with `falcli profile set-active-project`. Every command supports `--help`.

## Typical workflow

```bash
# Create a project
falcli project create --name pentest_q4

# Start a scan
falcli scan start --config scan_configs/http-only.yaml --targets-file hosts.txt

# Check status
falcli project scan status

# View results
falcli project ips get

# View what changed since last scan
falcli project ips history

# Export current state as Nmap XML
falcli project ips download
```

## Importing external reports

If you run scans outside of Falcoria (Nmap, Masscan, etc.), import the results directly:

```bash
falcli project ips import -f nmap_output.xml --mode append
```

The import mode controls how incoming data merges with existing records. See [Import Modes](https://falcoria.github.io/falcoria-docs/concepts/import-modes/) for details.

## Scan configs

Scan configs are YAML files in `app/data/scan_configs/`. They define port ranges, protocols, rate limits, and service detection options. falcli ships with built-in profiles for common scan types.

See [Scan Configs](https://falcoria.github.io/falcoria-docs/concepts/scan-configs/) for the full reference.

## Documentation

Full documentation: [https://falcoria.github.io/falcoria-docs/](https://falcoria.github.io/falcoria-docs/)

- [Getting Started](https://falcoria.github.io/falcoria-docs/getting-started/) — setup and first scan
- [Workflows](https://falcoria.github.io/falcoria-docs/workflows/) — common usage patterns

## License

MIT
