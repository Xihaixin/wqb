import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

import wqb
from wqb.config import enVars
from wqb import WQBSession, print, FilterRange


env_vars = enVars.get_env_vars()

## 配置日志模块
logger = wqb.wqb_logger(name="MyLoger")
wqb.print(f"{logger.name = }")

## 实例化wqb
wqbs = WQBSession(env_vars, logger=logger)
resp = wqbs.auth_request()
print(resp.status_code)
print(resp.ok)
print(resp.json()['user']['id'])

## 获取 Operators 操作

# resp = wqbs.search_operators()
# print(resp.json())

# operators = [item['name'] for item in resp.json()]
# print(operators)

# operators_by_category = {}
# for item in resp.json():
#     name = item['name']
#     category = item['category']
#     if category not in operators_by_category:
#         operators_by_category[category] = []
#     operators_by_category[category].append(name)

# print(operators_by_category)

# 获取 数据集 Datasets

# dataset_id = 'analyst10'
# resp = wqbs.locate_dataset(dataset_id)
# print(resp.json())

# region = 'USA'  # 'USA'
# delay = 1  # 1, 0
# universe = 'TOP3000'  # 'TOP3000'
# resp = wqbs.search_datasets_limited(
#     region,
#     delay,
#     universe,
#     # search='<search>',  # 'price'
#     # category='<category>',  # 'pv', 'model', 'analyst'
#     # theme=False,  # True, False
#     # coverage=FilterRange.from_str('[0.8, inf)'),
#     # value_score=FilterRange.from_str('(-inf, 5]'),
#     # alpha_count=FilterRange.from_str('[100, 200)'),
#     # user_count=FilterRange.from_str('[1, 99]'),
#     # order='<order>',  # 'coverage', '-coverage', 'valueScore', '-valueScore'
#     # limit=50,
#     # offset=0,
#     # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
# )
# print(resp.json())

# alpha_id = '<alpha_id>'
# resp = wqbs.locate_alpha(alpha_id)
# # print(resp.json())