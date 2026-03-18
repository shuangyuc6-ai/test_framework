"""
ExpandTesting 登录练习页 UI 自动化测试
站点: https://practice.expandtesting.com/login
测试数据: data/opencart_login.yaml

覆盖场景:
  1. 正常登录 —— 成功跳转到 Secure Area 页
  2. 错误凭据（数据驱动）—— 显示错误提示
  3. 空字段提交（数据驱动）—— 显示字段级错误或 alert
  4. 登录后跳转 URL 验证
  5. 登录后页面元素验证（退出链接可见）
"""
import yaml
import pytest
import allure
from pathlib import Path
from pages.opencart_login_page import OpenCartLoginPage

# ---------- 加载 YAML 测试数据 ----------
_DATA_FILE = Path(__file__).parents[2] / "data" / "opencart_login.yaml"
with open(_DATA_FILE, encoding="utf-8") as f:
    _DATA = yaml.safe_load(f)

_VALID   = _DATA["valid_credentials"]
_INVALID = _DATA["invalid_credentials"]
_EMPTY   = _DATA["empty_fields"]
_SECURE_PATH = _DATA["site"]["secure_path"]


def _invalid_ids():
    return [item["id"] for item in _INVALID]


def _empty_ids():
    return [item["id"] for item in _EMPTY]


# ---------- 测试类 ----------

@allure.feature("ExpandTesting 登录")
class TestExpandTestingLogin:

    # ------------------------------------------------------------------ #
    #  正常登录
    # ------------------------------------------------------------------ #

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, opencart_login_page: OpenCartLoginPage):
        """使用官方公开测试账号登录，应跳转到 Secure Area 页"""
        with allure.step("打开登录页"):
            opencart_login_page.open()

        with allure.step(f"输入正确账号: {_VALID['username']}"):
            opencart_login_page.login(_VALID["username"], _VALID["password"])

        with allure.step("断言：登录成功（Logout 链接可见）"):
            assert opencart_login_page.is_login_successful(), \
                f"登录失败，当前 URL: {opencart_login_page.current_url}"

        with allure.step(f"断言：URL 包含 {_SECURE_PATH}"):
            assert _SECURE_PATH in opencart_login_page.current_url, \
                f"未跳转到安全页，当前 URL: {opencart_login_page.current_url}"

    # ------------------------------------------------------------------ #
    #  登录后页面元素验证
    # ------------------------------------------------------------------ #

    @allure.story("登录后页面验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_redirect_and_elements(self, opencart_login_page: OpenCartLoginPage):
        """登录成功后页面应有退出链接，且不再显示登录按钮"""
        with allure.step("执行正常登录"):
            opencart_login_page.open()
            opencart_login_page.login(_VALID["username"], _VALID["password"])

        with allure.step("断言：Logout 链接存在"):
            assert opencart_login_page.is_login_successful(), "未找到 Logout 链接"

        with allure.step("断言：不再显示登录提交按钮"):
            login_btn_visible = opencart_login_page.is_visible(
                opencart_login_page.LOGIN_BTN
            )
            assert not login_btn_visible, "登录后仍显示登录按钮，可能未跳转"

    # ------------------------------------------------------------------ #
    #  错误密码/用户名 —— 数据驱动
    # ------------------------------------------------------------------ #

    @allure.story("错误凭据登录-数据驱动")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        _INVALID,
        ids=_invalid_ids(),
    )
    def test_login_with_invalid_credentials(
        self, opencart_login_page: OpenCartLoginPage, case: dict
    ):
        """错误用户名或密码应显示错误提示，不得登录成功"""
        with allure.step(f"场景: {case['desc']}"):
            opencart_login_page.open()
            opencart_login_page.login(case["username"], case["password"])

        with allure.step("断言：未登录成功"):
            assert not opencart_login_page.is_login_successful(), \
                f"错误凭据【{case['desc']}】不应登录成功"

        with allure.step("断言：页面显示错误提示"):
            error_msg = opencart_login_page.get_error_message()
            assert error_msg, \
                f"错误凭据【{case['desc']}】应出现错误提示，实际提示为空"

        with allure.step("记录错误提示内容"):
            allure.attach(error_msg, name="错误提示文本", attachment_type=allure.attachment_type.TEXT)

    # ------------------------------------------------------------------ #
    #  空字段提交 —— 数据驱动
    # ------------------------------------------------------------------ #

    @allure.story("空字段提交验证-数据驱动")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case",
        _EMPTY,
        ids=_empty_ids(),
    )
    def test_login_with_empty_fields(
        self, opencart_login_page: OpenCartLoginPage, case: dict
    ):
        """空字段提交应出现错误提示，不得登录成功"""
        with allure.step(f"场景: {case['desc']}"):
            opencart_login_page.open()
            opencart_login_page.login(case["username"], case["password"])

        with allure.step("断言：未登录成功"):
            assert not opencart_login_page.is_login_successful(), \
                f"空字段【{case['desc']}】不应登录成功"

        with allure.step("断言：页面存在错误提示"):
            has_error = opencart_login_page.has_any_error()
            assert has_error, \
                f"空字段【{case['desc']}】应显示错误提示，当前 URL: {opencart_login_page.current_url}"

    # ------------------------------------------------------------------ #
    #  截图存档
    # ------------------------------------------------------------------ #

    @allure.story("登录成功截图存档")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_success_screenshot(self, opencart_login_page: OpenCartLoginPage):
        """登录成功后截图，附加到 Allure 报告"""
        opencart_login_page.open()
        opencart_login_page.login(_VALID["username"], _VALID["password"])
        assert opencart_login_page.is_login_successful(), "登录失败，无法截图"

        with allure.step("截图并附加到报告"):
            path = opencart_login_page.screenshot("expandtesting_login_success")
            allure.attach.file(
                path,
                name="登录成功截图",
                attachment_type=allure.attachment_type.PNG,
            )
