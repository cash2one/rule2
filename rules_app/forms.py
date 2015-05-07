# -*- coding: UTF-8 -*-
__author__ = 'Aarion zh'

from django import forms


class search_condition(forms.Form):
    func = forms.CharField(max_length=50, initial='rule2')
    category = forms.CharField(max_length=50, label='类目')
    day = forms.IntegerField(label='天数')
    tag = forms.IntegerField(label='tag', initial=1)