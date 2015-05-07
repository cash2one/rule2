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
            '<option value="select_object_category">选择需要分析的类目ID</option>' +
            '<option value="category_trend">分析类目的行业趋势</option>' +
            '<option value="calculate_category_number">获取类目对应销售数量</option>' +
            '<option value="calculate_main_cat">获取主推类目</option>' +
            '<option value="calculate_main_item">根据主推类目抽取相应的主推产品</option>' +
            //'<option value="calculate_main_cat_item">o分析类目的趋势以及商家的库存</option>' +
        '</select>';
    var otd2 = document.createElement("td");
    otd2.innerHTML =
        '<select type="text" class="txt" name="infoValue_txt" id="infoValue_txt' + (document.getElementById('tab').rows.length - 1) + '">' +
            '<option value="0"> </option>' +
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

