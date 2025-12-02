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

## Phase 4: Google Indexing API 연동 ✅ 완료

1. ✅ Service Account 인증 구현
2. ✅ 단일 URL 인덱싱 함수 구현
3. ✅ 재시도 로직 구현 (최대 3회)
4. ✅ Rate Limiting 처리 (API 제한 고려)

### 구현된 기능:
- `create_indexing_service()`: Service Account 인증 및 API 서비스 생성
- `submit_urls()`: URL 인덱싱 (1~100개, 재시도 로직 포함)
  - 단일/배치 통합: 1개든 100개든 동일한 함수 사용
  - 자동 재시도: 실패한 URL만 선택적으로 재시도
  - 콜백 지원: 실시간 진행 상황 모니터링
- `get_url_status()`: URL 인덱싱 상태 조회

### API 사양:
- **엔드포인트**: `https://indexing.googleapis.com/v3/urlNotifications:publish`
- **인증**: Service Account 기반 OAuth2
- **Scope**: `https://www.googleapis.com/auth/indexing`
- **배치 제한**: 최대 100개 URL/요청
- **일일 제한**: 200개 요청 (배치 사용 시 20,000개 URL)

### 에러 처리:
- **403 Forbidden**: 권한 없음 또는 API 비활성화
- **429 Too Many Requests**: 할당량 초과
- **400 Bad Request**: 잘못된 요청 형식
- 재시도 간 지연 시간 적용 (REQUEST_DELAY)

### 테스트:
- Service Account 인증 테스트
- 단일 URL 제출 테스트
- 재시도 로직 테스트
- 배치 제출 테스트 (최대 100개)
- URL 상태 조회 테스트

## Phase 5: 로깅 및 에러 처리 ✅ 완료

1. ✅ 1~4 페이즈의 함수를 활용해 제대로 된 시스템 구축 (main.py에서 전체 프로세스 통합)
2. ✅ 로그 파일 생성 시스템 구현
3. ✅ 콘솔 출력 포맷팅
4. ✅ 에러 메시지 처리 (명확한 안내)
5. ✅ 진행 상황 표시 (진행률 표시)

### 구현된 파일:

#### src/logger.py - 로깅 시스템
- `setup_logger()`: 로거 설정 (파일 + 콘솔 출력)
- `print_header()`: 섹션 헤더 출력
- `print_step()`: 단계별 진행 상황 출력
- `print_progress()`: 진행률 바 표시
- `print_statistics()`: 통계 정보 테이블 출력
- `print_result_summary()`: 실행 결과 요약
- `print_error()`: 에러 메시지 출력
- `print_success()`: 성공 메시지 출력
- `print_warning()`: 경고 메시지 출력
- `print_info()`: 정보 메시지 출력

#### main.py - 전체 프로세스 통합
- `get_csv_path()`: 도메인 기반 CSV 경로 생성
- `step1_load_config()`: 설정 로드
- `step2_fetch_sitemap()`: 사이트맵 URL 추출
- `step3_sync_csv()`: CSV 동기화
- `step4_create_api_service()`: API 서비스 생성
- `step5_submit_urls()`: URL 인덱싱 실행
- `step6_print_summary()`: 결과 요약 출력
- `main()`: 전체 프로세스 실행

### 실행 흐름:
```
1. 설정 로드 (.env)
   ↓
2. 사이트맵 URL 추출 (블로그 글만 필터링)
   ↓
3. CSV 동기화 (새 URL만 PENDING으로 추가)
   ↓
4. API 서비스 생성 (Service Account 인증)
   ↓
5. URL 인덱싱 (PENDING만 처리, 일일 제한 적용)
   ↓
6. 결과 요약 출력
```

### 테스트 결과:
- ✅ CSV 파일 자동 생성 (data/도메인.csv)
- ✅ 기존 URL 중복 스킵
- ✅ SUCCESS 상태 URL 재실행 방지
- ✅ PENDING → SUCCESS/FAILED 상태 업데이트
- ✅ 로그 파일 저장 (logs/YYYY-MM-DD.log)
- ✅ 진행률 바 표시
- ✅ 통계 테이블 출력

### 실행 예시:
```
═══════════════════════════════════════════════════════
📌 티스토리 블로그 Google Indexing 시작
═══════════════════════════════════════════════════════
[1/6] 설정 파일 로드 중...
✅ 사이트맵: https://carbom.tistory.com/sitemap.xml
✅ 일일 제한: 10개
...
인덱싱 진행: [██████████████████████████████] 100.0% (10/10)
...
┌─────────────────────────────────┐
│         📊 최종 상태                │
├─────────────────────────────────┤
│ 전체 URL    │        232 개  │
│ 대기 중     │        212 개  │
│ 성공        │         20 개  │
│ 실패        │          0 개  │
└─────────────────────────────────┘
✅ 프로그램이 정상적으로 종료되었습니다.
```




## Phase 6: 통합 및 테스트

1. 각 단계별 테스트
2. 에러 케이스 테스트
3. 최종 검증

