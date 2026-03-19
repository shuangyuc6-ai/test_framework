"""
性能压测：httpbin.org（稳定公开服务，无鉴权，适合并发基准测试）
兼测 GitHub API 只读接口（匿名限速 60次/小时，作为补充场景）

运行方式（无头批量模式，自动生成 HTML 报告）：
  locust -f perf/locust_httpbin.py --headless \
    -u 20 -r 5 -t 30s \
    --html reports/perf_report.html \
    --host https://httpbin.org

参数说明：
  -u  并发用户数
  -r  每秒用户增长速率（ramp-up）
  -t  测试持续时间
  --html  HTML 报告输出路径
"""
import json
import random
from locust import HttpUser, task, between, tag


class HttpBinUser(HttpUser):
    """
    模拟对 httpbin.org 的混合 API 请求
    wait_time: 每次任务后随机等待 0.5~2 秒，模拟真实用户节奏
    """
    host = "https://httpbin.org"
    wait_time = between(0.5, 2)

    # ------------------------------------------------------------------ #
    #  GET 场景
    # ------------------------------------------------------------------ #

    @task(5)
    @tag("get", "smoke")
    def get_anything(self):
        """GET /get —— 最基础的 GET 请求，权重最高"""
        with self.client.get("/get", catch_response=True) as resp:
            if resp.status_code == 200:
                data = resp.json()
                if "url" in data:
                    resp.success()
                else:
                    resp.failure("响应缺少 url 字段")
            else:
                resp.failure(f"状态码异常: {resp.status_code}")

    @task(3)
    @tag("get")
    def get_with_params(self):
        """GET /get?key=value —— 携带查询参数"""
        params = {"user": "locust_tester", "run": random.randint(1, 1000)}
        with self.client.get("/get", params=params, name="/get?params", catch_response=True) as resp:
            if resp.status_code == 200:
                args = resp.json().get("args", {})
                if args.get("user") == "locust_tester":
                    resp.success()
                else:
                    resp.failure("params 回显不匹配")
            else:
                resp.failure(f"状态码异常: {resp.status_code}")

    @task(2)
    @tag("get")
    def get_uuid(self):
        """GET /uuid —— 生成随机 UUID"""
        with self.client.get("/uuid", catch_response=True) as resp:
            if resp.status_code == 200 and "uuid" in resp.json():
                resp.success()
            else:
                resp.failure("uuid 字段缺失或状态码异常")

    @task(2)
    @tag("get")
    def get_headers(self):
        """GET /headers —— 回显请求头"""
        headers = {"X-Custom-Header": "locust-perf-test"}
        with self.client.get("/headers", headers=headers, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"状态码异常: {resp.status_code}")

    @task(1)
    @tag("get")
    def get_ip(self):
        """GET /ip —— 获取客户端 IP"""
        with self.client.get("/ip", catch_response=True) as resp:
            if resp.status_code == 200 and "origin" in resp.json():
                resp.success()
            else:
                resp.failure("origin 字段缺失")

    # ------------------------------------------------------------------ #
    #  POST 场景
    # ------------------------------------------------------------------ #

    @task(3)
    @tag("post")
    def post_json(self):
        """POST /post —— 发送 JSON 请求体，校验回显"""
        payload = {
            "test_id": random.randint(1000, 9999),
            "action": "perf_test",
            "timestamp": "2026-03-18T00:00:00Z",
        }
        with self.client.post(
            "/post",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                echoed = resp.json().get("json", {})
                if echoed.get("action") == "perf_test":
                    resp.success()
                else:
                    resp.failure("POST JSON 回显不匹配")
            else:
                resp.failure(f"状态码异常: {resp.status_code}")

    @task(1)
    @tag("post")
    def post_form(self):
        """POST /post —— 表单格式提交"""
        with self.client.post(
            "/post",
            data={"username": "locust", "action": "form_submit"},
            name="/post[form]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"状态码异常: {resp.status_code}")

    # ------------------------------------------------------------------ #
    #  状态码验证场景
    # ------------------------------------------------------------------ #

    @task(1)
    @tag("status")
    def check_status_200(self):
        """GET /status/200 —— 验证指定状态码返回"""
        with self.client.get("/status/200", name="/status/[code]", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"期望 200，实际 {resp.status_code}")

    # ------------------------------------------------------------------ #
    #  延迟场景（模拟慢接口）
    # ------------------------------------------------------------------ #

    @task(1)
    @tag("latency", "slow")
    def get_with_delay(self):
        """GET /delay/1 —— 模拟 1 秒延迟接口，测试超时容忍度"""
        with self.client.get("/delay/1", name="/delay/[n]", timeout=10, catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"延迟接口状态码异常: {resp.status_code}")
