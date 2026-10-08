import hashlib, json, os, sys, urllib.request

repo, tag, asset_name, out = sys.argv[1:5]
token = os.environ["GITHUB_TOKEN"]

def api(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)

release = api(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")
assets, page = [], 1
while True:
    batch = api(f"https://api.github.com/repos/{repo}/releases/{release['id']}/assets?per_page=100&page={page}")
    if not batch:
        break
    assets += batch
    page += 1

asset = next((a for a in assets if a["name"] == asset_name), None)
if asset is None:
    print(f"{asset_name} не знайдено в релізі, пропускаю")
    sys.exit(0)

old = {}
if os.path.exists(out):
    with open(out, encoding="utf-8-sig") as f:
        old = json.load(f)

stamp = asset["updated_at"]
if old.get("stamp") == stamp and old.get("size") == asset["size"]:
    sha1 = old["sha1"]
else:
    h = hashlib.sha1()
    with urllib.request.urlopen(asset["browser_download_url"]) as r:
        for chunk in iter(lambda: r.read(1024 * 1024), b""):
            h.update(chunk)
    sha1 = h.hexdigest()

mc = "1.21.1"
if os.path.exists("mods.json"):
    with open("mods.json", encoding="utf-8-sig") as f:
        mc = json.load(f).get("minecraft", mc)

with open(out, "w", encoding="utf-8") as f:
    json.dump({
        "minecraft": mc,
        "url": asset["browser_download_url"],
        "sha1": sha1,
        "size": asset["size"],
        "stamp": stamp,
    }, f, indent=2)
    f.write("\n")
