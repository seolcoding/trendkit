# trendkit PRD (Product Requirements Document)

## Executive Summary

**Product**: trendkit — Token-Optimized Trends for AI
**Version**: 0.1.0 → 1.0.0 Roadmap
**Last Updated**: 2024-12-24

### Vision Statement

> AI 에이전트가 실시간 트렌드를 파악하는 가장 효율적인 방법을 제공한다.

### Problem Statement

| 문제 | 현재 상황 | trendkit 해결책 |
|------|----------|----------------|
| **토큰 낭비** | pytrends 응답 ~500 토큰/항목 | minimal 포맷 ~5 토큰/항목 |
| **설정 복잡성** | API 키, 인증, 의존성 | `pip install` 즉시 사용 |
| **MCP 부재** | Trends MCP 서버 없음 | 내장 MCP 서버 제공 |
| **벌크 수집 한계** | RSS 20개 제한 | Selenium 100+ 수집 |

---

## Target Users

### Primary: MCP/LLM 개발자

```
페르소나: AI Agent 개발자 민수
- Claude Desktop, Cursor 등 AI IDE 사용
- MCP 서버로 도구 확장 중
- 토큰 비용에 민감
- Python 중급 이상
```

### Secondary: 콘텐츠 마케터

```
페르소나: 콘텐츠 마케터 지영
- 트렌드 기반 콘텐츠 기획
- CLI로 빠른 조회 원함
- 코딩 지식 초급
```

### Tertiary: 데이터 분석가

```
페르소나: 데이터 분석가 현우
- 대량 트렌드 데이터 수집
- CSV/JSON 내보내기 필수
- 자동화 스크립트 작성
```

---

## Competitive Analysis

### Landscape

```
                 토큰 효율성
                     ↑
                     │    ★ trendkit
                     │      (목표)
              높음   │
                     │
                     │────────────────→ 기능 완성도
                     │ pytrends    SerpAPI
              낮음   │              (유료)
                     │
```

### Feature Comparison

| Feature | trendkit | pytrends | SerpAPI | Tavily |
|---------|----------|----------|---------|--------|
| 가격 | Free | Free | $50/mo | $20/mo |
| 토큰 최적화 | ★★★ | ☆☆☆ | ★☆☆ | ★☆☆ |
| MCP 지원 | ★★★ | ☆☆☆ | ☆☆☆ | ★★☆ |
| 벌크 수집 | ★★★ | ★☆☆ | ★★★ | ☆☆☆ |
| 설치 난이도 | Easy | Easy | Medium | Easy |
| 안정성 | Beta | Stable | Stable | Stable |

### Competitive Advantages

1. **유일한 LLM-native 설계** — 토큰 최적화가 핵심 설계 원칙
2. **MCP 네이티브** — Claude Desktop 즉시 연동
3. **무료 + 오픈소스** — 상용 API 대비 비용 제로
4. **다중 백엔드** — RSS(빠름) + Selenium(대량) 선택

---

## Product Requirements

### P0: Must Have (v1.0)

| ID | Requirement | Status | Notes |
|----|-------------|--------|-------|
| P0-1 | 실시간 트렌드 조회 (RSS) | ✅ Done | `trending()` |
| P0-2 | 벌크 트렌드 수집 (Selenium) | ✅ Done | `trending_bulk()` |
| P0-3 | 관련 검색어 조회 | ✅ Done | `related()` |
| P0-4 | 키워드 비교 | ✅ Done | `compare()` |
| P0-5 | 관심도 추이 | ✅ Done | `interest()` |
| P0-6 | MCP 서버 | ✅ Done | `trendkit-mcp` |
| P0-7 | CLI 인터페이스 | ✅ Done | `trendkit` command |
| P0-8 | 토큰 최적화 포맷 | ✅ Done | minimal/standard/full |

### P1: Should Have (v1.1)

| ID | Requirement | Status | Notes |
|----|-------------|--------|-------|
| P1-1 | 캐시 레이어 | 🔲 Todo | 중복 요청 방지 |
| P1-2 | 다국가 Geo 지원 확장 | 🔲 Todo | US, JP, EU 테스트 |
| P1-3 | 에러 핸들링 강화 | 🔲 Todo | Rate limit, timeout |
| P1-4 | 로깅 시스템 | 🔲 Todo | 디버그 모드 |

### P2: Nice to Have (v1.2+)

| ID | Requirement | Status | Notes |
|----|-------------|--------|-------|
| P2-1 | LangChain Tool 통합 | 🔲 Todo | langchain-community |
| P2-2 | 스케줄러 내장 | 🔲 Todo | 주기적 수집 |
| P2-3 | 웹훅 알림 | 🔲 Todo | 급상승 알림 |
| P2-4 | 히스토리 저장 | 🔲 Todo | SQLite 저장 |
| P2-5 | 웹 대시보드 | 🔲 Todo | Streamlit/Gradio |

---

## Non-Functional Requirements (NFR)

### Performance Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-P1 | RSS 백엔드 응답 시간 | < 2초 | `time.time()` 측정 |
| NFR-P2 | Selenium 백엔드 응답 시간 | < 30초 | `time.time()` 측정 |
| NFR-P3 | MCP 도구 호출 응답 시간 | < 3초 | Claude Desktop 로그 |
| NFR-P4 | 메모리 사용량 | < 500MB | `psutil` 측정 |

### Reliability Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-R1 | API 가용성 | > 99% | 에러 로그 분석 |
| NFR-R2 | 재시도 성공률 | > 80% | 재시도 메트릭 |
| NFR-R3 | Graceful degradation | 장애 시 캐시 반환 | 통합 테스트 |

### Scalability Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-S1 | 동시 요청 처리 | 10 req/sec | 부하 테스트 |
| NFR-S2 | 벌크 수집 한계 | 100+ items | 기능 테스트 |

### Security Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-SEC1 | 민감 정보 노출 없음 | 로그에 개인정보 없음 | 코드 리뷰 |
| NFR-SEC2 | 의존성 취약점 | 0 high/critical | `safety check` |

---

## Failure Handling Specification

### Error Scenarios

```gherkin
Scenario: Google Trends Rate Limit (429)
  Given Google Trends에서 429 응답이 반환된다
  When trending() 또는 관련 함수를 호출한다
  Then 자동으로 exponential backoff 재시도 (1s, 2s, 4s)
  And 최대 3회 재시도 후 TrendkitRateLimitError 발생
  And 에러 메시지에 재시도 대기 시간 포함

Scenario: Network Timeout
  Given 네트워크 연결이 30초 이상 응답 없음
  When trending_bulk()을 호출한다
  Then TrendkitTimeoutError 발생
  And 부분 수집 결과가 있으면 partial_results 속성에 포함

Scenario: Selenium Driver 실패
  Given ChromeDriver가 설치되지 않았거나 버전 불일치
  When trending_bulk()을 호출한다
  Then TrendkitDriverError 발생
  And 설치 안내 메시지 포함

Scenario: Invalid Geo Code
  Given 지원하지 않는 geo 코드가 입력됨
  When trending(geo="INVALID")를 호출한다
  Then TrendkitValidationError 발생
  And 지원되는 geo 코드 목록 제공
```

### Error Hierarchy

```python
TrendkitError (base)
├── TrendkitAPIError
│   ├── TrendkitRateLimitError
│   ├── TrendkitTimeoutError
│   └── TrendkitServiceError
├── TrendkitDriverError
└── TrendkitValidationError
```

### Circuit Breaker Pattern (v1.1+)

```python
# 5회 연속 실패 시 회로 열림
# 60초 후 half-open 상태로 전환
# 1회 성공 시 회로 닫힘

from trendkit import trending

# 회로가 열려 있으면 캐시된 결과 또는 빈 리스트 반환
result = trending(fallback="cache")  # 또는 fallback="empty"
```

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                      trendkit                           │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  Python API │     CLI     │ MCP Server  │  (LangChain) │
├─────────────┴─────────────┴─────────────┴──────────────┤
│                      core.py                            │
├─────────────┬─────────────┬────────────────────────────┤
│  RSS Backend│ Selenium BE │    pytrends Backend        │
│  (trendspyg)│ (selenium)  │    (pytrends)              │
├─────────────┴─────────────┴────────────────────────────┤
│                   Google Trends                         │
└─────────────────────────────────────────────────────────┘
```

### Backend Selection Logic

```python
# core.py 내부 로직
def get_trends(method="auto"):
    if method == "auto":
        if need_bulk:
            return selenium_backend()  # 100+ items
        else:
            return rss_backend()       # fast, ~20 items
    elif method == "analysis":
        return pytrends_backend()      # interest, compare
```

### Output Format Specification

```python
# minimal (~5 tokens/item)
["키워드1", "키워드2", "키워드3"]

# standard (~15 tokens/item)
[{"keyword": "키워드1", "traffic": "10만+"}]

# full (~100 tokens/item)
[{
    "keyword": "키워드1",
    "traffic": "10만+",
    "news": [{"headline": "...", "url": "..."}],
    "related": ["관련1", "관련2"],
    "image": {"url": "..."}
}]
```

---

## Success Metrics

### Adoption Metrics

| Metric | Current | 3-Month Target | 6-Month Target |
|--------|---------|----------------|----------------|
| GitHub Stars | 0 | 100 | 500 |
| PyPI Downloads/month | - | 500 | 2,000 |
| MCP 활성 사용자 | - | 50 | 200 |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Test Coverage | > 80% |
| API Response Time | < 2s (RSS), < 10s (Selenium) |
| Error Rate | < 1% |

### Engagement Metrics

| Metric | Target |
|--------|--------|
| GitHub Issues 응답 시간 | < 48h |
| PR 머지 시간 | < 1 week |
| 문서 완성도 | 100% API coverage |

---

## Go-to-Market Strategy

### Phase 1: Foundation (Week 1-2)

- [x] PyPI 패키지 배포
- [x] GitHub Actions CI/CD
- [ ] README 브랜딩 개선
- [ ] 로고 및 배지 추가

### Phase 2: Visibility (Week 3-4)

- [ ] awesome-mcp 목록 PR
- [ ] awesome-python 목록 PR
- [ ] DEV.to / Medium 소개 글
- [ ] Twitter/X 발표

### Phase 3: Integration (Month 2)

- [ ] LangChain Tool PR
- [ ] Claude MCP 추천 목록 신청
- [ ] YouTube 튜토리얼 (선택)

### Phase 4: Community (Month 3+)

- [ ] Discord/Slack 채널
- [ ] Contributor 가이드
- [ ] 첫 외부 PR 머지

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Google 정책 변경 | Medium | High | 다중 백엔드 추상화 유지 |
| Rate Limiting | High | Medium | 캐시 레이어, 재시도 로직 |
| Selenium 불안정 | Medium | Medium | headless 모드 최적화 |
| 경쟁 제품 출현 | Low | Medium | 빠른 기능 개발, 커뮤니티 구축 |

---

## Appendix

### A. User Stories

```gherkin
Feature: 실시간 트렌드 조회
  As a AI 에이전트 개발자
  I want to 최소 토큰으로 트렌드를 조회하고 싶다
  So that API 비용을 절감할 수 있다

  Scenario: minimal 포맷 조회
    Given trendkit이 설치되어 있다
    When trending(format="minimal")을 호출한다
    Then 키워드 리스트만 반환된다
    And 응답 크기가 100 토큰 미만이다
```

### B. Additional User Stories

```gherkin
Feature: 벌크 트렌드 수집
  As a 데이터 분석가
  I want to 100개 이상의 트렌드를 한번에 수집하고 싶다
  So that 충분한 데이터로 분석할 수 있다

  Scenario: 벌크 수집 성공
    Given trendkit[selenium]이 설치되어 있다
    And ChromeDriver가 설정되어 있다
    When trending_bulk(limit=100)을 호출한다
    Then 최소 100개 트렌드 항목이 반환된다
    And 각 항목에 keyword, rank, traffic이 포함된다

  Scenario: CSV 내보내기
    Given trending_bulk 결과가 있다
    When output="trends.csv"를 지정한다
    Then CSV 파일이 생성된다
    And 헤더에 keyword,rank,traffic이 포함된다

Feature: MCP 서버 통합
  As a Claude Desktop 사용자
  I want to MCP 도구로 트렌드를 조회하고 싶다
  So that 대화 중에 실시간 트렌드를 확인할 수 있다

  Scenario: trends_trending 도구 호출
    Given Claude Desktop에서 trendkit MCP가 연결되어 있다
    When "오늘의 인기 검색어 알려줘"라고 질문한다
    Then trends_trending 도구가 호출된다
    And 트렌드 키워드 목록이 응답에 포함된다

  Scenario: trends_compare 도구 호출
    Given Claude Desktop에서 trendkit MCP가 연결되어 있다
    When "삼성과 애플 중 뭐가 더 인기있어?"라고 질문한다
    Then trends_compare 도구가 호출된다
    And 두 키워드의 상대적 인기도가 응답에 포함된다

Feature: 관련 검색어 조회
  As a 콘텐츠 마케터
  I want to 특정 키워드의 관련 검색어를 알고 싶다
  So that 콘텐츠 주제를 확장할 수 있다

  Scenario: 관련 검색어 조회 성공
    Given trendkit이 설치되어 있다
    When related("아이폰", limit=5)를 호출한다
    Then 5개의 관련 검색어가 반환된다
    And 각 검색어는 문자열 형태이다

Feature: 에러 처리
  As a 개발자
  I want to 명확한 에러 메시지를 받고 싶다
  So that 문제를 빠르게 해결할 수 있다

  Scenario: Rate Limit 에러
    Given Google Trends에서 너무 많은 요청을 보냈다
    When trending()을 호출한다
    Then TrendkitRateLimitError가 발생한다
    And 에러 메시지에 대기 시간이 포함된다
    And retry_after 속성이 설정된다
```

### C. Glossary

| Term | Definition |
|------|------------|
| MCP | Model Context Protocol - AI 모델 도구 확장 프로토콜 |
| Token | LLM 입출력 단위, 비용 산정 기준 |
| Backend | 데이터 수집 방식 (RSS, Selenium, pytrends) |
