# PRD: trendkit

## Problem Statement

LLM 도구 호출에서 트렌드 데이터를 활용할 때 토큰 소비가 과다함.
기존 라이브러리들은 분석용으로 설계되어 LLM function calling에 비효율적.
다중 플랫폼(Google, Naver, YouTube) 통합 솔루션 부재.

## Goals

1. **토큰 최적화**: LLM tool call에 최적화된 최소 토큰 출력
2. **다중 플랫폼**: Google, Naver, YouTube 트렌드 통합
3. **직접 수집**: 외부 API 의존 없이 자체 스크래핑
4. **다중 인터페이스**: Python API, MCP Server, CLI 통합 지원

## Non-Goals

- 컨텐츠 생성 (downstream 책임)
- 데이터 시각화
- 데이터 저장/캐싱
- 35개+ 플랫폼 지원 (TrendRadar와 차별화)

## Solution

### 토큰 최적화 전략

| Format | Tokens/Item | Output |
|--------|-------------|--------|
| minimal | ~5 | `["kw1", "kw2"]` |
| standard | ~15 | `[{"keyword": "kw", "traffic": "5K+"}]` |
| full | ~100 | 뉴스 포함 전체 데이터 |

### 플랫폼별 구현

| Platform | Method | Status |
|----------|--------|--------|
| Google Trends | trendspyg RSS + pytrends | ✅ v0.1 |
| Naver Trends | DataLab API | 🔜 v0.2 |
| YouTube Trends | Data API v3 | 🔜 v0.3 |

### 핵심 API

```python
trending(geo, limit, format)  # 실시간 트렌딩
related(keyword, geo, limit)  # 연관 검색어
compare(keywords, geo, days)  # 키워드 비교
interest(keywords, geo, days) # 시계열 관심도
```

## Technical Decisions

### TrendRadar와 차별화

| 항목 | TrendRadar | trendkit |
|------|------------|----------|
| 데이터 소스 | newsnow API 의존 | 직접 수집 |
| 플랫폼 | 35개 (중국 중심) | 3개 (한국/글로벌) |
| 목적 | 뉴스/여론 모니터링 | LLM tool call |
| 출력 | 풍부한 컨텍스트 | 토큰 최적화 |

## Roadmap

- [x] v0.1 - Google Trends
- [ ] v0.2 - Naver Trends
- [ ] v0.3 - YouTube Trends

## Status

v0.1.0 구현 완료:
- [x] Core API (trending, related, compare, interest)
- [x] Google 백엔드 (RSS, pytrends, Selenium)
- [x] MCP Server
- [x] CLI
- [x] 테스트 8개 통과
