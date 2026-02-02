#!/usr/bin/env bash
set -euo pipefail

# Repository location for remote installs
REPO_URL="https://raw.githubusercontent.com/legout/pi-tk-workflow/main"

# Detect if script is being piped (not run from a local file)
is_piped() {
  # If BASH_SOURCE[0] is not a regular file, we're likely being piped
  [[ ! -f "${BASH_SOURCE[0]:-}" ]] || [[ -p /dev/stdin ]]
}

usage() {
  cat <<'EOF'
Usage:
  # Local install (from cloned repo)
  ./install.sh --global
  ./install.sh --project /path/to/project

  # Remote install (via curl)
  curl -fsSL https://raw.githubusercontent.com/legout/pi-tk-workflow/main/install.sh | bash -s -- --global
  curl -fsSL https://raw.githubusercontent.com/legout/pi-tk-workflow/main/install.sh | bash -s -- --project /path/to/project

Options:
  --global              Install into ~/.pi/agent
  --project <path>      Install into <path>/.pi (defaults to current dir)
  --remote              Force remote mode (download from GitHub)
  --help                Show this help

Notes:
  This script copies agents, skills, prompts, and workflow config.
  Use ./bin/irf setup for interactive setup (extensions + MCP).
EOF
}

log() {
  echo "[irf-install] $*" >&2
}

download_file() {
  local url="$1"
  local output="$2"
  local dir
  dir="$(dirname "$output")"

  if ! mkdir -p "$dir" 2>/dev/null; then
    log "ERROR: Cannot create directory $dir (permission denied?)"
    return 1
  fi

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output" 2>/dev/null
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$url" -O "$output" 2>/dev/null
  else
    log "ERROR: curl or wget required"
    return 1
  fi
}

# Remote install: download all files from GitHub
install_remote() {
  local target_base="$1"
  local temp_dir
  temp_dir="$(mktemp -d)"

  log "Downloading from $REPO_URL ..."

  # Download manifest
  local manifest_url="$REPO_URL/config/install-manifest.txt"
  local manifest_file="$temp_dir/install-manifest.txt"

  if ! download_file "$manifest_url" "$manifest_file"; then
    log "ERROR: Failed to download install manifest"
    rm -rf "$temp_dir"
    exit 1
  fi

  # Download each file in manifest
  local count=0
  local errors=0
  while IFS= read -r line || [ -n "$line" ]; do
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [ -z "$line" ] || [[ "$line" == \#* ]]; then
      continue
    fi

    local file_url="$REPO_URL/$line"
    local output_file="$target_base/$line"

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

  if [ "$count" -eq 0 ]; then
    log "ERROR: No files were installed"
    exit 1
  fi

  log "Installed $count files to: $target_base"
}

# Local install: copy files from repo
install_local() {
  local target_base="$1"
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  local manifest="$script_dir/config/install-manifest.txt"

  if [ ! -f "$manifest" ]; then
    log "ERROR: Install manifest not found: $manifest"
    exit 1
  fi

  local agents_count=0
  local skills_count=0
  local prompts_count=0
  local workflows_count=0

  while IFS= read -r line || [ -n "$line" ]; do
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [ -z "$line" ] || [[ "$line" == \#* ]]; then
      continue
    fi
    if [ ! -f "$script_dir/$line" ]; then
      log "WARNING: Missing file: $script_dir/$line"
      continue
    fi
    mkdir -p "$target_base/$(dirname "$line")"
    cp "$script_dir/$line" "$target_base/$line"
    case "$line" in
      agents/*) agents_count=$((agents_count + 1)) ;;
      skills/*) skills_count=$((skills_count + 1)) ;;
      prompts/*) prompts_count=$((prompts_count + 1)) ;;
      workflows/*) workflows_count=$((workflows_count + 1)) ;;
    esac
  done < "$manifest"

  # Create root AGENTS.md for project installs
  if [ -f "$script_dir/docs/AGENTS.md.template" ] && [ ! -f "AGENTS.md" ]; then
    if [[ "$target_base" != "$HOME/.pi/agent" ]]; then
      cp "$script_dir/docs/AGENTS.md.template" "AGENTS.md"
      log "Created AGENTS.md in project root"
    fi
  fi

  echo ""
  echo "Installed IRF workflow files to: $target_base"
  echo ""
  echo "Installed components:"
  echo "  - $agents_count agents (execution units)"
  echo "  - $skills_count skills (domain expertise)"
  echo "  - $prompts_count prompts (command entry points)"
  echo "  - $workflows_count workflow files"
}

# Main
main() {
  local target_base=""
  local use_remote=false

  # Check if being piped
  if is_piped; then
    use_remote=true
  fi

  # Parse arguments
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --global)
        target_base="$HOME/.pi/agent"
        shift
        ;;
      --project)
        if [ -z "${2:-}" ]; then
          log "ERROR: Missing path after --project"
          exit 1
        fi
        target_base="$2/.pi"
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

  # Default for project install if --project not specified
  if [ -z "$target_base" ]; then
    # If not global, default to current directory
    target_base="$(pwd)/.pi"
  fi

  # Create target directory
  if ! mkdir -p "$target_base" 2>/dev/null; then
    log "ERROR: Cannot create $target_base (permission denied?)"
    log "Try: sudo curl ... | bash -s -- --global"
    exit 1
  fi

  # Install
  if [ "$use_remote" = true ]; then
    install_remote "$target_base"
    echo ""
    echo "Next steps:"
    echo "  1. Install required Pi extensions:"
    echo "     pi install npm:pi-prompt-template-model"
    echo "     pi install npm:pi-model-switch"
    echo "     pi install npm:pi-subagents"
    echo "  2. Run setup: pi '/irf-sync'"
    echo "  3. Initialize Ralph: pi '/ralph init' (or manually create .pi/ralph/)"
    echo "  4. Start working: /irf <ticket>"
  else
    install_local "$target_base"
    echo ""
    echo "Next steps:"
    echo "  1. Review AGENTS.md (project patterns)"
    echo "  2. Initialize Ralph: ./bin/irf ralph init"
    echo "  3. Start working: /irf <ticket>"
  fi
}

main "$@"
