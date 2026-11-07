"""认证模块接口测试:验证码 + 密码登录 + 当前用户"""
import pytest

from api_client import (
    ADMIN_PASSWORD,
    ADMIN_PHONE,
    new_phone,
    register_user,
    trpc_mutation,
    trpc_query,
)


# ---------- 发送验证码 ----------

def test_send_code_valid_phone():
    """正常手机号:发送成功且返回 6 位数字验证码"""
    res = trpc_mutation("auth.sendCode", {"phone": new_phone()})
    assert res["success"] is True
    assert len(res["code"]) == 6 and res["code"].isdigit()


@pytest.mark.parametrize("bad_phone", ["123", "123456789012", "abc", ""])
def test_send_code_invalid_phone(bad_phone):
    """非法手机号:被后端校验拒绝(parametrize 一条用例测 4 组数据)"""
    with pytest.raises(AssertionError):
        trpc_mutation("auth.sendCode", {"phone": bad_phone})


def test_verify_code_wrong_code():
    """错误验证码:业务层返回失败(不是抛异常,是 success=False)"""
    phone = new_phone()
    trpc_mutation("auth.sendCode", {"phone": phone})
    res = trpc_mutation("auth.verifyCode", {"phone": phone, "code": "000000"})
    assert res["success"] is False


def test_full_sms_login_flow():
    """核心链路:发码 → 验码 → 拿到 token(新用户自动注册)"""
    phone, token = register_user()
    assert token and len(token) > 20


# ---------- 密码登录 ----------

def test_password_login_success():
    """管理员正确密码:返回 token 和用户信息"""
    res = trpc_mutation(
        "auth.loginPassword", {"phone": ADMIN_PHONE, "password": ADMIN_PASSWORD}
    )
    assert res["success"] is True
    assert res["user"]["phone"] == ADMIN_PHONE


def test_password_login_wrong_password():
    """错误密码:业务失败,并给出明确提示"""
    res = trpc_mutation(
        "auth.loginPassword", {"phone": ADMIN_PHONE, "password": "wrong-password"}
    )
    assert res["success"] is False
    assert "密码错误" in res["message"]


def test_password_short():
    """密码少于 6 位:被后端格式校验拒绝,且提示"密码至少6位"""
    with pytest.raises(AssertionError, match="密码至少6位"):
        trpc_mutation("auth.loginPassword", {"phone": ADMIN_PHONE, "password": "12345"})


# ---------- 当前用户 ----------

def test_me_without_token():
    """未登录:返回空"""
    assert trpc_query("auth.me") is None


def test_me_with_token(admin_token):
    """带 token:能认出管理员身份(fixture 自动注入,不用自己登录)"""
    me = trpc_query("auth.me", token=admin_token)
    assert me["phone"] == ADMIN_PHONE
    assert me["role"] == "admin"
