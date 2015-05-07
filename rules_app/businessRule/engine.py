# -*- coding: UTF8 -*-
from fields import FIELD_NO_INPUT


def run_all(rule_list,
            defined_variables,
            defined_actions,
            stop_on_first_trigger=False):
    rule_was_triggered = False
    for rule in rule_list:
        result = run(rule, defined_variables, defined_actions)
        if result:
            rule_was_triggered = True
            if stop_on_first_trigger:
                return result
    return rule_was_triggered


def run(rule, defined_variables, defined_actions):
    conditions, actions = rule['conditions'], rule['actions']
    rule_triggered = check_conditions_recursively(conditions, defined_variables)
    if rule_triggered:
        return do_actions(actions, defined_actions)
        # return True
    return False


def check_conditions_recursively(conditions, defined_variables):
    keys = list(conditions.keys())
    if keys == ['all']:
        assert len(conditions['all']) >= 1
        for condition in conditions['all']:
            if not check_conditions_recursively(condition, defined_variables):
                return False
        return True

    elif keys == ['any']:
        assert len(conditions['any']) >= 1
        for condition in conditions['any']:
            if check_conditions_recursively(condition, defined_variables):
                return True
        return False

    else:
        # help prevent errors - any and all can only be in the condition dict
        # if they're the only item
        assert not ('any' in keys or 'all' in keys)
        return check_condition(conditions, defined_variables)


def check_condition(condition, defined_variables):
    """ Checks a single rule condition - the condition will be made up of
    variables, values, and the comparison operator. The defined_variables
    object must have a variable defined for any variables in this condition.
    """
    name, op, value = condition['name'], condition['operator'], condition['value']
    operator_type = _get_variable_value(defined_variables, name)
    return _do_operator_comparison(operator_type, op, value)


def _get_variable_value(defined_variables, name):
    """ Call the function provided on the defined_variables object with the
    given name (raise exception if that doesn't exist) and casts it to the
    specified type.

    Returns an instance of operators.BaseType
    """

    def fallback(*args, **kwargs):
        raise AssertionError("Variable {0} is not defined in class {1}".format(
            name, defined_variables.__class__.__name__))

    method = getattr(defined_variables, name, fallback)
    val = method()
    return method.field_type(val)


def _do_operator_comparison(operator_type, operator_name, comparison_value):
    """ Finds the method on the given operator_type and compares it to the
    given comparison_value.

    operator_type should be an instance of operators.BaseType
    comparison_value is whatever python type to compare to
    returns a bool
    """

    def fallback(*args, **kwargs):
        raise AssertionError("Operator {0} does not exist for type {1}".format(
            operator_name, operator_type.__class__.__name__))

    method = getattr(operator_type, operator_name, fallback)
    if getattr(method, 'input_type', '') == FIELD_NO_INPUT:
        return method()
    return method(comparison_value)


def do_actions(actions, defined_actions):
    for action in actions:
        method_name = action['name']

        def fallback(*args, **kwargs):
            raise AssertionError("Action {0} is not defined in class {1}" \
                                 .format(method_name, defined_actions.__class__.__name__))

        params = action.get('params') or {}
        method = getattr(defined_actions, method_name, fallback)
        return method(**params)


# def runsql(table, time_begin, time_end, month):
# return "SELECT `a`.`date` AS `{0}`,SUM(`a`.`fee`) AS `total_fee_{0}`,`a`.`sellernick` " \
#            "FROM( " \
#            "SELECT `date`,`pid`,`number`*`price` AS `fee`,`sellernick` " \
#            "FROM `{1}` " \
#            "WHERE `date`>'{2}' AND `date`<'{3}'" \
#            ") AS `a` " \
#            "GROUP BY `a`.`sellernick`".format(month, table, time_begin, time_end)


# def sql_fee(table):
#     return "SELECT SUBSTRING(`date`,1,10) AS `Date`, `pid`, `number`*`price` AS `fee`, `sellernick`, `number`, `price`" \
#            "FROM `{Table}`".format(Table=table)
#
#
# def sql_day(table):
#     sqlFee = sql_fee(table)
#     return "SELECT `d`.`Date`, `d`.`pid`, SUM(`d`.`fee`) AS `dFee`, `d`.`sellernick`" \
#            "FROM ({SQL}) AS `d`" \
#            "GROUP BY `d`.`Date`, `d`.`sellernick`".format(SQL=sqlFee)
#
#
# def sql_month(table):
#     sqlDay = sql_day(table)
#     return "SELECT MONTH(`m`.`Date`) AS `month`, SUM(`m`.`dFee`) AS `mFee`, `m`.`sellernick`" \
#            "FROM ({SQL}) AS `m`" \
#            "GROUP BY MONTH(`m`.`Date`), `m`.`sellernick`".format(SQL=sqlDay)
#
#
# def sql_Column2Row(table):
#     sqlColumn2Row = sql_month(table)
#     # SELECT `a`.`sellernick`, MAX(CASE `a`.`month` WHEN '11' THEN `a`.`mFee` ELSE 0 END) AS `m_11`, MAX(CASE `a`.`month` WHEN '12' THEN `a`.`mFee` ELSE 0 END) AS `m_12`
#     return "SELECT `a`.`sellernick`, SUM(IF(`a`.`month` = '11', `a`.`mFee`, 0)) AS `m_11`, SUM(IF(`a`.`month` = '12', `a`.`mFee`, 0)) AS `m_12`" \
#            "FROM({SQL}) AS `a`" \
#            "GROUP BY `a`.`sellernick`".format(SQL=sqlColumn2Row)