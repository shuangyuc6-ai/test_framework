"""
全局 Pytest Fixture 配置
- browser / page 生命周期管理
- 页面对象工厂
- HTTP 客户端
- 失败自动截图
"""
import os
import pytest
import allure
from playwright.sync_api import sync_playwright, Browser, Page

from core.http_client import HttpClient
from pages.baidu_page import BaiduPage
from pages.opencart_login_page import OpenCartLoginPage

os.makedirs("reports", exist_ok=True)


# ========================
#  浏览器 Fixtures
# ========================

@pytest.fixture(scope="session")
def browser():
    """整个测试会话共享一个浏览器实例"""
    with sync_playwright() as p:
        b: Browser = p.chromium.launch(headless=False)
        yield b
        b.close()


@pytest.fixture
def page(browser) -> Page:
    """每个测试用例独立 Page，测试后关闭"""
    p = browser.new_page()
    yield p
    p.close()


# ========================
#  页面对象 Fixtures
# ========================

@pytest.fixture
def baidu_page(page) -> BaiduPage:
    return BaiduPage(page)


@pytest.fixture
def opencart_login_page(page) -> OpenCartLoginPage:
    """OpenCart Demo 登录页面对象，每条用例独立 Page"""
    return OpenCartLoginPage(page)


# ========================
#  接口客户端 Fixtures
# ========================

@pytest.fixture(scope="session")
def http_client() -> HttpClient:
    return HttpClient()


@pytest.fixture(scope="session")
def weather_client() -> HttpClient:
    """高德天气 API 客户端"""
    return HttpClient(base_url="https://restapi.amap.com")


@pytest.fixture(scope="session")
def github_client() -> HttpClient:
    """GitHub REST API 客户端（无需 Key，匿名限速 60次/小时）"""
    client = HttpClient(base_url="https://api.github.com")
    client.set_header("Accept", "application/vnd.github+json")
    client.set_header("X-GitHub-Api-Version", "2022-11-28")
    return client


# ========================
#  失败自动截图 Hook
# ========================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page_fixture = item.funcargs.get("page") or item.funcargs.get("baidu_page")
        if page_fixture:
            _page = page_fixture.page if hasattr(page_fixture, "page") else page_fixture
            screenshot_path = f"reports/FAIL_{item.name}.png"
            try:
                _page.screenshot(path=screenshot_path, timeout=5000)
                allure.attach.file(
                    screenshot_path,
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception:
                pass  # 页面已不可用（超时/已关闭），跳过截图，避免 INTERNALERROR
