# trendkit TODO

> 우선순위별 작업 목록

## Legend

- `[ ]` Todo
- `[~]` In Progress
- `[x]` Done
- `[-]` Cancelled

Priority: `P0` (Critical) → `P1` (High) → `P2` (Medium) → `P3` (Low)

---

## This Week (Immediate)

### Branding (P0)

- [x] README 태그라인 추가: "Token-Optimized Trends for AI"
- [x] README "Why trendkit?" 섹션 추가
- [x] README 배지 추가 (PyPI, Python, License, MCP)
- [ ] GitHub repository description 업데이트
- [ ] GitHub topics 추가 (google-trends, mcp, llm, claude, ai)

### Documentation (P0)

- [x] 경쟁 비교표 작성 (vs pytrends, SerpAPI, Tavily)
- [x] 토큰 절감 효과 수치화 (Before/After 예시)

---

## Next 2 Weeks (Short-term)

### Branding (P1)

- [ ] 로고 제작 (SVG, 64x64, 128x128)
- [ ] Social preview 이미지 (1280x640)
- [ ] PyPI 프로젝트 설명 개선

### Documentation (P1)

- [x] Use Case 문서
  - [x] AI 뉴스봇 구축 예시
  - [x] 콘텐츠 추천 시스템 예시
  - [x] 마케팅 트렌드 분석 예시
- [x] CONTRIBUTING.md 작성
- [ ] API docstrings 완성

### Marketing (P1)

- [ ] awesome-mcp PR 제출
- [ ] awesome-python PR 제출
- [ ] DEV.to 소개글 작성
- [ ] Twitter/X 발표 트윗

---

## This Month (Mid-term)

### Features (P1)

- [x] 캐시 레이어 구현
  - [x] 인메모리 캐시 (LRU)
  - [x] TTL 설정 지원
  - [x] 캐시 무효화 API
  - **완료 기준:**
    - [x] `trending(cache=True, ttl=300)` 동작 확인
    - [x] 캐시 히트 시 응답 시간 < 10ms
    - [x] `trendkit.cache.clear()` API 동작
    - [x] 단위 테스트 추가 (`tests/test_cache.py`)
  - **검증:** `uv run pytest tests/test_cache.py -v` ✅ 24 passed

- [x] 에러 핸들링 강화
  - [x] Rate limit 자동 재시도
  - [x] Timeout 설정 지원
  - [x] 상세 에러 메시지
  - **완료 기준:**
    - [x] `TrendkitError` 예외 계층 구현
    - [x] exponential backoff 재시도 (1s, 2s, 4s)
    - [x] 에러 메시지에 해결 방법 포함
    - [x] 단위 테스트 추가 (`tests/test_exceptions.py`)
  - **검증:** `uv run pytest tests/test_exceptions.py -v` ✅ 22 passed

### Quality (P1)

- [ ] 테스트 커버리지 80% 달성
  - **완료 기준:** `uv run pytest --cov=trendkit` 출력에서 80% 이상
  - **검증:** `uv run pytest --cov=trendkit --cov-fail-under=80`

- [ ] 타입 힌트 100% 완성
  - **완료 기준:** 모든 public 함수에 타입 힌트 추가
  - **검증:** `uv run mypy src/trendkit --strict`

- [ ] mypy strict 모드 통과
  - **완료 기준:** `mypy --strict` 에러 0개
  - **검증:** `uv run mypy src/trendkit --strict`

### Integration (P2)

- [ ] LangChain Tool PR
- [ ] Claude MCP 추천 목록 신청

---

## Backlog (Future)

### Features (P2)

- [ ] 다국가 Geo 지원 확장 (US, JP, GB, DE)
- [ ] 로깅 시스템 (DEBUG/INFO/WARNING/ERROR)
- [ ] Verbose 모드 (--verbose flag)

### Features (P3)

- [ ] 스케줄러 내장
- [ ] 웹훅 알림
- [ ] 히스토리 저장 (SQLite)
- [ ] Streamlit 대시보드

### Community (P3)

- [ ] Discord 채널 개설
- [ ] 첫 외부 contributor PR 머지
- [ ] 릴리즈 노트 자동화

---

## Done

### v0.1.1 Features

- [x] 캐시 레이어 (`src/trendkit/cache.py`)
  - LRU 캐시 with TTL
  - `trending(cache=True, ttl=300)` API
  - `trendkit.cache.clear()`, `trendkit.cache.stats()`
- [x] 예외 계층 (`src/trendkit/exceptions.py`)
  - `TrendkitError` 기본 예외
  - `TrendkitRateLimitError`, `TrendkitTimeoutError`
  - `TrendkitDriverError`, `TrendkitValidationError`
  - exponential backoff `RetryConfig`
- [x] 입력 유효성 검증
  - `_validate_geo()`, `_validate_limit()`
  - 친절한 에러 메시지 with suggestion
- [x] 테스트 추가 (59개 테스트 통과)
  - `tests/test_cache.py` (24 tests)
  - `tests/test_exceptions.py` (22 tests)
  - `tests/test_validation.py` (5 tests)

### v0.1.0 Release

- [x] Core API 구현 (trending, trending_bulk, related, compare, interest)
- [x] 다중 백엔드 (RSS, Selenium, pytrends)
- [x] 토큰 최적화 포맷 (minimal/standard/full)
- [x] CLI 인터페이스
- [x] MCP 서버
- [x] Enriched bulk export
- [x] PyPI 배포
- [x] GitHub Actions CI/CD
- [x] 기본 README 작성
- [x] 테스트 기본 구조

---

## Notes

### 브랜딩 전략 (Seth Godin)

> "Purple Cow를 만들어라" - 기억에 남는 차별점 필요

- 핵심 메시지: **"5토큰으로 트렌드 조회"**
- 스토리: "Claude에게 트렌드를 물었더니 5,000 토큰 → 5토큰으로"

### 경쟁 전략 (Michael Porter)

> "MCP 생태계 선점이 핵심"

- awesome-mcp 등록 우선
- Claude Desktop 공식 추천 목표

### 리스크 관리 (Nassim Taleb)

> "Google 정책 변경에 Antifragile하게"

- 백엔드 추상화 유지
- 대체 데이터 소스 준비 (Twitter, Reddit)
