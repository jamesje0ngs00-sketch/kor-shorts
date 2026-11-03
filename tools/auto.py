# 작업 스케줄러가 하루 두 번 돌리는 자동 갱신: 최신 받기 → update.py → 바뀐 게 있으면 commit·push.
# 기록은 auto.log (저장소에는 안 올라감)
import datetime, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "auto.log"
# 작업 스케줄러는 창 없는 pythonw로 띄우지만, yt-dlp는 그 아래에서 안 돌아서 하위 실행은 python.exe로 한다
PY = str(pathlib.Path(sys.executable).with_name("python.exe"))
# 작업 스케줄러 환경에서는 사용자 패키지 폴더의 yt-dlp를 못 찾아서, 저장소 안 _pkgs에 따로 설치해 쓴다 (갈 때마다 최신으로)
PKGS = ROOT / "_pkgs"

def run(*cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(PKGS)}, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode, (r.stdout + r.stderr).strip()

def main():
    out = []
    code, msg = run("git", "pull", "--rebase", "--autostash", "-q")
    if code: out.append("pull 실패: " + msg)
    code, msg = run(PY, "-m", "pip", "install", "-q", "-U", "--target", str(PKGS), "--upgrade-strategy", "eager", "yt-dlp")
    if code: out.append("yt-dlp 설치 실패: " + msg[-300:])
    code, msg = run(PY, "-W", "ignore", str(ROOT / "tools" / "update.py"))
    out.append(msg)
    if code:
        return out
    run("git", "add", "videos.js", "dates.json")
    if run("git", "diff", "--cached", "--quiet")[0] == 0:
        out.append("바뀐 것 없음")
        return out
    run("git", "commit", "-q", "-m", "새 영상 자동 반영")
    code, msg = run("git", "push", "-q")
    out.append("push 완료" if code == 0 else "push 실패: " + msg)
    return out

lines = main()
with LOG.open("a", encoding="utf-8") as f:
    f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] " + " / ".join(l.replace("\n", " ") for l in lines if l) + "\n")
