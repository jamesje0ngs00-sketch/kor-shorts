# 국어 쇼츠 모음

유튜브 채널 [@블랙락-u2v](https://www.youtube.com/@블랙락-u2v/shorts)의 쇼츠를 문학/비문학, 분야, 시험별로 모아 보는 페이지.

- 페이지: `index.html` (데이터는 `videos.js`)
- 갱신: `python tools/update.py` → 채널 목록을 다시 가져와 제목으로 분류하고 `videos.js`를 새로 만든다 (yt-dlp 필요).
- 제목 규칙이 다른 영상은 `overrides.json`에서 직접 지정한다 (`hidden: true`로 숨김, `_era` 현대·고전, `_q` 문학 표지 질문).
- 올린 날짜는 `dates.json`에 모아 두고, 7일 안에 올린 영상에 NEW 표시를 붙인다.
