describe('$.fn.conditionsBuilder', function() {
  var container, rules;
  var occupationOptions = [ "Software Engineer", "Biz Dev", "Marketing" ];

  beforeEach(function() {
    container = $("<div>");
    container.conditionsBuilder({
      variables: [
            { "name": "expiration_days",
              "label": "时间范围",
              "field_type": "numeric",
              "options": []},
            { "name": "current_month",
              "label": "商家名称",
              "field_type": "string",
              "options": []},
            { "name": "goes_well_with",
              "label": "商品类目",
              "field_type": "select",
              "options": ["保暖内衣", "内裤", "被心"]}
      ],
      variable_type_operators: {
            "numeric": [ {"name": "equal_to",
                          "label": "等于",
                          "input_type": "numeric"},
                         {"name": "less_than",
                          "label": "小于",
                          "input_type": "numeric"},
                         {"name": "greater_than",
                          "label": "大于",
                          "input_type": "numeric"}],
            "string": [ { "name": "equal_to",
                          "label": "等于",
                          "input_type": "text"},
                        { "name": "non_empty",
                          "label": "所有",
                          "input_type": "none"}],
            "select": [ { "name": "contains",
                          "label": "包含关键字",
                          "input_type": "select"},
                        { "name": "does_not_contain",
                          "label": "不包含关键字",
                          "input_type": "select"}]
      },
      data: {"all": [
        {name: "expiration_days", operator: "greater_than", value: 3},
        {name: "current_month", operator: "equal_to", value: "December"}
      ]}
    });
    rules = container.find(".all .rule");
  });

  it('adds a condition row for each data point', function() {
    expect(rules.length).toEqual(2);
    expect(rules.eq(0).find("select.field").val()).toEqual("expiration_days");
    expect(rules.eq(0).find("select.operator").val()).toEqual("greater_than");
    expect(rules.eq(0).find("input.value").val()).toEqual('3');
    expect(rules.eq(1).find("select.field").val()).toEqual("current_month");
    expect(rules.eq(1).find("select.operator").val()).toEqual("equal_to");
    expect(rules.eq(1).find("input.value").val()).toEqual("December");
  });

  it('gives each row a remove link', function() {
    rules.eq(0).find(".remove").click();
    expect(container.find(".all .rule").length).toEqual(1);
  });

  it('adds an "Add rule" link', function() {
    var addLink = container.find(".add-rule");
    addLink.click();
    expect(container.find(".all .rule").length).toEqual(3);
  });

  it('denormalizes the response from the server', function() {
    var variables = [{ "name": "expiration_days",
                      "label": "时间范围",
                      "field_type": "numeric",
                      "options": []}];
    var operators = { "numeric": [ {"name": "equal_to",
                                  "label": "等于",
                                  "field_type": "numeric"},
                                 {"name": "less_than",
                                  "label": "小于",
                                  "field_type": "numeric"}]};
    var results = ConditionsBuilder.prototype.denormalizeOperators(variables, operators);
    expect(results.length).toEqual(1);
    expect(results[0].operators.length).toEqual(2);
    expect(results[0].operators[0].name).toEqual("equal_to");
    expect(results[0].operators[1].name).toEqual("less_than");
  });

  describe('$.fn.conditionsBuilder("data")', function() {
    it('returns serialized data', function() {
      rules.eq(0).find("input.value").val("4");
      expect(container.conditionsBuilder("data")).toEqual({"all":[
        {name: "expiration_days", operator: "greater_than", value: 4},
        {name: "current_month", operator: "equal_to", value: "December"}
      ]});
    });
  });
});
