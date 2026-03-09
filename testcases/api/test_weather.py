"""
高德天气 API 接口测试用例
API 文档: https://lbs.amap.com/api/webservice/guide/api/weatherinfo
免费注册 Key: https://lbs.amap.com/

覆盖场景：正常城市查询、字段完整性、异常参数、多城市数据驱动
"""
import pytest
import allure
from core.http_client import HttpClient

# ⚠️  替换为你自己的高德 Key（免费注册即可获得）
AMAP_KEY = "your_amap_key_here"

WEATHER_PATH = "/v3/weather/weatherInfo"

# 城市编码参考: https://lbs.amap.com/api/webservice/download
CITY_CASES = [
    ("110000", "北京"),
    ("310000", "上海"),
    ("440100", "广州"),
    ("440300", "深圳"),
]


@allure.feature("高德天气 API")
class TestWeatherAPI:

    @allure.story("正常城市查询-数据驱动")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("city_code, city_name", CITY_CASES)
    def test_get_weather_success(self, weather_client: HttpClient, city_code, city_name):
        """正常城市编码应返回天气数据，状态码200，infocode为10000"""
        with allure.step(f"请求 {city_name}（{city_code}）天气"):
            resp = weather_client.get(WEATHER_PATH, params={
                "key": AMAP_KEY,
                "city": city_code,
                "extensions": "base"
            })

        with allure.step("断言 HTTP 状态码 200"):
            weather_client.assert_status(resp, 200)

        with allure.step("断言业务状态码 infocode=10000"):
            data = resp.json()
            assert data.get("infocode") == "10000", f"业务异常: {data}"

        with allure.step("断言返回 lives 天气数组非空"):
            lives = data.get("lives", [])
            assert len(lives) > 0, "lives 字段为空"

        with allure.step("断言关键字段完整性"):
            required_fields = ["city", "weather", "temperature", "humidity", "winddirection"]
            for field in required_fields:
                assert field in lives[0], f"缺少字段: {field}"

    @allure.story("响应字段完整性")
    def test_response_fields_completeness(self, weather_client: HttpClient):
        """校验顶层响应字段完整性"""
        resp = weather_client.get(WEATHER_PATH, params={
            "key": AMAP_KEY,
            "city": "110000",
        })
        weather_client.assert_status(resp, 200)
        for field in ["status", "info", "infocode", "lives"]:
            weather_client.assert_json_field(resp, field)

    @allure.story("异常参数-无效城市编码")
    def test_invalid_city_code(self, weather_client: HttpClient):
        """传入无效城市编码，接口应返回错误信息而非崩溃"""
        resp = weather_client.get(WEATHER_PATH, params={
            "key": AMAP_KEY,
            "city": "999999",
        })
        weather_client.assert_status(resp, 200)
        data = resp.json()
        # 无效编码时 infocode 不为 10000
        assert data.get("infocode") != "10000" or data.get("lives") == [], \
            "无效城市编码应返回错误或空数据"

    @allure.story("异常参数-缺少 Key")
    def test_missing_api_key(self, weather_client: HttpClient):
        """不传 Key 应返回鉴权失败"""
        resp = weather_client.get(WEATHER_PATH, params={"city": "110000"})
        weather_client.assert_status(resp, 200)
        data = resp.json()
        assert data.get("infocode") != "10000", "缺少 Key 时不应返回成功"

    @allure.story("预报天气查询")
    def test_forecast_weather(self, weather_client: HttpClient):
        """extensions=all 返回预报数据，应包含 forecasts 字段"""
        resp = weather_client.get(WEATHER_PATH, params={
            "key": AMAP_KEY,
            "city": "310000",
            "extensions": "all"
        })
        weather_client.assert_status(resp, 200)
        data = resp.json()
        if data.get("infocode") == "10000":
            assert "forecasts" in data, "预报模式应返回 forecasts 字段"
