# Sticker Wear API Tests

基于 `pytest + requests` 的 Sticker Wear 电商后端接口测试项目。

> 初始测试框架由 AI 辅助生成；后续新增用例由本人根据测试设计补充、运行并提交。

## 测试范围

- 用户认证
  - 手机验证码发送
  - 验证码登录与自动注册
  - 密码登录
  - 使用 JWT 获取当前用户
  - 密码长度不足校验
  - 验证码只能使用一次
- 商品接口
  - 商品列表
  - 商品关键字段与数据合法性
- 订单接口
  - 未登录下单校验
  - 下单后库存扣减
  - 库存不足与补偿逻辑
  - 管理员发货及用户侧状态更新

当前共有 17 个测试函数，其中手机号参数化后展开为 20 个测试用例。

## 技术栈

- Python
- pytest
- requests
- python-dotenv
- tRPC over HTTP

## 项目结构

```text
Sticker-wear-tests/
├── tests/
│   ├── api_client.py      # HTTP 与 tRPC 请求封装
│   ├── conftest.py        # pytest 共享 fixture
│   ├── test_auth.py       # 认证接口测试
│   ├── test_products.py   # 商品接口测试
│   └── test_order.py      # 订单接口测试
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md