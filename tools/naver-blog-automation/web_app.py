"""기프트클린 네이버 블로그 작성 도우미 — 로컬 웹 앱 런처.

이 한 파일만 실행하면 로컬 웹 서버가 뜨고 브라우저가 자동으로 열립니다.

실행 방법:
  cd "<이 프로젝트 폴더>"
  .venv/bin/python web_app.py     (Windows: .venv\\Scripts\\python web_app.py)

종료: 터미널에서 Ctrl+C

이 서버는 항상 127.0.0.1(localhost)에서만 열립니다(config/safety.py로 강제).
"""
from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.safety import SERVER_HOST, SERVER_PORT, enforce_local_host, DRY_RUN  # noqa: E402

HOST = enforce_local_host(SERVER_HOST)
PORT = SERVER_PORT
URL = f"http://{HOST}:{PORT}"


def _open_browser_when_ready():
    import urllib.request
    for _ in range(40):
        time.sleep(0.25)
        try:
            urllib.request.urlopen(URL + "/api/status", timeout=1)
            break
        except Exception:
            continue
    webbrowser.open(URL)


def main():
    try:
        import uvicorn
    except ImportError:
        print("\n[!] fastapi/uvicorn이 설치되어 있지 않습니다. 먼저 설치하세요:")
        print('    pip install "fastapi>=0.110.0" "uvicorn>=0.27.0"\n')
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  기프트클린 네이버 블로그 작성 도우미")
    print(f"  브라우저에서 열기:  {URL}")
    print(f"  DRY_RUN(모의실행) 모드: {'켜짐 — 실제 네이버에 저장하지 않습니다' if DRY_RUN else '꺼짐 — 실제 임시저장이 수행됩니다'}")
    print("  종료:  Ctrl+C")
    print("=" * 60 + "\n")

    threading.Thread(target=_open_browser_when_ready, daemon=True).start()
    uvicorn.run("web.server:app", host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
