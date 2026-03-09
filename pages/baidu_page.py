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
    # 百度隐私协议弹窗的关闭按钮（出现时需要先关掉）
    # 多个选择器用逗号分隔，兼容百度不同时期的弹窗 DOM 结构
    PRIVACY_BTN    = "#s-def-map-close"
    PRIVACY_BTN2   = ".c-privacy-agree-btn"
    PRIVACY_BTN3   = "button:has-text('同意'), button:has-text('确定'), button:has-text('我知道了')"

    # ---------- 动作 ----------
    def open(self):
        self.navigate(BAIDU_URL)
        self._close_popup()

    def _close_popup(self):
        """关闭百度可能出现的隐私协议/广告弹窗，不出现则跳过"""
        for selector in [self.PRIVACY_BTN, self.PRIVACY_BTN2, self.PRIVACY_BTN3]:
            try:
                btn = self.page.locator(selector).first
                btn.wait_for(state="visible", timeout=3000)
                btn.click(force=True)
                btn.wait_for(state="hidden", timeout=3000)
                return  # 成功关闭，退出
            except Exception:
                continue  # 当前选择器未匹配，尝试下一个

    def search(self, keyword: str):
        """输入关键词并提交搜索（用 Enter 键提交，绕开按钮被遮挡的问题）"""
        self.open()
        self.fill(self.SEARCH_INPUT, keyword)
        # 用 Enter 键提交，比点击 #su 更稳定（不受弹窗遮挡影响）
        self.page.locator(self.SEARCH_INPUT).press("Enter")
        # 等待结果容器出现，比 networkidle 更可靠（百度有持续后台请求）
        self.page.wait_for_selector(self.RESULT_ITEMS, state="attached", timeout=15000)

    def get_result_count(self) -> int:
        return self.count(self.RESULT_ITEMS)

    def get_first_result_title(self) -> str:
        return self.find(self.RESULT_TITLE).first.inner_text()

    def is_on_result_page(self) -> bool:
        return "s?wd=" in self.current_url or "s?ie=" in self.current_url

    def search_and_screenshot(self, keyword: str) -> str:
        self.search(keyword)
        return self.screenshot(f"baidu_search_{keyword[:10]}")