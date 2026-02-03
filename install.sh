#!/usr/bin/env bash
set -euo pipefail

# Repository location for remote installs
REPO_URL="https://raw.githubusercontent.com/legout/pi-ticketflow/main"

# Detect if script is being piped (not run from a local file)
is_piped() {
  [[ ! -f "${BASH_SOURCE[0]:-}" ]] || [[ -p /dev/stdin ]]
}

usage() {
  cat <<'EOF'
Usage:
  # Local install (from cloned repo)
  ./install.sh --global
  ./install.sh --project /path/to/project

  # Remote install (via curl)
  curl -fsSL https://raw.githubusercontent.com/legout/pi-ticketflow/main/install.sh | bash -s -- --global
  curl -fsSL https://raw.githubusercontent.com/legout/pi-ticketflow/main/install.sh | bash -s -- --project /path/to/project

Options:
  --global              Install Pi assets into ~/.pi/agent and TF runtime/state into ~/.tf.
                        Installs the tf CLI to ~/.local/bin/tf.
  --project <path>      Install Pi assets into <path>/.pi and TF runtime/state into <path>/.tf.
                        Installs the tf CLI to <path>/.tf/bin/tf.
  --remote              Force remote mode (download from GitHub)
  --help                Show this help

Notes:
  - Pi-discoverable files (agents, prompts, skills) remain under .pi/ or ~/.pi/agent/.
  - TF-owned state lives under .tf/ (knowledge, ralph) and TF config/scripts under .tf/ as well.
  - After install, run 'tf setup' (global) or './.tf/bin/tf setup' (project).
EOF
}

log() {
  echo "[tf-install] $*" >&2
}

download_file() {
  local url="$1"
  local output="$2"
  local dir
  dir="$(dirname "$output")"

  mkdir -p "$dir" 2>/dev/null || {
    log "ERROR: Cannot create directory $dir (permission denied?)"
    return 1
  }

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output" 2>/dev/null
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$url" -O "$output" 2>/dev/null
  else
    log "ERROR: curl or wget required"
    return 1
  fi
}

route_dest_base() {
  local rel="$1"
  case "$rel" in
    agents/*|skills/*|prompts/*)
      echo "$PI_BASE"
      ;;
    *)
      echo "$TF_BASE"
      ;;
  esac
}

install_cli() {
  local source_file="$1"
  chmod +x "$source_file"

  mkdir -p "$TF_BASE/bin"
  cp "$source_file" "$TF_BASE/bin/tf"
  chmod +x "$TF_BASE/bin/tf"

  if [ "$IS_GLOBAL" = true ]; then
    local global_bin="${HOME}/.local/bin/tf"

    if ! mkdir -p "${HOME}/.local/bin" 2>/dev/null; then
      log "WARNING: Cannot create ${HOME}/.local/bin"
      log "          CLI is installed at: $TF_BASE/bin/tf"
      return 0
    fi

    # Prefer symlink so tf can find its sibling scripts/config in ~/.tf
    if ln -sf "$TF_BASE/bin/tf" "$global_bin" 2>/dev/null; then
      log "Installed CLI symlink to: $global_bin -> $TF_BASE/bin/tf"
    else
      cp "$TF_BASE/bin/tf" "$global_bin" 2>/dev/null || {
        log "WARNING: Cannot write $global_bin (permission denied?)"
        log "          CLI is installed at: $TF_BASE/bin/tf"
        return 0
      }
      log "Installed CLI to: $global_bin"
    fi

    if [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
      echo ""
      echo "WARNING: ${HOME}/.local/bin is not in your PATH"
      echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
      echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
  else
    log "Installed CLI to: $TF_BASE/bin/tf"
  fi
}

install_remote() {
  local temp_dir
  temp_dir="$(mktemp -d)"

  log "Downloading from $REPO_URL ..."

  local manifest_url="$REPO_URL/config/install-manifest.txt"
  local manifest_file="$temp_dir/install-manifest.txt"

  download_file "$manifest_url" "$manifest_file" || {
    log "ERROR: Failed to download install manifest"
    rm -rf "$temp_dir"
    exit 1
  }

  # Download CLI first
  local cli_url="$REPO_URL/bin/tf"
  local cli_temp="$temp_dir/tf-cli"
  if download_file "$cli_url" "$cli_temp"; then
    install_cli "$cli_temp"
  else
    log "WARNING: Failed to download CLI"
  fi

  local count=0
  local errors=0

  while IFS= read -r line || [ -n "$line" ]; do
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [ -z "$line" ] || [[ "$line" == \#* ]]; then
      continue
    fi

    # Skip CLI (handled above)
    if [ "$line" = "bin/tf" ]; then
      continue
    fi

    local dest_base
    dest_base="$(route_dest_base "$line")"

    local file_url="$REPO_URL/$line"
    local output_file="$dest_base/$line"

    if download_file "$file_url" "$output_file"; then
      count=$((count + 1))
    else
      log "WARNING: Failed to download $line"
      errors=$((errors + 1))
    fi
  done < "$manifest_file"

  rm -rf "$temp_dir"

  if [ "$errors" -gt 0 ]; then
    log "WARNING: $errors files failed to download"
  fi

  log "Installed $count files (excluding CLI)"
}

install_local() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  local manifest="$script_dir/config/install-manifest.txt"
  if [ ! -f "$manifest" ]; then
    log "ERROR: Install manifest not found: $manifest"
    exit 1
  fi

  # Install CLI first
  if [ -f "$script_dir/bin/tf" ]; then
    install_cli "$script_dir/bin/tf"
  fi

  local count=0
  local errors=0

  while IFS= read -r line || [ -n "$line" ]; do
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [ -z "$line" ] || [[ "$line" == \#* ]]; then
      continue
    fi

    # Skip CLI (already handled)
    if [ "$line" = "bin/tf" ]; then
      continue
    fi

    if [ ! -f "$script_dir/$line" ]; then
      log "WARNING: Missing file: $script_dir/$line"
      errors=$((errors + 1))
      continue
    fi

    local dest_base
    dest_base="$(route_dest_base "$line")"

    mkdir -p "$dest_base/$(dirname "$line")"
    cp "$script_dir/$line" "$dest_base/$line"
    count=$((count + 1))
  done < "$manifest"

  # Create root AGENTS.md for project installs
  if [ "$IS_GLOBAL" = false ] && [ -f "$script_dir/docs/AGENTS.md.template" ] && [ ! -f "AGENTS.md" ]; then
    cp "$script_dir/docs/AGENTS.md.template" "AGENTS.md"
    log "Created AGENTS.md in project root"
  fi

  if [ "$errors" -gt 0 ]; then
    log "WARNING: $errors file(s) were missing during local install"
  fi

  log "Installed $count files (excluding CLI)"
}

main() {
  PI_BASE=""
  TF_BASE=""
  IS_GLOBAL=false
  local use_remote=false

  if is_piped; then
    use_remote=true
  fi

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --global)
        PI_BASE="$HOME/.pi/agent"
        TF_BASE="$HOME/.tf"
        IS_GLOBAL=true
        shift
        ;;
      --project)
        if [ -z "${2:-}" ]; then
          log "ERROR: Missing path after --project"
          exit 1
        fi
        PI_BASE="$2/.pi"
        TF_BASE="$2/.tf"
        IS_GLOBAL=false
        shift 2
        ;;
      --remote)
        use_remote=true
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        log "ERROR: Unknown option: $1"
        usage
        exit 1
        ;;
    esac
  done

  # Default: project install into current directory
  if [ -z "$PI_BASE" ] || [ -z "$TF_BASE" ]; then
    PI_BASE="$(pwd)/.pi"
    TF_BASE="$(pwd)/.tf"
    IS_GLOBAL=false
  fi

  mkdir -p "$PI_BASE" "$TF_BASE" 2>/dev/null || {
    log "ERROR: Cannot create install directories"
    log "  PI_BASE: $PI_BASE"
    log "  TF_BASE: $TF_BASE"
    exit 1
  }

  if [ "$use_remote" = true ]; then
    install_remote
  else
    install_local
  fi

  echo ""
  if [ "$IS_GLOBAL" = true ]; then
    echo "Installed Pi assets to: $PI_BASE"
    echo "Installed TF runtime/state to: $TF_BASE"
    echo ""
    echo "Next steps:"
    echo "  1. Run interactive setup:"
    echo "     tf setup"
    echo "  2. Sync configuration to agents/prompts:"
    echo "     tf sync"
    echo "  3. Initialize Ralph (per-project, in the repo you work on):"
    echo "     tf ralph init"
    echo "  4. Start working:"
    echo "     /tf <ticket>"
  else
    echo "Installed Pi assets to: $PI_BASE"
    echo "Installed TF runtime/state to: $TF_BASE"
    echo ""
    echo "Next steps:"
    echo "  1. Run interactive setup:"
    echo "     ./.tf/bin/tf setup"
    echo "  2. Sync configuration to agents/prompts:"
    echo "     ./.tf/bin/tf sync"
    echo "  3. Initialize Ralph:"
    echo "     ./.tf/bin/tf ralph init"
    echo "  4. Start working:"
    echo "     /tf <ticket>"
  fi
}

main "$@"
