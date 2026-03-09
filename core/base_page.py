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
        # 等待网络完全空闲，确保动态页面（如百度）完全加载
        self.page.goto(url, wait_until="networkidle", timeout=30000)

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
        # 先等元素可见再点击，避免元素还未渲染就操作
        self.page.wait_for_selector(selector, state="visible", timeout=15000)
        self.page.locator(selector).click()

    def fill(self, selector: str, text: str):
        logger.info(f"输入 [{text}] -> {selector}")
        # 先等元素可见再输入，解决动态渲染页面元素未就绪的问题
        self.page.wait_for_selector(selector, state="visible", timeout=15000)
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