"""
GitHub REST API 接口测试
API 文档: https://docs.github.com/en/rest
公开 API 无需 Key（匿名限速 60次/小时，足够测试使用）

覆盖场景：
  - 搜索仓库（关键词、排序、字段完整性）
  - 获取用户信息（公开字段、用户不存在）
  - 获取仓库详情（知名项目、字段完整性）
  - 获取仓库 Topics 标签
  - 获取组织信息
  - 响应头校验（Rate-Limit、Content-Type）
"""
import pytest
import allure
from core.http_client import HttpClient

GITHUB_BASE = "https://api.github.com"

# 知名公开仓库，长期稳定存在
KNOWN_OWNER = "torvalds"
KNOWN_REPO  = "linux"
KNOWN_USER  = "torvalds"
KNOWN_ORG   = "github"


@allure.feature("GitHub REST API")
class TestGitHubSearchRepo:
    """仓库搜索接口"""

    @allure.story("按关键词搜索仓库")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("keyword", ["pytest", "playwright", "requests"])
    def test_search_repo_by_keyword(self, github_client: HttpClient, keyword):
        """按关键词搜索仓库，应返回结果且字段完整"""
        with allure.step(f"搜索仓库关键词: {keyword}"):
            resp = github_client.get("/search/repositories", params={
                "q": keyword,
                "per_page": 5,
                "sort": "stars",
                "order": "desc",
            })

        with allure.step("断言 HTTP 状态码 200"):
            github_client.assert_status(resp, 200)

        with allure.step("断言返回结果数量 > 0"):
            data = resp.json()
            assert data.get("total_count", 0) > 0, f"关键词 [{keyword}] 未搜索到任何仓库"
            items = data.get("items", [])
            assert len(items) > 0, "items 列表为空"

        with allure.step("断言仓库核心字段完整性"):
            required_fields = ["id", "name", "full_name", "html_url",
                               "description", "stargazers_count", "language"]
            for field in required_fields:
                assert field in items[0], f"仓库对象缺少字段: {field}"

        with allure.step("断言搜索结果按星数降序排列"):
            if len(items) >= 2:
                assert items[0]["stargazers_count"] >= items[1]["stargazers_count"], \
                    "搜索结果未按星数降序排列"

    @allure.story("搜索结果分页")
    def test_search_repo_pagination(self, github_client: HttpClient):
        """per_page 参数生效，返回条数与请求一致"""
        resp = github_client.get("/search/repositories", params={
            "q": "python",
            "per_page": 3,
        })
        github_client.assert_status(resp, 200)
        items = resp.json().get("items", [])
        assert len(items) == 3, f"期望返回 3 条，实际返回 {len(items)} 条"

    @allure.story("空关键词搜索")
    def test_search_repo_empty_keyword(self, github_client: HttpClient):
        """空关键词应返回 422 参数错误"""
        resp = github_client.get("/search/repositories", params={"q": ""})
        assert resp.status_code == 422, \
            f"空关键词期望 422，实际 {resp.status_code}"


@allure.feature("GitHub REST API")
class TestGitHubUser:
    """用户信息接口"""

    @allure.story("获取已知公开用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_known_user(self, github_client: HttpClient):
        """获取 torvalds 用户信息，字段应完整"""
        with allure.step(f"请求用户: {KNOWN_USER}"):
            resp = github_client.get(f"/users/{KNOWN_USER}")

        with allure.step("断言状态码 200"):
            github_client.assert_status(resp, 200)

        with allure.step("断言核心字段"):
            data = resp.json()
            required = ["login", "id", "avatar_url", "html_url",
                        "type", "public_repos", "followers", "created_at"]
            for field in required:
                assert field in data, f"用户对象缺少字段: {field}"

        with allure.step("断言 login 与请求一致"):
            assert data["login"].lower() == KNOWN_USER.lower(), \
                f"login 不一致: {data['login']}"

        with allure.step("断言用户类型为 User"):
            assert data["type"] == "User", f"类型异常: {data['type']}"

    @allure.story("获取不存在的用户")
    def test_get_nonexistent_user(self, github_client: HttpClient):
        """不存在的用户名应返回 404"""
        resp = github_client.get("/users/this-user-definitely-does-not-exist-xyzxyz123")
        assert resp.status_code == 404, \
            f"不存在用户期望 404，实际 {resp.status_code}"

    @allure.story("获取用户公开仓库列表")
    def test_get_user_repos(self, github_client: HttpClient):
        """获取用户仓库列表，应为数组且每项含仓库基本信息"""
        resp = github_client.get(f"/users/{KNOWN_USER}/repos", params={"per_page": 5})
        github_client.assert_status(resp, 200)
        repos = resp.json()
        assert isinstance(repos, list), "响应应为数组"
        assert len(repos) > 0, "仓库列表为空"
        for field in ["id", "name", "full_name", "html_url"]:
            assert field in repos[0], f"仓库对象缺少字段: {field}"


@allure.feature("GitHub REST API")
class TestGitHubRepo:
    """仓库详情接口"""

    @allure.story("获取知名仓库详情")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_known_repo(self, github_client: HttpClient):
        """获取 torvalds/linux 仓库详情，字段应完整"""
        with allure.step(f"请求仓库: {KNOWN_OWNER}/{KNOWN_REPO}"):
            resp = github_client.get(f"/repos/{KNOWN_OWNER}/{KNOWN_REPO}")

        with allure.step("断言状态码 200"):
            github_client.assert_status(resp, 200)

        with allure.step("断言仓库核心字段"):
            data = resp.json()
            required = ["id", "name", "full_name", "owner", "html_url",
                        "description", "stargazers_count", "forks_count",
                        "open_issues_count", "default_branch", "created_at"]
            for field in required:
                assert field in data, f"仓库对象缺少字段: {field}"

        with allure.step("断言 full_name 与请求路径一致"):
            assert data["full_name"].lower() == f"{KNOWN_OWNER}/{KNOWN_REPO}".lower(), \
                f"full_name 不一致: {data['full_name']}"

        with allure.step("断言星数 > 100000（知名仓库）"):
            assert data["stargazers_count"] > 100_000, \
                f"linux 仓库星数异常: {data['stargazers_count']}"

    @allure.story("获取不存在的仓库")
    def test_get_nonexistent_repo(self, github_client: HttpClient):
        """不存在的仓库应返回 404"""
        resp = github_client.get("/repos/this-owner-xyz/this-repo-xyz-not-exist")
        assert resp.status_code == 404, \
            f"不存在仓库期望 404，实际 {resp.status_code}"

    @allure.story("获取仓库 Topics 标签")
    def test_get_repo_topics(self, github_client: HttpClient):
        """获取 torvalds/linux 的 topics，响应应包含 names 数组"""
        resp = github_client.get(
            f"/repos/{KNOWN_OWNER}/{KNOWN_REPO}/topics",
            headers={"Accept": "application/vnd.github.mercy-preview+json"},
        )
        github_client.assert_status(resp, 200)
        data = resp.json()
        assert "names" in data, "topics 响应缺少 names 字段"
        assert isinstance(data["names"], list), "names 应为数组"

    @allure.story("获取仓库 Contributors")
    def test_get_repo_contributors(self, github_client: HttpClient):
        """获取仓库贡献者列表，返回数组且字段完整
        注：torvalds/linux 贡献者数量过大，GitHub API 会返回 403，
        改用 pytest/pytest（规模适中的知名仓库）
        """
        resp = github_client.get(
            "/repos/pytest-dev/pytest/contributors",
            params={"per_page": 3, "anon": "false"},
        )
        github_client.assert_status(resp, 200)
        contributors = resp.json()
        assert isinstance(contributors, list), "响应应为数组"
        assert len(contributors) > 0, "贡献者列表为空"
        for field in ["login", "id", "avatar_url", "contributions"]:
            assert field in contributors[0], f"贡献者对象缺少字段: {field}"


@allure.feature("GitHub REST API")
class TestGitHubOrg:
    """组织信息接口"""

    @allure.story("获取已知组织信息")
    def test_get_known_org(self, github_client: HttpClient):
        """获取 github 组织信息，字段应完整"""
        resp = github_client.get(f"/orgs/{KNOWN_ORG}")
        github_client.assert_status(resp, 200)
        data = resp.json()
        required = ["login", "id", "avatar_url", "html_url",
                    "type", "public_repos", "created_at"]
        for field in required:
            assert field in data, f"组织对象缺少字段: {field}"
        assert data["type"] == "Organization", f"type 异常: {data['type']}"

    @allure.story("获取不存在的组织")
    def test_get_nonexistent_org(self, github_client: HttpClient):
        """不存在的组织应返回 404"""
        resp = github_client.get("/orgs/this-org-definitely-not-exist-xyzxyz")
        assert resp.status_code == 404, \
            f"不存在组织期望 404，实际 {resp.status_code}"


@allure.feature("GitHub REST API")
class TestGitHubResponseHeaders:
    """响应头校验"""

    @allure.story("Rate-Limit 响应头存在")
    def test_rate_limit_headers(self, github_client: HttpClient):
        """GitHub API 响应头应包含 Rate-Limit 相关字段"""
        resp = github_client.get(f"/users/{KNOWN_USER}")
        github_client.assert_status(resp, 200)
        for header in ["x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset"]:
            assert header in resp.headers, f"响应头缺少: {header}"
        remaining = int(resp.headers.get("x-ratelimit-remaining", -1))
        assert remaining >= 0, "x-ratelimit-remaining 值异常"

    @allure.story("Content-Type 为 JSON")
    def test_content_type_is_json(self, github_client: HttpClient):
        """API 响应 Content-Type 应为 application/json"""
        resp = github_client.get(f"/repos/{KNOWN_OWNER}/{KNOWN_REPO}")
        github_client.assert_status(resp, 200)
        content_type = resp.headers.get("content-type", "")
        assert "application/json" in content_type, \
            f"Content-Type 异常: {content_type}"
