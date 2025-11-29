프로그램 요구사항 문서

프로그램 이름 : 구글 인덱싱 프로그램.
목적 : 블로그글을 구글에 보내서 인덱싱을 시키는 것이 목적.

## 기술 스택 및 코딩 규칙
- 가상환경은 UV를 통해 사용합니다. (.venv)
- 코드는 초보자도 이해할 수 있게 가독성 있게 작성하고, 주석을 상세히 달 것!
- Class보다는 함수형으로 작성해줄것!
- 기능 구현시 항상 context7 MCP 서버를 사용할 것!
- Python을 사용할 것!

## 기능 요구사항

### 1. 사이트맵 다운로드
- 티스토리 사이트맵 URL에서 XML 다운로드
- 사이트맵에서 모든 게시글 URL 파싱
- 사이트맵 인덱스 파일 처리 (여러 사이트맵이 있을 경우)

### 2. Google Indexing API 연동
- Service Account JSON 키 파일을 통한 인증
- 배치 처리: 여러 URL을 한 번에 처리
- API 호출 결과 로깅 (성공/실패)
- 실패 시 자동 재시도 로직 (최대 3회)
- API Rate Limiting 자동 처리 (지연 시간 조절)

### 3. 설정 관리
- .env 파일로 설정 관리:
  - 티스토리 사이트맵 URL
  - Google Service Account JSON 파일 경로
  - 기타 필요한 설정값

### 4. 중복 방지 시스템
- CSV 파일로 URL 상태 관리 (도메인명.csv)
- CSV 구조:
  ```csv
  url,status,indexed_date
  https://yourblog.tistory.com/1,SUCCESS,2025-01-15 10:30:25
  https://yourblog.tistory.com/2,PENDING,
  https://yourblog.tistory.com/3,FAILED,2025-01-16 14:20:10
  ```
- 상태 값:
  - `PENDING`: 아직 인덱싱 안 됨
  - `SUCCESS`: 인덱싱 성공
  - `FAILED`: 3번 재시도 후 실패
- 처리 로직:
  1. 사이트맵에서 추출한 URL이 CSV에 없으면 `PENDING` 상태로 추가
  2. `PENDING` 상태인 URL만 인덱싱 시도
  3. 성공 시 `SUCCESS`로 상태 변경 + 날짜 기록
  4. 3번 재시도 후 실패 시 `FAILED`로 상태 변경 + 날짜 기록
  5. `SUCCESS`와 `FAILED` 상태는 건너뛰기

### 5. 실행 결과 저장
- 로그 파일 생성 (logs/indexing_YYYYMMDD_HHMMSS.log)
- 저장 내용:
  - 실행 시작/종료 시간
  - 처리된 URL 개수
  - 각 URL별 성공/실패 상태
  - 실패 시 에러 메시지
  - 건너뛴 URL (이미 인덱싱된 URL)

### 6. Google API 키 발급 안내
- README에 Service Account 생성 및 키 발급 과정 문서화
- Google Search Console 등록 과정 안내
- 필요한 API 활성화 안내

## 프로그램 흐름
1. .env 파일에서 설정 로드
2. 도메인명.csv 파일 로드 (없으면 생성)
3. 사이트맵 URL에서 XML 다운로드
4. 사이트맵에서 URL 목록 추출 (최신 글부터 정렬)
5. CSV 파일 업데이트:
   - 새로운 URL → `PENDING` 상태로 추가
   - 기존 URL → 상태 유지
6. `PENDING` 상태인 URL만 필터링 (최대 200개)
7. Google Indexing API로 인덱싱 시도
8. 각 URL별 처리:
   - 성공 → CSV에 `SUCCESS` + 날짜 기록
   - 실패 → 최대 3회 재시도
   - 3회 실패 → CSV에 `FAILED` + 날짜 기록
9. 결과 로그 파일 생성 및 콘솔 출력

## 실행 방법
```bash
python main.py
```
- 별도의 옵션 없이 단순 실행
- 모든 처리 과정이 자동으로 진행됨

## 개발 순서

### Phase 1: 기본 설정 및 환경 구성
1. UV 가상환경 설정
2. 필요한 패키지 설치 (requests, google-auth, python-dotenv 등)
3. .env.example 파일 생성 (템플릿)
4. 프로젝트 폴더 구조 생성 (logs/, data/ 등)

### Phase 2: 사이트맵 다운로드 및 파싱
1. 사이트맵 XML 다운로드 함수 구현
2. XML 파싱하여 URL 추출 함수 구현
3. 사이트맵 인덱스 처리 (여러 사이트맵 파일 처리)
4. URL 최신순 정렬 기능 구현

### Phase 3: CSV 관리 시스템
1. CSV 파일 읽기/쓰기 함수 구현
2. URL 상태 확인 함수 구현
3. URL 추가 및 상태 업데이트 함수 구현
4. PENDING 상태 URL 필터링 함수 구현

### Phase 4: Google Indexing API 연동
1. Service Account 인증 구현
2. 단일 URL 인덱싱 함수 구현
3. 재시도 로직 구현 (최대 3회)
4. Rate Limiting 처리 (API 제한 고려)

### Phase 5: 로깅 및 에러 처리
1. 로그 파일 생성 시스템 구현
2. 콘솔 출력 포맷팅
3. 에러 메시지 처리 (명확한 안내)
4. 진행 상황 표시 (진행률 표시)

### Phase 6: 통합 및 테스트
1. main.py에서 전체 프로세스 통합
2. 각 단계별 테스트
3. 에러 케이스 테스트
4. 최종 검증

### Phase 7: 문서화
1. README.md 작성
2. Google API 키 발급 가이드 작성
3. 사용 방법 및 주의사항 문서화
4. 코드 주석 최종 검토

