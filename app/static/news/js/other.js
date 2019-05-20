// 解析url中的查询字符串
// function decodeQuery(){
//     var search = decodeURI(document.location.search);
//     return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
//         values = item.split('=');
//         result[values[0]] = values[1];
//         return result;
//     }, {});
// }
//刷新图片验证码
function generateImageCode() {
    //1、生成一个UUID
    imageCodeId=generateUUID();
    //2、拼接一个url地址
    var imageCodeIdUrl='/passport/image_code?code_id='+imageCodeId;
    // 3. 设置页面中图片验证码img标签的src属性
    $('.get_pic_code').attr('src',imageCodeIdUrl)
}
$(function(){
    // 页面加载完毕，获取新闻列表
    // getNewsList(1)

    // TODO 关注当前作者
    $(".focus").click(function () {
            var user_id = $(this).attr('data-userid')
    var params = {
        "action": "follow",
        "user_id": user_id
    }
    $.ajax({
        url: "/news/followed_user",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 关注成功
                var count = parseInt($(".follows b").html());
                count++;
                $(".follows b").html(count + "")
                $(".focus").hide()
                $(".focused").show()
            }else if (resp.errno == "4101"){
                // 未登录，弹出登录框
                $('.login_form_con').show();
                generateImageCode()
            }else {
                // 关注失败
                alert(resp.errmsg)
            }
        }
    })
    })

    // TODO 取消关注当前作者
    $(".focused").click(function () {
        var user_id = $(this).attr('data-userid')
    var params = {
        "action": "unfollow",
        "user_id": user_id
    }
    $.ajax({
        url: "/news/followed_user",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 取消关注成功
                var count = parseInt($(".follows b").html());
                count--;
                $(".follows b").html(count + "")
                $(".focus").show()
                $(".focused").hide()
            }else if (resp.errno == "4101"){
                // 未登录，弹出登录框
                $('.login_form_con').show();
                generateImageCode()
            }else {
                // 取消关注失败
                alert(resp.errmsg)
            }
        }
    })
    })
})

// // TODO 获取新闻列表
// function getNewsList(page) {
//  var query = decodeQuery()
//     var params = {
//         "p": page,
//         "id": query["id"]
//     }
//     $.ajax({
//         url: "/other",
//         type: "post",
//         contentType: "application/json",
//         headers: {
//             "X-CSRFToken": getCookie("csrf_token")
//         },
//         data: JSON.stringify(params),
//         success: function (resp){
//             if(resp.errno=="4001")
//         }
//     })
// }
