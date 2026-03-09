"""
Mock 数据生成工具（基于 Faker）
- 生成中文测试数据
- 支持批量生成
"""
from faker import Faker

fake = Faker("zh_CN")


def random_name() -> str:
    return fake.name()


def random_phone() -> str:
    return fake.phone_number()


def random_email() -> str:
    return fake.email()


def random_address() -> str:
    return fake.address()


def random_sentence(nb_words: int = 6) -> str:
    return fake.sentence(nb_words=nb_words)


def random_keywords(count: int = 5) -> list[str]:
    """生成随机中文搜索关键词列表"""
    topics = [
        "Python自动化测试", "Pytest框架", "接口测试", "性能测试",
        "Docker部署", "数据库优化", "机器学习", "Vue3开发",
        "测试开发工程师", "软件质量", "CI/CD", "Playwright"
    ]
    import random
    return random.sample(topics, min(count, len(topics)))


if __name__ == "__main__":
    print("姓名:", random_name())
    print("手机:", random_phone())
    print("邮箱:", random_email())
    print("关键词:", random_keywords(3))
