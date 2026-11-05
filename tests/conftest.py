"""pytest 共享配置。

fixture 是 pytest 的核心概念:定义在这里的"前置条件",
任何用例只要在参数里写上同名变量,就能自动注入,不用手动调用。
"""
import pytest

from api_client import ADMIN_PASSWORD, ADMIN_PHONE, trpc_mutation


@pytest.fixture(scope="session")
def admin_token():
    """管理员登录凭证:整个测试会话只登录一次(scope='session')"""
    res = trpc_mutation(
        "auth.loginPassword", {"phone": ADMIN_PHONE, "password": ADMIN_PASSWORD}
    )
    assert res["success"] is True, "管理员登录失败,请先跑 npm run db:seed"
    return res["token"]
