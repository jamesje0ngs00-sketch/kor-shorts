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
    core = re.split(r"\s#", title, maxsplit=1)[0].strip()
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

DATES = ROOT / "dates.json"   # 올린 날짜 캐시 (영상마다 한 번만 가져온다)
_dates = json.loads(DATES.read_text(encoding="utf-8")) if DATES.exists() else {}
def upload_date(vid):
    if vid not in _dates:
        d = subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--print", "%(upload_date)s",
                            f"https://www.youtube.com/shorts/{vid}"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
        _dates[vid] = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None
    return _dates[vid]

def main():
    over = json.loads((ROOT / "overrides.json").read_text(encoding="utf-8"))
    vids = []
    for i, (vid, title) in enumerate(fetch()):
        v = classify(vid, title)
        v.update(over.get(vid, {}))
        if v["type"] == "문학":
            v["era"] = over.get("_era", {}).get(v["work"])   # 현대 / 고전 (작품 이름으로)
            v["question"] = over.get("_q", {}).get(v["work"])  # 표지 질문
        v["date"] = upload_date(vid)
        v["order"] = i            # 0 = 가장 최근
        vids.append(v)
    miss = [v["raw"] for v in vids if not v["type"]]
    if miss: print("분류 안 된 영상(overrides.json에 추가):", *miss, sep="\n  ")
    noera = [v["work"] for v in vids if v["type"] == "문학" and not v.get("era")]
    if noera: print("현대/고전이 정해지지 않은 작품(overrides.json의 _era에 추가):", *noera, sep="\n  ")
    DATES.write_text(json.dumps(_dates, indent=1), encoding="utf-8")
    (ROOT / "videos.js").write_text("window.VIDEOS = " + json.dumps(vids, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(len(vids), "편 →", ROOT / "videos.js")

main()
