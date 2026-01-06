#!/usr/bin/env python3
# scripts/create_md_log.py
"""
간단한 MD 변경 로그 생성기 — 파일명을 한국시간(Asia/Seoul) 기준으로 생성합니다.
사용법:
  python scripts/create_md_log.py "제목" "본문 내용"
또는 본문을 표준 입력으로 전달할 수 있습니다.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import sys

MD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'md_files')


def current_kst_timestamp():
    return datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d_%H_%M')


def create_md_log(title: str, body: str):
    os.makedirs(MD_DIR, exist_ok=True)
    ts = current_kst_timestamp()
    filename = f"{ts}.md"
    path = os.path.join(MD_DIR, filename)
    content = f"# {ts} 변경 로그 - {title}\n\n{body}\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        title = sys.argv[1]
        body = sys.argv[2]
    else:
        title = sys.argv[1] if len(sys.argv) >= 2 else 'Change Log'
        print('본문을 입력하세요. 끝내려면 EOF(ctrl+d)를 누르세요:')
        body = sys.stdin.read()

    created = create_md_log(title, body)
    print(f'Created: {created}')
