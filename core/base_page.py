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
        # 等待元素挂载到 DOM（不要求可见，避免被弹窗遮挡时超时）
        self.page.wait_for_selector(selector, state="attached", timeout=15000)
        # force=True：跳过可见性检查，直接点击；适用于元素被弹窗遮挡的场景
        self.page.locator(selector).click(force=True)

    def fill(self, selector: str, text: str):
        logger.info(f"输入 [{text}] -> {selector}")
        # 等待元素挂载到 DOM（不要求可见，避免被遮挡时超时）
        self.page.wait_for_selector(selector, state="attached", timeout=15000)
        # force=True：跳过可见性检查，直接填充；适用于元素被弹窗遮挡的场景
        self.page.locator(selector).fill(text, force=True)

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
        # timeout=10000：防止页面字体/资源加载卡住导致截图超时
        self.page.screenshot(path=path, timeout=10000)
        logger.info(f"截图已保存: {path}")
        return path