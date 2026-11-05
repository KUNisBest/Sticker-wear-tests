"""订单模块接口测试:下单 / 库存扣减 / 订单流转"""
import pytest

from api_client import new_phone, register_user, trpc_mutation, trpc_query


def _pick_product(min_stock=1):
    """从商品列表里挑一个库存足够的商品"""
    products = trpc_query("admin.getPublicProducts")
    for p in products:
        if p["stock"] >= min_stock:
            return p
    return None


def _create_order(token, product, quantity=1):
    return trpc_mutation(
        "order.create",
        {
            "items": [{"productId": product["id"], "quantity": quantity}],
            "shippingName": "测试用户",
            "shippingPhone": new_phone(),
            "shippingAddress": "测试地址 1 号",
            "note": "pytest 自动化下单",
        },
        token=token,
    )


def test_create_order_requires_login():
    """未登录下单:被业务拒绝"""
    res = trpc_mutation(
        "order.create",
        {
            "items": [{"productId": 1, "quantity": 1}],
            "shippingName": "x",
            "shippingPhone": new_phone(),
            "shippingAddress": "x",
        },
    )
    assert res["success"] is False
    assert "登录" in res["message"]


def test_create_order_decreases_stock():
    """下单成功:库存精确 -1"""
    product = _pick_product()
    if not product:
        pytest.skip("所有商品已售罄,先用管理员账号补库存再跑")
    _, token = register_user()
    before = product["stock"]

    res = _create_order(token, product)
    assert res["success"] is True, res.get("message")
    assert res["orderId"] > 0

    after = next(
        p for p in trpc_query("admin.getPublicProducts") if p["id"] == product["id"]
    )
    assert after["stock"] == before - 1


def test_create_order_insufficient_stock():
    """库存不足:下单失败,且库存分毫不差(补偿回滚)"""
    product = trpc_query("admin.getPublicProducts")[0]
    _, token = register_user()
    before = product["stock"]

    res = _create_order(token, product, quantity=before + 1000)
    assert res["success"] is False
    assert "库存不足" in res["message"]

    after = next(
        p for p in trpc_query("admin.getPublicProducts") if p["id"] == product["id"]
    )
    assert after["stock"] == before, "失败后库存必须原样(不能扣成负数)"


def test_order_status_flow(admin_token):
    """订单状态机:pending → 管理员发货 shipped → 用户侧可见"""
    product = _pick_product()
    if not product:
        pytest.skip("所有商品已售罄,先用管理员账号补库存再跑")
    _, token = register_user()

    created = _create_order(token, product)
    order_id = created["orderId"]

    # 管理员能看到这笔订单
    all_orders = trpc_query("order.listAll", token=admin_token)
    assert any(int(o["id"]) == order_id for o in all_orders)

    # 管理员发货
    upd = trpc_mutation(
        "order.updateStatus", {"orderId": order_id, "status": "shipped"}, token=admin_token
    )
    assert upd["success"] is True

    # 用户侧看到状态已流转
    mine = trpc_query("order.myOrders", token=token)
    mine_order = next(o for o in mine if int(o["id"]) == order_id)
    assert mine_order["status"] == "shipped"
