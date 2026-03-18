"""
ExpandTesting 登录练习页页面对象（Page Object Model）
站点: https://practice.expandtesting.com/login
公开测试账号: practice / SuperSecretPassword!

专为自动化测试设计，无 Bot 检测，无 CloudFlare 拦截，稳定可用。
"""
from core.base_page import BasePage

LOGIN_URL  = "https://practice.expandtesting.com/login"
SECURE_URL = "https://practice.expandtesting.com/secure"


class OpenCartLoginPage(BasePage):
    # ---------- 元素定位器 ----------
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BTN      = "#submit-login"
    # 登录失败时展示的 flash 错误提示
    ERROR_FLASH    = "#flash.alert-danger"
    # 登录成功后 /secure 页面的标志性元素
    LOGOUT_LINK    = "a[href='/logout']"
    SECURE_HEADING = "h1"

    # ---------- 动作 ----------
    def open(self):
        """导航到登录页，等待表单可见"""
        self.navigate(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        self.page.wait_for_selector(self.USERNAME_INPUT, state="visible", timeout=15000)

    def login(self, username: str, password: str):
        """填写用户名、密码并点击登录"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)
        self.page.wait_for_load_state("domcontentloaded", timeout=15000)

    # ---------- 断言辅助 ----------
    def is_login_successful(self) -> bool:
        """判断是否登录成功：URL 跳转到 /secure 且 Logout 链接可见"""
        try:
            self.page.wait_for_selector(self.LOGOUT_LINK, state="visible", timeout=8000)
            return "/secure" in self.current_url
        except Exception:
            return False

    def get_error_message(self) -> str:
        """获取登录失败的 flash 错误提示文本"""
        try:
            self.page.wait_for_selector(self.ERROR_FLASH, state="visible", timeout=8000)
            return self.get_text(self.ERROR_FLASH).strip()
        except Exception:
            return ""

    def has_any_error(self) -> bool:
        """页面出现任何错误提示则返回 True"""
        return bool(self.get_error_message())
