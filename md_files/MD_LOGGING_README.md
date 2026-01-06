**MD 생성 규칙 (한국시간 적용)**

- 모든 자동 또는 수동 변경 로그(.md)는 한국시간(Asia/Seoul, KST) 기준으로 파일명을 생성합니다.
- 파일명 형식: `YYYY-MM-DD_HH_MM.md` (예: `2026-01-06_15_40.md`)
- 프로젝트에 스크립트가 추가되어 있습니다: `scripts/create_md_log.py`
  - 사용 예: `python scripts/create_md_log.py "변경 제목" "변경 내용 요약"`
  - 본문을 표준 입력으로 전달할 수도 있습니다.
- `basic.md` 지침을 준수하여 코드 수정 시 반드시 `md_files`에 로그를 남기세요.
