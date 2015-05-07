# -*- coding: UTF-8 -*-
from businessRule import run_all
from func.ruleactions import RuleActions
from func.rulevaribles import RuleVariables

__author__ = 'AaronZh'


rules = [{
    "conditions": {
        "all": [{"name": "hours", "operator": "equal_to", "value": 15},
                {"name": "minutes", "operator": "equal_to", "value": 50}]
    },
    "actions": [{
        "name": 'test_SSP02',  # 入口函数
        "params": {}
    }]
}]

run_all(rules, RuleVariables(), RuleActions(), True)