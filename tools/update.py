# 채널 쇼츠 목록을 가져와 제목으로 분류하고 videos.js를 만든다.
#   python tools/update.py
# 제목 규칙: 비문학 = "제목 (출처) #국어 #비문학 … #분야", 문학 = "작가,「작품」"
# 규칙에 안 맞는 영상은 overrides.json에서 직접 지정한다.
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANNEL = "https://www.youtube.com/@블랙락-u2v/shorts"
COMMON = {"국어", "비문학", "문학", "수능", "모의고사", "모의평가", "학력평가", "수능완성", "EBS", "shorts"}

def fetch():
    out = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print", "%(id)s\t%(title)s", CHANNEL],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return [l.split("\t", 1) for l in out.splitlines() if "\t" in l]

def classify(vid, title):
    tags = re.findall(r"#(\S+)", title)
    core = re.split(r"\s#", title, 1)[0].strip()
    v = {"id": vid, "raw": title, "type": None, "title": core, "field": None, "source": None, "exam": None, "items": None,
         "author": None, "work": None}
    m = re.search(r"\(([^()]*\d[^()]*)\)\s*$", core)
    if m:
        v["source"] = m.group(1).strip()
        v["title"] = core[:m.start()].strip()
        sm = re.match(r"(.*?)\s*(\d+\s*~\s*\d+)$", v["source"])
        v["exam"], v["items"] = (sm.group(1), sm.group(2).replace(" ", "")) if sm else (v["source"], None)
    if "비문학" in tags:
        v["type"] = "비문학"
        rest = [t for t in tags if t not in COMMON]
        v["field"] = rest[0] if rest else None
    elif "「" in core:
        v["type"] = "문학"
        wm = re.search(r"「(.+?)」", core)
        v["work"] = wm.group(1)
        au = core[:wm.start()].strip(" ,")
        v["author"] = au or None
        v["title"] = v["work"]
    return v

def main():
    over = json.loads((ROOT / "overrides.json").read_text(encoding="utf-8"))
    vids = []
    for i, (vid, title) in enumerate(fetch()):
        v = classify(vid, title)
        v.update(over.get(vid, {}))
        v["order"] = i            # 0 = 가장 최근
        vids.append(v)
    miss = [v["raw"] for v in vids if not v["type"]]
    if miss: print("분류 안 된 영상(overrides.json에 추가):", *miss, sep="\n  ")
    (ROOT / "videos.js").write_text("window.VIDEOS = " + json.dumps(vids, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(len(vids), "편 →", ROOT / "videos.js")

main()
