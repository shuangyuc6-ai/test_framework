#  Web AutoTest Framework

> 一个基于 **Pytest + Playwright + Requests + Allure** 的 Web 端到端自动化测试框架
> 覆盖 UI 自动化、接口测试、数据驱动、失败截图、CI/CD 全链路实践

![CI](https://github.com/your-username/web-autotest-framework/actions/workflows/autotest.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Pytest](https://img.shields.io/badge/Pytest-8.x-green)

---

## 框架架构

```
web-autotest-framework/
├── core/                    # 框架核心层
│   ├── base_page.py         # UI POM 基类（封装 Playwright 操作）
│   └── http_client.py       # 接口请求封装（Session / 断言 / 日志）
├── pages/                   # 页面对象层
│   └── baidu_page.py        # 百度搜索页面对象
├── testcases/               # 测试用例层
│   ├── ui/
│   │   └── test_baidu.py    # 百度 UI 测试（参数化 / 截图）
│   └── api/
│       └── test_weather.py  # 高德天气接口测试
├── data/
│   └── test_data.yaml       # 测试数据配置
├── utils/
│   ├── faker_helper.py      # Mock 数据生成
│   └── logger.py            # 统一日志
├── .github/workflows/
│   └── autotest.yml         # GitHub Actions CI 配置
├── conftest.py              # 全局 Fixture + 失败自动截图
├── pytest.ini               # Pytest 配置
└── requirements.txt
```

---

## 框架特性

| 特性 | 说明 |
|------|------|
| POM 设计模式 | 页面与用例解耦，维护成本低 |
| 数据驱动 | YAML + Parametrize，用例与数据分离 |
| 失败自动截图 | 用例失败时自动截图并附加到 Allure 报告 |
| 接口断言封装 | 统一状态码 / 字段断言，减少重复代码 |
| Allure 可视化报告 | 包含步骤、截图、请求/响应详情 |
| CI/CD | GitHub Actions 自动触发，结果发布至 GitHub Pages |
| Mock 数据 | 基于 Faker 生成中文测试数据 |

---

## 快速上手

### 1. 克隆项目

```bash
git clone https://github.com/your-username/web-autotest-framework.git
cd web-autotest-framework
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 配置 API Key（接口测试需要）

在 `testcases/api/test_weather.py` 中替换：
```python
AMAP_KEY = "your_amap_key_here"  # 前往 https://lbs.amap.com 免费注册
```

### 4. 运行测试

```bash
# 运行全部测试
pytest

# 只运行 UI 测试
pytest testcases/ui -v

# 只运行接口测试
pytest testcases/api -v

# 运行并生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 测试报告示例

运行后执行 `allure serve reports/allure-results` 可查看如下报告：

- 测试用例通过/失败统计
- 失败截图自动附加
- 接口请求/响应详情
- 每次 CI 运行历史趋势

---

## 测试用例覆盖

### UI 测试（百度搜索）

| 用例 | 场景 |
|------|------|
| test_search_returns_results | 正常关键词搜索，数据驱动 4 组 |
| test_homepage_title | 首页标题包含"百度" |
| test_search_input_visible | 搜索框/按钮可见性 |
| test_special_character_search | 特殊字符不崩溃 |
| test_search_with_screenshot | 搜索截图存档 |

### 接口测试（高德天气 API）

| 用例 | 场景 |
|------|------|
| test_get_weather_success | 多城市数据驱动查询 |
| test_response_fields_completeness | 响应字段完整性 |
| test_invalid_city_code | 无效城市编码容错 |
| test_missing_api_key | 缺少 Key 鉴权校验 |
| test_forecast_weather | 预报天气查询 |

---

## 技术栈

- **Python 3.12**
- **Pytest 9.0.2** — 测试框架（Fixture / Parametrize / Hook）
- **Playwright** — 现代 UI 自动化
- **Requests** — HTTP 接口测试
- **Allure** — 可视化测试报告
- **Faker** — Mock 数据生成
- **GitHub Actions** — CI/CD 自动化

---
