# -*- coding: UTF-8 -*-
__author__ = 'Aaron zh'
from function import *
from Raw_SQL import *
from rules_app.models import *
import sys, time, threading
from django.db import connection

global current_time
current_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
reload(sys)
sys.setdefaultencoding("utf-8")
from ..businessRule.actions import *


class MyThread(object):
    def __init__(self, func_list=None):
        self.func_list = func_list
        self.threads = []

    def set_thread_func_list(self, func_list):
        """
        @note: func_list是一个list，每个元素是一个dict，有func和args两个参数
        """
        self.func_list = func_list

    @staticmethod
    def trace_func(func, *args, **kwargs):
        """
        @note:替代profile_func，新的跟踪线程返回值的函数，对真正执行的线程函数包一次函数，以获取返回值
        """
        func(*args, **kwargs)

    def start(self):
        """
        @note: 启动多线程执行，并阻塞到结束
        """
        self.threads = []
        for func_dict in self.func_list:
            if func_dict["args"]:
                new_arg_list = [func_dict["func"]]
                for arg in func_dict["args"]:
                    new_arg_list.append(arg)
                new_arg_tuple = tuple(new_arg_list)
                task = threading.Thread(target=self.trace_func, args=new_arg_tuple)
            else:
                task = threading.Thread(target=self.trace_func, args=(func_dict["func"],))
            self.threads.append(task)

        for thread_obj in self.threads:
            thread_obj.start()

        for thread_obj in self.threads:
            thread_obj.join()


class RuleActions(BaseActions):
    def __init__(self):
        pass

    @rule_action()
    def cal_store_number(self, res_list):        # 根据商品ID，查询商品的库存
        cur = connection.cursor()
        for res in res_list:
            cur.execute('SELECT `quantity` FROM `dim_auction` WHERE `auction_id` = %s' % res['AuctionId'])
            res_store = cur.fetchall()
            res['Store'] = res_store[0][0]  # 商品的库存量
        return res_list

    @rule_action()
    def item_auction_number(self, res_list):  # 分析产品对应的商品上架数量
        for res in res_list:
            cur = connection.cursor()
            sql = get_auction_num(res['ItemNum'])  # 获取产品的上架数量
            cur.execute(sql)
            res_cate = cur.fetchall()
            for temp in res_cate:
                res['ItemStoreNumber'] = temp[0]

        return res_list

    @rule_action()
    def select_object_auction(self, res_list):          # 选择要分析的是具体商品还是全部商品
        list_item = []                  # 获取需要分析的商家商品列表
        if res_list == 'all':                 # 默认值为all，先查找该商家的所有货号，增加到list_item列表中
            cur = connection.cursor()
            cur.execute("select distinct(dim_auction.auction_id) "\
                "from dim_auction "\
                "left join fact_shop_order "\
                "on dim_auction.auction_id = fact_shop_order.auction_id "\
                "left join dim_sku "\
                "on dim_sku.cat_id = dim_auction.cat_id "\
                "where dim_auction.itemnum is not null and fact_shop_order.auction_id is not null")
            res_cate = cur.fetchall()
            for temp in res_cate:
                # add_item = dict(AuctionId=int(temp[0]))
                add_item = dict(AuctionId=str(temp[0]))
                list_item.append(add_item)
        else:
            add_item = dict(AuctionId=str(res_list))  # 增加商品ID到list中
            list_item.append(add_item)

        return list_item

    @rule_action()
    def select_object_itemnum(self, res_list):         # 选择要分析的是具体产品还是全部产品
        list_item = []
        if res_list == 'all':   # 默认值为all，查询该商家的所有产品ID
            cur = connection.cursor()
            cur.execute("select distinct `itemnum` from `dim_auction` where `itemnum` is not null")
            # cur.execute("select distinct(dim_auction.itemnum) "\
            #     "from dim_auction "\
            #     "left join fact_shop_order "\
            #     "on dim_auction.auction_id = fact_shop_order.auction_id "\
            #     "left join dim_sku "\
            #     "on dim_sku.cat_id = dim_auction.cat_id "\
            #     "where dim_auction.itemnum is not null and fact_shop_order.auction_id is not null")
            res_cate = cur.fetchall()
            for temp in res_cate:
                add_item = dict(ItemNum=temp[0])
                list_item.append(add_item)
        else:
            add_item = dict(ItemNum=res_list)  # 添加产品Id
            list_item.append(add_item)
        return list_item

    @rule_action()
    def select_object_category(self, res_list):      # 选择要分析的是具体类目还是全部类目
        list_cat = []
        if res_list == 'all':
            cur = connection.cursor()
            cur.execute('SELECT DISTINCT `cat_id` FROM `dim_sku`')
            res_cate = cur.fetchall()
            for temp in res_cate:
                add_item = dict(CategoryId=temp[0])
                list_cat.append(add_item)
        else:
            add_item = dict(CategoryId=res_list)  # 添加产品Id
            list_cat.append(add_item)
        return list_cat


    @rule_action()
    def get_auction_days_number(self, res_list):        # 抽取商品的最近60天的销售数量
        for temp in res_list:
            temp_res = []
            res = calculate_days_number(temp['AuctionId'], day=60)
            for temp_number in res:
                ii = int(temp_number[1])
                temp_res.append(ii)
            temp['Number'] = temp_res  # 增加商品最近60天的销售额明细
        return res_list

    @rule_action()
    def calculate_seller_trend(self, res_list):
        """
        计算商家的销售数量趋势
        """
        for temp in res_list:
            days = [10, 20, 45]
            args_seller = {'trigger': 'all_number', 'auction_id': temp['AuctionId'], 'Days': days, 'Number': temp['Number']}
            slopes = calculate_trend(**args_seller)
            temp['SellerSlopes'] = slopes

        return res_list

    @rule_action()
    def industry_category_trend(self, res_list):   # 计算类目的行业趋势
        """
        计算类目的行业的趋势，如果没有该类目需要查找该类目
        """
        for res in res_list:
            if 'CategoryId' not in res:    # 如果货号不在list中，那么就查询对应的货号
                cur = connection.cursor()
                sql = query_category(res['AuctionId'])
                cur.execute(sql)
                res_cate = cur.fetchall()
                res['CategoryId'] = res_cate[0][0]

            days = [20, 30, 45]
            args_industry_category = {'trigger': 'all_number_industry', 'category_id': res['CategoryId'], 'Days': days}
            industry_category_slopes = calculate_trend(**args_industry_category)
            res['CategorySlopes'] = industry_category_slopes
        return res_list

    @rule_action()
    def fenxiao_category_trend(self, res_list):   # 计算分销商的类目的行业趋势
        """
        计算类目的行业的趋势，如果没有该类目需要查找该类目
        """
        for res in res_list:
            if 'CategoryId' not in res:    # 如果货号不在list中，那么就查询对应的货号
                cur = connection.cursor()
                sql = query_category(res['AuctionId'])
                cur.execute(sql)
                res_cate = cur.fetchall()
                res['CategoryId'] = res_cate[0][0]
            days = [20, 30, 45]
            args_industry_category = {'trigger': 'all_number_fenxiao', 'category_id': res['CategoryId'], 'Days': days}
            industry_category_slopes = calculate_trend(**args_industry_category)
            res['CategorySlopesFX'] = industry_category_slopes
        return res_list

    @rule_action()
    def forecast_days_number(self, res_list):
        """
        SSP02R2015 - 2    【根据商品ID，预测未来销售量】
        """
        for res in res_list:
            if 'CategorySlopes' not in res:    # 如果货号不在list中，那么就查询对应的货号
                temp_list = []
                temp_list.append(res)
                temp_list = self.industry_category_trend(temp_list)
                res = temp_list[0]

            sum_this_year = 0
            res_near = calculate_n_days_number(res['AuctionId'], day=10)  # 计算最近三十天的销售额
            for res_temp in res_near:
                ii = int(res_temp[1])
                sum_this_year += ii  # 取最近三十天的销售总数目

            res['FutureNumber'] = round(sum_this_year*(1 + res['CategorySlopes']))  # 增加预测的未来的销售量到结果列表

        return res_list

    @rule_action()
    def uv_abnormal_find_object(self, res_list):   # 分析流量数据
        cur = connection.cursor()
        for res in res_list:
            if 'CategoryId' not in res:
                cur.execute('SELECT `cat_id` FROM `dim_auction` WHERE `auction_id` = %s' % res['AuctionId'])
                resul = cur.fetchall()
                for temp in resul:
                    res['CategoryId'] = temp[0]
            sql = uv_abnormal_sql(res['CategoryId'], 10)   # 获取最近十天的流量数据
            cur.execute(sql)
            result = cur.fetchall()
            data = []
            today = result[-1][0]    # 今天的流量数据
            for temp in result[:-1]:
                data.append(temp[0])
            abnor = test_abnormal(data, today)
            res['Abnormal'] = abnor
        return res_list

    @rule_action()
    def ctr_abnormal_find_object(self, res_list):    # 分析转化率
        cur = connection.cursor()
        for res in res_list:
            sql = ctr_abnormal_sql(res['CategoryId'], 10)   # 获取最近十天的转化率  【sql函数没有完善】
            cur.execute(sql)
            result = cur.fetchall()
            data = []
            today = result[-1][0]    # 今天的流量数据
            for temp in result[:-1]:
                data.append(temp[0])
            abnor = test_abnormal(data, today)
            res['Abnormal'] = abnor
        return res_list

    @rule_action()
    def rank_abnormal_find_object(self, res_list):    # 分析商品排名
        cur = connection.cursor()
        for res in res_list:
            sql = rank_abnormal_sql(res['CategoryId'], 10)   # 获取最近十天的排名  【sql函数没有完善】
            cur.execute(sql)
            result = cur.fetchall()
            data = []
            today = result[-1][0]    # 今天的流量数据
            for temp in result[:-1]:
                data.append(temp[0])
            abnor = test_abnormal(data, today)
            res['Abnormal'] = abnor
        return res_list

    @rule_action()
    def judge_abnormal(self, res_list):
        for res in res_list:
            if res['Abnormal'] == 1:
                res['IsAbnormal'] = '异常'
            elif res['Abnormal'] == 0:
                res['IsAbnormal'] = '正常'
        return res_list

    @rule_action()
    def select_object_seller(self, res_list):      # 根据类目ID增加自有的分销商ID,以及商品的ID
        cur = connection.cursor()
        for res in res_list:
            sql = select_seller(res['CategoryId'])
            cur.execute(sql)
            result = cur.fetchall()
            # print result
            res['SellerAuction'] = []
            for temp in result:
                a = dict(SellerNick=str(temp[0]), AuctionId=str(temp[1]), Store=int(temp[2]), CategorySlopes=res['CategorySlopes'])
                res['SellerAuction'].append(a)

        return res_list

    @rule_action()
    def forecast_R1_number(self, res_list):   # 对于渠道商，分析商家的产品未来的销售量
        for res in res_list:
            res = self.forecast_days_number(res['SellerAuction'])   # 根据商品Id计算未来的销售量
        return res_list

    @rule_action()
    def calculate_category_number(self, res_list):   # 计算各个类目的销售额
        cur = connection.cursor()
        for res in res_list:
            sql = select_category_number(res['CategoryId'])
            cur.execute(sql)
            result = cur.fetchall()
            res['Number'] = float(result[0][2])  # 各类目的销售数量

        return res_list

    @rule_action()
    def calculate_main_cat(self, res_list):    # 获取主推类目以及主推产品
        res_list.sort(key=lambda x: x['Number'], reverse=True)
        index = percent2(res_list, 'Number', 0.8, 1)      # 计算主要(80%)
        res_list = res_list[:index]
        return res_list

    @rule_action()
    def calculate_main_item(self, res_list):  # 获取主推类目下的主推产品
        cur = connection.cursor()
        for res in res_list:
            cur.execute("SELECT `itemnum` FROM `dim_sku` WHERE `cat_id` = '%s'" % res['CategoryId'])
            result = cur.fetchall()
            list = []
            for temp in result:
                list.append(dict(ItemNum=temp[0]))
            res['Item'] = list
        return res_list

    @rule_action()
    def calculate_item_up_number(self, res_list):  # 抽取各产品的上架商家数量
        cur = connection.cursor()
        for res in res_list:
            sql = item_upnumber_sql(res['ItemNum'])
            cur.execute(sql)
            result = cur.fetchall()
            res['UpNumber'] = float(result[0][1])
        return res_list

    @rule_action()
    def item_need2up(self, res_list):   # 计算需要上架的产品
        res_list.sort(key=lambda x: x['UpNumber'], reverse=True)  # 从大到小排序
        index = percent2(res_list, 'UpNumber', 0.8, 1)      # 计算主要
        res_list = res_list[index:]
        return res_list

    @rule_action()
    def seller_need2up_item(self, res_list):   # 需要上架某产品的商家
        cur = connection.cursor()
        for res in res_list:
            sql = seller_need2up_item_sql(res['ItemNum'])
            cur.execute(sql)
            result = cur.fetchall()
            list = []
            for temp in result:
                list.append(dict(SellerNick=temp[0]))
            res['Seller'] = list
        return res_list

    @rule_action()
    def seller_need2up_category(self, res_list):   # 需要上架某产品的商家 seller_have_up_category
        cur = connection.cursor()
        for res in res_list:
            sql = seller_need2up_cate_sql(res['CategoryId'])
            cur.execute(sql)
            result = cur.fetchall()
            list = []
            for temp in result:
                list.append(dict(SellerNick=temp[0]))
            res['Seller'] = list
        return res_list

    @rule_action()
    def seller_have_up_category(self, res_list):   # 需要上架某产品的商家
        cur = connection.cursor()
        for res in res_list:
            sql = seller_have_up_cate_sql(res['CategoryId'])
            cur.execute(sql)
            result = cur.fetchall()
            list = []
            for temp in result:
                list.append(dict(SellerNick=temp[0]))
            res['Seller'] = list
        return res_list

    @rule_action()
    def seller_have_up_item(self, res_list):   # 需要上架的商家
        cur = connection.cursor()
        for res in res_list:
            sql = seller_have_up_item_sql(res['ItemNum'])
            cur.execute(sql)
            result = cur.fetchall()
            list = []
            for temp in result:
                list.append(dict(SellerNick=temp[0]))
            res['Seller'] = list
        return res_list

    @rule_action()
    def final_handle(self, res_list):   # 最后处理函数
        for res in res_list:
            if ('CategorySlopes' in res) and ('SellerSlopes' in res):
                if res['CategorySlopes'] > res['SellerSlopes']:
                    res['TagSlopes'] = '低于行业趋势'
                else:
                    res['TagSlopes'] = '高于行业趋势'
                continue
            if 'ItemStoreNumber' in res:
                if res['ItemStoreNumber'] == 0:
                    res['Tag'] = '产品待上架'
                else:
                    res['Tag'] = '产品已上架'
                continue
            if 'Abnormal' in res:  # 数据异常的规则
                if res['Abnormal'] == 1:
                    res['IsAbnormal'] = '异常'
                elif res['Abnormal'] == 0:
                    res['IsAbnormal'] = '正常'
                continue

        return res_list

    @rule_action()
    def test(self, res_list):

        res1 = self.select_object_category('all')
        res2 = self.industry_category_trend(res1)
        res3 = self.calculate_category_number(res2)
        res4 = self.calculate_main_cat(res3)
        res5 = self.fenxiao_category_trend(res4)
        res6 = self.seller_need2up_category(res5)
        print res6

    @rule_action()
    def test_SSP02(self):

        step1 = self.select_object_auction('all')
        step2 = self.get_auction_days_number(step1)
        step3 = self.forecast_days_number(step2)
        step4 = self.cal_store_number(step3)
        step5 = self.industry_category_trend(step4)
        for res in step5:
            exit_temp1 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='行业趋势')
            exit_temp2 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='库存')
            exit_temp3 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='未来销量')

            if not exit_temp1:   # 数据库中不存在该记录
                temp1 = Result(rule_id=1, item=res['AuctionId'], name='行业趋势', value=float(res['CategorySlopes']))
                temp1.save(using='Cloud_drools')
            else:  # 对于数据库中存在的数据需要更新
                exit_1 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='行业趋势')
                exit_1.value = float(res['CategorySlopes'])
                exit_1.save(using='Cloud_drools')

            if not exit_temp2:
                temp2 = Result(rule_id=1, item=res['AuctionId'], name='库存', value=float(res['Store']))
                temp2.save(using='Cloud_drools')
            else:
                exit_2 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='库存')
                exit_2.value = float(res['Store'])
                exit_2.save(using='Cloud_drools')

            if not exit_temp3:   # 数据库中不存在该记录
                temp2 = Result(rule_id=1, item=res['AuctionId'], name='未来销量', value=float(res['FutureNumber']))
                temp2.save(using='Cloud_drools')
            else:
                exit_3 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='未来销量')
                exit_3.value = float(res['FutureNumber'])
                exit_3.save(using='Cloud_drools')

        return step5

    @rule_action()
    def rule_one(self):
        step1 = self.select_object_auction("all")    # 抽取商品
        step2 = self.get_auction_days_number(step1)  # 抽取商品的数据
        step3 = self.calculate_seller_trend(step2)   # 计算自己的销售趋势
        step4 = self.industry_category_trend(step3)  # 计算行业的销售趋势
        step5 = self.forecast_days_number(step4)     # 计算未来的销量
        step6 = self.cal_store_number(step5)         # 抽取库存量

        for res in step6:
            exit_temp1 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='行业增速')
            exit_temp2 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='库存')
            exit_temp3 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='未来销量')
            exit_temp4 = Result.objects.using('Cloud_drools').filter(item=res['AuctionId'], name='自身增速')

            if not exit_temp1:  # 数据库中不存在该记录
                temp1 = Result(rule_id=1, item=res['AuctionId'], name='行业增速', value=float(res['CategorySlopes']))
                temp1.save(using='Cloud_drools')
            else:  # 对于数据库中存在的数据需要更新
                exit_1 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='行业增速')
                exit_1.value = float(res['CategorySlopes'])
                exit_1.save(using='Cloud_drools')

            if not exit_temp2:
                temp2 = Result(rule_id=1, item=res['AuctionId'], name='库存', value=float(res['Store']))
                temp2.save(using='Cloud_drools')
            else:
                exit_2 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='库存')
                exit_2.value = float(res['Store'])
                exit_2.save(using='Cloud_drools')

            if not exit_temp3:
                temp2 = Result(rule_id=1, item=res['AuctionId'], name='未来销量', value=float(res['FutureNumber']))
                temp2.save(using='Cloud_drools')
            else:
                exit_3 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='未来销量')
                exit_3.value = float(res['FutureNumber'])
                exit_3.save(using='Cloud_drools')

            if not exit_temp4:   # 数据库中不存在该记录
                temp2 = Result(rule_id=1, item=res['AuctionId'], name='自身增速', value=float(res['SellerSlopes']))
                temp2.save(using='Cloud_drools')
            else:
                exit_3 = Result.objects.using('Cloud_drools').get(item=res['AuctionId'], name='自身增速')
                exit_3.value = float(res['SellerSlopes'])
                exit_3.save(using='Cloud_drools')

        return step6