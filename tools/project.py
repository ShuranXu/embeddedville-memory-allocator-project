#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, os, pathlib, re, shutil, subprocess, sys, time, urllib.request, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / ".embeddedville-workspace.json").read_text())

def run(command, check=True):
    return subprocess.run(command, cwd=ROOT, check=check)

def doctor(_):
    missing = [tool for tool in ("make", "python3", "qemu-system-x86_64") if shutil.which(tool) is None]
    compiler = shutil.which("gcc-13") or shutil.which("gcc")
    if not compiler: missing.append("gcc-13")
    print(json.dumps({"workspace": "ok", "compiler": compiler, "missing": missing, "kernel": "7.2.13", "commit": "3c172eede0d6b889ead876f45cc843070209208f"}, indent=2))
    if missing: raise SystemExit("install the missing tools or rebuild the Codespace")

def make_target(target): run(["make", target])
def baseline(_): make_target("baseline")
def build(_): make_target("all")
def test(_): make_target("test")

def write_linux_views(evidence):
    """Create deterministic, inspectable views from the raw guest evidence."""
    trace = (evidence / "kmem-trace.txt").read_text(errors="replace").splitlines()
    timeline = [line.strip() for line in trace if any(event in line for event in (
        "kmalloc:", "kfree:", "mm_page_alloc:", "mm_page_free:",
    ))]
    (evidence / "kmem-timeline.txt").write_text("\n".join(timeline) + "\n")

    requests = []
    request_pattern = re.compile(r"kmalloc:.*bytes_req=(\d+).*bytes_alloc=(\d+)")
    for line in timeline:
        match = request_pattern.search(line)
        if match and int(match.group(1)) in {24, 96, 512, 4096, 32768}:
            requested, allocated = map(int, match.groups())
            row = {"requestedBytes": requested, "allocatedBytes": allocated,
                   "roundingBytes": allocated - requested}
            if row not in requests:
                requests.append(row)
    requests.sort(key=lambda row: row["requestedBytes"])
    with (evidence / "kmalloc-request-table.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("requestedBytes", "allocatedBytes", "roundingBytes"))
        writer.writeheader(); writer.writerows(requests)

    buddy_rows = []
    for line in (evidence / "buddyinfo.txt").read_text(errors="replace").splitlines():
        match = re.match(r"Node\s+(\d+),\s+zone\s+(\S+)\s+(.+)", line)
        if not match:
            continue
        node, zone, counts = match.groups()
        for order, count in enumerate(int(value) for value in counts.split()):
            buddy_rows.append({"node": node, "zone": zone, "order": order,
                               "freeBlocks": count, "freePages": count * (1 << order)})
    with (evidence / "buddy-orders.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("node", "zone", "order", "freeBlocks", "freePages"))
        writer.writeheader(); writer.writerows(buddy_rows)

    sources = [evidence / name for name in (
        "slabinfo.txt", "slabinfo-extended.txt", "buddyinfo.txt", "kmem-trace.txt",
    )]
    summary = {
        "schemaVersion": 1,
        "kernel": {"version": "7.2.13", "commit": "3c172eede0d6b889ead876f45cc843070209208f"},
        "requestRows": requests,
        "buddyRows": buddy_rows,
        "timelineEvents": len(timeline),
        "sourceDigests": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
        "interpretationBoundary": "Public tracepoints show layer events, not every internal sheaf or PCP transition.",
    }
    (evidence / "linux-observation-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Generated request, timeline, buddy-order, and provenance views from raw guest evidence")

def linux_observe(_):
    image = ROOT / "linux" / "out" / "bzImage"
    initrd = ROOT / "linux" / "out" / "initramfs.cpio.gz"
    if not image.is_file() or not initrd.is_file():
        raise SystemExit("Pinned QEMU artifacts are absent. Rebuild the released Codespace or run linux/build-kernel.sh.")
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    result = subprocess.run([
        "qemu-system-x86_64", "-nodefaults", "-nographic", "-no-reboot", "-serial", "mon:stdio",
        "-net", "none", "-m", "512M",
        "-kernel", str(image), "-initrd", str(initrd),
        "-append", "console=ttyS0 panic=-1 random.trust_cpu=on",
    ], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    pattern = re.compile(r"EV_EVIDENCE_BEGIN:([^\r\n]+)\r?\n(.*?)EV_EVIDENCE_END:\1", re.DOTALL)
    print(pattern.sub(lambda match: f"EV_EVIDENCE_CAPTURED:{match.group(1)} ({len(match.group(2).encode())} bytes)", result.stdout), end="")
    captured = 0
    for match in pattern.finditer(result.stdout):
        name = pathlib.Path(match.group(1)).name
        (evidence / name).write_text(match.group(2).replace("\r\n", "\n"))
        captured += 1
    if captured != 4:
        raise SystemExit(f"guest returned {captured}/4 evidence files")
    write_linux_views(evidence)
    print(f"Captured {captured} Linux allocator evidence files in {evidence}")

def digest_tree(paths):
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode()); digest.update(b"\0"); digest.update(path.read_bytes()); digest.update(b"\0")
    return digest.hexdigest()

def analyze(_):
    evidence = ROOT / "evidence"; evidence.mkdir(exist_ok=True)
    sources = [p for base in (ROOT / "src", ROOT / "include") for p in base.rglob("*") if p.is_file()]
    report = json.loads((evidence / "allocator-report.template.json").read_text())
    report["sourceDigest"] = digest_tree(sources)
    report["allocator"]["generatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (evidence / "allocator-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(evidence / "allocator-report.json")

def snapshot():
    report = ROOT / "evidence" / "allocator-report.json"
    if not report.is_file(): analyze(None)
    mapping = [ROOT / "src" / "allocator.c", ROOT / "include" / "ev_allocator.h", report, ROOT / ".embeddedville-workspace.json"]
    entries=[]
    for path in mapping: entries.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size, "type":"file"})
    entries.sort(key=lambda e:e["path"]); manifest={"schemaVersion":1,"files":entries}; canonical=json.dumps(manifest,separators=(",",":")).encode()
    output=ROOT/"evidence"/"memory-allocator-capstone.zip"
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in mapping: archive.write(path,path.relative_to(ROOT).as_posix())
    return output,manifest,hashlib.sha256(canonical).hexdigest(),hashlib.sha256(output.read_bytes()).hexdigest()

def post_json(url,payload,token=None):
    headers={"Content-Type":"application/json"}
    if token: headers["Authorization"]="Bearer "+token
    with urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(payload).encode(),headers=headers,method="POST"),timeout=30) as response: return json.load(response)

def submit(_):
    output,manifest,manifest_digest,snapshot_digest=snapshot(); origin=os.environ.get("EMBEDDEDVILLE_ORIGIN","https://embeddedville.com")
    session=post_json(origin+"/api/workspace-submission-sessions",{"courseId":IDENTITY["courseId"],"activityId":"memory-allocator-capstone","repository":IDENTITY["repository"],"starterVersion":IDENTITY["starterVersion"],"baseRef":IDENTITY["intendedImmutableRef"],"headCommit":None,"dirty":True,"manifestSha256":manifest_digest,"snapshotSha256":snapshot_digest,"snapshotBytes":output.stat().st_size})
    print("Approve this exact snapshot:",session["verificationUri"])
    while True:
        req=urllib.request.Request(origin+f"/api/workspace-submission-sessions/{session['id']}/status",headers={"Authorization":"Bearer "+session["pollToken"]})
        with urllib.request.urlopen(req,timeout=30) as response: status=json.load(response)["status"]
        if status=="approved": break
        if status in {"denied","expired","consumed"}: raise SystemExit("pairing "+status)
        time.sleep(2)
    token=post_json(origin+f"/api/workspace-submission-sessions/{session['id']}/exchange",{},session["pollToken"])["submissionToken"]
    boundary="----embeddedville-memory-allocator"; body=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"manifest\"\r\n\r\n{json.dumps(manifest,separators=(',',':'))}\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"snapshot\"; filename=\"{output.name}\"\r\nContent-Type: application/zip\r\n\r\n").encode()+output.read_bytes()+f"\r\n--{boundary}--\r\n".encode()
    req=urllib.request.Request(origin+f"/api/workspace-submission-sessions/{session['id']}/submit",data=body,headers={"Authorization":"Bearer "+token,"Content-Type":"multipart/form-data; boundary="+boundary},method="POST")
    with urllib.request.urlopen(req,timeout=60) as response: print(json.dumps(json.load(response),indent=2))

def main():
    parser=argparse.ArgumentParser(prog="./project"); commands={"doctor":doctor,"linux-observe":linux_observe,"baseline":baseline,"build":build,"test":test,"analyze":analyze,"submit":submit}; sub=parser.add_subparsers(required=True)
    for name,function in commands.items(): command=sub.add_parser(name); command.set_defaults(function=function)
    args=parser.parse_args(); args.function(args)
if __name__=="__main__": main()
