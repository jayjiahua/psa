/**
 * Created by Jay on 2017/4/6 0006.
 */

$("#search").bind("input propertychange", function() {
    var keyword = $.trim($(this).val());
    if (!!keyword) {
        $.get("/api/search_news/", {
            keyword: keyword
        }, function(result) {
            var html = "";
            if (result.data.length) {
                for (var i in result.data) {
                    var label = '<span class="label label-primary">' + result.data[i].channel + "</span> ";
                    html += "<li class='search-li' data-url='/news/" + result.data[i].news_id + "/'>" + label + result.data[i].title + "</li>";
                }
            } else {
                html = "<li>找不到含有该关键词的新闻</li>";
            }
            $("#search-result-ul").html(html);
            if (!!$.trim($("#search").val())) {
                $("#search-result-container").slideDown(300);
            } else {
                $("#search-result-container").slideUp(300);
            }

        }, "json");
    } else {
        $("#search-result-container").slideUp(300);
    }
});

$("#search-result-ul").on("click", ".search-li", function() {
    var news_url = $(this).data("url");
    window.location.href = news_url;
});