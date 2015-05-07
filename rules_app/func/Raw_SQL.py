# -*- coding: UTF-8 -*-
__author__ = 'Aarion zh'

# =========================================重新定义规则=========================================


def category_n_days_fee(day):
    """
    计算当前各类目ID，抽取去年这个时候往后推n天（自有/行业）的每个类目的销售额(所有类目)
    :return:
    """
    return "select `m`.`tag1`, `m`.`tag2`, `m`.`tag3`, sum(`m`.`fee_total`) as `T` "\
        "from( "\
            "select `status_order`.`itemnum`, `status_order`.`fee_total`, `a`.`tag1`, `a`.`tag2`, `a`.`tag3` "\
            "from `status_order` "\
            "inner join( "\
                "select `tag1`, `tag2`, `tag3`, `itemnum` "\
                "from `meta_sku` "\
                "where `itemnum` != '-1' and `tag1` is not null "\
            ")as `a` "\
            "on `a`.`itemnum` = `status_order`.`itemnum` "\
            "where (date_sub(curdate(), INTERVAL 1 year) <= date(`status_order`.`createtime`)) " \
                " and (date_add(date_sub(curdate(), INTERVAL 1 year), INTERVAL {Day} day) > date(`status_order`.`createtime`))" \
                " and `status_order`.`itemnum` != '-1' "\
        ") as `m` "\
        "group by `m`.`tag1`, `m`.`tag2`, `m`.`tag3` "\
        "order by `T` desc".format(Day=day)


def category_main_itemnum(tag1, tag2, tag3):
    """
    获取当前主推类目的所有产品号
    :return:
    """
    return "select `itemnum` "\
        "from `meta_sku` "\
        "where `itemnum` != '-1' and `tag1` = '{Tag1}' and `tag2` = '{Tag2}' and `tag3` = '{Tag3}'"\
        .format(Tag1=tag1, Tag2=tag2, Tag3=tag3)


def item_day_fee(itemnum, day):
    """
    计算给定货号，给定时间区间，的每天销售额
    :param itemnum:
    :param day:
    :return:
    """
    return "select `created`, sum(`fee_total`) "\
        "from `status_order` "\
        "where date_sub(curdate(), INTERVAL {Day} DAY) <= date(`status_order`.`createtime`) "\
            "and `status_order`.`itemnum` = '{ItemNum}' "\
        "group by `created`"\
        .format(Day=day, ItemNum=itemnum)


def item_total_fee(item, day):
    """
    计算给定货号最近30天的总销售额
    """
    return "select if(sum(`fee_total`) > 0, sum(`fee_total`), 0) "\
        "from `status_order` "\
        "where `itemnum` = '{Item}' and date_sub(curdate(), interval {Day} day) <= `createtime`"\
        .format(Item=item, Day=day)


def recommend_itemnum_seller(item, day):
    """
    寻找没有商家给产品的自有商家
    :param item: 给定的产品
    :param day: 最近n天新进的商家
    """
    return "select `sellernick`, `status`, `is_zhuican` "\
        "from `meta_cooperation` "\
        "where `is_zhuican` = '1' and `status` > '0' and `sellernick` not in ( "\
            "select `sellernick` "\
            "from `meta_item` "\
            "where `itemnum` = '{Item}' "\
        ") and `startdate` > date_sub(curdate(), interval {Day} day)".format(Item=item, Day=day)


def seller_category_percent(seller, category_total, tag1, tag2, tag3, day=30):
    return "select if(sum(`fee_total`)>0, sum(`fee_total`), 0)/{CategotyTotal} "\
        "from `status_order`  "\
        "where `sellernick` = '{Seller}' and `created` > date_sub(curdate(), interval {Day} day) "\
            "and `itemnum` in ( "\
                "select `itemnum` "\
                "from `meta_sku` "\
                "where `tag1` = '{Tag1}' and `tag2` = '{Tag2}' and `tag3` = '{Tag3}' "\
            ")"\
        .format(Seller=seller, Tag1=tag1, Tag2=tag2, Tag3=tag3, Day=day, CategotyTotal=category_total)


# ===**********************=== 更改2015/2/11 ===**********************===
# 此处转化为对特定商家的分析，而非对渠道商的分析

def seller_n_near_days_number(auction_id=10000, day=60):
    """
    计算商家具体商品最近n天每天的销售数量（为的是计算安全库存）
    """
    return "SELECT `thedate`, sum(`gmv_auction_num`) "\
        "FROM `fact_shop_order` "\
        "WHERE  DATE_SUB(CURDATE(), INTERVAL {Day} DAY) <= DATE(`thedate`) "\
            "AND DATE(`thedate`) < CURDATE() AND `auction_id` = '{AuctionId}' "\
        "GROUP BY `thedate`".format(Day=day, AuctionId=auction_id)


def query_store_number(auction_id=10000):
    """
    查询商品的库存
    """
    return "SELECT `quantity` "\
        "FROM `dim_auction` "\
        "WHERE `auction_id` = '{AuctionId}'".format(AuctionId=auction_id)


def query_category(auction_id=1000):
    """
    查询商品对应的类目
    """
    return "select `cat_id` "\
        "from `dim_auction` "\
        "where `auction_id` = '{AuctionId}'".format(AuctionId=auction_id)


def category_industry_sql(cat_id, day):
    """
    求出类目最近n天行业数据
    """
    return "SELECT `dim_date`.`dateindex`, if(`a`.`NUM`>0, `a`.`NUM`, 0) "\
        "FROM `dim_date` "\
        "left join( "\
            "select `thedate`, sum(`uv_index_top100`) as `NUM` "\
            "from `fact_ind_uv_trend` "\
            "where date(`thedate`) > date_sub(curdate(), INTERVAL {Day} day) and `cat_id` = '{CatId}' "\
            "group by `thedate` "\
        ") as `a` "\
        "on `a`.`thedate` = `dim_date`.`dateindex` "\
        "where date_sub(curdate(), INTERVAL {Day} day) <= date(`dateindex`)  AND date(`dateindex`) < CURDATE()"\
        .format(Day=day, CatId=cat_id)


def query_seller_auction_number(auction_id, day):
    """
    求出该该商家的最近n天每天的销售额
    """
    return "SELECT `dim_date`.`dateindex`, if(`a`.`NUM`>0, `a`.`NUM`, 0) "\
        "FROM `dim_date` "\
        "left join( "\
            "select `thedate`, sum(`gmv_auction_num`) as `NUM` "\
            "from `fact_shop_order` "\
            "where date(`thedate`) > date_sub(curdate(), INTERVAL {Day} day) and `auction_id` = '{AuctionId}' "\
            "group by `thedate` "\
        ") as `a` "\
        "on `a`.`thedate` = `dim_date`.`dateindex` "\
        "where date_sub(curdate(), INTERVAL {Day} day) <= date(`dateindex`)  AND date(`dateindex`) < CURDATE()"\
        .format(Day=day, AuctionId=auction_id)


def get_auction_num(item_id):
    """
    获取对应产品的上架的商品数量
    """
    return "SELECT IF(COUNT(`itemnum`)>0, COUNT(`itemnum`), 0) "\
        "FROM `dim_auction` "\
        "WHERE `itemnum` = '{ItemNum}'".format(ItemNum=item_id)


def uv_abnormal_sql(cat_id, day):
    """
    获取流量数据                                    【因为数据不全的原因，暂时用的是去年这个时间的数据】
    """
    return "SELECT `uv_index_top100`, `thedate` "\
        "FROM `fact_ind_uv_trend`  "\
        "WHERE `cat_id` = '{CatId}' AND `thedate` >= DATE_SUB(DATE_SUB(CURDATE(), INTERVAL {Day} DAY), INTERVAL 1 YEAR) "\
            "AND `thedate` <= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)".format(CatId=cat_id, Day=day)


def ctr_abnormal_sql():
    """
    获取转换率数据                                   【转化率数据没有】
    """
    return ""


def rank_abnormal_sql():
    """
    获取商品的行业排名数据                             【行业排名数据没有】
    """
    return ""


def calculate_days_number_sql(auction_id=10000, day=60):
    """
    计算最近60天的销售额                             【因为数据不全的原因，暂时用的是去年这个时间的数据】
    """
    return "SELECT `dateindex`, if(`A`.`total`> 0, `A`.`total`, 0) "\
        "FROM `dim_date` "\
        "LEFT JOIN ( "\
            "SELECT `thedate`, sum(`gmv_auction_num`) as `total` "\
            "FROM `fact_shop_order` "\
            "WHERE DATE_SUB(DATE_SUB(CURDATE(), INTERVAL {Day} DAY), INTERVAL 1 YEAR) <= DATE(`thedate`) "\
                "AND DATE(`thedate`) < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "\
                "AND `auction_id` = '{AuctionId}' "\
            "GROUP BY `thedate` "\
        ") AS `A` "\
        "ON `A`.`thedate` = `dim_date`.`dateindex` "\
        "WHERE DATE_SUB(DATE_SUB(CURDATE(), INTERVAL {Day} DAY), INTERVAL 1 YEAR) <= DATE(`dateindex`) AND DATE(`dateindex`) < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "\
        "ORDER BY `dateindex`".format(Day=day, AuctionId=auction_id)


def industry_category_number_sql(cat_id, day):
    """
    计算该类目去年这个时候后60天的销售额  【这一步作为预测，数据可以取去年这个时间的后n天】 【因为数据不全的原因，暂时用的是去年这个时间的数据】
    """
    return "SELECT `dim_date`.`dateindex`, if(`a`.`NUM`>0, `a`.`NUM`, 0) "\
        "FROM `dim_date`  "\
        "left join(  "\
           "select `thedate`, sum(`uv_index_top100`) as `NUM` "\
           "from `fact_ind_uv_trend`  "\
           "where `cat_id` = '{CatId}' "\
           "group by `thedate` "\
        ") as `a` "\
        "on `a`.`thedate` = `dim_date`.`dateindex` "\
        "where DATE_SUB(DATE_ADD(CURDATE(), INTERVAL {Day} day), INTERVAL 1 YEAR) >= `dateindex` "\
            "AND DATE(`dateindex`) > DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "\
        "ORDER BY `dateindex`".format(Day=day, CatId=cat_id)


def fenxiao_category_number_sql(cat_id, day):
    """
    计算分销商对应类目的商家的每天销售额                            【因为数据不全的原因，暂时用的是去年这个时间的数据】
    """
    return "select `dim_date`.`dateindex`, if(`a`.`num` is not null, `a`.`num`, 0) "\
        "from `dim_date` "\
        "left join( "\
            "select `thedate`, `auction_id`, sum(`gmv_auction_num`) as `num` "\
            "from `fact_shop_order` "\
            "where `auction_id` in ( select `auction_id` from `dim_auction` where `cat_id` = '{CatId}') "\
            "group by `thedate` "\
        ")as `a` on `a`.`thedate` = `dim_date`.`dateindex` "\
        "where `dateindex` > DATE_SUB(DATE_SUB(CURDATE(), INTERVAL 1 YEAR), INTERVAL {Day} DAY) "\
                "and `dateindex` < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "\
        "order by `dateindex`".format(CatId=cat_id, Day=day)


def select_seller(cat_id):
    """
    获取自有的商家的名称以及商品id(特定类目)
    """
    return "SELECT `dim_auction`.`sellernick`, `auction_id`, `quantity` "\
        "FROM `dim_auction` "\
        "LEFT JOIN ( "\
            "SELECT `sellernick` "\
            "FROM `dim_seller_list` "\
            "WHERE `status` > '0' AND `is_zhuican` = '1' "\
        ") AS `a` ON `a`.`sellernick` = `dim_auction`.`sellernick` "\
        "WHERE `cat_id` = '{CatId}'".format(CatId=cat_id)


def select_category_number(cat_id):
    """
    获取所有类目的销售总额                                         【因为数据不全的原因，暂时用的是去年这个时间的数据】
    """
    return "SELECT `C`.`cat_id`, `C`.`auction_id`, IF(SUM(`D`.`number`) > 0, SUM(`D`.`number`), 0) AS `Number` "\
        "FROM( "\
            "SELECT `cat_id`, `auction_id` "\
            "FROM `dim_auction` "\
            "WHERE `cat_id` = '{CatId}' "\
        ") AS `C` "\
        "LEFT JOIN( "\
            "SELECT `auction_id`, SUM(`gmv_auction_num`) AS `number` "\
            "FROM `fact_shop_order` "\
            "WHERE `thedate` > DATE_SUB(DATE_SUB(CURDATE(), INTERVAL 1 YEAR), INTERVAL 30 DAY) "\
                "AND `thedate` < DATE_SUB(CURDATE(), INTERVAL 1 YEAR) "\
            "GROUP BY `auction_id` "\
        ") AS `D` ON `C`.`auction_id` = `D`.`auction_id`".format(CatId=cat_id)


def item_upnumber_sql(item):
    """
    获取产品的上架商家数量
    """
    return "select `itemnum`, if(count(distinct `sellernick`) is null, 0, count(distinct `sellernick`)) "\
        "from `dim_auction` where `itemnum` = '{ItemNum}'".format(ItemNum=item)


def seller_need2up_item_sql(item):
    """
    获取未上架该产品的商家名单【自有的商家】
    """
    return "select `sellernick` "\
        "from `dim_seller_list` "\
        "where `status` > '0' and `is_zhuican` = '1' and `seller_id` not in ( "\
            "select `seller_id` "\
            "from `dim_auction` "\
            "where `itemnum` = '{ItemNum}' )".format(ItemNum=item)


def seller_need2up_cate_sql(cat_id):
    """
    获取未上架该类目产品的商家名单【自有的商家】
    """
    return "select `sellernick` "\
        "from `dim_seller_list` "\
        "where `status` > '0' and `is_zhuican` = '1' and `seller_id` not in ( "\
            "select `seller_id` "\
            "from `dim_auction` "\
            "where `cat_id` = '{CatId}' )".format(CatId=cat_id)


def seller_have_up_cate_sql(cat_id):
    """
    获取已经上架该类目产品的商家名单【自有的商家】
    """
    return "select `sellernick` "\
        "from `dim_seller_list` "\
        "where `status` > '0' and `is_zhuican` = '1' and `seller_id` in ( "\
            "select `seller_id` "\
            "from `dim_auction` "\
            "where `cat_id` = '{CatId}' )".format(CatId=cat_id)


def seller_have_up_item_sql(item):
    """
    获取已经上架该产品的商家
    """
    return "select `sellernick` "\
        "from `dim_seller_list` "\
        "where `status` > '0' and `is_zhuican` = '1' and `seller_id` in ( "\
            "select `seller_id` "\
            "from `dim_auction` "\
            "where `itemnum` = '{ItemNum}' )".format(ItemNum=item)