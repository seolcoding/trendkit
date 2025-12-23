# PRD: Google Trends API

## Problem Statement

LLM 도구 호출에서 Google Trends 데이터를 활용할 때 토큰 소비가 과다함.
기존 라이브러리들은 분석용으로 설계되어 LLM function calling에 비효율적.

## Goals

1. **토큰 최적화**: LLM tool call에 최적화된 최소 토큰 출력
2. **다중 인터페이스**: Python API, MCP Server, CLI 통합 지원
3. **백엔드 조합**: 용도별 최적 데이터 소스 선택

## Non-Goals

- 컨텐츠 생성 (downstream 책임)
- 데이터 시각화
- 데이터 저장/캐싱

## Solution

### 토큰 최적화 전략

| Format | Tokens/Item | Output |
|--------|-------------|--------|
| minimal | ~5 | `["kw1", "kw2"]` |
| standard | ~15 | `[{"keyword": "kw", "traffic": "5K+"}]` |
| full | ~100 | 뉴스 포함 전체 데이터 |

### 백엔드 조합

| Use Case | Backend | Speed | Volume |
|----------|---------|-------|--------|
| 실시간 트렌딩 | trendspyg RSS | Fast | 10-20 |
| 벌크 수집 | Selenium | Slow | 100+ |
| 분석 기능 | pytrends | Medium | N/A |

### 핵심 API

```python
trending(geo, limit, format)  # 실시간 트렌딩
related(keyword, geo, limit)  # 연관 검색어
compare(keywords, geo, days)  # 키워드 비교
interest(keywords, geo, days) # 시계열 관심도
```

## Technical Decisions

### pytrends 제한사항

- `trending_searches()` 404 오류 → trendspyg RSS 대체
- `interest_over_time()`, `related_queries()` 정상 동작

### 의존성 분리

```toml
[project.optional-dependencies]
selenium = ["selenium>=4.0.0"]
mcp = ["mcp>=1.0.0"]
cli = ["typer>=0.9.0", "rich>=13.0.0"]
```

## Success Metrics

- minimal format 사용 시 토큰 80% 감소
- API 응답시간: RSS < 1초, pytrends < 3초
- MCP 도구 4종 완성

## Status

v0.1.0 구현 완료:
- [x] Core API (trending, related, compare, interest)
- [x] 3개 백엔드 (RSS, pytrends, Selenium)
- [x] MCP Server
- [x] CLI
