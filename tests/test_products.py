"""商品模块接口测试"""
from api_client import trpc_query


def test_get_products_not_empty():
    """商品列表不为空(依赖 seed 数据)"""
    products = trpc_query("admin.getPublicProducts")
    assert len(products) > 0


def test_product_fields_complete():
    """每个商品都有关键字段,价格和库存数值合法"""
    products = trpc_query("admin.getPublicProducts")
    for p in products:
        assert p["id"] > 0
        assert p["name"], "商品名不能为空"
        assert p["price"] > 0, "价格必须大于 0"
        assert p["stock"] >= 0, "库存不能为负"
