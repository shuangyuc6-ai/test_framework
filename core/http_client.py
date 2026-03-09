"""
统一 HTTP 请求封装
- 自动记录请求/响应日志
- 支持 Session 保持（Token 自动关联）
- 统一响应断言入口
"""
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class HttpClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = requests.Session()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self.base_url + path
        logger.info(f"[{method.upper()}] {url}  params={kwargs.get('params')}  json={kwargs.get('json')}")
        response = self.session.request(method, url, timeout=10, **kwargs)
        logger.info(f"  ← {response.status_code}  {response.text[:200]}")
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def set_header(self, key: str, value: str):
        """设置全局请求头（如 Authorization Token）"""
        self.session.headers.update({key: value})

    def assert_status(self, response: requests.Response, expected: int = 200):
        assert response.status_code == expected, (
            f"期望状态码 {expected}，实际 {response.status_code}，响应：{response.text}"
        )

    def assert_json_field(self, response: requests.Response, field: str, expected_value=None):
        """断言响应 JSON 中某字段存在，可选校验值"""
        data = response.json()
        assert field in data, f"响应中缺少字段 [{field}]，实际响应：{data}"
        if expected_value is not None:
            assert data[field] == expected_value, (
                f"字段 [{field}] 期望 {expected_value}，实际 {data[field]}"
            )
