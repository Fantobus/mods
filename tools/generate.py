import hashlib, json, os, sys, urllib.request

kind, exts, out, repo, tag = sys.argv[1:6]
exts = tuple(exts.split(","))
token = os.environ["GITHUB_TOKEN"]

def api(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)

old = {}
if os.path.exists(out):
    with open(out, encoding="utf-8-sig") as f:
        old = json.load(f)
old_files = {x["file"]: x for x in old.get("files", [])}

release = api(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")
assets, page = [], 1
while True:
    batch = api(f"https://api.github.com/repos/{repo}/releases/{release['id']}/assets?per_page=100&page={page}")
    if not batch:
        break
    assets += batch
    page += 1

files = []
for a in assets:
    name = a["name"]
    if not name.lower().endswith(exts):
        continue
    prev = old_files.get(name)
    stamp = a["updated_at"]
    if prev and prev.get("stamp") == stamp and prev.get("size") == a["size"]:
        sha1 = prev["sha1"]
    else:
        h = hashlib.sha1()
        with urllib.request.urlopen(a["browser_download_url"]) as r:
            for chunk in iter(lambda: r.read(1024 * 1024), b""):
                h.update(chunk)
        sha1 = h.hexdigest()
    files.append({
        "file": name,
        "sha1": sha1,
        "size": a["size"],
        "side": prev.get("side", "both") if prev else "both",
        "stamp": stamp,
    })

files.sort(key=lambda x: x["file"])

manifest = {
    "type": kind,
    "minecraft": old.get("minecraft", "1.21.1"),
    "baseUrl": old.get("baseUrl", f"https://github.com/{repo}/releases/download/{tag}/"),
    "mode": old.get("mode", "additive"),
    "allowedExtra": old.get("allowedExtra", []),
    "files": files,
}

with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")
