#!/usr/bin/env bash
set -euo pipefail

# badges-audit.sh
# Usage: ./scripts/badges-audit.sh [OWNER] [CUTOFF] [QUERY]
#  OWNER  – GitHub owner/user (default: Olagoldstx)
#  CUTOFF – e.g. '>=2025-10-31T21:00:00Z' or '2025-10-31T21:00:00Z'
#  QUERY  – search string (default: 'chore: badges')

OWNER="${1:-Olagoldstx}"
RAW_CUTOFF="${2:-}"
QUERY="${3:-chore: badges}"

# Compute default cutoff if not supplied (last 24h, UTC), including the >= prefix.
if [ -z "${RAW_CUTOFF}" ]; then
  CUTOFF="$(date -u -d '24 hours ago' +'>=%Y-%m-%dT%H:%M:%SZ')"
else
  case "$RAW_CUTOFF" in
    ">="*) CUTOFF="$RAW_CUTOFF" ;;
    *)     CUTOFF=">=$RAW_CUTOFF" ;;
  esac
fi

echo "🔎 Querying for: \"$QUERY\""
echo "└ Owner: $OWNER"
echo "└ Cutoff: $CUTOFF"
echo

echo "=== Owner-wide (everything under $OWNER) ==="
gh search commits "$QUERY" \
  --owner "$OWNER" \
  --committer-date "$CUTOFF" \
  --limit 100 \
  --json repository,commit,url \
  --jq '.[] | [
      (.repository.full_name // .repository.name // ""),
      .commit.author.date,
      (.commit.message | gsub("\n";" ") | .[0:120]),
      .url
    ] | @tsv' \
  || true
echo

echo "=== Author-only by login ($OWNER) ==="
gh search commits "$QUERY" \
  --author "$OWNER" \
  --committer-date "$CUTOFF" \
  --limit 100 \
  --json repository,commit,url \
  --jq '.[] | [
      (.repository.full_name // .repository.name // ""),
      .commit.author.date,
      (.commit.message | gsub("\n";" ") | .[0:120]),
      .url
    ] | @tsv' \
  || true
echo

EMAIL="$(git config --get user.email || true)"
[ -n "$EMAIL" ] || EMAIL="${OWNER}@users.noreply.github.com"

echo "=== Author-only by git email ($EMAIL) ==="
gh api /search/commits \
  -H "Accept: application/vnd.github+json" \
  -F q="$QUERY author:$EMAIL committer-date:$CUTOFF" \
  --jq '.items[] | [
      .repository.full_name,
      .commit.author.date,
      (.commit.message | gsub("\n";" ") | .[0:120]),
      .html_url
    ] | @tsv' \
  || true

OUT="/tmp/badges-commits.tsv"
{
  echo -e "repo\tdate\tmessage\turl"
  gh search commits "$QUERY" \
    --owner "$OWNER" \
    --committer-date "$CUTOFF" \
    --limit 100 \
    --json repository,commit,url \
    --jq '.[] | [
        (.repository.full_name // .repository.name // ""),
        .commit.author.date,
        (.commit.message | gsub("\n";" ") | .[0:120]),
        .url
      ] | @tsv' || true
} > "$OUT"
echo "✅ Done. Results saved to $OUT"
