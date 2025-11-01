# ============================================
# 🛡️ SecureTheCloud — Audit Makefile (clean v2)
# ============================================

SHELL := /bin/bash

# ---- Defaults (override at runtime) ----
OWNER   ?= Olagoldstx
OUTDIR  ?= out
QUERIES ?= chore:\ badges docs: ci: chore:
STATE   ?=

# Portable last-24h ISO timestamp (no ">=" here)
CUTOFF_ISO ?= $(shell if date -u -v-24H +%Y-%m-%dT%H:%M:%SZ >/dev/null 2>&1; then date -u -v-24H +%Y-%m-%dT%H:%M:%SZ; else date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ; fi)
# Allow user to pass either ISO or ">=ISO" via CUTOFF; we normalize to a single ">=" usage.
# If CUTOFF is provided, strip a leading ">="; else use CUTOFF_ISO.
CUTOFF_RAW := $(if $(CUTOFF),$(patsubst >=%,%,$(CUTOFF)),$(CUTOFF_ISO))
CUTOFF_GE  := >=$(CUTOFF_RAW)

# ---- jq programs ----
define PR_JQ
.[] | [
  (
    .repository.full_name
    // (.url | sub("^https?://github.com/";"") | split("/")[0:2] | join("/"))
  ),
  .state,
  .updatedAt,
  (.title | gsub("\n";" ") | .[0:160]),
  .url
] | @tsv
endef
export PR_JQ

define COMMIT_JQ
.[] | [
  (
    .repository.full_name
    // (.url | sub("^https?://github.com/";"") | split("/")[0:2] | join("/"))
  ),
  .commit.author.date,
  (.commit.message | gsub("\n";" ") | .[0:160]),
  .url
] | @tsv
endef
export COMMIT_JQ

# ---- Targets ----
.PHONY: audit-prs audit-badges audit-all show-outputs commits-by-email

## Scan PRs matching $(QUERIES), updated since $(CUTOFF_GE); optional STATE=open|closed.
audit-prs:
	@mkdir -p "$(OUTDIR)"
	@echo "🧭 Auditing PRs updated since $(CUTOFF_GE) for $(OWNER)"
	@for q in $(QUERIES); do \
	  safe=$$(printf "%s" "$$q" | tr ' /:' '__'); \
	  out="$(OUTDIR)/prs-$$safe.tsv"; \
	  echo "  • PRs: $$q → $$out"; \
	  if [ -n "$(STATE)" ]; then \
	    gh search prs "$$q" \
	      --owner "$(OWNER)" \
	      --updated "$(CUTOFF_GE)" \
	      --state "$(STATE)" \
	      --limit 100 \
	      --json repository,title,state,updatedAt,url \
	      --jq "$$PR_JQ" \
	      > "$$out" 2>/dev/null || true; \
	  else \
	    gh search prs "$$q" \
	      --owner "$(OWNER)" \
	      --updated "$(CUTOFF_GE)" \
	      --limit 100 \
	      --json repository,title,state,updatedAt,url \
	      --jq "$$PR_JQ" \
	      > "$$out" 2>/dev/null || true; \
	  fi; \
	done
	@echo "✅ All PR audits complete. See '$(OUTDIR)/*.tsv'"

## Commit audit for "chore: badges"
audit-badges:
	@mkdir -p "$(OUTDIR)"
	@echo "🔍 Running badge commit audit since $(CUTOFF_GE) for $(OWNER)…"
	@gh search commits 'chore: badges' \
	  --owner "$(OWNER)" \
	  --committer-date "$(CUTOFF_GE)" \
	  --limit 100 \
	  --json repository,commit,url \
	  --jq "$$COMMIT_JQ" \
	  > "$(OUTDIR)/commits-chore__badges.tsv" 2>/dev/null || true
	@echo "✅ Badge commit audit → $(OUTDIR)/commits-chore__badges.tsv"

## Email-based commit sweep (calls the script)
commits-by-email:
	@mkdir -p "$(OUTDIR)"; \
	bash scripts/commits-by-email.sh "$(OWNER)" "$(CUTOFF_RAW)" "$(OUTDIR)/commits-by-email.tsv"

## Run everything
audit-all: audit-prs audit-badges commits-by-email
	@echo "🎯 Full audit complete."

## Peek outputs
show-outputs:
	@echo; for f in $(OUTDIR)/*.tsv; do \
	  echo "== $$f ($$(wc -l < "$$f") lines) =="; \
	  head -n 8 "$$f" || true; \
	  echo; \
	done
