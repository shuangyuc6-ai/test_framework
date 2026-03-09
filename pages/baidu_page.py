"""
百度搜索页面对象（Page Object Model）
封装百度首页和搜索结果页的所有操作
"""
from core.base_page import BasePage

BAIDU_URL = "https://www.baidu.com"


class BaiduPage(BasePage):
    # ---------- 元素定位器 ----------
    SEARCH_INPUT   = "#kw"
    SEARCH_BTN     = "#su"
    RESULT_ITEMS   = ".result, .c-container"
    RESULT_TITLE   = "h3"
    NEWS_TAB       = "text=资讯"
    SUGGESTION_BOX = ".bdsug-s"

    # ---------- 动作 ----------
    def open(self):
        self.navigate(BAIDU_URL)

    def search(self, keyword: str):
        """输入关键词并提交搜索"""
        self.open()
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BTN)
        self.wait_network_idle()

    def get_result_count(self) -> int:
        return self.count(self.RESULT_ITEMS)

    def get_first_result_title(self) -> str:
        return self.find(self.RESULT_TITLE).first.inner_text()

    def is_on_result_page(self) -> bool:
        return "s?wd=" in self.current_url or "s?ie=" in self.current_url

    def search_and_screenshot(self, keyword: str) -> str:
        self.search(keyword)
        return self.screenshot(f"baidu_search_{keyword[:10]}")
