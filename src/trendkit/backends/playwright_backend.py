"""Playwright backend for bulk trending data collection with stealth."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PlaywrightBackend:
    """Bulk trending data collection via Playwright with stealth (100+ items).

    Uses playwright-stealth to bypass bot detection:
    - navigator.webdriver is set to undefined
    - Browser fingerprints are spoofed
    - WebGL vendor/renderer spoofing
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self._stealth = None

    async def _setup_browser(self):
        """Setup browser with stealth mode."""
        try:
            from playwright.async_api import async_playwright
            from playwright_stealth import Stealth
        except ImportError as e:
            raise ImportError(
                "Playwright dependencies not installed. "
                "Install with: pip install trendkit[playwright]"
            ) from e

        self._stealth = Stealth()
        self._playwright = await self._stealth.use_async(async_playwright())

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )

        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )

        self._page = await self._context.new_page()
        logger.info("Playwright browser initialized with stealth mode")

    async def _fetch_trending_async(
        self,
        geo: str = "KR",
        hours: int = 168,
        limit: int = 100,
    ) -> list[dict]:
        """Async implementation of fetch_trending."""
        url = f"https://trends.google.co.kr/trending?geo={geo}&hours={hours}"
        pages = min((limit // 25) + 1, 4)  # Max 4 pages

        try:
            if not self._page:
                await self._setup_browser()

            logger.info(f"Navigating to {url}")
            await self._page.goto(url, wait_until="networkidle", timeout=30000)

            all_data = []

            for page_num in range(pages):
                logger.info(f"Processing page {page_num + 1}/{pages}")

                # Wait for table
                try:
                    await self._page.wait_for_selector("table", timeout=20000)
                except Exception:
                    if page_num == 0:
                        logger.warning("Table not found on first page")
                        return []
                    break

                await self._page.wait_for_timeout(2000)

                # Extract rows using JavaScript for better performance
                rows_data = await self._page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('tr');
                        const data = [];
                        rows.forEach((row, idx) => {
                            if (idx === 0) return; // Skip header
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 2) {
                                const keyword = cells[1]?.innerText?.trim();
                                const traffic = cells[2]?.innerText?.trim() || 'N/A';
                                if (keyword) {
                                    data.push({
                                        keyword: keyword,
                                        traffic: traffic.split('\\n')[0] || 'N/A'
                                    });
                                }
                            }
                        });
                        return data;
                    }
                """)

                for idx, row in enumerate(rows_data):
                    all_data.append({
                        "keyword": row["keyword"],
                        "rank": (page_num * 25) + idx + 1,
                        "traffic": row["traffic"],
                    })

                # Navigate to next page
                if page_num < pages - 1:
                    if not await self._click_next_page_async():
                        break

                if len(all_data) >= limit:
                    break

            return all_data[:limit]

        except Exception as e:
            logger.error(f"Error fetching trending: {e}")
            return []

    async def _click_next_page_async(self) -> bool:
        """Click next page button."""
        try:
            await self._page.wait_for_timeout(1000)
            await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._page.wait_for_timeout(1000)

            # Find and click next page button
            next_button = await self._page.query_selector(
                "xpath=//div[contains(text(), '다음 페이지로 이동')]/.."
                "/button[not(@disabled)]"
            )

            if not next_button:
                # Try English version
                next_button = await self._page.query_selector(
                    "xpath=//div[contains(text(), 'Go to next page')]/.."
                    "/button[not(@disabled)]"
                )

            if next_button:
                await next_button.click()
                await self._page.wait_for_timeout(3000)
                return True

            return False

        except Exception as e:
            logger.error(f"Error clicking next page: {e}")
            return False

    def fetch_trending(
        self,
        geo: str = "KR",
        hours: int = 168,
        limit: int = 100,
    ) -> list[dict]:
        """
        Fetch bulk trending data with pagination.

        Args:
            geo: Country code (e.g., "KR", "US", "JP")
            hours: Time period (4, 24, 48, 168)
            limit: Maximum items to fetch (max ~100)

        Returns:
            [{"keyword": "...", "rank": 1, "traffic": "..."}, ...]
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already in async context
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self._fetch_trending_async(geo, hours, limit))
                return future.result()
        else:
            return asyncio.run(self._fetch_trending_async(geo, hours, limit))

    def _close_sync(self):
        """Synchronously clean up resources without async."""
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

    async def _close_async(self):
        """Async close browser."""
        try:
            if self._page:
                await self._page.close()
        except Exception:
            pass
        self._page = None

        try:
            if self._context:
                await self._context.close()
        except Exception:
            pass
        self._context = None

        try:
            if self._browser:
                await self._browser.close()
        except Exception:
            pass
        self._browser = None

        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        self._playwright = None

    def close(self):
        """Close browser."""
        if not any([self._page, self._context, self._browser, self._playwright]):
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Can't run async close, just clear references
            self._close_sync()
        else:
            try:
                asyncio.run(self._close_async())
            except RuntimeError:
                # Fallback to sync cleanup
                self._close_sync()

    def __del__(self):
        # Only do sync cleanup in destructor to avoid async issues
        self._close_sync()


class AsyncPlaywrightBackend:
    """Async version of PlaywrightBackend for better performance."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self._stealth = None

    async def __aenter__(self):
        await self._setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _setup_browser(self):
        """Setup browser with stealth mode."""
        try:
            from playwright.async_api import async_playwright
            from playwright_stealth import Stealth
        except ImportError as e:
            raise ImportError(
                "Playwright dependencies not installed. "
                "Install with: pip install trendkit[playwright]"
            ) from e

        self._stealth = Stealth()
        self._playwright = await self._stealth.use_async(async_playwright())

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )

        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )

        self._page = await self._context.new_page()
        logger.info("Playwright browser initialized with stealth mode")

    async def fetch_trending(
        self,
        geo: str = "KR",
        hours: int = 168,
        limit: int = 100,
    ) -> list[dict]:
        """
        Fetch bulk trending data with pagination.

        Args:
            geo: Country code (e.g., "KR", "US", "JP")
            hours: Time period (4, 24, 48, 168)
            limit: Maximum items to fetch (max ~100)

        Returns:
            [{"keyword": "...", "rank": 1, "traffic": "..."}, ...]
        """
        url = f"https://trends.google.co.kr/trending?geo={geo}&hours={hours}"
        pages = min((limit // 25) + 1, 4)

        try:
            if not self._page:
                await self._setup_browser()

            logger.info(f"Navigating to {url}")
            await self._page.goto(url, wait_until="networkidle", timeout=30000)

            all_data = []

            for page_num in range(pages):
                logger.info(f"Processing page {page_num + 1}/{pages}")

                try:
                    await self._page.wait_for_selector("table", timeout=20000)
                except Exception:
                    if page_num == 0:
                        logger.warning("Table not found on first page")
                        return []
                    break

                await self._page.wait_for_timeout(2000)

                rows_data = await self._page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('tr');
                        const data = [];
                        rows.forEach((row, idx) => {
                            if (idx === 0) return;
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 2) {
                                const keyword = cells[1]?.innerText?.trim();
                                const traffic = cells[2]?.innerText?.trim() || 'N/A';
                                if (keyword) {
                                    data.push({
                                        keyword: keyword,
                                        traffic: traffic.split('\\n')[0] || 'N/A'
                                    });
                                }
                            }
                        });
                        return data;
                    }
                """)

                for idx, row in enumerate(rows_data):
                    all_data.append({
                        "keyword": row["keyword"],
                        "rank": (page_num * 25) + idx + 1,
                        "traffic": row["traffic"],
                    })

                if page_num < pages - 1:
                    if not await self._click_next_page():
                        break

                if len(all_data) >= limit:
                    break

            return all_data[:limit]

        except Exception as e:
            logger.error(f"Error fetching trending: {e}")
            return []

    async def _click_next_page(self) -> bool:
        """Click next page button."""
        try:
            await self._page.wait_for_timeout(1000)
            await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._page.wait_for_timeout(1000)

            next_button = await self._page.query_selector(
                "xpath=//div[contains(text(), '다음 페이지로 이동')]/.."
                "/button[not(@disabled)]"
            )

            if not next_button:
                next_button = await self._page.query_selector(
                    "xpath=//div[contains(text(), 'Go to next page')]/.."
                    "/button[not(@disabled)]"
                )

            if next_button:
                await next_button.click()
                await self._page.wait_for_timeout(3000)
                return True

            return False

        except Exception as e:
            logger.error(f"Error clicking next page: {e}")
            return False

    async def close(self):
        """Close browser."""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
