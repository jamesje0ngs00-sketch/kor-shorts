# 작업 스케줄러가 하루 두 번 돌리는 자동 갱신: 최신 받기 → update.py → 바뀐 게 있으면 commit·push.
# 기록은 auto.log (저장소에는 안 올라감)
import datetime, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "auto.log"

def run(*cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode, (r.stdout + r.stderr).strip()

def main():
    out = []
    code, msg = run("git", "pull", "--rebase", "--autostash", "-q")
    if code: out.append("pull 실패: " + msg)
    code, msg = run(sys.executable, "-W", "ignore", str(ROOT / "tools" / "update.py"))
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
