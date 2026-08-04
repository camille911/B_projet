# Order API B 0.1.0 契约

本文档是 `order-api-b==0.1.0` 的规范性公开契约，供不读取 B 项目源码的模块开发者、制品使用方和测开人员使用。结构化契约见 `api-contracts.json`，JSON Schema 位于 `schemas/`，互操作向量见 `golden-vectors.json`。

## 1. 制品、版本与依赖

| 项目 | 值 |
|---|---|
| Python 包 | `order-api-b` |
| 导入包 | `order_api_b` |
| API 版本 | `0.1.0` |
| Python | `>=3.11` |
| 初始基线 | `demo-start` / `9bcd42d0ebb48aa75492930a9b3c7c44726ba3e9`，仅 B1 |
| B3 集成标签 | `b3-integrated` / `d05546158e224be41dd554f05daf61f8da568b71` |
| B3 契约包 | `b-contracts==0.1.0` |
| B3 实现制品 | `order-outbound-b3==0.1.0` |
| 签名制品 | `company-shared-api==0.1.0`，由 B3 间接调用 |

本次演示保存的依赖制品参考哈希：

| 制品 | SHA-256 |
|---|---|
| `b-contracts==0.1.0` | `40e0b168198bb17e25ab87ab09786a5aca7f94244aae7693710a097ca93d00f4` |
| `order-outbound-b3==0.1.0` | `b3aec7a07c8a8b4d660be35ac7ccaa3f5996b55adeb180dfae9fea1b0d74c3c0` |
| `company-shared-api==0.1.0` | `4b6cb914cd1398bb8a7ae08489bd36281eb294406f5feb905665b120aa54e067` |

参考哈希只对应本次保存的 wheel。制品重新构建后，调用方必须使用新交付清单中的哈希。

公共导入：

```python
from order_api_b import (
    OrderValidationError,
    build_outbound_request,
    validate_order,
)
from order_api_b.ports import OrderValidator, order_validator_port
```

在 `demo-start` 基线上，B3 依赖尚未交付，`build_outbound_request` 不可用。使用当前集成版本时必须安装上述固定依赖，并确认该导出是可调用函数而不是 `None`。

## 2. 订单数据契约

订单是一个字典，Schema 见 `schemas/order.schema.json`。

| 字段 | 类型 | 必填 | 约束 | 是否原样进入 B3 body |
|---|---|---:|---|---:|
| `order_id` | `str` | 是 | `strip()` 后非空 | 是 |
| `customer_id` | `str` | 是 | `strip()` 后非空，支持 Unicode | 是 |
| `amount` | `str` | 是 | 正则 `^(?:0|[1-9]\d*)\.\d{2}$` 且十进制值大于 0 | 是 |
| `currency` | `str` | 是 | 仅 `CNY`、`HKD`、`USD`，区分大小写 | 是 |

输入订单允许附加字段。B1 校验忽略附加字段；B3 出站 body 必须丢弃全部附加字段。`order_id` 和 `customer_id` 只使用 `strip()` 判断是否为空，返回 body 时保留原字符串，不自动裁剪或标准化。

金额特别说明：

- 合法：`"0.01"`、`"1.00"`、`"10.25"`；
- 非法：`"0.00"`、`"01.00"`、`"1"`、`"1.0"`、`"-1.00"`、`"1e2"`、数字类型 `1.00`。

## 3. B1 订单校验

### 接口

```python
validate_order(order: dict) -> None
```

### 行为与副作用

- 按第 2 节规则依次校验订单；合法时返回 `None`。
- 不修改输入字典及其字段。
- 不访问网络、数据库或系统时间。
- 第一个失败规则立即抛出 `OrderValidationError`；不聚合多个错误。

### 异常

`OrderValidationError` 继承 `ValueError`。

| 条件 | 精确消息 |
|---|---|
| `order` 不是字典 | `order must be a dictionary` |
| `order_id` 缺失、非字符串或空白 | `order_id must be a non-empty string` |
| `customer_id` 缺失、非字符串或空白 | `customer_id must be a non-empty string` |
| 金额类型、格式或数值不合法 | `amount must be a positive two-decimal string` |
| 币种不合法 | `currency must be one of CNY, HKD, USD` |

调用方可以依赖异常类型和消息进行诊断，但业务流程不应通过解析消息决定分支；优先捕获 `OrderValidationError`。

## 4. B1 依赖注入端口

### 接口

```python
OrderValidator = Callable[[dict], None]
order_validator_port() -> OrderValidator
```

`order_validator_port()` 无参数，返回真实 B1 `validate_order` 可调用对象。独立模块只应依赖 `b-contracts` 中等价的 `OrderValidator` 协议和 Mock；测开集成时由 B 适配器绑定真实 B1。

端口调用约束：

- 输入、返回和异常必须与第 3 节一致；
- 调用方不得假定具体类、模块路径或内部校验顺序以外的实现细节；
- 契约 Mock 和真实 B1 必须运行同一组契约测试，防止行为漂移。

## 5. B3 订单出站请求

### 接口

```python
build_outbound_request(
    order: dict,
    secret: str,
    timestamp: int,
) -> dict
```

### 输入

| 参数 | 类型和约束 | 说明 |
|---|---|---|
| `order` | 满足第 2 节的数据契约 | 首先由真实 B1 校验 |
| `secret` | 非空 `str` | 传给固定版本公司签名资产，不得记录 |
| `timestamp` | `int`，`bool` 不接受 | 原样进入响应并参与签名 |

### 必须执行的步骤

1. 通过作用域化的契约端口调用真实 `validate_order`。
2. 按固定顺序构造只包含 `order_id`、`customer_id`、`amount`、`currency` 的新 body。
3. 调用 `company-shared-api==0.1.0` 的公司标准签名能力；不得在 B 或 B3 中复制 HMAC 实现。
4. 返回新的响应字典，不修改输入订单。

### 返回结构

Schema 见 `schemas/outbound-response.schema.json`。

```json
{
  "body": {
    "order_id": "ORD-1",
    "customer_id": "客户-001",
    "amount": "12.34",
    "currency": "CNY"
  },
  "timestamp": 1735689600,
  "signature": "cc5a2da1c12fe20f83e401cccdd95445d4b63053ee292d500a5a2aa2634d8bf0"
}
```

返回对象顶层只允许 `body`、`timestamp`、`signature`；body 只允许四个订单字段。签名是 64 位小写十六进制字符串。

### 异常传播

| 条件 | 异常 |
|---|---|
| 订单不符合 B1 | 原样传播 `OrderValidationError` |
| `secret` 不是字符串或为空 | 传播签名资产的 `ValueError` |
| `timestamp` 不是整数或是布尔值 | 传播签名资产的 `TypeError` |
| 固定依赖未安装或版本不匹配 | 安装/导入阶段失败，不应降级为本地签名实现 |

B3 不吞掉、不包装业务校验和签名输入异常。依赖不可用时必须让部署或测试失败，禁止静默降级。

## 6. 签名互操作契约

B3 签名的 payload 是过滤后的 `body`，不是原始 `order`。签名规范：排序键、紧凑 JSON 分隔符、不转义 Unicode，签名消息为 `timestamp + "." + canonical_json`，UTF-8 HMAC-SHA256，输出小写十六进制。

完整向量见 `golden-vectors.json`。同一组 body、secret、timestamp 在字段插入顺序变化后必须得到同一签名。附加订单字段被丢弃，因此也不得影响签名。

## 7. 依赖图与复用证明

```text
order-api-b 0.1.0
  -> order-outbound-b3 0.1.0
       -> b-contracts 0.1.0
       -> company-shared-api 0.1.0 / sign_request
```

验收时必须同时证明：

- 固定依赖实际安装且哈希符合交付清单；
- B3 运行时真实调用签名资产，而不是只返回伪造摘要；
- B3 制品中不存在 `hmac.new`、`hashlib.sha256` 或等价复制实现；
- 集成测试使用真实 B1，而不是只使用契约 Mock。

## 8. 无源码开发与测试边界

后端开发者无需访问 B 源码，但必须获得：本文档、结构化契约、Schema、`b-contracts` 端口/Mock、固定依赖坐标、资产检索权限和模块级验收用例。

开发岗位可以证明 B3 满足公开契约，但不能声称已经通过 B 的真实集成测试。测开岗位必须在有权访问 B 的独立环境中完成：

- 正常订单；
- 缺失字段、非法金额和非法币种；
- 中文 `customer_id`；
- 字段顺序和附加字段；
- golden vector；
- 真实 B1/B3/签名资产调用；
- 静态重复实现扫描；
- B 全量回归。

## 9. 安全与变更规则

- 不记录或持久化 `secret`、Authorization、完整订单正文或内部 token。
- 不在异常、测试快照和证据中包含真实密钥。
- Python wheel 可以被解包，不能作为强源码保密机制；强保密场景应使用受控内部服务或二进制制品。
- 输入规则、错误类型、返回字段、签名载荷、依赖版本或端口语义变化都属于契约变化，必须发布新版本并同步更新本文档、Schema、结构化契约、资产清单和契约测试。
- 文档与制品行为不一致时，停止集成并按契约缺陷处理，不得通过猜测源码或放宽测试绕过。
