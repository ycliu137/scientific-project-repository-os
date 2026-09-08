#!/usr/bin/env bash
# Copy to env/create_<name>.sh, set NAME/KIND, point SPEC at env/specs/*.yml
# Usage: ./env/create_<name>.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

NAME="${ENV_NAME:-REPLACE_ME}"
KIND="${ENV_KIND:-venv}"          # micromamba | conda | venv
SPEC="${ENV_SPEC:-}"            # e.g. env/specs/default.yml
PYTHON="${PYTHON:-python3}"

if [[ "$NAME" == "REPLACE_ME" ]]; then
  echo "Set ENV_NAME or edit NAME= in this script." >&2
  exit 2
fi

create_venv() {
  local dir="${ROOT}/.venv-${NAME}"
  if [[ ! -d "$dir" ]]; then
    "$PYTHON" -m venv "$dir"
  fi
  # shellcheck disable=SC1090
  source "$dir/bin/activate"
  python -m pip install -U pip
  if [[ -n "$SPEC" && -f "$SPEC" ]]; then
    python -m pip install -r "$SPEC"
  elif [[ -f requirements.txt ]]; then
    python -m pip install -r requirements.txt
  fi
  echo "Created/updated venv $dir"
  echo "Activate: source $dir/bin/activate"
}

create_conda() {
  local exe="$1"
  if [[ -n "$SPEC" && -f "$SPEC" ]]; then
    "$exe" env create -n "$NAME" -f "$SPEC" 2>/dev/null || "$exe" env update -n "$NAME" -f "$SPEC"
  else
    echo "Set ENV_SPEC to an environment.yml" >&2
    exit 2
  fi
  echo "Created/updated $KIND env $NAME"
  echo "Activate: $exe activate $NAME"
}

case "$KIND" in
  venv) create_venv ;;
  conda)
    command -v conda >/dev/null || { echo "conda not on PATH" >&2; exit 2; }
    create_conda conda
    ;;
  micromamba)
    command -v micromamba >/dev/null || { echo "micromamba not on PATH" >&2; exit 2; }
    create_conda micromamba
    ;;
  *)
    echo "Unknown KIND=$KIND" >&2
    exit 2
    ;;
esac
