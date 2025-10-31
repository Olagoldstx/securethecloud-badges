# SecureTheCloud — Shields Badge Kit

<!-- BADGES:START -->

<div align="left">
[![](https://img.shields.io/github/license/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/stars/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a&logo=github)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/last-commit/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/issues/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/issues-pr/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/repo-size/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/languages/top/Olagoldstx/securethecloud-badges?style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
[![](https://img.shields.io/github/actions/workflow/status/Olagoldstx/securethecloud-badges/ci.yml?branch=main&style=for-the-badge&labelColor=0f172a)](https://github.com/Olagoldstx/securethecloud-badges)
</div>

<!-- BADGES:END -->


This repo auto-injects Shields.io badges into all repos for: `olagoldstx`, `cloudlab`, `olumidetowoju` (edit in `config.yml`).
It skips any repo whose name/description contains: `trumind`, `psychiatry`.

It also produces `site/badges.json` for securethecloud.dev.

## Quick start
```bash
# requires: gh (GitHub CLI), git, python3
# set a classic PAT with repo scope or use GH CLI auth
export GITHUB_TOKEN=YOUR_GH_PAT

python3 scripts/update_readmes.py