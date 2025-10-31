#!/usr/bin/env python3
import os, re, json, base64, random, string, sys, time
from typing import List, Dict
import requests
import yaml

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def die(msg):
    print(f"[error] {msg}", file=sys.stderr); sys.exit(1)

if not TOKEN:
    die("Set GITHUB_TOKEN (classic PAT with repo scope)")

with open("config.yml") as f:
    CFG = yaml.safe_load(f)

START = CFG["readme"]["start_marker"]
END   = CFG["readme"]["end_marker"]
STYLE = CFG["readme"]["style"]
LABEL_COLOR = CFG["readme"]["theme"]["labelColor"]
DEFAULTS = CFG["default_badges"]
TOPIC_BADGES = CFG.get("topic_badges", {})
WF_FILE = CFG["workflow"]["file"]
SITE_PATH = CFG["site_export"]["path"]
EXCLUDES = [s.lower() for s in CFG["exclude_name_contains"]]
BR_PREFIX = CFG["branch"]["name_prefix"]
PR_TITLE_PREFIX = CFG["branch"]["pr_title_prefix"]
COMMIT_MSG = CFG["branch"]["commit_message"]

def slug():
    return ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))

def gh(url, params=None, method="GET", json_body=None):
    r = requests.request(method, url, headers=HEADERS, params=params, json=json_body)
    if r.status_code >= 300:
        raise RuntimeError(f"{method} {url} -> {r.status_code} {r.text[:300]}")
    return r.json()

def list_repos(user: str):
    repos = []
    page=1
    while True:
        rs = gh(f"{API}/users/{user}/repos", params={"per_page":100,"page":page,"type":"owner","sort":"updated"})
        if not rs: break
        repos += rs; page+=1
    return repos

def skip_repo(r):
    text = (r["name"] + " " + (r.get("description") or "")).lower()
    return any(x in text for x in EXCLUDES)

def badge_url(kind, owner, name, default_branch, topics):
    base = "https://img.shields.io"
    qb = f"&style={STYLE}&labelColor={LABEL_COLOR}"
    if kind=="github_license":
        return f"{base}/github/license/{owner}/{name}?{qb[1:]}"
    if kind=="github_stars":
        return f"{base}/github/stars/{owner}/{name}?{qb[1:]}&logo=github"
    if kind=="last_commit":
        return f"{base}/github/last-commit/{owner}/{name}?{qb[1:]}"
    if kind=="issues":
        return f"{base}/github/issues/{owner}/{name}?{qb[1:]}"
    if kind=="prs":
        return f"{base}/github/issues-pr/{owner}/{name}?{qb[1:]}"
    if kind=="repo_size":
        return f"{base}/github/repo-size/{owner}/{name}?{qb[1:]}"
    if kind=="languages":
        return f"{base}/github/languages/top/{owner}/{name}?{qb[1:]}"
    if kind=="workflow_status":
        return f"{base}/github/actions/workflow/status/{owner}/{name}/{WF_FILE.split('/')[-1]}?branch={default_branch}{qb}"
    raise KeyError(kind)

def custom_badge(label, message, color, logo=None):
    from urllib.parse import quote
    u = f"https://img.shields.io/badge/{quote(label)}-{quote(message)}-{quote(color)}?style={STYLE}&labelColor={LABEL_COLOR}"
    if logo: u += f"&logo={logo}"
    return u

def build_badge_block(owner, name, default_branch, topics):
    lines = [START, "", "<div align=\"left\">"]
    # defaults
    for d in DEFAULTS:
        try:
            u = badge_url(d["type"], owner, name, default_branch, topics)
            lines.append(f"[![]({u})](https://github.com/{owner}/{name})")
        except KeyError:
            pass
    # topic-driven
    for t in topics:
        tkey = t.lower()
        if tkey in TOPIC_BADGES:
            for b in TOPIC_BADGES[tkey]:
                if b["type"]=="custom":
                    u = custom_badge(b["label"], b["message"], b["color"], b.get("logo"))
                    lines.append(f"[![]({u})](https://github.com/{owner}/{name})")
    lines += ["</div>", "", END]
    return "\n".join(lines)

def get_default_branch(owner, repo):
    r = gh(f"{API}/repos/{owner}/{repo}")
    return r["default_branch"], r.get("topics", [])

def get_file(owner, repo, path):
    try:
        r = gh(f"{API}/repos/{owner}/{repo}/contents/{path}")
        return base64.b64decode(r["content"]).decode(), r["sha"]
    except Exception:
        return None, None

def put_file(owner, repo, path, content, sha=None, branch=None, message="update"):
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch
    }
    if sha: data["sha"]=sha
    return gh(f"{API}/repos/{owner}/{repo}/contents/{path}", method="PUT", json_body=data)

def ensure_branch(owner, repo, base, new_branch):
    ref = gh(f"{API}/repos/{owner}/{repo}/git/ref/heads/{base}")
    sha = ref["object"]["sha"]
    try:
        gh(f"{API}/repos/{owner}/{repo}/git/refs", method="POST",
           json_body={"ref": f"refs/heads/{new_branch}", "sha": sha})
    except Exception as e:
        # branch may exist; ignore
        pass

def ensure_default_branch_exists(owner, repo, default_branch):
    """
    If the repository is empty (no commits), create an initial README on the default branch.
    This implicitly creates the default branch so subsequent ref lookups work.
    """
    try:
        # Will fail with 409 on empty repositories
        gh(f"{API}/repos/{owner}/{repo}/git/ref/heads/{default_branch}")
        return  # branch exists with at least one commit
    except RuntimeError as e:
        if "Git Repository is empty" in str(e):
            # Create the first commit by writing a README onto the intended default branch
            initial = f"# {repo}\n\nInitialized for automated Shields.io badges.\n"
            put_file(
                owner, repo, "README.md", initial,
                sha=None,
                branch=default_branch,  # <-- IMPORTANT: create the default branch with this commit
                message="chore: initial README for badges bootstrap"
            )
            return
        raise


def open_pr(owner, repo, head, base, title):
    try:
        gh(f"{API}/repos/{owner}/{repo}/pulls", method="POST",
           json_body={"title": title, "head": head, "base": base, "body": "Automated Shields.io badge injection."})
    except Exception as e:
        pass

def upsert_badges(owner, repo):
    default_branch, topics = get_default_branch(owner, repo)

    # Ensure even empty repos have a default branch
    ensure_default_branch_exists(owner, repo, default_branch)

    br = BR_PREFIX + slug()
    ensure_branch(owner, repo, default_branch, br)

    readme_path_candidates = ["README.md", "Readme.md", "readme.md"]
    raw, sha, path = None, None, None
    for p in readme_path_candidates:
        raw, sha = get_file(owner, repo, p)
        if raw is not None:
            path = p; break
    if raw is None:
        # create README
        path = "README.md"
        raw = f"# {repo}\n\n"
        sha = None
    block = build_badge_block(owner, repo, default_branch, topics)
    if START in raw and END in raw:
        new = re.sub(re.compile(rf"{re.escape(START)}.*?{re.escape(END)}", re.S), block, raw, count=1)
    else:
        # insert under title if possible
        lines = raw.splitlines()
        if lines and lines[0].startswith("# "):
            lines.insert(1, "\n" + block + "\n")
            new = "\n".join(lines)
        else:
            new = block + "\n\n" + raw
    if new != raw:
        put_file(owner, repo, path, new, sha=sha, branch=br, message=COMMIT_MSG)
        open_pr(owner, repo, br, default_branch, f"{PR_TITLE_PREFIX} {repo}")
        changed = True
    else:
        changed = False
    # ensure we have a minimal workflow file if none exists (optional)
    wf_raw, wf_sha = get_file(owner, repo, WF_FILE)
    if wf_raw is None:
        minimal = """name: ci
on: [push, pull_request]
jobs:
  echo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "ci alive"
"""
        dir_parts = WF_FILE.split("/")[:-1]
        # cannot create dirs via contents API explicitly; creating file creates parents automatically
        put_file(owner, repo, WF_FILE, minimal, branch=br, message="chore: add minimal ci for badge visibility")
    return {
        "repo": repo,
        "owner": owner,
        "branch": br,
        "default_branch": default_branch,
        "topics": topics,
        "changed": changed
    }

def main():
    users = CFG["users"]
    all_export = []
    for u in users:
        print(f"\n=== scanning @{u} ===")
        repos = list_repos(u)
        for r in repos:
            if r["archived"] or r["fork"]:
                continue
            if skip_repo(r):
                print(f"skip {r['name']}")
                continue
            info = upsert_badges(r["owner"]["login"], r["name"])
            print(("updated " if info["changed"] else "nochange ") + info["repo"])
            # build site export entry
            owner = info["owner"]; name = info["repo"]
            default_branch = info["default_branch"]
            topics = info["topics"]
            # construct the exact same badge URLs used in README
            badge_urls = []
            for d in DEFAULTS:
                try:
                    badge_urls.append(badge_url(d["type"], owner, name, default_branch, topics))
                except KeyError:
                    pass
            for t in topics:
                if t in TOPIC_BADGES:
                    for b in TOPIC_BADGES[t]:
                        if b["type"]=="custom":
                            badge_urls.append(custom_badge(b["label"], b["message"], b["color"], b.get("logo")))
            all_export.append({
                "repo": f"{owner}/{name}",
                "default_branch": default_branch,
                "topics": topics,
                "badges": badge_urls,
                "url": f"https://github.com/{owner}/{name}"
            })
    os.makedirs(os.path.dirname(SITE_PATH), exist_ok=True)
    with open(SITE_PATH, "w") as f:
        json.dump(all_export, f, indent=2)
    print(f"\nExported site data -> {SITE_PATH}")

if __name__=="__main__":
    main()
