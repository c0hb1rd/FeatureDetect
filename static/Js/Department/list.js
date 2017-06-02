/**
 * Created by c0hb1rd on 2017/3/20.
 */

/** node-data-format
 * node_data = {
 *     name: "",
 *     id: "",
 *     members: [{name: "", id: ""}],
 *     children: [node_data]
 * };
 */


var treeBlock =
    '<ul class="level0"></ul>';

var nodeBlock =
    '<li class="node${ nodeID }">' +
    '<span></span>' +
    '<section>' +
    '<p class="dep" data-id="${ dataID }">${ name }</p>' +
    '</section>' +
    '<ul class="level${ levelID }"></ul>' +
    '</li>';

var memberBlock =
    '<span></span>' +
    '<section>' +
    '<ul class=".members"></ul>' +
    '</section>';

var memberLi =
    '<li class="member" data-id="${ dataID }">${ member }</li>';

var personItem =
    '<section class="person-item">' +
    '<span id="person-id">${ id },</span>' +
    '<header>' +
    '<img src="/static/Image/Users/${ picture }.jpg" alt="">' +
    '<aside>' +
    '<p>${ name }</p>' +
    '<section>' +
    '<a href="/user/edit/${ id }" class="ctrl-edit" ></a>' +
    '<a href="/user/delete/${ id }" class="ctrl-delete" ></a>' +
    '</section>' +
    '</aside>' +
    '</header>' +
    '<aside>' +
    '<ul>' +
    '<li>' +
    '<span>登录名</span>' +
    '<p>${ loginName }</p>' +
    '</li>' +
    '<li>' +
    '<span>性别</span>' +
    '<p>${ gender }</p>' +
    '</li>' +
    '<li>' +
    '<span>身份证</span>' +
    '<p>${ userID }</p>' +
    '</li>' +
    '<li>' +
    '<span>录入时间</span>' +
    '<p>${ recordTime }</p>' +
    '</li>' +
    '<li>' +
    '<span>部门</span>' +
    '<p>${ department }</p>' +
    '</li>' +
    '<li>' +
    '<span>登录身份</span>' +
    '<p>${ rights }</p>' +
    '</li>' +
    '<li>' +
    '<span>角色</span>' +
    '<p>${ roles }</p>' +
    '</li>' +
    '</ul>' +
    '</aside>' +
    '</section>';


$.template("rootNode", treeBlock);
$.template("nodeBlock", nodeBlock);
$.template("memberBlock", memberBlock);
$.template("memberLi", memberLi);
$.template("personItem", personItem);

function initPerson(data, appendTo) {
    $("#member").text("人数（"+ data.length +"）");
    for (var i in data) {
        if (data.hasOwnProperty(i)) {
            var d = data[i];
            var params = {
                name: d.userName,
                rights: d.rights,
                gender: d.gender,
                loginName: d.loginName,
                recordTime: d.recordTime,
                department: d.department,
                roles: d.roles,
                userID: d.userID,
                id: d.id,
                picture: "default"
            };
            if (d.hasLogo) {
                params['picture'] = d.id
            }
            $.tmpl("personItem", params).appendTo(appendTo)
        }
    }
}

function initNodeEvent() {
    $("section>ul>li").children("span").css("display", "none");
    $(".left ul").each(function () {
        $(this).children("li").last().addClass("last-li");
        if ($(this).children().length == 0) {
            $(this).remove();
        }
    });
    var p = $(".left p");
    p.on("click", function () {
        $(this).parent().next("ul").slideToggle();
    });

    p.each(function () {
        if ($(this).parent().next().text() == "") {
            $(this).css("cursor", "not-allowed")
        }
    });

    p.on("mouseover", function () {
        // alert($(this).attr("data-id"))
    });


}

function initTree(data, levelID, appendTo) {
    var nodeID = 0;
    var currentNodeLevel = levelID + 1;
    var currentChildrenlNodeLevel = " .level" + currentNodeLevel;

    for (var i in data) {
        if (data.hasOwnProperty(i)) {
            var name = data[i].name;
            var dataID = data[i].id;
            var node = " .node" + nodeID;

            $.tmpl("nodeBlock", {nodeID: nodeID, name: name, levelID: levelID + 1, dataID: dataID}).appendTo(appendTo);

            if (data[i].hasOwnProperty("members")) {
                var members = data[i].members;
                if (members.length > 0) {
                    $.tmpl("memberBlock", {}).appendTo(appendTo + ">.node"+ nodeID +">section");
                    for (var j in members) {
                        if (members.hasOwnProperty(j)) {
                            var member = members[j];
                            $.tmpl("memberLi", {member: member.userName, dataID: member.id}).appendTo(appendTo + ">.node"+ nodeID +">section>section>ul")
                        }
                    }
                }
            }

            if (data[i].hasOwnProperty("children")) {
                var children = data[i].children;
                if (children.length > 0) {
                    var nextAppendTo = appendTo + node + currentChildrenlNodeLevel;
                    initTree(children, levelID+1, nextAppendTo)
                }
            }

            nodeID += 1;
        }

    }

}

/**
 * Created by c0hb1rd on 2017/3/10.
 */
function initPersonEvent() {
    //open popup
    var yes = $("#yes");
    var no = $("#no");
    var cdPopup = $('.cd-popup');

    no.on("click", function () {
        cdPopup.removeClass('is-visible');
    });

    $('.right .ctrl-delete').on('click', function (event) {

        yes.on("click", function () {
            location.href = event.target.href;

            return false;
        });
        cdPopup.addClass('is-visible');

        return false;
    });

    //close popup
    cdPopup.on('click', function (event) {
        if ($(event.target).is('.cd-popup-close') || $(event.target).is('.cd-popup')) {
            event.preventDefault();
            $(this).removeClass('is-visible');
        }
    });
    //close popup when clicking the esc keyboard button
    $(document).keyup(function (event) {
        if (event.which == '27') {
            $('.cd-popup').removeClass('is-visible');
        }
    });
}
