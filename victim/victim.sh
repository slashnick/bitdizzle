#!/bin/bash
set -ueo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
source venv/bin/activate
exec python victim.py
