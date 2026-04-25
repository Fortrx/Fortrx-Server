# Fortrx Server

Run the Fortrx backend from a fresh clone with one guided command.

## Stack

- `fortrx`: FastAPI app, serving as the core backend for the secure communication engine.
- `postgres`: PostgreSQL database for durable message and authentication data storage.
- `redis`: Redis for managing live delivery and presence updates, ensuring real-time communication.
- `minio`: S3-compatible object storage for sealed blob storage, enhancing data security.
- `caddy`: Caddy server for HTTPS and WebSocket reverse proxy in production environments.
- `duckdns`: Dynamic DNS updater for production deployments, ensuring continuous accessibility.

## Quick Start

After cloning the repo on a Debian/Ubuntu machine, run the `launch.sh` script:

```bash
bash ops/launch.sh
```

The script automates the setup process:

- Installs Docker and Docker Compose v2 if not already present.
- Prompts you to choose between `local` (development) or `prod` (production) mode.
- Automatically creates a local `.env` file for `local` mode.
- For `prod` mode, it prompts for Infisical login and exports `.env.runtime`.
- Launches the entire stack using the `compose.yml` configuration.

## Modes

### Local Development

Select `local` when running `ops/launch.sh`.

**Endpoints:**

- **API:** `http://localhost:8000`
- **MinIO API:** `http://localhost:9000`
- **MinIO Console:** `http://localhost:9001`

### Production Deployment

Select `prod` when running `ops/launch.sh`.

**Requirements:**

- Your repository must be linked to the correct Infisical project.
- The `prod` environment in Infisical should contain all necessary runtime secrets.
- **Optional but Recommended:** Provide `INFISICAL_TOKEN` as an environment variable for non-interactive authentication.

**The production script will:**

- Install Docker, Docker Compose v2, cron, and `restic`.
- Utilize `INFISICAL_TOKEN` if available, otherwise fallback to Infisical login.
- Export production secrets into `.env.runtime`.
- Start the production stack with all `prod` services enabled.
- Configure nightly backups.

## Backup and Restore

**Manual Backup:**

```bash
bash ops/backup.sh
```

**Restore a Snapshot:**

```bash
bash ops/restore.sh <snapshot-id>
```

**Backup Contents:**

- A logical PostgreSQL database dump.
- A MinIO volume archive.
- Metadata related to the current environment.

The remote backup script leverages `restic`, allowing any backend supported by `restic` to be used. Configure the necessary environment variables in Infisical alongside `RESTIC_REPOSITORY` and `RESTIC_PASSWORD`.
