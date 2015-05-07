# -*- coding: UTF-8 -*-
from django.db import connection
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from businessRule import run_all
from func.rulevaribles import RuleVariables
from func.ruleactions import RuleActions
from rules_app.models import *
import time
import json
global current_time
current_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))


@login_required(login_url='/admin/login')
def task_list(req):
    return render(req, 'task_list.html', {})


def get_info(req):   # function to get all post data
    List = []
    if req.method == "POST":
        q = req.POST.getlist('infoName_txt')
        p = req.POST.getlist('infoValue_txt')
        i = 0
        while i < len(q):
            a = dict(Func=q[i], Arg=p[i])
            List.append(a)
            i += 1
    return List


def func_map(func_id, tag):
    map_list = {
        'select_auction': ['select_object_auction', '选择需要分析的商品'],    # 选择要分析的是具体商品还是全部商品
        'select_itemnum': ['select_object_itemnum', '选择需要分析的产品'],    # 选择要分析的是具体产品还是全部产品
        'select_object_category': ['select_object_category', '选择需要分析的类目'],
        'get_auction_number': ['get_auction_days_number', '抽取各个商品的销售数量'],    # 抽取商品的销售数量
        'calculate_seller_trend': ['calculate_seller_trend', '根据商品的销售数量计算销售趋势'],  # 计算商品的销售趋势
        'category_trend': ['industry_category_trend', '计算类目的行业趋势'],     # 计算类目的行业趋势
        'fenxiao_category_trend': ['fenxiao_category_trend', '计算自有的销售趋势'],
        'forecast_number': ['forecast_days_number', '根据行业趋势预测未来销售数量（商家）'],  # 计算未来销量
        'cal_store_number': ['cal_store_number', '根据商品号抽取商品库存'],  # 抽取商家的库存
        'item_auction_number': ['item_auction_number', '获取具体产品下的上架商品数量'],  # 获取该产品的商品数量
        'uv_abnormal_find_object': ['uv_abnormal_find_object', '获取商品的每日流量'],
        'ctr_abnormal_find_object': ['ctr_abnormal_find_object', '获取商品的每日转化率'],
        'rank_abnormal_find_object': ['rank_abnormal_find_object', '获取商品的每日行业排名数据'],
        'forecast_R1_number': ['forecast_R1_number', '根据行业趋势预测未来销售数量（渠道商）'],
        'select_object_seller': ['select_object_seller', '获取销售类目的自有商家,及其销售的商品'],
        'calculate_category_number': ['calculate_category_number', '获取各个类目的销售数量'],
        'calculate_main_cat': ['calculate_main_cat', '根据销售数量获取主推类目'],
        'calculate_main_item': ['calculate_main_item', '根据主推类目找出主推产品'],
        'calculate_item_up_number': ['calculate_item_up_number', '抽取各产品的上架商家数量'],
        'item_need2up': ['item_need2up', '抽取需要上架的产品'],
        'seller_need2up': ['seller_need2up_item', '抽取未上架该类目产品的商家名单'],
        'seller_have_up': ['seller_have_up_item', '抽取已经上架该类目产品的商家名单'],
        'seller_need2up_category': ['seller_need2up_category', '抽取未上架该类目的商家名单'],
        'seller_have_up_category': ['seller_have_up_category', '抽取已经上架该类目的商家名单'],
        'judge_abnormal': ['judge_abnormal', '判断数据是否异常'],
        'final_handle': ['final_handle', '处理结果'],  # 最终的操作

        # '': ['', ''],
        'all': ['', 'all'],
        '-1': ['', '选择上一步作为这一步的输入'],
    }
    if tag == 0:
        return map_list[func_id][0]
    elif tag == 2:
        for temp_list in func_id:
            temp_list['Value'] = map_list[temp_list['Func']][1]
        return func_id
    elif tag == 1:
        for temp_list in func_id:
            if temp_list['Arg'] in map_list:
                temp_list['Arg'] = map_list[temp_list['Arg']][0]
            temp_list['Func'] = map_list[temp_list['Func']][1]
        return func_id


def result_all(req):
    if req.method == "POST":    # get all post data
        r = req.POST.get('rule_name')
        p = req.POST.get('rule_id')
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='all')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存

        qq = RuleChose(task_id=p, rule_id=r, res=json.dumps(inp))
        qq.save()

        Result_1 = json.dumps(Result)
        return render(req, 'result_all.html', {'Result': Result_1})
    else:
        all_obj = get_all(0)  # 获取所有的类目
        return render_to_response('set_condition_all.html', {'Which': 'all', 'AllItem': all_obj, 'total_auction': all_obj['Auction'][-1]['Id']+1, 'total_item': all_obj['Item'][-1]['Id']+1, 'total_category': all_obj['Category'][-1]['Id']+1})


def test_bak(req):      # 此界面是用作测试
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='test_bak')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        return render(req, 'result_all.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='test_bak')
        res_2 = json.loads(publisher_list.res)
        all_obj = get_all(0)  # 获取所有的类目
        chosed = func_map(res_2, 2)
        return render_to_response('set_condition_bak.html', {'Which': 'all', 'total_auction': all_obj['Auction'][-1]['Id']+1, 'total_item': all_obj['Item'][-1]['Id']+1, 'total_category': all_obj['Category'][-1]['Id']+1, 'AllItem': all_obj, 'Chosed': chosed})


# @login_required(login_url='/admin/login')
def result_fx_one(req):                                      # 渠道商的规则
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_one')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        for temp in Result:
            if temp['CategorySlopes'] > 0:
                temp['Trend'] = '上升'
                for temp1 in temp['SellerAuction']:
                    if temp1['Store'] < temp1['FutureNumber']:
                        temp1['TagStore'] = '需要增加库存'
                    else:
                        temp1['TagStore'] = '库存可以满足'
            else:
                temp['Trend'] = '下降'
                for temp1 in temp['SellerAuction']:
                    if temp1['Store'] < temp1['FutureNumber']:
                        temp1['TagStore'] = '库存安全'
                    else:
                        temp1['TagStore'] = '库存不安全'
        return render(req, 'result_list_fx_one.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_one')
        res_1 = json.loads(publisher_list.res)
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res2 = func_map(res_1, 1)
            tag = 1
        all_obj = get_all(3)  # 获取所有的类目
        return render_to_response('set_condition.html', {'Which': 'fx_one', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_fx_seven(req):                                      # 渠道商的规则 --- 产品需要上架，匹配但未上架的商家名单
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_seven')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        return render(req, 'result_list_fx_seven.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_seven')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(3)  # 获取所有的类目
        return render_to_response('set_condition.html', {'Which': 'fx_seven', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_fx_five(req):                                      # 渠道商的规则 --- 产品需要上架，匹配但未上架的商家名单
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_five')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        return render(req, 'result_list_fx_five.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_five')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(3)  # 获取所有的类目
        return render_to_response('set_condition.html', {'Which': 'fx_five', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_fx_four(req):                                      # 渠道商的规则 --- 产品需要上架，匹配但未上架的商家名单
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_four')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        # print result
        return render(req, 'result_list_fx_four.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_four')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(2)  # 获取所有的产品
        return render_to_response('set_condition.html', {'Which': 'fx_four', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_fx_three(req):                                      # 渠道商的规则 --- 产品需要上架，匹配但未上架的商家名单
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_three')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        # print result
        return render(req, 'result_list_fx_three.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_three')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(2)  # 获取所有的产品
        return render_to_response('set_condition.html', {'Which': 'fx_three', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_fx_two(req):                                      # 渠道商的规则 --- 获取主推类目以及主推商品
    if req.method == "POST":    # get all post data
        inp = get_info(req)     # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='fx_two')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        for temp in Result:
            if temp['CategorySlopes'] > 0:
                temp['Trend'] = '上升'
            else:
                temp['Trend'] = '下降'
        return render(req, 'result_list_fx_two.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='fx_two')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(3)  # 获取所有的类目
        return render_to_response('set_condition.html', {'Which': 'fx_two', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_SPP01R2015(req):
    if req.method == "POST":    # get all post data
        inp = get_info(req)   # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='SPP01R2015')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        # print Result
        Result = json.dumps(Result)
        return render(req, 'result_list_SPP01.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SPP01R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(1)  # 获取所有的商品号
        return render_to_response('set_condition.html', {'Which': 'SPP01R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_SPP03R2015(req):
    if req.method == "POST":    # get all post data
        inp = get_info(req)   # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='SPP03R2015')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        return render(req, 'result_list_SPP03.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SPP03R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(1)  # 获取所有的商品号
        return render_to_response('set_condition.html', {'Which': 'SPP03R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_SSP03R2015(req):
    if req.method == "POST":    # get all post data
        inp = get_info(req)   # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='SSP03R2015')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        # print Result
        Result = json.dumps(Result)
        return render(req, 'result_list_SSP03.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SSP03R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(1)  # 获取所有的商品号
        return render_to_response('set_condition.html', {'Which': 'SSP03R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_SSP02R2015(req):
    if req.method == "POST":  # get all post data
        inp = get_info(req)  # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        for temp in Result:
            if temp['CategorySlopes'] < 0:
                temp['Trend'] = '淡季'
                if temp['Store'] < temp['FutureNumber']:
                    temp['SafeStore'] = '安全库存'
                else:
                    temp['SafeStore'] = '不安全库存'
            else:
                temp['Trend'] = '旺季'
                if temp['Store'] < temp['FutureNumber']:
                    temp['SafeStore'] = '不安全库存'
                else:
                    temp['SafeStore'] = '安全库存'
            print temp['CategorySlopes']
            temp1 = Result(item=temp['AuctionId'], name='行业趋势', value=float(temp['CategorySlopes']))
            temp1.save(using='Local_drools')

        # temp = TestJZJ.objects.using('JZJ').get(resid='SSP03R2015')
        temp = RuleChose.objects.get(rule_id='SSP02R2015')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        Result = json.dumps(Result)
        # print Result
        return render(req, 'result_list_SSP02.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SSP02R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(1)  # 获取所有的商品号
        return render_to_response('set_condition.html', {'Which': 'SSP02R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


def test_SSP02(req):     # 这个是一个规则的完整的函数，将一个规则的所有步骤都写进了一个完整的函数中
    rules = [{
        "conditions": {
            "all": [{"name": "hours", "operator": "less_than", "value": 24},
                    {"name": "minutes", "operator": "greater_than", "value": 0}]
        },
        "actions": [{
            "name": 'test_SSP02',  # 入口函数
            "params": {}
        }]
    }]
    result = run_all(rules, RuleVariables(), RuleActions(), True)
    resultTemp = json.dumps(result)
    return render_to_response('result_list_SSP02.html', {'Result': resultTemp})


# @login_required(login_url='/admin/login')
def result_SPP02R2015(req):
    if req.method == "POST":        # get all post data
        inp = get_info(req)        # count loop
        Result = cation_loop(inp)   # 执行选择的函数操作
        temp = RuleChose.objects.get(rule_id='SPP02R2015')
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        Result = json.dumps(Result)
        return render(req, 'result_list_SPP02.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SPP02R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(1)  # 获取所有的商品号
        return render_to_response('set_condition.html', {'Which': 'SPP02R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


# @login_required(login_url='/admin/login')
def result_SSP01R2015(req):
    if req.method == "POST":        # get all post data
        inp = get_info(req)          # count loop
        Result = cation_loop(inp)     # 执行选择的函数操作
        temp = RuleChose.objects.get(rule_id='SSP01R2015')
        TaskId = temp.task_id
        temp.res = json.dumps(inp)
        temp.save()   # 修改后保存
        for temp_res in Result:
            exit_temp = ActivityTag.objects.filter(task_id=TaskId, target=temp_res['ItemNum'])
            if temp_res['ItemStoreNumber'] == 0 and (not exit_temp):   # 数据库中不存在该记录
                P = ActivityTag(createtime=current_time, task_id=TaskId, target=temp_res['ItemNum'], target_type="产品")
                P.save()
        # print Result
        Result = json.dumps(Result)
        return render(req, 'result_list_SSP01.html', {'Result': Result})
    else:
        publisher_list = RuleChose.objects.get(rule_id='SSP01R2015')
        if publisher_list.res is None:
            res2 = ''
            tag = 0
        else:
            res = json.loads(publisher_list.res)
            res2 = func_map(res, 1)
            tag = 1
        all_obj = get_all(2)  # 获取所有的产品号
        return render_to_response('set_condition.html', {'Which': 'SSP01R2015', 'Result': res2, 'Tag': tag, 'AllItem': all_obj, 'Total': all_obj[-1]['Id']+1})


def rule_one(req):  # 计算行业趋势，自身趋势，库存量，未来销售量的预测
    rules = [{
        "conditions": {
            "all": [{"name": "hours", "operator": "less_than", "value": 24},
                    {"name": "minutes", "operator": "greater_than", "value": 0}]
        },
        "actions": [{
            "name": 'rule_one',  # 入口函数
            "params": {}
        }]
    }]
    result = run_all(rules, RuleVariables(), RuleActions(), True)
    resultTemp = json.dumps(result)
    return render_to_response('result_all.html', {'Result': resultTemp})


# @login_required(login_url='/admin/login')
def test(req):  # 第三方测试进程
    rules = [{
        "conditions": {
            "all": [{"name": "hours", "operator": "less_than", "value": 24},
                    {"name": "minutes", "operator": "greater_than", "value": 0}]
        },
        "actions": [{
            "name": 'rule_test',  # 入口函数
            "params": {}
        }]
    }]
    result = run_all(rules, RuleVariables(), RuleActions(), True)
    resultTemp = json.dumps(result)
    return render_to_response('result_all.html', {'Result': resultTemp})


def cation_loop(inp):
    global result
    for k in inp:
        func = func_map(k['Func'], 0)
        arg = k['Arg']
        if arg == '-1':   # 默认-1则将上一步的结果传给下一步
            arg_temp = result
        else:
            arg_temp = arg
        rules = [{
            "conditions": {
                "all": [{"name": "hours", "operator": "less_than", "value": 24},
                        {"name": "minutes", "operator": "greater_than", "value": 0}]
            },
            "actions": [{
                "name": func,  # 入口函数
                "params": {'res_list': arg_temp}
            }]
        }]
        result = run_all(rules, RuleVariables(), RuleActions(), True)
    return result


def get_all(tag):
    all_item = []   # 产品号
    all_auction = []  # 商品号
    all_category = []  # 类目号
    all = []  # 所有的信息
    cur = connection.cursor()
    i = 1
    if tag == 1:  # 获取全部的商品  此处的商品ID是有销售记录的商品ID【特殊的情况下可能需要更改货号的来源】
        cur.execute("select distinct(dim_auction.auction_id) "\
                "from dim_auction "\
                "left join fact_shop_order "\
                "on dim_auction.auction_id = fact_shop_order.auction_id "\
                "left join dim_sku "\
                "on dim_sku.cat_id = dim_auction.cat_id "\
                "where dim_auction.itemnum is not null and fact_shop_order.auction_id is not null")
        res_auction = cur.fetchall()
        for temp_auction in res_auction:
            add_auction = dict(AuctionId=str(temp_auction[0]), Id=i)
            all_auction.append(add_auction)
            i += 1
        return all_auction
    elif tag == 2:  # 获取所有的产品
        cur.execute("select distinct `itemnum` from `dim_auction` where `itemnum` is not null")
        # cur.execute("select distinct(dim_auction.itemnum) "\
        #         "from dim_auction "\
        #         "left join fact_shop_order "\
        #         "on dim_auction.auction_id = fact_shop_order.auction_id "\
        #         "left join dim_sku "\
        #         "on dim_sku.cat_id = dim_auction.cat_id "\
        #         "where dim_auction.itemnum is not null and fact_shop_order.auction_id is not null")
        res_item = cur.fetchall()
        for temp_item in res_item:
            add_item = dict(AuctionId=str(temp_item[0]), Id=i)
            all_item.append(add_item)
            i += 1
        return all_item
    elif tag == 3:  # 获取所有的类目
        cur.execute('SELECT DISTINCT `cat_id` FROM `dim_sku`')
        res_category = cur.fetchall()
        for temp_category in res_category:
            add_category = dict(AuctionId=str(temp_category[0]), Id=i)
            all_category.append(add_category)
            i += 1
        return all_category
    elif tag == 0:
        all = {'Auction': get_all(1), 'Item': get_all(2), 'Category': get_all(3)}
        # all.append(dict(Auction=get_all(1)))
        # all.append(dict(Item=get_all(2)))
        # all.append(dict(Category=get_all(3)))
        return all


def BusinessRule():

    CallBack = {
        "variables": [
            {
                "name": "expiration_days",
                "label": "Days until expiration",
                "field_type": "numeric",
                "options": []
            },
            {
                "name": "current_month",
                "label": "Current Month",
                "field_type": "string",
                "options": []
            },
            {
                "name": "goes_well_with",
                "label": "Goes Well With",
                "field_type": "select",
                "options": ["Eggnog", "Cookies", "Beef Jerkey"]
            }
        ],
        "actions": [
            {
                "name": "put_on_sale",
                "label": "Put On Sale",
                "params": {"sale_percentage": "numeric"}
            },
            {
                "name": "order_more",
                "label": "Order More",
                "params": {"number_to_order": "numeric"}
            }
        ],
        "variable_type_operators": {
            "numeric": [
                {
                    "name": "equal_to",
                    "label": "Equal To",
                    "input_type": "numeric"
                },
                {
                    "name": "less_than",
                    "label": "Less Than",
                    "input_type": "numeric"
                },
                {
                    "name": "greater_than",
                    "label": "Greater Than",
                    "input_type": "numeric"
                }
            ],
            "string": [
                {
                    "name": "equal_to",
                    "label": "Equal To",
                    "input_type": "text"
                },
                {
                    "name": "non_empty",
                    "label": "Non Empty",
                    "input_type": "none"
                }
            ]
        }
    }