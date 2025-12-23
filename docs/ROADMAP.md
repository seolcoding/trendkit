# trendkit Roadmap

> Token-Optimized Trends for AI

## Overview

```
v0.1.0 (현재)     v1.0.0           v1.1.0           v1.2.0
    │               │                │                │
    ▼               ▼                ▼                ▼
 [Beta]         [Stable]         [Enhanced]       [Extended]
 Core API       브랜딩/문서       캐시/안정성       통합/확장
```

---

## Current Status: v0.1.0 (Beta)

### Completed Features

- [x] Core API (`trending`, `trending_bulk`, `related`, `compare`, `interest`)
- [x] Multiple backends (RSS, Selenium, pytrends)
- [x] Token-optimized output formats (minimal/standard/full)
- [x] CLI interface (`trendkit` command)
- [x] MCP server (`trendkit-mcp` command)
- [x] Enriched bulk export (news, images, related queries)
- [x] PyPI package deployment
- [x] GitHub Actions CI/CD

---

## v1.0.0 — Stable Release

**Theme**: 브랜딩 확립 & 문서화 완성

**Target**: 2025 Q1

### Branding & Identity

- [ ] **태그라인 적용**: "Token-Optimized Trends for AI"
- [ ] **로고 제작**: SVG 로고 (📈⚡ 컨셉)
- [ ] **배지 추가**: PyPI, Python, MCP, License badges
- [ ] **Social Preview**: GitHub og:image 설정

### Documentation

- [ ] **Why trendkit?** 섹션 추가
- [ ] **경쟁 비교표** 작성 (vs pytrends, SerpAPI)
- [ ] **Use Case 문서화**
  - [ ] AI 뉴스봇 예시
  - [ ] 콘텐츠 추천 시스템
  - [ ] 마케팅 트렌드 분석
- [ ] **API 문서 완성** (docstrings → mkdocs)
- [ ] **CONTRIBUTING.md** 작성

### Quality

- [ ] **테스트 커버리지 80%+**
- [ ] **타입 힌트 100%**
- [ ] **에러 메시지 개선**

### Distribution

- [ ] **awesome-mcp 등록**
- [ ] **awesome-python 등록**
- [ ] **DEV.to 소개글 작성**

---

## v1.1.0 — Enhanced

**Theme**: 안정성 & 성능 개선

**Target**: 2025 Q2

### Caching Layer

- [ ] **인메모리 캐시** (기본)
  ```python
  trending(cache=True, ttl=300)  # 5분 캐시
  ```
- [ ] **파일 캐시** (선택)
  ```python
  trending(cache="file", cache_dir="~/.trendkit")
  ```
- [ ] **Redis 캐시** (선택, 고급)

### Error Handling

- [ ] **Rate Limit 처리**
  - 자동 재시도 (exponential backoff)
  - 사용자 알림
- [ ] **Timeout 처리**
  - 설정 가능한 timeout
  - 부분 결과 반환 옵션
- [ ] **Network Error 복구**

### Multi-Geo Support

- [ ] **Geo 확장 테스트**
  - US (미국)
  - JP (일본)
  - GB (영국)
  - DE (독일)
- [ ] **Geo별 기본값 최적화**

### Logging & Debugging

- [ ] **로깅 시스템**
  ```python
  import trendkit
  trendkit.set_log_level("DEBUG")
  ```
- [ ] **Verbose 모드**
  ```bash
  trendkit trend --verbose
  ```

---

## v1.2.0 — Extended

**Theme**: 생태계 통합 & 기능 확장

**Target**: 2025 Q3

### LangChain Integration

- [ ] **langchain-community Tool**
  ```python
  from langchain_community.tools import TrendkitTool
  tool = TrendkitTool()
  ```
- [ ] **LangChain 문서 PR**

### Automation Features

- [ ] **스케줄러**
  ```python
  from trendkit import Scheduler
  s = Scheduler()
  s.every(hours=1).do(trending, output="trends.json")
  s.run()
  ```
- [ ] **Webhook 알림**
  ```python
  trending(
      webhook="https://hooks.slack.com/...",
      alert_if=lambda x: x["traffic"] > "10만+"
  )
  ```

### Data Persistence

- [ ] **히스토리 저장**
  ```python
  trending(save_history=True)  # ~/.trendkit/history.db
  ```
- [ ] **트렌드 비교**
  ```python
  from trendkit import history
  history.compare("2024-12-01", "2024-12-24")
  ```

### UI/Dashboard (Optional)

- [ ] **Streamlit 대시보드**
  ```bash
  trendkit dashboard
  ```

---

## v2.0.0 — Future Vision

**Theme**: 플랫폼화

### Ideas (Unplanned)

- [ ] 다중 소스 통합 (Twitter Trends, Reddit, etc.)
- [ ] AI 기반 트렌드 예측
- [ ] 실시간 스트리밍 API
- [ ] SaaS 버전 (hosted)
- [ ] Browser Extension

---

## Priority Matrix

```
                    Impact
                 Low    High
              ┌───────┬───────┐
        High  │ P2    │ P0    │  ← Do First
   Effort     ├───────┼───────┤
        Low   │ P3    │ P1    │  ← Quick Wins
              └───────┴───────┘

P0: 브랜딩, 문서화 (v1.0)
P1: 캐시, awesome 등록
P2: LangChain, 스케줄러
P3: 대시보드
```

---

## Testing Strategy

### Test Pyramid

```
        ╱╲
       ╱  ╲      E2E Tests (5%)
      ╱────╲     - Claude Desktop 연동
     ╱      ╲    - CLI 전체 워크플로우
    ╱────────╲
   ╱          ╲  Integration Tests (25%)
  ╱────────────╲ - Google Trends 실제 호출
 ╱              ╲- MCP 서버 도구 호출
╱────────────────╲
                  Unit Tests (70%)
                  - 백엔드별 단위 테스트
                  - Output format 변환
                  - 파라미터 유효성 검증
```

### Test Categories

| Category | Coverage Target | Tools |
|----------|-----------------|-------|
| Unit Tests | > 80% | pytest, pytest-cov |
| Integration | > 60% | pytest-asyncio |
| E2E | Manual | Claude Desktop |
| Performance | Baseline | pytest-benchmark |

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=trendkit --cov-report=html

# Unit tests only
uv run pytest tests/unit/

# Integration tests (requires network)
uv run pytest tests/integration/ -m "not slow"

# Performance benchmark
uv run pytest tests/benchmark/ --benchmark-only
```

---

## Breaking Changes

### v1.0.0 (from v0.1.0)

- **No breaking changes** - First stable release
- All v0.1.0 APIs remain compatible

### v1.1.0 (planned)

- **New**: `TrendkitError` exception hierarchy introduced
- **New**: `cache` parameter added to all API functions
- **Deprecation**: None

### v1.2.0 (planned)

- **New**: `Scheduler` class for automated collection
- **Deprecation warning**: `output` parameter file extension auto-detection

### Migration Guides

**v0.1.0 → v1.0.0**
```python
# No changes required
# All existing code works as-is
```

**v1.0.0 → v1.1.0**
```python
# Before: Unhandled exceptions
result = trending()

# After: Proper error handling (recommended)
from trendkit import trending, TrendkitRateLimitError

try:
    result = trending()
except TrendkitRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
```

---

## Contributing

로드맵 항목에 기여하고 싶다면:

1. 관심 있는 항목에 Issue 생성
2. `[Roadmap]` 태그 추가
3. 구현 계획 논의
4. PR 제출

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## Changelog

### v0.1.0 (2024-12-23)

- Initial release
- Core API implementation
- CLI and MCP server
- PyPI deployment
