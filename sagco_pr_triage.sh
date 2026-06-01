#!/usr/bin/env sh
set -eu

LIMIT="${1:-25}"
OUT="reports/pr_triage"
mkdir -p "$OUT"

echo "[SAGCO] fetching PR heads..."
git fetch origin 'pull/*/head:refs/remotes/origin/pr/*' --quiet || true

git for-each-ref --format='%(refname:short)' refs/remotes/origin/pr \
| sed 's#origin/pr/##' \
| sort -n \
| tail -n "$LIMIT" \
| while read -r PR; do
  REPORT="$OUT/pr_${PR}.md"
  echo "# PR $PR triage" > "$REPORT"
  echo "stamp: $(date)" >> "$REPORT"
  echo "" >> "$REPORT"

  echo "[SAGCO] testing PR $PR"
  git checkout -q "origin/pr/$PR" || {
    echo "checkout_failed" >> "$REPORT"
    continue
  }

  echo "## status" >> "$REPORT"
  git status --short >> "$REPORT" || true

  echo "\n## file inventory" >> "$REPORT"
  find . -maxdepth 3 -type f \
    ! -path './.git/*' \
    | sed 's#^\./##' \
    | sort \
    | head -120 >> "$REPORT"

  echo "\n## smoke tests" >> "$REPORT"

  if find . -name '*.py' | head -1 | grep -q .; then
    echo "python compile:" >> "$REPORT"
    python3 -m compileall -q . >> "$REPORT" 2>&1 && echo "PASS" >> "$REPORT" || echo "FAIL" >> "$REPORT"
  fi

  if find . -name '*.sh' | head -1 | grep -q .; then
    echo "shell syntax:" >> "$REPORT"
    find . -name '*.sh' ! -path './.git/*' -print0 \
      | xargs -0 -n1 sh -n >> "$REPORT" 2>&1 && echo "PASS" >> "$REPORT" || echo "FAIL" >> "$REPORT"
  fi

  if [ -f Cargo.toml ]; then
    echo "rust check:" >> "$REPORT"
    cargo check >> "$REPORT" 2>&1 && echo "PASS" >> "$REPORT" || echo "FAIL" >> "$REPORT"
  fi

  echo "done: $REPORT"
done

git checkout -q main || git checkout -q claude/sagco-rust-compiler-archive-ZQXKs || true

echo "[SAGCO] PR triage complete"
ls -lh "$OUT"
