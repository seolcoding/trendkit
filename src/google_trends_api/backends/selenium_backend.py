"""Selenium backend for bulk trending data collection."""

import time
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class SeleniumBackend:
    """Bulk trending data collection via Selenium (100+ items)."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        """Setup Chrome driver with options."""
        from selenium import webdriver

        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=options)

    def fetch_trending(
        self,
        geo: str = "KR",
        hours: int = 168,
        limit: int = 100,
    ) -> list[dict]:
        """
        Fetch bulk trending data with pagination.

        Args:
            geo: Country code
            hours: Time period (4, 24, 48, 168)
            limit: Maximum items to fetch (max ~100)

        Returns:
            [{"keyword": "...", "rank": 1, "traffic": "..."}, ...]
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException

        url = f"https://trends.google.co.kr/trending?geo={geo}&hours={hours}"
        pages = min((limit // 25) + 1, 4)  # Max 4 pages

        try:
            if not self.driver:
                self._setup_driver()

            logger.info(f"Navigating to {url}")
            self.driver.get(url)

            wait = WebDriverWait(self.driver, 20)
            all_data = []

            for page_num in range(pages):
                logger.info(f"Processing page {page_num + 1}/{pages}")

                # Wait for table
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
                except TimeoutException:
                    if page_num == 0:
                        logger.warning("Table not found on first page")
                        return []
                    break

                time.sleep(2)

                # Extract rows
                rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")

                for idx, row in enumerate(rows):
                    if idx == 0:  # Skip header
                        continue

                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        if len(cells) >= 2:
                            keyword = cells[1].text.strip()
                            if keyword:
                                traffic = cells[2].text.strip() if len(cells) > 2 else "N/A"
                                all_data.append({
                                    "keyword": keyword,
                                    "rank": (page_num * 25) + idx,
                                    "traffic": traffic.split("\n")[0] if traffic else "N/A",
                                })
                    except Exception as e:
                        logger.warning(f"Error processing row: {e}")
                        continue

                # Navigate to next page
                if page_num < pages - 1:
                    if not self._click_next_page():
                        break

                if len(all_data) >= limit:
                    break

            return all_data[:limit]

        except Exception as e:
            logger.error(f"Error fetching trending: {e}")
            return []

    def _click_next_page(self) -> bool:
        """Click next page button."""
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        try:
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            next_div = self.driver.find_element(
                By.XPATH, "//div[contains(text(), '다음 페이지로 이동')]"
            )
            button = next_div.find_element(By.XPATH, "..").find_element(By.TAG_NAME, "button")

            if button.get_attribute("disabled"):
                return False

            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
            return True

        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error clicking next page: {e}")
            return False

    def close(self):
        """Close browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close()
