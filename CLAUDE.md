# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

티스토리 블로그 글을 Google Indexing API를 통해 자동으로 인덱싱하는 프로그램입니다.

## 개발 환경

- Python 3.13+
- UV 가상환경 사용 (.venv)
- 패키지 관리: pyproject.toml

## 주요 명령어

```bash
# 가상환경 활성화
source .venv/bin/activate

# 패키지 설치
uv add <package-name>

# 프로그램 실행
python main.py
```

## 코딩 규칙

- **함수형 프로그래밍**: Class 대신 함수 사용
- **상세한 주석**: 초보자도 이해할 수 있게 작성
- **Context7 MCP 서버**: 기능 구현 시 항상 context7 MCP 서버 참조
- 커밋은 요청시에만 진행 할것!

## 프로젝트 구조

```
post_google_index/
├── main.py              # 메인 실행 파일
├── src/                 # 소스 코드 모듈
│   ├── sitemap.py      # 사이트맵 다운로드/파싱
│   ├── csv_manager.py  # CSV 상태 관리
│   ├── indexing.py     # Google Indexing API
│   ├── logger.py       # 로깅 시스템
│   └── config.py       # 설정 로드
├── docs/               # 문서 폴더
│   └── development-plan.md  # 개발 순서 문서
├── data/               # CSV 파일 저장
├── logs/               # 로그 파일 저장
├── .env                # 환경 변수 (SITEMAP_URL, SERVICE_ACCOUNT_FILE 등)

```

## 핵심 데이터 흐름

1. `.env`에서 사이트맵 URL 로드
2. 사이트맵 XML 다운로드 → URL 추출
3. CSV 파일에서 상태 관리 (PENDING/SUCCESS/FAILED)
4. PENDING 상태 URL만 Google Indexing API로 전송 (일일 최대 200개)
5. 결과를 CSV 업데이트 및 로그 저장

## CSV 상태 값

- `PENDING`: 인덱싱 대기 중
- `SUCCESS`: 인덱싱 성공
- `FAILED`: 3회 재시도 후 실패

## API 제한사항

- Google Indexing API: 일일 200개 요청 제한
- 재시도: 실패 시 최대 3회

## 문서

- [docs/development-plan.md](docs/development-plan.md) - 개발 순서 (Phase 1~7)

