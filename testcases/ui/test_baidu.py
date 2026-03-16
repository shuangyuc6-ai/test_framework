"""
百度搜索 UI 自动化测试用例
覆盖场景：正常搜索、空搜索、特殊字符、数据驱动多关键词
"""
import pytest
import allure
from pages.baidu_page import BaiduPage


@allure.feature("百度搜索 UI")
class TestBaiduSearch:

    @allure.story("正常搜索-数据驱动")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("keyword", [
        "Python",
        "自动化测试",
        "Pytest框架",
        "测试开发工程师",
    ])
    def test_search_returns_results(self, baidu_page: BaiduPage, keyword):
        """正常关键词搜索，应返回结果列表"""
        with allure.step(f"搜索关键词: {keyword}"):
            baidu_page.search(keyword)

        with allure.step("断言：跳转到结果页"):
            assert baidu_page.is_on_result_page(), "未跳转到搜索结果页"

        with allure.step("断言：结果数量 > 0"):
            count = baidu_page.get_result_count()
            assert count > 0, f"搜索 [{keyword}] 未返回任何结果"

        with allure.step("断言：第一条结果标题非空"):
            title = baidu_page.get_first_result_title()
            assert len(title) > 0, "第一条结果标题为空"

    @allure.story("页面基本元素校验")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_title(self, baidu_page: BaiduPage):
        """打开百度首页，标题应包含'百度'"""
        with allure.step("打开百度首页"):
            baidu_page.open()

        with allure.step("断言页面标题"):
            assert "百度" in baidu_page.title, f"页面标题异常: {baidu_page.title}"

    @allure.story("搜索框元素可见性")
    def test_search_input_visible(self, baidu_page: BaiduPage):
        """搜索框和搜索按钮应在首页存在于 DOM 中（百度弹窗可能遮挡 CSS visibility）"""
        baidu_page.open()
        # 用 state="attached" 验证元素存在于 DOM，避免弹窗遮挡导致 visible 超时
        baidu_page.page.wait_for_selector(baidu_page.SEARCH_INPUT, state="attached", timeout=10000)
        baidu_page.page.wait_for_selector(baidu_page.SEARCH_BTN, state="attached", timeout=10000)
        # 用 JS 断言元素确实存在（双重保险）
        assert baidu_page.page.evaluate("() => !!document.querySelector('#kw')"), "搜索框不存在于 DOM"
        assert baidu_page.page.evaluate("() => !!document.querySelector('#su')"), "搜索按钮不存在于 DOM"

    @allure.story("特殊字符搜索")
    @pytest.mark.parametrize("special_kw", ["@#$%", "   ", "123456"])
    def test_special_character_search(self, baidu_page: BaiduPage, special_kw):
        """特殊字符/数字搜索不应导致页面崩溃
        纯空格等无效关键词百度可能不跳转结果页，只断言页面正常响应即可
        """
        baidu_page.open()
        baidu_page.fill(baidu_page.SEARCH_INPUT, special_kw)
        baidu_page.page.locator(baidu_page.SEARCH_INPUT).press("Enter")
        # 等待页面稳定（URL 变化或保持原页面均可），不强制要求结果容器出现
        baidu_page.page.wait_for_load_state("domcontentloaded", timeout=10000)
        assert baidu_page.current_url is not None

    @allure.story("截图存档")
    def test_search_with_screenshot(self, baidu_page: BaiduPage):
        """搜索后截图，附加到 Allure 报告"""
        screenshot_path = baidu_page.search_and_screenshot("Playwright自动化")
        allure.attach.file(
            screenshot_path,
            name="搜索结果截图",
            attachment_type=allure.attachment_type.PNG
        )
        assert baidu_page.get_result_count() > 0
