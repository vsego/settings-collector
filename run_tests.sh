set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PYTHONPATH="$SCRIPT_DIR/src/:PYTHONPATH" python -m coverage run -m unittest tests/test_*.py "$@"
python -m coverage report
python -m coverage html
