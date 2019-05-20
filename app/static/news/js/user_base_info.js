function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $(".user_data button").click(function () {
        $(".change_user_data").hide()
        $(".base_info").show()
    })
    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender[name='gender']:checked").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        var params = {
            "signature": signature,
            "nick_name": nick_name,
            "gender": gender
        }

        $.ajax({
            url: "/user/base_info",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 更新父窗口内容
                    $('.user_center_name', parent.document).html(params['nick_name'])
                    $('#nick_name', parent.document).html(params['nick_name'])
                    $("#index_nick_name",parent.document).html(params['nick_name'])
                    $("#user_nick",parent.document).html(params['nick_name'])
                    $('.input_sub').blur()
                    $(".base_info").hide()
                    $(".change_user_data").show()
                    $("#nick_name_data").html(params["nick_name"])
                    $("#signature_data").html(params["signature"])
                    if (params["gender"] == "man"){  $("#gender_data").html("男")}
                    if (params["gender"] == "woman"){  $("#gender_data").html("女")}

                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})