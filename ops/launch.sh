#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE=""

usage() {
  cat <<'EOF'
Usage: bash ops/launch.sh [local|prod]

With no argument, the script prompts for a mode.
EOF
}

say() {
  printf '\n==> %s\n' "$1"
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

linux_only() {
  if ! need_cmd apt-get; then
    echo "Automatic bootstrap currently supports Debian/Ubuntu hosts." >&2
    exit 1
  fi
}

sudo_run() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

docker_cmd() {
  if docker info >/dev/null 2>&1; then
    docker "$@"
  else
    sudo docker "$@"
  fi
}

compose_cmd() {
  docker_cmd compose "$@"
}

random_value() {
  if need_cmd openssl; then
    openssl rand -hex 24
  else
    tr -dc 'A-Za-z0-9' </dev/urandom | head -c 48
  fi
}

choose_mode() {
  if [[ -n "$MODE" ]]; then
    return
  fi

  printf 'Run mode [local/prod]: '
  read -r MODE
  MODE="${MODE,,}"
}

infisical_export_cmd() {
  local cmd
  cmd=(infisical export --env=prod --format=dotenv)
  if [[ -n "${INFISICAL_PROJECT_ID:-}" ]]; then
    cmd+=(--projectId="$INFISICAL_PROJECT_ID")
  fi
  "${cmd[@]}"
}

install_docker_stack() {
  linux_only

  say "Installing Docker, Docker Compose v2, and base utilities"
  sudo_run apt-get update
  sudo_run apt-get install -y ca-certificates curl cron jq

  if ! need_cmd docker; then
    curl -fsSL https://get.docker.com | sudo sh
  fi

  if ! docker_cmd compose version >/dev/null 2>&1; then
    sudo_run apt-get install -y docker-compose-plugin
  fi

  sudo_run systemctl enable --now docker
  sudo_run systemctl enable --now cron

  if [[ -n "${SUDO_USER:-}" ]]; then
    sudo_run usermod -aG docker "$SUDO_USER" || true
  else
    sudo_run usermod -aG docker "$USER" || true
  fi
}

install_restic() {
  linux_only

  if ! need_cmd restic; then
    say "Installing restic for production backups"
    sudo_run apt-get update
    sudo_run apt-get install -y restic
  fi
}

install_infisical() {
  linux_only

  if need_cmd infisical; then
    return
  fi

  say "Installing the Infisical CLI"
  curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash
  sudo_run apt-get update
  sudo_run apt-get install -y infisical
}

write_local_env() {
  local secret_key postgres_password minio_password

  if [[ -f "$REPO_ROOT/.env" ]]; then
    return
  fi

  say "Creating .env for local mode"
  secret_key="$(random_value)$(random_value)"
  postgres_password="$(random_value)"
  minio_password="$(random_value)"

  cat > "$REPO_ROOT/.env" <<EOF
SECRET_KEY=$secret_key
DATABASE_URL=postgresql+psycopg2://fortrx_user:$postgres_password@db:5432/fortrx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SQL_ECHO=false
PUBLIC_BASE_URL=http://localhost:8000
DEPLOY_ENV=local
POSTGRES_DB=fortrx
POSTGRES_USER=fortrx_user
POSTGRES_PASSWORD=$postgres_password
S3_PROVIDER=minio
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=fortrx_minio
S3_SECRET_KEY=$minio_password
S3_REGION=us-east-1
S3_BUCKET_NAME=fortrx-messages
MINIO_ROOT_USER=fortrx_minio
MINIO_ROOT_PASSWORD=$minio_password
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_STORAGE=redis://redis:6379/1
MAX_SEALED_BLOB_BYTES=262144
MAX_MESSAGE_TTL_SECONDS=604800
FORTRX_COMMAND=alembic -c /app/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --forwarded-allow-ips='*'
EOF
}

link_infisical_project() {
  if [[ -n "${INFISICAL_PROJECT_ID:-}" ]]; then
    return
  fi

  if [[ -f "$REPO_ROOT/infisical.json" || -f "$REPO_ROOT/.infisical.json" ]]; then
    return
  fi

  say "Linking this repo to your Infisical project"
  (
    cd "$REPO_ROOT"
    infisical init
  )
}

prompt_for_project_id() {
  if [[ -n "${INFISICAL_PROJECT_ID:-}" ]]; then
    return
  fi

  printf 'Infisical project ID: '
  read -r INFISICAL_PROJECT_ID
  export INFISICAL_PROJECT_ID
}

setup_infisical_auth() {
  if [[ -n "${INFISICAL_TOKEN:-}" ]]; then
    say "Using existing INFISICAL_TOKEN for prod"
    return
  fi

  if [[ -n "${INFISICAL_UNIVERSAL_AUTH_CLIENT_ID:-}" && -n "${INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET:-}" ]]; then
    say "Using Infisical Universal Auth to obtain a short-lived token"
    export INFISICAL_TOKEN="$(
      infisical login --method=universal-auth \
        --client-id="$INFISICAL_UNIVERSAL_AUTH_CLIENT_ID" \
        --client-secret="$INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET" \
        --silent --plain
    )"
    return
  fi

  say "Infisical login is required for prod. Please log in interactively or set INFISICAL_UNIVERSAL_AUTH_CLIENT_ID and INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET."
  infisical login
}

export_prod_env() {
  local tmp_env
  tmp_env="$(mktemp)"

  setup_infisical_auth

  if ! (
    cd "$REPO_ROOT"
    infisical_export_cmd > "$tmp_env"
  ); then
    prompt_for_project_id
    if ! (
      cd "$REPO_ROOT"
      infisical_export_cmd > "$tmp_env"
    ); then
      link_infisical_project
      (
        cd "$REPO_ROOT"
        infisical_export_cmd > "$tmp_env"
      )
    fi
  fi

  {
    cat "$tmp_env"
    echo "DEPLOY_ENV=prod"
    echo "FORTRX_ENV_FILE=.env.runtime"
  } > "$REPO_ROOT/.env.runtime"

  rm -f "$tmp_env"
}

start_local() {
  install_docker_stack
  write_local_env

  say "Starting the local stack"
  (
    cd "$REPO_ROOT"
    compose_cmd --env-file .env up -d --build
  )

  cat <<'EOF'

Local stack is up.
- API: http://localhost:8000
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001
EOF
}

start_prod() {
  install_docker_stack
  install_restic
  install_infisical
  export_prod_env

  say "Starting the production stack"
  (
    cd "$REPO_ROOT"
    compose_cmd --profile prod --env-file .env.runtime up -d --build
  )

  bash "$REPO_ROOT/ops/host/install-cron.sh" "$REPO_ROOT"

  cat <<'EOF'

Production stack is up.
- Runtime env: .env.runtime
- Backups: nightly via cron + restic
EOF
}

main() {
  if [[ $# -gt 1 ]]; then
    usage
    exit 1
  fi

  if [[ $# -eq 1 ]]; then
    MODE="${1,,}"
  fi

  choose_mode

  case "$MODE" in
    local)
      start_local
      ;;
    prod)
      start_prod
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
