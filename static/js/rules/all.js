/**
 * Created by Aaron Zhang on 2015/3/1.
 */
function add() {
    var otr = document.getElementById("tab").insertRow(-1);
    var checkTd = document.createElement("td");
    checkTd.innerHTML = '<input type="checkbox" class="check" onclick="ccolor()" name="checkItem">';
    var otd1 = document.createElement("td");
    otd1.innerHTML =
        '<select onChange="changeOtd2()" name="infoName_txt" id="infoName_txt' + (document.getElementById('tab').rows.length - 1) + '">' +
            '<option selected value=" ">请选择</option>' +
            '<option value="select_auction">选择需要分析的商品</option>' +
            '<option value="select_itemnum">选择需要分析的产品</option>' +
            '<option value="select_object_category">选择需要分析的类目</option>' +
            '<option value="get_auction_number">抽取各个商品的销售数量</option>' +
            '<option value="calculate_seller_trend">根据商品的销售数量计算销售趋势</option>' +
            '<option value="category_trend">计算类目的行业趋势</option>' +
            '<option value="fenxiao_category_trend">计算自有的销售趋势</option>' +
            '<option value="forecast_number">根据行业趋势预测未来销售数量（商家）</option>' +
            '<option value="cal_store_number">根据商品号抽取商品库存</option>' +
            '<option value="item_auction_number">获取具体产品下的上架商品数量</option>' +
            '<option value="uv_abnormal_find_object">获取商品的每日流量</option>' +
            '<option value="ctr_abnormal_find_object">获取商品的每日转化率</option>' +
            '<option value="rank_abnormal_find_object">获取商品的每日行业排名数据</option>' +
            '<option value="forecast_R1_number">根据行业趋势预测未来销售数量（渠道商）</option>' +
            '<option value="select_object_seller">获取销售类目的自有商家,及其销售的商品</option>' +
            '<option value="calculate_category_number">获取各个类目的销售数量</option>' +
            '<option value="calculate_main_cat">根据销售数量获取主推类目</option>' +
            '<option value="calculate_main_item">根据主推类目找出主推产品</option>' +
            '<option value="calculate_item_up_number">抽取各产品的上架的商家数量</option>' +
            '<option value="item_need2up">抽取需要上架的产品</option>' +
            '<option value="seller_need2up">抽取未上架该产品的商家名单</option>' +
            '<option value="seller_have_up">抽取已经上架该类目产品的商家名单</option>' +
            '<option value="seller_need2up_category">抽取未上架该类目的商家名单</option>' +
            '<option value="seller_have_up_category">抽取已经上架该类目的商家名单</option>' +
            '<option value="judge_abnormal">判断数据是否异常</option>' +
            '<option value="final_handle">处理结果</option>' +
        '</select>';
    var otd2 = document.createElement("td");
    otd2.innerHTML =
        '<select type="text" class="txt" name="infoValue_txt" id="infoValue_txt' + (document.getElementById('tab').rows.length - 1) + '">' +
            '<option value="0"> </option>' +
        '</select>';
    var otd3 = document.createElement("td");
    otd3.innerHTML = '<input type="text" name="infoInput_txt" id="infoInput_txt" class="" >';
    otr.appendChild(checkTd);
    otr.appendChild(otd1);
    otr.appendChild(otd2);
    //otr.appendChild(otd3);
}

function ccolor() {
    var c1 = document.getElementsByName('checkItem');
    for (var i = 0; i < c1.length; i++)
        if (c1[i].checked) {
            c1[i].parentNode.parentNode.className = "checkBg";
            c1[i].parentNode.nextSibling.firstChild.className = "checkTxt";
            c1[i].parentNode.nextSibling.nextSibling.firstChild.className = "checkTxt";
        }
        else {
            c1[i].parentNode.parentNode.className = "";
            c1[i].parentNode.nextSibling.firstChild.className = "";
            c1[i].parentNode.nextSibling.nextSibling.firstChild.className = "";
        }
}
function del() {
    var c = document.getElementsByName('checkItem');
    var idArray = new Array();
    for (var i = 0; i < c.length; i++)
        if (c[i].checked)
            idArray.push(i);
    var rowIndex;
    var nextDiff = 0;
    for (j = 0; j < idArray.length; j++) {
        rowIndex = idArray[j] + 1 - nextDiff++;
        document.getElementById("tab").deleteRow(rowIndex);
    }
}
function save() {
    var postString = document.getElementById("postString");
    var checkboxs = document.getElementsByName("checkItem");
    var ttab = document.getElementsByName("infoName_txt");
    var tt2 = document.getElementsByName("infoValue_txt");

    var idArray = new Array();
    for (i = 0; i < checkboxs.length; i++) {
        idArray.push(ttab[i].value + "|" + tt2[i].value);
    }

    postString.value = idArray.join("-");
    alert(postString.value);
}

function alldell() {
    var des = document.getElementsByName('checkItem');
    for (var i = 0; i < des.length; i++) {
        if (des[i].checked = document.getElementById('delall').checked) {
            des[i].parentNode.parentNode.className = "checkBg";
            des[i].parentNode.nextSibling.firstChild.className = "checkTxt";
            des[i].parentNode.nextSibling.nextSibling.firstChild.className = "checkTxt";
        }
        else {
            des[i].parentNode.parentNode.className = "";
            des[i].parentNode.nextSibling.firstChild.className = "";
            des[i].parentNode.nextSibling.nextSibling.firstChild.className = "";
        }
    }
}

