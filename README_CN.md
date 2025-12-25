[TOC]
# 技术翻译
## 项目名称：wqb
一款更易用的机器学习工具库

## 核心亮点
- [世坤量化智能平台（WorldQuant BRAIN）](https://platform.worldquantbrain.com/)
- [Python包索引（PyPI）](https://pypi.org/)
- [可配置日志功能](#创建日志记录器对象-可选但建议配置)
  - 支持文件日志与控制台（终端）日志双输出
  - 支持 `INFO` 和 `WARNING` 两种日志级别
- [持久化会话](#创建wqb会话对象)
  - 基于 `requests.Session` 扩展实现
  - 支持自动鉴权（防过期/永不失效）
- [丰富的请求功能](#使用方法)
  - [搜索运算符](#运算符)
  - [数据集定位/检索](#数据集)
  - [字段定位/检索](#字段)
  - [阿尔法因子定位/筛选](#阿尔法因子)
  - [属性修改](#阿尔法因子)
  - [（异步并发）因子回测](#回测)
  - [（异步并发）提交结果校验](#校验)
  - [（异步并发）因子提交](#提交)

## 前置条件
请先确保你已配置好符合要求的 Python 环境（版本 ≥ 3.11），推荐使用虚拟环境管理工具（如 `virtualenv`、`conda` 等）。
- Python 版本要求：≥ 3.11
- 网络环境要求：可正常访问互联网

### 创建 Conda 虚拟环境（可选）
```sh
conda create -y -n wqb-py311 python=3.11
conda activate wqb-py311
```

### 安装包
```sh
python -m pip install wqb
```

### 升级包
```sh
python -m pip install wqb --upgrade --extra-index-url https://pypi.org/simple
```

## 使用方法
**务必牢记以下规则**：
1.  手动触发鉴权请求的操作**完全不需要**（包括首次初始化），你可以将其视为一个永不失效的持久化会话。
2.  所有**位置参数均为必填项**，反之亦然。
3.  所有**关键字参数均为可选项**，反之亦然。
    - 若不清楚参数含义，请直接使用默认值。
4.  类型 `Generator[requests.Response, None, None]` 可等价视为 `Iterable[requests.Response]`。
5.  所有请求方法的返回值均为 `requests.Response` 对象或其可迭代类型。
6.  通用可选关键字参数说明：
    - `log: str | None`
      - 传 `None` 表示禁用日志
      - 传空字符串 `''` 表示启用日志
      - 传字符串 `<content>` 表示启用日志，且该内容会被追加到日志条目末尾
    - `retry_log: str | None`
      - **仅当方法为协程函数（通过 `async def` 定义）时才会包含该参数**（`wqb.WQBSession.retry` 方法除外），反之亦然
      - 传 `None` 表示禁用重试日志
      - 传空字符串 `''` 表示启用重试日志
      - 传字符串 `<content>` 表示启用重试日志，且该内容会被追加到重试日志条目末尾
    - `log_gap: int`
      - **仅当方法返回值为可迭代的 `requests.Response` 时才会包含该参数**，反之亦然
      - 当日志间隔参数 `log_gap ≠ 0` 且请求索引 `idx % log_gap == 0` 时（索引 `idx` 从 1 开始计数），会输出一条子日志
      - 传 `0` 表示禁用子日志功能

### 创建 `logging.Logger` 对象（可选但建议配置）
```python
import wqb

# 创建日志记录器
logger = wqb.wqb_logger()
wqb.print(f"{logger.name = }")  # 等价于 print(f"{logger.name = }", flush=True)

# 手动输出日志示例
# logger.info('这是一条测试信息日志')
# logger.warning('这是一条测试警告日志')
```

### 创建 `wqb.WQBSession` 会话对象
```python
from wqb import WQBSession, print

# 初始化会话对象
wqbs = WQBSession(('<邮箱>', '<密码>'), logger=logger)
# 若未创建日志记录器，可使用如下代码初始化
# wqbs = WQBSession(('<邮箱>', '<密码>'))

# 测试连通性（可选操作）
resp = wqbs.auth_request()
print(resp.status_code)           # 成功时返回 201
print(resp.ok)                    # 成功时返回 True
print(resp.json()['user']['id'])  # 输出你的 BRAIN 平台用户 ID
```

### 运算符
#### `wqb.WQBSession.search_operators(...)`
```python
resp = wqbs.search_operators()
# print(resp.json())  # 打印运算符列表

# 提取所有运算符名称
operators = [item['name'] for item in resp.json()]
# print(operators)

# 按分类对运算符进行分组
operators_by_category = {}
for item in resp.json():
    name = item['name']
    category = item['category']
    if category not in operators_by_category:
        operators_by_category[category] = []
    operators_by_category[category].append(name)
# print(operators_by_category)
```

### 数据集
#### `wqb.WQBSession.locate_dataset(...)`
```python
dataset_id = '<数据集ID>'  # 示例值：'pv1'
resp = wqbs.locate_dataset(dataset_id)
# print(resp.json())  # 打印数据集详情
```

#### `wqb.WQBSession.search_datasets_limited(...)`
```python
from wqb import FilterRange

region = '<地区>'  # 示例值：'USA'
delay = 1  # 可选值：1, 0
universe = '<股票池>'  # 示例值：'TOP3000'
resp = wqbs.search_datasets_limited(
    region,
    delay,
    universe,
    # search='<搜索关键词>',  # 示例值：'price'
    # category='<数据集分类>',  # 示例值：'pv', 'model', 'analyst'
    # theme=False,  # 可选值：True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),  # 覆盖率筛选范围
    # value_score=FilterRange.from_str('(-inf, 5]'),  # 价值评分筛选范围
    # alpha_count=FilterRange.from_str('[100, 200)'),  # 关联因子数量筛选范围
    # user_count=FilterRange.from_str('[1, 99]'),  # 用户使用量筛选范围
    # order='<排序字段>',  # 示例值：'coverage', '-coverage', 'valueScore', '-valueScore'
    # limit=50,  # 返回结果数量上限
    # offset=0,  # 分页偏移量
    # others=[],  # 其他自定义参数，格式：['other_param_0=xxx', 'other_param_1=yyy']
)
# print(resp.json())  # 打印筛选后的数据集列表
```

#### `wqb.WQBSession.search_datasets(...)`
```python
from wqb import FilterRange

region = '<地区>'  # 示例值：'USA'
delay = 1  # 可选值：1, 0
universe = '<股票池>'  # 示例值：'TOP3000'
resps = wqbs.search_datasets(
    region,
    delay,
    universe,
    # 可选参数同 search_datasets_limited 方法
    # search='<搜索关键词>',
    # category='<数据集分类>',
    # ...
)
# 遍历分页返回的所有响应对象
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.json())
```

### 字段
#### `wqb.WQBSession.locate_field(...)`
```python
field_id = '<字段ID>'  # 示例值：'open'
resp = wqbs.locate_field(field_id)
# print(resp.json())  # 打印字段详情
```

#### `wqb.WQBSession.search_fields_limited(...)`
```python
from wqb import FilterRange

region = '<地区>'  # 示例值：'USA'
delay = 1  # 可选值：1, 0
universe = '<股票池>'  # 示例值：'TOP3000'
resp = wqbs.search_fields_limited(
    region,
    delay,
    universe,
    # dataset_id='<数据集ID>',  # 示例值：'pv1'
    # search='<搜索关键词>',  # 示例值：'open'
    # category='<字段分类>',  # 示例值：'pv', 'model', 'analyst'
    # theme=False,  # 可选值：True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),  # 覆盖率筛选范围
    # type='<字段类型>',  # 示例值：'MATRIX', 'VECTOR', 'GROUP', 'UNIVERSE'
    # alpha_count=FilterRange.from_str('[100, 200)'),  # 关联因子数量筛选范围
    # user_count=FilterRange.from_str('[1, 99]'),  # 用户使用量筛选范围
    # order='<排序字段>',  # 示例值：'coverage', '-coverage', 'alphaCount', '-alphaCount'
    # limit=50,  # 返回结果数量上限
    # offset=0,  # 分页偏移量
    # others=[],  # 其他自定义参数
)
# print(resp.json())  # 打印筛选后的字段列表
```

#### `wqb.WQBSession.search_fields(...)`
```python
from wqb import FilterRange

region = '<地区>'  # 示例值：'USA'
delay = 1  # 可选值：1, 0
universe = '<股票池>'  # 示例值：'TOP3000'
resps = wqbs.search_fields(
    region,
    delay,
    universe,
    # 可选参数同 search_fields_limited 方法
    # dataset_id='<数据集ID>',
    # search='<搜索关键词>',
    # ...
)
# 遍历分页返回的所有响应对象
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.json())
```

### 阿尔法因子
#### `wqb.WQBSession.locate_alpha(...)`
```python
alpha_id = '<阿尔法因子ID>'
resp = wqbs.locate_alpha(alpha_id)
# print(resp.json())  # 打印因子详情
```

#### `wqb.WQBSession.filter_alphas_limited(...)`
```python
from datetime import datetime
from wqb import FilterRange

# 定义时间筛选范围
lo = datetime.fromisoformat('2025-01-28T00:00:00-05:00')
hi = datetime.fromisoformat('2025-01-29T00:00:00-05:00')
resp = wqbs.filter_alphas_limited(
    status='UNSUBMITTED',  # 因子状态：未提交
    region='USA',  # 地区
    delay=1,  # 延迟参数
    universe='TOP3000',  # 股票池
    sharpe=FilterRange.from_str('[1.58, inf)'),  # 夏普比率筛选：≥1.58
    fitness=FilterRange.from_str('[1, inf)'),  # 适应度筛选：≥1
    turnover=FilterRange.from_str('(-inf, 0.7]'),  # 换手率筛选：≤0.7
    date_created=FilterRange.from_str(f"[{lo.isoformat()}, {hi.isoformat()})"),  # 创建时间范围
    order='dateCreated',  # 按创建时间排序
)
# 提取符合条件的因子ID列表
alpha_ids = [item['id'] for item in resp.json()['results']]
# print(alpha_ids)
```

#### `wqb.WQBSession.filter_alphas(...)`
```python
from datetime import datetime
from wqb import FilterRange

lo = datetime.fromisoformat('2025-01-28T00:00:00-05:00')
hi = datetime.fromisoformat('2025-01-29T00:00:00-05:00')
resps = wqbs.filter_alphas(
    status='UNSUBMITTED',
    region='USA',
    delay=1,
    universe='TOP3000',
    sharpe=FilterRange.from_str('[1.58, inf)'),
    fitness=FilterRange.from_str('[1, inf)'),
    turnover=FilterRange.from_str('(-inf, 0.7]'),
    date_created=FilterRange.from_str(f"[{lo.isoformat()}, {hi.isoformat()})"),
    order='dateCreated',
)
# 遍历所有分页结果，汇总因子ID
alpha_ids = []
for resp in resps:
    alpha_ids.extend(item['id'] for item in resp.json()['results'])
# print(alpha_ids)
```

#### `wqb.WQBSession.patch_properties(...)`
```python
from wqb import NULL

# 注意：传 None 表示不修改该属性
# 传 wqb.NULL 表示将该属性值设为 JSON 格式的 null

alpha_id = '<阿尔法因子ID>'
resp = wqbs.patch_properties(
    alpha_id,
    # favorite=False,  # 是否收藏：False/True
    # hidden=False,  # 是否隐藏：False/True
    # name=NULL,  # 因子名称，传字符串如 '<name>' 可修改
    # category=NULL,  # 因子分类，可选值：'ANALYST', 'FUNDAMENTAL'
    # tags=NULL,  # 因子标签，支持字符串 '<tag>' 或列表 ['tag_0', 'tag_1']
    # color=NULL,  # 因子颜色，可选值：'RED', 'YELLOW', 'GREEN', 'BLUE', 'PURPLE'
    # regular_description=NULL,  # 因子描述，传字符串 '<regular_description>' 可修改
)
# print(resp.json())  # 打印修改后的因子属性
```


### 回测
#### `wqb.WQBSession.simulate(...)`
```python
import asyncio

# 定义单个阿尔法因子
alpha = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',  # 标的类型：股票
        'region': 'USA',  # 地区
        'universe': 'TOP3000',  # 股票池
        'delay': 1,  # 延迟参数
        'decay': 13,  # 衰减系数
        'neutralization': 'INDUSTRY',  # 中性化类型：行业中性
        'truncation': 0.13,  # 截尾比例
        'pasteurization': 'ON',  # 巴氏过滤：开启
        'unitHandling': 'VERIFY',  # 单位处理：校验
        'nanHandling': 'OFF',  # 空值处理：关闭
        'language': 'FASTEXPR',  # 因子语言：快速表达式
        'visualization': False  # 是否开启可视化
    },
    'regular': 'liabilities/assets',  # 因子表达式：负债/资产
}
# 多因子回测可传入列表：multi_alpha = [<alpha_0>, <alpha_1>, <alpha_2>]
resp = asyncio.run(
    wqbs.simulate(
        alpha,  # 传入单个因子或多因子列表
        # 回调函数可选，用于监听回测过程
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
# print(resp.status_code)  # 打印回测请求状态码
# print(resp.text)  # 打印回测结果
```

#### `wqb.WQBSession.concurrent_simulate(...)`
```python
import asyncio
import wqb

# 定义多因子列表
alphas = [{...}, {...}, {...}]  # 示例：包含3个因子的列表
# 按批次分组，每组最多10个因子
multi_alphas = wqb.to_multi_alphas(alphas, 10)
# 并发数：1 ≤ concurrency ≤ 10
concurrency = 8
resps = asyncio.run(
    wqbs.concurrent_simulate(
        multi_alphas,  # 传入因子列表或分组后的多因子列表
        concurrency,
        # return_exceptions=True,  # 是否返回异常对象
        # 回调函数可选，用于监听并发回测过程
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
# 遍历所有并发回测的响应结果
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.status_code)
    # print(resp.text)
```

### 校验
#### `wqb.WQBSession.check(...)`
```python
import asyncio

alpha_id = '<阿尔法因子ID>'
resp = asyncio.run(
    wqbs.check(
        alpha_id,
        # 回调函数可选，用于监听校验过程
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
# print(resp.status_code)  # 打印校验请求状态码
# print(resp.text)  # 打印校验结果
```

#### `wqb.WQBSession.concurrent_check(...)`
```python
import asyncio

# 定义待校验的因子ID列表
alpha_ids = ['<alpha_id_0>', '<alpha_id_1>', '<alpha_id_2>']
# 设置并发数
concurrency = 2
resps = asyncio.run(
    wqbs.concurrent_check(
        alpha_ids,
        concurrency,
        # return_exceptions=True,  # 是否返回异常对象
        # 回调函数可选
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
# 遍历所有并发校验的响应结果
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.status_code)
    # print(resp.text)
```

### 提交
#### `wqb.WQBSession.submit(...)`
> **注意**：该功能尚未完全实现，可能无法正常工作。

```python
import asyncio

alpha_id = '<阿尔法因子ID>'
resp = asyncio.run(
    wqbs.submit(
        alpha_id,
        # 回调函数可选
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
# print(resp.status_code)  # 打印提交请求状态码
# print(resp.text)  # 打印提交结果
```

---

# 功能解释

`wqb` 是一款针对 **WorldQuant BRAIN 量化平台**开发的 Python 工具库，核心目标是简化量化因子的开发、回测与提交流程，主要功能和设计亮点如下：
1.  **持久化自动鉴权会话**
    基于 `requests.Session` 扩展，无需手动管理 token，会话自动保持有效，解决了频繁鉴权的痛点。
2.  **完善的日志系统**
    支持文件+控制台双输出，可配置日志级别、日志间隔，还能通过参数动态控制日志开关，方便调试和生产环境监控。
3.  **全链路因子管理**
    覆盖因子开发全流程：从**数据集/字段检索**获取基础数据，到**因子筛选**定位目标因子，再到**属性修改**调整因子配置，最后通过**异步回测/校验/提交**完成量化分析。
4.  **异步并发支持**
    针对回测、校验等耗时操作提供并发接口（`concurrent_simulate`/`concurrent_check`），支持自定义并发数，大幅提升批量因子处理效率。
5.  **灵活的筛选能力**
    通过 `FilterRange` 类支持区间筛选，可按夏普比率、换手率、创建时间等指标精准定位符合要求的阿尔法因子。

这个库的设计完全贴合量化研究员的工作流，尤其适合需要批量处理因子、自动化回测的场景。

我可以帮你编写一个**完整的批量因子回测+校验的可运行Demo**，需要吗？

## wqb.filter_alphas 与 wqb.filter_alphas_limited之间的区别

## 两个函数功能的作用效果差异

### 1. **返回的数据量不同**
- **`filter_alphas_limited`**：返回**单页数据**（最多 `limit` 条记录）。例如，设置 `limit=50` 则返回最多 50 个 alpha，同时响应中包含总记录数 `count`。
- **`filter_alphas`**：返回**所有符合条件的数据**（多页）。它会自动遍历所有分页，每次 yield 一页，最终获取全部 alpha。

### 2. **使用场景与便利性**
- **`filter_alphas_limited`**：适用于**需要精确控制分页**的场景，比如：
  - 只获取第一页进行预览。
  - 实现自定义的分页逻辑（如跳转到特定页）。
  - 只需要总数而不需要具体数据（通过 `limit=1` 获取 `count`）。
- **`filter_alphas`**：适用于**需要批量处理所有 alpha** 的场景，比如：
  - 导出所有 alpha 进行本地分析。
  - 遍历每个 alpha 执行检查、提交等操作。
  - 简化代码，无需手动处理分页循环。

### 3. **网络请求次数与性能**
- **`filter_alphas_limited`**：**单次请求**，网络开销小，响应快。
- **`filter_alphas`**：**多次请求**（至少两次：一次获取总数，一次或多次获取数据页）。如果数据量很大（例如 1000 个 alpha，每页 100 条），则需要 11 次请求（1 次获取总数 + 10 次获取数据页）。因此网络开销较大，但通过生成器惰性加载，可以边获取边处理。

### 4. **代码编写复杂度**
- **`filter_alphas_limited`**：需要手动处理分页循环，代码更繁琐：
  ```python
  offset = 0
  while True:
      resp = session.filter_alphas_limited(..., offset=offset)
      data = resp.json()
      # 处理 data['items']
      if offset + len(data['items']) >= data['count']:
          break
      offset += limit
  ```
- **`filter_alphas`**：直接使用生成器，代码简洁：
  ```python
  for resp in session.filter_alphas(...):
      data = resp.json()
      # 处理 data['items']
  ```

### 5. **错误处理与日志**
- **`filter_alphas_limited`**：每次调用可独立处理错误和日志。
- **`filter_alphas`**：内置了进度日志（通过 `log_gap` 参数），可定期输出进度百分比。错误处理可以在生成器外部统一进行。

### 6. **实际输出效果示例**
假设有 150 个 alpha，每页 limit=100：
- **`filter_alphas_limited(limit=100, offset=0)`**：返回第 1 页（100 个 alpha），响应中 `count=150`。
- **`filter_alphas(limit=100)`**：生成器首先 yield 第 1 页（100 个 alpha），然后 yield 第 2 页（剩余 50 个 alpha）。总共产生两个 Response 对象。

## 总结
- **功能定位**：`filter_alphas_limited` 是基础的分页请求工具；`filter_alphas` 是基于它的高级封装，提供自动分页遍历。
- **效果差异**：前者返回单页，后者返回所有页；前者需手动管理分页，后者自动管理；前者网络请求少，后者请求多但方便。
- **选择建议**：
  - 若只需单页或自定义分页，使用 `filter_alphas_limited`。
  - 若需获取全部数据并进行批量处理，使用 `filter_alphas` 更简洁高效。

因此，两个方法在作用效果上的核心差异在于**数据完整性**和**使用便利性**，开发者可根据具体需求选择合适的方法。