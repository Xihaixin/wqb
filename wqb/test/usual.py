import wqb
import json
from wqb.config import enVars
from wqb import WQBSession, print, FilterRange
from pathlib import Path

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

OUT_PUT_PATH = enVars.get_root_path() / "out"

def save_to_json(data, file_name, out_path):
    import requests
    out_path = Path(out_path)
    file_name = Path(out_path) / file_name
    
    def serialize(obj):
        if isinstance(obj, requests.Response):
            try:
                return obj.json()
            except ValueError:
                return obj.text
        elif isinstance(obj, (list, tuple)):
            return [serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: serialize(value) for key, value in obj.items()}
        else:
            return obj

    try:
        with open(str(file_name), "w", encoding="utf-8") as f:
            json.dump(
                serialize(data), f,
                indent=2,
                ensure_ascii=True,
            )
            
    except (OSError, IOError) as e:
        # 文件系统相关错误：权限不足、路径不存在、磁盘满等
        print(f"无法写入文件 {file_name}: {e}"+"=" * 10)
    except TypeError as e:
        # data 中包含不可序列化的对象（如自定义类、函数等）
        print(f"写入文件{file_name}时-->JSON 序列化失败: {e}"+"=" * 10)
    except Exception as e:
        # 其他未预期的错误（谨慎使用）
        print(f"写入文件{file_name}时-->发生未知错误: {e}"+"=" * 10)

auth_request = "auth_request.json"
save_to_json(resp, auth_request, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 1. 获取 Operators 操作 -> wqb.WQBSession.search_operators(...)
##----------------------------------------------------------------------
search_operators_file = "search_operators.json"
operators_by_category_file = "operators_by_category.json"

resp = wqbs.search_operators()
print(resp.json())

save_to_json(resp, search_operators_file, out_path=OUT_PUT_PATH)

operators = [item['name'] for item in resp.json()]
print(operators)

operators_by_category = {}
for item in resp.json():
    name = item['name']
    category = item['category']
    if category not in operators_by_category:
        operators_by_category[category] = []
    operators_by_category[category].append(name)

print(operators_by_category)
save_to_json(operators_by_category, operators_by_category_file, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 2. 获取数据集 Datasets -> wqb.WQBSession.locate_dataset(...)
##----------------------------------------------------------------------
dataset_id = 'analyst10'
locate_dataset_analyst10 = "locate_dataset_analyst10.json"

resp = wqbs.locate_dataset(dataset_id)
print(resp.json())
save_to_json(resp, locate_dataset_analyst10, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 3. 在条件限制下搜索关键词 search: dataset | field | description 
# -> wqb.WQBSession.search_datasets_limited(...)
##----------------------------------------------------------------------
search_datasets_limited_USA_1_TOP3000_price = "search_datasets_limited_USA_1_TOP3000_price.json"
region = 'USA'  # 'USA'
delay = 1  # 1, 0
universe = 'TOP3000'  # 'TOP3000'
resp = wqbs.search_datasets_limited(
    region,
    delay,
    universe,
    search='price',  # 'price'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # value_score=FilterRange.from_str('(-inf, 5]'),
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'valueScore', '-valueScore'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
print(resp.json())
save_to_json(resp, search_datasets_limited_USA_1_TOP3000_price, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 4. 搜索数据集：wqb.WQBSession.search_datasets(...)
#   写入文件D:\ProgramFile2_OR\pythonProgramUpStage\wqb\out\search_datasets_EUR_1_TOP3000.json时-->JSON 序列化失败: 
#   Object of type generator is not JSON serializable==========
##----------------------------------------------------------------------

from wqb import FilterRange

search_datasets_EUR_1_TOP3000 = "search_datasets_EUR_1_TOP3000.json"

region = 'EUR'  # 示例值：'EUR'
delay = 1  # 可选值：1, 0
universe = 'TOP3000'  # 示例值：'TOP3000'
resps = wqbs.search_datasets(
    region,
    delay,
    universe,
    # 可选参数同 search_datasets_limited 方法
    # search='<搜索关键词>',
    # category='<数据集分类>',
    # ...
)

save_to_json(resps, search_datasets_EUR_1_TOP3000, out_path=OUT_PUT_PATH)

# 遍历分页返回的所有响应对象
for idx, resp in enumerate(resps, start=1):
    print(idx)
    print(resp.json())


##----------------------------------------------------------------------
# 5. 加载数据字段：wqb.WQBSession.locate_field(...)
##----------------------------------------------------------------------

locate_field_open = "locate_field_open.json"
field_id = "open"
resp = wqbs.locate_field(field_id)
print(resp.json())
save_to_json(resp, locate_field_open, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 6.在给定限制设置下搜索数据字段 wqb.WQBSession.search_fields_limited(...)
##----------------------------------------------------------------------
from wqb import FilterRange
search_fields_limited_USA_1_TOP3000_Fundamental = "search_fields_limited_USA_1_TOP3000_Fundamental.json"
region = 'USA'  # 'USA'
delay = 1  # 1, 0
universe = 'TOP3000'  # 'TOP3000'
resp = wqbs.search_fields_limited(
    region,
    delay,
    universe,
    dataset_id='fundamental17',  # 'pv1'
    search='open',  # 'open'
    category='Fundamental',  # 'pv', 'model', 'analyst'
    theme=False,  # True, False
    coverage=FilterRange.from_str('[0.8, inf)'),
    # type='UNIVERSE',  # 'MATRIX', 'VECTOR', 'GROUP', 'UNIVERSE'
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'alphaCount', '-alphaCount'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)
print(resp.json())
save_to_json(resp, search_fields_limited_USA_1_TOP3000_Fundamental, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 7. 搜索数据字段：wqb.WQBSession.search_fields(...)
#   写入文件D:\ProgramFile2_OR\pythonProgramUpStage\wqb\out\search_fields_EUP_1_TOP3000_Fundamental.json时
#   -->JSON 序列化失败: 
#   Object of type generator is not JSON serializable==========
##----------------------------------------------------------------------

search_fields_EUP_1_TOP3000_Fundamental = "search_fields_EUP_1_TOP3000_Fundamental.json"
region = 'EUP'  # 'USA'
delay = 1  # 1, 0
universe = 'TOP3000'  # 'TOP3000'
resps = wqbs.search_fields(
    region,
    delay,
    universe,
    dataset_id='fundamental17',  # 'pv1'
    # search='<search>',  # 'open'
    # category='<category>',  # 'pv', 'model', 'analyst'
    # theme=False,  # True, False
    # coverage=FilterRange.from_str('[0.8, inf)'),
    # type='<type>',  # 'MATRIX', 'VECTOR', 'GROUP', 'UNIVERSE'
    # alpha_count=FilterRange.from_str('[100, 200)'),
    # user_count=FilterRange.from_str('[1, 99]'),
    # order='<order>',  # 'coverage', '-coverage', 'alphaCount', '-alphaCount'
    # limit=50,
    # offset=0,
    # others=[],  # ['other_param_0=xxx', 'other_param_1=yyy']
)

for idx, resp in enumerate(resps, start=1):
    print(idx)
    print(resp.json())  # 404 -> {"detail":"Not found."}

save_to_json(resps, search_fields_EUP_1_TOP3000_Fundamental, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 二. Alpha
##----------------------------------------------------------------------


##----------------------------------------------------------------------
# 1. 加载alpha：wqb.WQBSession.locate_alpha(...)
##----------------------------------------------------------------------

locate_alpha_3yYPdo4 = "locate_alpha_3yYPdo4.json"

alpha_id = '3yYPdo4'
resp = wqbs.locate_alpha(alpha_id)
print(resp.json()) # {'detail': 'Not found.'}

save_to_json(resp, locate_alpha_3yYPdo4, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 2. 筛选alpha：wqb.WQBSession.filter_alphas_limited(...)
##----------------------------------------------------------------------

from datetime import datetime
from wqb import FilterRange

filter_alphas_limited_lo_hi = "filter_alphas_limited_lo_hi.json"

lo = datetime.fromisoformat('2025-12-16T00:00:00-05:00')
hi = datetime.fromisoformat('2025-12-17T00:00:00-05:00')
resp = wqbs.filter_alphas_limited(
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
alpha_ids = [item['id'] for item in resp.json()['results']]
print(alpha_ids)

save_to_json(resp, filter_alphas_limited_lo_hi, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 3. 筛选alpha：wqb.WQBSession.filter_alphas(...)
#  写入文件D:\ProgramFile2_OR\pythonProgramUpStage\wqb\out\filter_alphas_lo_hi.json时-->JSON 序列化失败:
#  Object of type generator is not JSON serializable==========
##----------------------------------------------------------------------

filter_alphas_lo_hi = "filter_alphas_lo_hi.json"
lo = datetime.fromisoformat('2025-12-15T00:00:00-05:00')
hi = datetime.fromisoformat('2025-12-16T00:00:00-05:00')
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
alpha_ids = []
for resp in resps:
    alpha_ids.extend(item['id'] for item in resp.json()['results'])
print(alpha_ids)

save_to_json(resps, filter_alphas_lo_hi, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 4. 设置alpha属性：wqb.WQBSession.patch_properties(...)
##----------------------------------------------------------------------

# 注意：传 None 表示不修改该属性
# 传 wqb.NULL 表示将该属性值设为 JSON 格式的 null
patch_properties_3yYPdo4 = "patch_properties_3yYPdo4.json"
alpha_id = '3yYPdo4'
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
print(resp.json())  # 打印修改后的因子属性

save_to_json(resp, patch_properties_3yYPdo4, out_path=OUT_PUT_PATH)

##----------------------------------------------------------------------
# 三. 回测仿真 - 检查 - 提交
##----------------------------------------------------------------------


##----------------------------------------------------------------------
# 1. 回测仿真：wqb.WQBSession.simulate(...)
##----------------------------------------------------------------------

simulate_single_alpha = "simulate_single_alpha.json"

import asyncio

alpha = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',
        'region': 'USA',
        'universe': 'TOP3000',
        'delay': 1,
        'decay': 13,
        'neutralization': 'INDUSTRY',
        'truncation': 0.13,
        'pasteurization': 'ON',
        'unitHandling': 'VERIFY',
        'nanHandling': 'OFF',
        'language': 'FASTEXPR',
        'visualization': False
    },
    'regular': 'liabilities/assets',
}
# multi_alpha = [<alpha_0>, <alpha_1>, <alpha_2>]
resp = asyncio.run(
    wqbs.simulate(
        alpha,  # `alpha` or `multi_alpha`
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
print(resp.status_code)
print(resp.text)

save_to_json(resp, simulate_single_alpha, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 2. 批量回测仿真：wqb.WQBSession.simulate(...)
##----------------------------------------------------------------------

alpha_express =  ['winsorize(ts_backfill(anl4_afv4_eps_low, 120), std=4)',
 'winsorize(ts_backfill(anl4_afv4_eps_mean, 120), std=4)',
 'winsorize(ts_backfill(vec_sum(previous_recommendation_value), 120), std=4)',
 'winsorize(ts_backfill(vec_avg(sales_estimate_value), 120), std=4)',
 'winsorize(ts_backfill(vec_sum(sales_estimate_value), 120), std=4)',
 'winsorize(ts_backfill(vec_avg(sales_previous_estimate_value), 120), std=4)',
 'winsorize(ts_backfill(vec_sum(sales_previous_estimate_value), 120), std=4)']

def generate_sim_data(alpha_list, region, uni, neut):
    sim_data_list = []
    for alpha, decay in alpha_list:
        simulation_data = {
            'type': 'REGULAR',
            'settings': {
                'instrumentType': 'EQUITY',
                'region': region,
                'universe': uni,
                'delay': 1,
                'decay': decay,
                'neutralization': neut,
                'truncation': 0.08,
                'pasteurization': 'ON',
                'testPeriod': 'P0Y',
                'unitHandling': 'VERIFY',
                'nanHandling': 'ON',
                'language': 'FASTEXPR',
                'visualization': False
            },
            'regular': alpha,
        }
        sim_data_list.append(simulation_data)
    return sim_data_list

## <!--这里需要生成alphas 列表-->
concurrent_simulate_to_multi_alphas = "concurrent_simulate_to_multi_alphas.json"
alphas = generate_sim_data(alpha_express, 'USA', 'TOP3000', "SUBINDUSTRY")  # [<alpha_0>, <alpha_1>, <alpha_2>]

multi_alphas = wqb.to_multi_alphas(alphas, 3)
concurrency = 2  # 1 <= concurrency <= 10
resps = asyncio.run(
    wqbs.concurrent_simulate(
        multi_alphas,  # `alphas` or `multi_alphas`
        concurrency,
        # return_exceptions=True,
        # on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    )
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    print(resp.status_code)
    print(resp.text)

save_to_json(resps, concurrent_simulate_to_multi_alphas, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 3. 检测：wqb.WQBSession.check(...)
##----------------------------------------------------------------------

check_3yYPdo4 = "check_3yYPdo4.json"
alpha_id = '3yYPdo4'
resp = asyncio.run(
    wqbs.check(
        alpha_id,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
print(resp.status_code)
print(resp.text)

save_to_json(resp, check_3yYPdo4, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 4. 批量检测：wqb.WQBSession.concurrent_check(...)
##----------------------------------------------------------------------

concurrent_check_alpha_ids_concurrency = "concurrent_check_alpha_ids_concurrency.json"

alpha_ids = ['<alpha_id_0>', '<alpha_id_1>', '<alpha_id_2>']
concurrency = 2
resps = asyncio.run(
    wqbs.concurrent_check(
        alpha_ids,
        concurrency,
        # return_exceptions=True,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
for idx, resp in enumerate(resps, start=1):
    print(idx)
    # print(resp.status_code)
    # print(resp.text)

save_to_json(resps, concurrent_check_alpha_ids_concurrency, out_path=OUT_PUT_PATH)


##----------------------------------------------------------------------
# 5. 提交 Submit：wqb.WQBSession.submit(...)
##----------------------------------------------------------------------

submit_3yYPdo4 = "submit_3yYPdo4.json"
alpha_id = '3yYPdo4'
resp = asyncio.run(
    wqbs.submit(
        alpha_id,
        # on_start=lambda vars: print(vars['url']),
        # on_finish=lambda vars: print(vars['resp']),
        # on_success=lambda vars: print(vars['resp']),
        # on_failure=lambda vars: print(vars['resp']),
    ),
)
print(resp.status_code)
print(resp.text)

save_to_json(resp, submit_3yYPdo4, out_path=OUT_PUT_PATH)