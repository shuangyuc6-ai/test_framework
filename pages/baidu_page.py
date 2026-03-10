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

    # 百度隐私/广告弹窗：列出已知所有变体选择器，逐一尝试
    _POPUP_SELECTORS = [
        "#s-def-map-close",                   # 地图弹窗关闭
        ".c-privacy-agree-btn",               # 隐私协议同意按钮
        "#s-top-loginbanner-close",           # 登录提示关闭
        ".samModel_agree_btn",                # 隐私协议变体
        "button:has-text('同意')",
        "button:has-text('确定')",
        "button:has-text('我知道了')",
        "a:has-text('同意')",
        "span:has-text('同意')",
    ]

    # ---------- 动作 ----------
    def open(self):
        self.navigate(BAIDU_URL)
        self._close_popup()
        # 等待搜索框可见，确认弹窗已关闭
        try:
            self.page.wait_for_selector(self.SEARCH_INPUT, state="visible", timeout=8000)
        except Exception:
            pass  # 后续操作用 force=True 兜底

    def _close_popup(self):
        """关闭百度可能出现的隐私协议/广告弹窗"""
        # 逐一尝试已知弹窗选择器
        for selector in self._POPUP_SELECTORS:
            try:
                btn = self.page.locator(selector).first
                btn.wait_for(state="visible", timeout=2000)
                btn.click(force=True)
                # 等待搜索框出现即认为弹窗已关闭
                self.page.wait_for_selector(self.SEARCH_INPUT, state="visible", timeout=3000)
                return
            except Exception:
                continue

        # 兜底1：尝试按 Escape 关闭弹窗
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_selector(self.SEARCH_INPUT, state="visible", timeout=3000)
            return
        except Exception:
            pass

        # 兜底2：JS 强制移除所有全屏遮罩层，直接让搜索框露出
        self.page.evaluate("""
            () => {
                // 移除固定定位的全屏遮罩（z-index 较高的 fixed/absolute 元素）
                document.querySelectorAll('div, section').forEach(el => {
                    const s = window.getComputedStyle(el);
                    const z = parseInt(s.zIndex) || 0;
                    if ((s.position === 'fixed' || s.position === 'absolute') && z > 100) {
                        el.remove();
                    }
                });
            }
        """)
        # JS 移除遮罩后再等一次，确认搜索框真正可见
        try:
            self.page.wait_for_selector(self.SEARCH_INPUT, state="visible", timeout=5000)
            return
        except Exception:
            pass

        # 兜底3：直接用 JS 强制设置搜索框 display/visibility，绕开所有 CSS 遮挡
        self.page.evaluate("""
            () => {
                const kw = document.querySelector('#kw');
                if (kw) {
                    kw.style.visibility = 'visible';
                    kw.style.display    = 'block';
                    kw.style.opacity    = '1';
                    // 同时把父元素链路上的隐藏属性清掉
                    let el = kw.parentElement;
                    while (el && el !== document.body) {
                        el.style.visibility = 'visible';
                        el.style.display    = el.style.display === 'none' ? 'block' : el.style.display;
                        el = el.parentElement;
                    }
                }
            }
        """)

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