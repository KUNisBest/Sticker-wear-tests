"""tRPC 接口调用封装:把 HTTP 细节收进函数,用例里只关心业务。

测试代码和被测代码一样需要"封装复用"——
所有用例共用的请求逻辑写一遍,业务断言里不出现 URL/JSON 格式。
"""
import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000").rstrip("/")
ADMIN_PHONE = os.getenv("TEST_ADMIN_PHONE", "")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "")

if not ADMIN_PHONE or not ADMIN_PASSWORD:
    raise RuntimeError(
        "缺少管理员测试账号配置，请复制 .env.example 为 .env，"
        "并填写 TEST_ADMIN_PHONE 和 TEST_ADMIN_PASSWORD"
    )


def _unpack(resp):
    """从 tRPC 响应里取出业务数据;接口报错时抛出带原因的异常"""
    body = resp.json()
    if "error" in body:
        err = body["error"].get("json", {})
        raise AssertionError(f"接口报错: {err.get('message', err)}")
    return body.get("result", {}).get("data", {}).get("json")


def trpc_mutation(name, payload, token=None):
    """调用修改类接口(POST):如 auth.sendCode、order.create"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.post(
        f"{BASE_URL}/api/trpc/{name}",
        json={"json": payload},
        headers=headers,
        timeout=15,
    )
    return _unpack(resp)


def trpc_query(name, token=None):
    """调用查询类接口(GET):如 auth.me、admin.getPublicProducts"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(f"{BASE_URL}/api/trpc/{name}", headers=headers, timeout=15)
    return _unpack(resp)


def new_phone():
    """随机生成 11 位测试手机号(1 开头),避免测试数据互相污染"""
    return "1" + "".join(str(random.randint(0, 9)) for _ in range(10))


def register_user():
    """走验证码登录注册一个新用户,返回 (phone, token)"""
    phone = new_phone()
    send = trpc_mutation("auth.sendCode", {"phone": phone})
    login = trpc_mutation("auth.verifyCode", {"phone": phone, "code": send["code"]})
    assert login["success"] is True, "注册失败,无法继续"
    return phone, login["token"]
