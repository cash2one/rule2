/**
 * Created by Aaron Zhang on 2015/2/13.
 */

function add() {
    var otr = document.getElementById("tab").insertRow(-1);
    var checkTd = document.createElement("td");
    checkTd.innerHTML = '<input type="checkbox" class="check" onclick="ccolor()" name="checkItem">';
    var otd1 = document.createElement("td");
    //otd1.innerHTML = '<input type="text" class="txt" name="infoName_txt" id="infoName_txt' + (document.getElementById('tab').rows.length - 1) + '" maxlength="250" value="SSP02R2015-1"/>';
    otd1.innerHTML =
        '<select onChange="changeOtd2()" name="infoName_txt" id="infoName_txt' + (document.getElementById('tab').rows.length - 1) + '">' +
            '<option selected value=" ">请选择</option>' +
            '<option value="select_auction">选择所操作的对象</option>' +
            '<option value="get_auction_number">获取商品的销售数据</option>' +
            '<option value="forecast_number">预测产品的未来销售数量</option>' +
            '<option value="cal_store_number">获取商品的库存</option>' +
            '<option value="category_trend">获取商品的行业趋势</option>' +
            '<option value="final_handle">综上，查看商品的情况</option>' +
        '</select>';
    var otd2 = document.createElement("td");
    otd2.innerHTML =
        '<select type="text" class="txt" name="infoValue_txt" id="infoValue_txt' + (document.getElementById('tab').rows.length - 1) + '" maxlength="250">' +
            '<option value=" "> </option>' +
        '</select>';

    otr.appendChild(checkTd);
    otr.appendChild(otd1);
    otr.appendChild(otd2);
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
    for (var j = 0; j < idArray.length; j++) {
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
    for (var i = 0; i < checkboxs.length; i++) {
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

