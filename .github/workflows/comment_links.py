import os, json, subprocess

records = json.load(open("metadata/last_ingest.json","r",encoding="utf-8"))
issue = os.environ["ISSUE_NUMBER"]
repo  = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY")

def url_for(path):
    # Use jsDelivr CDN (fast). If you prefer raw GitHub, swap the return.
    return f"https://cdn.jsdelivr.net/gh/{repo}@main/{path}"
    # return f"https://raw.githubusercontent.com/{repo}/main/{path}"

lines = ["Thanks! Your image links are ready:\n"]
for r in records:
    full = url_for(r["path"])
    alt  = r.get("alt") or "image"
    lines.append(f"![{alt}]({full})\n\n`{full}`")

comment = "\n\n---\n\n".join(lines)

# Use GitHub CLI preinstalled on Actions runners
subprocess.run(["gh","issue","comment", issue, "-b", comment], check=True)
