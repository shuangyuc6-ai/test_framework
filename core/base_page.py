"""
UI 自动化 POM 基类
- 封装 Playwright 常用操作
- 统一等待策略、截图、日志
"""
from playwright.sync_api import Page, Locator
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # ---------- 导航 ----------
    def navigate(self, url: str):
        logger.info(f"导航至: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    # ---------- 元素操作 ----------
    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str):
        logger.info(f"点击: {selector}")
        self.page.locator(selector).click()

    def fill(self, selector: str, text: str):
        logger.info(f"输入 [{text}] → {selector}")
        self.page.locator(selector).fill(text)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    # ---------- 等待 ----------
    def wait_for_selector(self, selector: str, timeout: int = 5000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_network_idle(self):
        self.page.wait_for_load_state("networkidle")

    # ---------- 截图 ----------
    def screenshot(self, name: str):
        path = f"reports/{name}.png"
        self.page.screenshot(path=path)
        logger.info(f"截图已保存: {path}")
        return path
