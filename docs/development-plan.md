# 개발 순서

## Phase 1: 기본 설정 및 환경 구성

1. UV 가상환경 설정
2. 필요한 패키지 설치 (requests, google-auth, python-dotenv 등)
3. .env.example 파일 생성 (템플릿)
4. 프로젝트 폴더 구조 생성 (logs/, data/, src/)

## Phase 2: 사이트맵 다운로드 및 파싱

1. 사이트맵 XML 다운로드 함수 구현
2. XML 파싱하여 URL 추출 함수 구현
3. 사이트맵 인덱스 처리 (여러 사이트맵 파일 처리)
4. URL 최신순 정렬 기능 구현

## Phase 3: CSV 관리 시스템 ✅ 완료

1. ✅ CSV 파일 읽기/쓰기 함수 구현
2. ✅ URL 상태 확인 함수 구현
3. ✅ URL 추가 및 상태 업데이트 함수 구현
4. ✅ PENDING 상태 URL 필터링 함수 구현 (URL,상태,날짜)

### 구현된 기능:
- `read_csv()`: CSV 파일 읽기
- `write_csv()`: CSV 파일 쓰기
- `get_url_status()`: 특정 URL의 상태 확인
- `add_url()`: 단일 URL 추가 (중복 체크 포함)
- `update_url_status()`: URL 상태 업데이트 (재시도 횟수 증가 옵션)
- `get_pending_urls()`: PENDING 상태 URL 필터링 (limit 옵션)
- `add_urls_batch()`: 여러 URL 일괄 추가
- `get_statistics()`: 통계 정보 조회

### CSV 필드 구조:
- `url`: URL 주소
- `status`: 상태 (PENDING/SUCCESS/FAILED)
- `lastmod`: 마지막 수정일
- `created_at`: 생성 시간
- `updated_at`: 업데이트 시간
- `retry_count`: 재시도 횟수

### 테스트 결과:
- 단일/배치 URL 추가: 정상 작동
- 중복 URL 처리: 정상 작동
- 상태 업데이트 및 재시도 횟수 증가: 정상 작동
- PENDING URL 필터링 및 limit: 정상 작동
- 통계 정보 조회: 정상 작동

## Phase 4: Google Indexing API 연동

1. Service Account 인증 구현
2. 단일 URL 인덱싱 함수 구현
3. 재시도 로직 구현 (최대 3회)
4. Rate Limiting 처리 (API 제한 고려)

## Phase 5: 로깅 및 에러 처리

1. 로그 파일 생성 시스템 구현
2. 콘솔 출력 포맷팅
3. 에러 메시지 처리 (명확한 안내)
4. 진행 상황 표시 (진행률 표시)

## Phase 6: 통합 및 테스트

1. main.py에서 전체 프로세스 통합
2. 각 단계별 테스트
3. 에러 케이스 테스트
4. 최종 검증

## Phase 7: 문서화

1. README.md 작성
2. Google API 키 발급 가이드 작성
3. 사용 방법 및 주의사항 문서화
4. 코드 주석 최종 검토
