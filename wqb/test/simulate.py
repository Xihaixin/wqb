import asyncio
from wqb import WQBSession
from wqb.config import enVars

envars = enVars.get_env_vars()

wqbs = WQBSession(envars)
resp = wqbs.auth_request()
print(resp.status_code)           # 201
print(resp.ok)                    # True
print(resp.json()['user']['id'])  # <Your BRAIN User ID>

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
