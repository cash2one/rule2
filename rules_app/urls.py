# -*- coding: UTF-8 -*-
from django.conf.urls import include, url, patterns
from rules_app import views

__author__ = 'Aarion zh'

urlpatterns = patterns(
    '',
    url(r'^task_list$', views.task_list),

    url(r'^result_list_SSP01R2015', views.result_SSP01R2015),
    url(r'^result_list_SSP02R2015', views.result_SSP02R2015),
    url(r'^result_list_SPP01R2015', views.result_SPP01R2015),
    url(r'^result_list_SPP02R2015', views.result_SPP02R2015),
    url(r'^result_list_SPP03R2015', views.result_SPP03R2015),
    url(r'^result_list_SSP03R2015', views.result_SSP03R2015),

    url(r'^result_list_fx_one', views.result_fx_one),    # 渠道商规则
    url(r'^result_list_fx_two', views.result_fx_two),     # 渠道商规则
    url(r'^result_list_fx_three', views.result_fx_three),    # 渠道商规则
    url(r'^result_list_fx_four', views.result_fx_four),    # 渠道商规则
    url(r'^result_list_fx_five', views.result_fx_five),     # 渠道商规则
    url(r'^result_list_fx_seven', views.result_fx_seven),    # 渠道商规则

    url(r'^SSP02_result', views.test_SSP02),   # SSP02的每一步规则整合进一个主程序中

    url(r'^rule_one', views.rule_one),  #

    url(r'^all', views.result_all),  # 所有的规则

    url(r'^test_bak', views.test_bak),

    url(r'^test', views.test)   # 第三方测试进程
)