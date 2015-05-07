var conditions, actions, nameField, ageField, occupationField, submit, allData, resultRule;
(function($) {
    var occupationOptions = ["Software Engineer", "Biz Dev", "Marketing"];

    function getInitialData() {
        return {
            "variables": [{
                "name": "expiration_days",
                "label": "时间范围",
                "field_type": "numeric",
                "options": []
            }, {
                "name": "current_month",
                "label": "商家名称",
                "field_type": "string",
                "options": []
            }, {
                "name": "goes_well_with",
                "label": "商品类目",
                "field_type": "select",
                "options": ["保暖内衣", "内裤", "被心"]
            }],
            "actions": [{
                "name": "put_on_sale",
                "label": "上架",
                "params": [{
                    name: "sale_percentage",
                    label: "上架数量",
                    fieldType: "numeric"
                }]
            }, {
                "name": "order_more",
                "label": "订货",
                "params": [{
                    name: "number_to_order",
                    label: "订货数量",
                    fieldType: "numeric"
                }]
            }, {
                "name": "analysis",
                "label": "分析",
                "params": [{
                    name: "number_to_order",
                    label: "分析趋势",
                    fieldType: "numeric"
                }]
            }],
            "variable_type_operators": {
                "numeric": [{
                    "name": "equal_to",
                    "label": "等于",
                    "input_type": "numeric"
                }, {
                    "name": "less_than",
                    "label": "小于",
                    "input_type": "numeric"
                }, {
                    "name": "greater_than",
                    "label": "大于",
                    "input_type": "numeric"
                }],
                "string": [{
                    "name": "equal_to",
                    "label": "等于",
                    "input_type": "text"
                }, {
                    "name": "non_empty",
                    "label": "所有",
                    "input_type": "none"
                }],
                "select": [{
                    "name": "contains",
                    "label": "包含关键字",
                    "input_type": "select"
                }, {
                    "name": "does_not_contain",
                    "label": "不包含关键字",
                    "input_type": "select"
                }]
            }
        };
    }

    function onReady() {
        conditions = $("#conditions");
        actions = $("#actions");
        nameField = $("#nameField");
        occupationField = $("#occupationField");
        ageField = $("#ageField");
        submit = $("#submit");
        resultRule = $("#result");
        allData = getInitialData();

        initializeConditions(allData);
        initializeActions(allData);
        initializeForm();
    }

    function initializeConditions(data) {
        conditions.conditionsBuilder(data)
    }

    function initializeActions(data) {
        actions.actionsBuilder(data);
    }

    function initializeForm() {
        for (var i = 0; i < occupationOptions.length; i++) {
            var o = occupationOptions[i];
            occupationField.append($("<option>", {
                value: o.name,
                text: o.label
            }));
        }

        submit.click(function(e) {
            e.preventDefault();
            var text = "rules = [{" + '<br/>';
            console.log("CONDITIONS");
            text += '"conditions":';
            console.log(JSON.stringify(conditions.conditionsBuilder("data")));
            text += JSON.stringify(conditions.conditionsBuilder("data")) + ',' + '<br/>';
            console.log("ACTIONS");
            text += '"actions":';
            console.log(JSON.stringify(actions.actionsBuilder("data")));
            text += JSON.stringify(actions.actionsBuilder("data")) + '<br/>' + '}]';
            resultRule.html(text);
            //window.location.href="result_list"
        });
    }
    $(onReady);
})(jQuery);