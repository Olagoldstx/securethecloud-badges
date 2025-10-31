# SecureTheCloud — Shields Badge Kit

This repo auto-injects Shields.io badges into all repos for: `olagoldstx`, `cloudlab`, `olumidetowoju` (edit in `config.yml`).
It skips any repo whose name/description contains: `trumind`, `psychiatry`.

It also produces `site/badges.json` for securethecloud.dev.

## Quick start
```bash
# requires: gh (GitHub CLI), git, python3
# set a classic PAT with repo scope or use GH CLI auth
export GITHUB_TOKEN=YOUR_GH_PAT

python3 scripts/update_readmes.py
