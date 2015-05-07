# -*- coding:utf-8 -*-
from django.db import models


class RuleChose(models.Model):

    task_id = models.CharField(max_length=50)
    rule_id = models.TextField()
    res = models.TextField()

    class Meta:
        db_table = "rule_chosed"


class BpmActivity(models.Model):

    createtime = models.DateField(auto_now=True)
    due_date = models.DateField(auto_now_add=True)
    task_id = models.CharField(max_length=50)
    task_title = models.CharField(max_length=50)

    class Meta:
        db_table = "dim_bpm_activity"


class ActivityTag(models.Model):

    createtime = models.DateField(auto_now=True)
    task_id = models.CharField(max_length=50)   # 任务编号
    target = models.CharField(max_length=50)   # 任务对象
    target_type = models.CharField(max_length=11)    # 对象的类型，商品/产品...

    class Meta:
        db_table = "raw_activity_tag"


class Result(models.Model):

    rule_id = models.IntegerField(max_length=11)
    item = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=20, decimal_places=6)   # 对应数据库的decimal类型字段

    class Meta:
        db_table = "result"