# 🛡️ SecureTheCloud — Multi-Repo Audit Framework

> A fully automated audit system to track **commits**, **pull requests**, and **badge updates** across all repositories under `Olagoldstx`.

---

## 🧭 Overview

**SecureTheCloud-Badges** provides a unified way to audit all GitHub activities from your ecosystem — spanning commits, PRs, CI updates, and automated badge pushes.  
It’s optimized for transparency, repeatability, and simple daily reporting via Makefile commands.

📍 **Audits include:**
- `audit-prs` → open & closed PRs (chore, docs, CI)
- `audit-badges` → badge update commits
- `commits-by-email` → commits authored under your GitHub noreply email
- `audit-all` → everything combined
- `show-outputs` → pretty terminal summaries of the TSV results

---

## 🪶 Banner

*(Place your SecureTheCloud banner here)*  
<img width="1024" height="1024" alt="file_00000000816c62309e3965308b9c7d19" src="https://github.com/user-attachments/assets/a64d42b9-f6d1-42ef-b414-0dfa264e2d89" />
---

## ⚙️ Prerequisites

| Requirement | Description |
|--------------|-------------|
| 🐧 Linux / WSL2 / macOS | Tested on Ubuntu 22.04 / 24.04 |
| 🧰 `gh` GitHub CLI | Must be logged in (`gh auth login`) |
| 🔧 jq | For JSON processing |
| 🧩 make | For running the automation targets |
| 🔐 Token | Must have scopes `repo`, `read:org`, `gist` |

Check auth:
```bash
gh auth status -h github.com
Example:

pgsql
Copy code
github.com
  ✓ Logged in to github.com account Olagoldstx
  - Token scopes: 'gist', 'read:org', 'repo'
🚀 Quick Start
Clone and move into your project:

bash
Copy code
git clone https://github.com/Olagoldstx/securethecloud-badges.git
cd securethecloud-badges
Run your first full audit:

bash
Copy code
make audit-all
Then view results:

bash
Copy code
make show-outputs
All results will appear in:

csharp
Copy code
out/
├── commits-chore__badges.tsv
├── commits-by-email.tsv
├── prs-chore_.tsv
├── prs-ci_.tsv
├── prs-docs_.tsv
└── ...
🧩 Command Reference
🔹 Full System Scan
Runs PR and commit audits together:

bash
Copy code
make audit-all
🔹 Pull Request Audit
bash
Copy code
make audit-prs
Open PRs only:

bash
Copy code
make audit-prs STATE=open
Specific date range:

bash
Copy code
make audit-prs CUTOFF=">=2025-11-01T00:00:00Z"
🔹 Badge Commits
bash
Copy code
make audit-badges
🔹 Email-Based Commits
bash
Copy code
make commits-by-email
🔹 Show Outputs
bash
Copy code
make show-outputs
📄 Output Format
All .tsv files (tab-separated) follow this structure:

bash
Copy code
repo    date/state   message/title   url
Preview in terminal:

bash
Copy code
column -t -s $'\t' out/commits-chore__badges.tsv | less -S
Or convert to CSV:

bash
Copy code
awk -v OFS=',' 'BEGIN{FS="\t"} {print $0}' out/commits-by-email.tsv > commits.csv
🧰 Example Workflows
🔸 Daily Badge and PR Review
bash
Copy code
make audit-all
make show-outputs
🔸 Open PR Summary
bash
Copy code
make audit-prs STATE=open | tee out/open-prs.log
🔸 Cross-check Commits by Email
bash
Copy code
make commits-by-email
🔒 Troubleshooting
Issue	Fix
gh: Not Found (HTTP 404)	Ensure token has repo scope
make: *** No rule to make target 'audit-all'	Run git pull — Makefile may be missing
syntax error in conditional expression: unexpected token '>'	Update your Makefile to latest version (syntax patch applied)
permission denied on out/	Fix with chmod -R 755 out/

🧱 Directory Layout
csharp
Copy code
securethecloud-badges/
├── Makefile                    # Main command automation
├── scripts/
│   ├── badges-audit.sh         # Badge commit audit
│   └── commits-by-email.sh     # Email-based commit scan
├── out/                        # Generated TSVs
├── README.md                   # This file
└── assets/
    └── banner-securethecloud-dark.png
🧭 Future Enhancements
 Auto-summary report (out/summary.log)

 Slack or email notifications

 Optional CSV → HTML dashboard

✨ Credits
Maintained by:
@Olagoldstx — Multi-Cloud Security Architect
Creator of SecureTheCloud.dev 🛡️

“Audit everything. Secure everything. Know everything.”

✅ Ready to go.
To finalize:

bash
Copy code
nano README.md
# paste this content
chmod 644 README.md
git add README.md
git commit -m "docs: add SecureTheCloud audit framework README"
git push
yaml
Copy code

---

### ✅ After pasting:
1. Press **Ctrl + O** → **Enter** (to save).  
2. Press **Ctrl + X** (to exit).  
3. Then run:
   ```bash
   git add README.md
   git commit -m "docs: add SecureTheCloud audit framework README"
   git push

---

## 🚀 Usage Guide

This repository provides an automated audit and badge reporting system for the **SecureTheCloud** ecosystem.  
It uses the GitHub CLI (`gh`) and Makefile automation to track commits, pull requests, and badge updates across all repositories owned by `Olagoldstx`.

### 🧩 Prerequisites
- GitHub CLI (`gh`) installed and authenticated  
  ```bash
  gh auth status

⚙️ Core Commands
Command	Description
make audit-all	Runs a full sweep — PR audits, badge commit scans, and email-based commits.
make audit-prs	Scans all repositories for pull requests matching key tags like chore, docs, or ci.
make audit-prs STATE=open	Limits the PR audit to open PRs only.
make audit-prs CUTOFF=">=2025-11-01T00:00:00Z"	Runs PR audits starting from a specific date/time.
make audit-badges	Scans for chore: badges commits across all repos and outputs results to /out/commits-chore__badges.tsv.
make commits-by-email	Finds commits authored by your GitHub noreply email (for privacy-protected commits).
make show-outputs	Displays summaries of all .tsv output files (commits, PRs, badges).
📂 Output Files

All reports are generated in the /out/ directory.

File	Description
prs-*.tsv	Pull request audit reports
commits-*.tsv	Commit activity reports
commits-by-email.tsv	Commits linked to your noreply email
commits-chore__badges.tsv	Badge-related commits
prs-chore__badges.tsv	Badge-related PRs
🖼️ Brand Integration

To display the SecureTheCloud banner at the top of your README:

<p align="center">
  <img src="assets/securethecloud-banner-light.png" alt="SecureTheCloud Banner" width="800"/>
</p>

✅ Example Workflow
# Run all audits and update reports
make audit-all

# Inspect latest badge commits
make audit-badges

# Review reports
make show-outputs

# Commit and push updates
git add .
git commit -m "chore: finalize SecureTheCloud badges and audit system v2.5"
git push origin main

🧠 Credits

Built by Olagoldstx for the SecureTheCloud initiative —
an evolving ecosystem of multi-cloud security, automation, and observability tools.
