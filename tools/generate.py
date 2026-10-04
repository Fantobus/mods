import hashlib, json, os, sys

kind, folder, ext, out, repo = sys.argv[1:6]

old = {}
if os.path.exists(out):
    with open(out, encoding="utf-8-sig") as f:
        old = json.load(f)

old_side = {x["file"]: x.get("side", "both") for x in old.get("files", [])}

files = []
for name in sorted(os.listdir(folder)):
    if not name.lower().endswith(ext):
        continue
    with open(os.path.join(folder, name), "rb") as f:
        data = f.read()
    files.append({
        "file": name,
        "sha1": hashlib.sha1(data).hexdigest(),
        "size": len(data),
        "side": old_side.get(name, "both"),
    })

manifest = {
    "type": kind,
    "minecraft": old.get("minecraft", "1.21.1"),
    "baseUrl": old.get("baseUrl",
        f"https://raw.githubusercontent.com/{repo}/main/{folder}/"),
    "mode": old.get("mode", "additive"),
    "allowedExtra": old.get("allowedExtra", []),
    "files": files,
}

with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")
