#!/usr/bin/env bash
set -euo pipefail

DEPRECATED_PATTERNS=(
  "volterraedge/volterra"
  "registry.terraform.io/providers/volterraedge"
  "github.com/volterraedge/terraform-provider-volterra"
  "console.ves.volterra.io"
)

EXIT_CODE=0

for file in "$@"; do
  [[ "$file" == *.tf ]] || [[ "$file" == *.tf.json ]] || continue

  for pattern in "${DEPRECATED_PATTERNS[@]}"; do
    if grep -qn "$pattern" "$file" 2>/dev/null; then
      echo "ERROR: Deprecated reference '$pattern' found in $file:"
      grep -n "$pattern" "$file"
      echo "  Use f5xc-salesdemos/f5xc instead."
      echo ""
      EXIT_CODE=1
    fi
  done
done

exit $EXIT_CODE
