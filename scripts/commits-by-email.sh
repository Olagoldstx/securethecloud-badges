#!/usr/bin/env bash
set -euo pipefail

OWNER="${1:-Olagoldstx}"
SINCE_ISO="${2:-}"                 # raw ISO, e.g., 2025-11-01T00:00:00Z
OUT="${3:-out/commits-by-email.tsv}"

# If SINCE_ISO missing, default to 24h ago UTC
if [[ -z "$SINCE_ISO" ]]; then
  if date -u -v-24H +%Y-%m-%dT%H:%M:%SZ >/dev/null 2>&1; then
    SINCE_ISO="$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)"
  else
    SINCE_ISO="$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)"
  fi
fi

# Try to learn your noreply email; fallback to login lookup
LOGIN="$(gh api user --jq .login 2>/dev/null || echo "$OWNER")"
EMAIL="$(gh api user --jq '.id|tostring' 2>/dev/null | xargs -I{} echo "{}+${LOGIN}@users.noreply.github.com")"

echo -e "repo\tdate\tmessage\turl" > "$OUT"

echo "📬 Scanning commits by email since $SINCE_ISO for $OWNER (email: $EMAIL)"

# List repos under the owner (public only here; add --visibility private if needed)
gh repo list "$OWNER" --limit 200 --json nameWithOwner,defaultBranchRef \
  | jq -r '.[] | [.nameWithOwner, .defaultBranchRef.name] | @tsv' \
  | while IFS=$'\t' read -r REPO BRANCH; do
      [[ -z "$REPO" || -z "$BRANCH" ]] && continue

      for ROLE in author committer; do
        RESP="$(gh api "repos/$REPO/commits" -F "$ROLE=$EMAIL" -F "since=$SINCE_ISO" -F "sha=$BRANCH" 2>/dev/null || true)"
        if jq -e 'type=="array" and length>0' >/dev/null 2>&1 <<<"$RESP"; then
          jq -r --arg repo "$REPO" '
            .[] | [
              $repo,
              .commit.author.date,
              (.commit.message | gsub("\n";" ") | .[0:160]),
              .html_url
            ] | @tsv
          ' <<<"$RESP" >> "$OUT"
        fi
      done
    done

echo "📄 Results saved → $OUT"
