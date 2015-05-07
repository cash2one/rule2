# -*- coding: UTF-8 -*-
__author__ = 'Aarion zh'
from scipy import stats
from Raw_SQL import *
from django.db import connection
import numpy as np
import math


def percent2(temp_list, dict_index, threshold, tag):  # 计算占比的函数
    """
    计算主要的函数
    dict_index:  要分析数据对应的下标
    """
    temp_total = 0
    total = 0
    index = 0
    for ii in temp_list:
        total += ii[dict_index]

    if tag == 1:  # 从大到小排序   【其中temp_list已经把所有数据的和求出，并放在了temp_list[0]中】
        for i in temp_list[1:]:
            temp_total += i[dict_index]
            index += 1
            if temp_total / (total * 1.0) > threshold:
                return index


def culcate_slope(res, count):
    """
    计算给定数组值的拟合斜率
    """
    date = []
    i = 0
    x = range(count)
    for key in res:
        date.insert(i, float(key[1]))  # 进行强制类型转换
        i += 1
    # var_1 = np.var(date)
    # mean = np.mean(date)
    max_date = max(date)
    if max(date) == 0:
        max_date = 1
    min_date = min(date)
    data = []
    for ii in date:
        ii = abs((ii-min_date) / max_date)
        data.append(ii)
    # print data
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
    return slope


def calcute_all_category_fee(day=60):
    """
    计算当前各类目ID，抽取最近60(默认)天（自有/行业）销售额    【计算的是每个类目去年这个时候未来n天的销售额】
    :param day:   类目分析的销售额天数
    :return:
    """
    cur = connection.cursor()
    sql_all_category_fee = category_n_days_fee(day)  # 获取所有销售类目的去年这个时候后n天的销售额
    cur.execute(sql_all_category_fee)
    res = cur.fetchall()

    return res


def calculate_trend(**arg):
    """
    计算趋势的函数
    """
    cur = connection.cursor()
    if arg['trigger'] == 'industry_category':  # 行业的趋势
        # slopes = 0
        # total_number = 0
        # for days in arg['Days']:  # Days是分析的时间区间，比如10天，20天，30天斜率，目的是取一个平均值
        #     sql_industry_current = category_industry_sql(arg['category_id'], days)  # 求出去年n天左右的销售趋势
        #     count_ind = cur.execute(sql_industry_current)
        #     if count_ind > 1:  # 比较的对象大小要至少两个
        #         res_industry_current = cur.fetchall()
        #         slo = culcate_slope(res_industry_current, count_ind)
        #         slopes += slo
        #         total_number += 1
        # if total_number > 0:    # 分母不能为零
        #     slopes = slopes / total_number               # 三枪该类目去年行业的销售趋势
        # # slopes = (slopes if slopes > 0 else -slopes)     # 【这里做了特殊处理】  计算的类目必须趋势是上升的
        # return slopes
        pass

    elif arg['trigger'] == 'all_number_fenxiao':     # 计算分销商所下属的所有店铺的的销售趋势
        slopes = 0
        total_number = 0
        number_list = []
        sql = fenxiao_category_number_sql(arg['category_id'], 60)  # 抽取类目的数据
        cur.execute(sql)
        res_cat_number = cur.fetchall()
        for temp_cat_number in res_cat_number:
            number_list.append(float(temp_cat_number[1]))
        for days in arg['Days']:
            slop2 = cul_slope(number_list[-days:], days)
            slopes += slop2
            total_number += 1
        if total_number > 0:
            slopes = slopes / total_number

        return slopes

    elif arg['trigger'] == 'all_number_industry':  # 计算类目的行业趋势
        slopes = 0
        total_number = 0
        number_list = []
        sql = industry_category_number_sql(arg['category_id'], 60)  # 抽取类目的数据
        cur.execute(sql)
        res_cat_number = cur.fetchall()
        for temp_cat_number in res_cat_number:
            number_list.append(float(temp_cat_number[1]))
        for days in arg['Days']:
            slop2 = cul_slope(number_list[-days:], days)
            slopes += slop2
            total_number += 1
        if total_number > 0:
            slopes = slopes / total_number

        return slopes

    elif arg['trigger'] == 'all_number':
        slopes = 0
        total_number = 0   # 计算有销售记录的个数
        for days in arg['Days']:
            slop2 = cul_slope(arg['Number'][-days:], days)
            slopes += slop2
            total_number += 1
        if total_number > 0:
            slopes = slopes / total_number

        return slopes


def cul_slope(date, count):
    """
    计算给定数组值的拟合斜率       [ 此处为已经处理好的数据，无需进行重新处理]
    """
    data = []

    max_date = max(date)
    if max(date) == 0:
        max_date = 1
    min_date = min(date)
    for ii in date:
        iii = float(ii-min_date) / float(max_date - min_date)
        data.append(iii)

    # var_1 = np.var(date)
    # mean = np.mean(date)
    # for ii in date:
    #     iii = float(ii - mean) / float(math.sqrt(var_1))
    #     data.append(iii)

    # print data

    x = range(count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
    return slope


def calculate_n_days_number(auction_id, day):
    """
    获取商家商品最近n天的销售数量
    """
    cur = connection.cursor()
    # sql = seller_n_near_days_number(auction_id, day)
    # cur.execute(sql)
    cur.execute("SELECT `thedate`, sum(`gmv_auction_num`) "\
        "FROM `fact_shop_order` "\
        "WHERE  DATE_SUB(DATE_SUB(CURDATE(), INTERVAL %d DAY), INTERVAL 1 YEAR) <= DATE(`thedate`) "\
            "AND DATE(`thedate`) < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND `auction_id` = '%s' "\
        "GROUP BY `thedate`" % (day, auction_id))
    res = cur.fetchall()
    return res


def add_store_number(item):
    """
    查询商品的的库存以及所对应的类目
    """
    cur = connection.cursor()
    sql = query_store_number(item)
    cur.execute(sql)
    res = cur.fetchall()
    return res


def test_abnormal(data, today):
    scope = [np.mean(data) - math.sqrt(np.var(data)), np.mean(data) + math.sqrt(np.var(data))]
    print scope
    if scope[0] < today < scope[1]:
        return 0  # 正常
    else:
        return 1  # 异常


def calculate_days_number(auction_id, day):
    """
    抽取最近day的销售数量
    """
    cur = connection.cursor()
    sql = calculate_days_number_sql(auction_id, day)
    cur.execute(sql)
    res = cur.fetchall()
    return res