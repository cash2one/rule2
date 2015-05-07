# -*- coding: utf-8 -*-
import os, time, datetime, sys, inspect
from ..businessRule.variables import BaseVariables
from ..businessRule.variables import (numeric_rule_variable, string_rule_variable, select_rule_variable)


class RuleVariables(BaseVariables):

    def __init__(self):
        pass

    @numeric_rule_variable(label='Hours')
    def hours(self):
        t = time.localtime()
        y, m, d, h1, mt1 = t[:5]
        return h1

    @numeric_rule_variable(label='Minutes')
    def minutes(self):
        t = time.localtime()
        y, m, d, h1, mt1 = t[:5]
        return mt1