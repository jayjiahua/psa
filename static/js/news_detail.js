/* Theme Name: Worthy - Free Powerful Theme by HtmlCoder
 * Author:HtmlCoder
 * Author URI:http://www.htmlcoder.me
 * Version:1.0.0
 * Created:November 2014
 * License: Creative Commons Attribution 3.0 License (https://creativecommons.org/licenses/by/3.0/)
 * File Description: Place here your custom scripts
 */

window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(231,233,237)'
};


var color = Chart.helpers.color;

function emotionsCanvas(emotionsData) {
    var data = {
        labels: ["乐", "好", "怒", "哀", "惧", "恶", "惊"],
        datasets: [
            {
                backgroundColor: color(window.chartColors.blue).alpha(0.2).rgbString(),
                borderColor: window.chartColors.blue,
                pointBackgroundColor: window.chartColors.blue,
                data: emotionsData
            }
        ]
    };

    var config = {
        type: 'radar',
        data: data,
        options: {

            legend: {
                display: false,
            },
            title: {
                display: true,
                text: '情绪值',
                fontSize: 20
            },
            scale: {
                ticks: {
                    beginAtZero: true,
                },
                pointLabels: {
                    fontSize: 20,
                    fontColor: "#339BEB"
                }
            },
            elements: {
                arc: {
                    borderColor: "#ffffff"
                }
            }
        }
    };

    return new Chart(document.getElementById("emotions-canvas"), config);
}

function polarityCanvas(polarityData) {
    var config = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: polarityData,
                backgroundColor: [
                    window.chartColors.orange,
                    window.chartColors.green,
                    window.chartColors.blue,
                ],
                label: 'Dataset 1'
            }],
            labels: [
                "正面",
                "中性",
                "负面",
            ]
        },
        options: {
            responsive: true,
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: '情感极性',
                fontSize: 20
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    };

    var ctx = document.getElementById("polarity-canvas").getContext("2d");
    return new Chart(ctx, config);
}

function createRandomItemStyle() {
    return {
        normal: {
            color: 'rgb(' + [
                Math.round(Math.random() * 160 + 95),
                Math.round(Math.random() * 160 + 95),
                Math.round(Math.random() * 160 + 95)
            ].join(',') + ')'
        }
    };
}


function wordCountCanvas(wordCountData) {
    require(
        [
            'echarts',
            'echarts/chart/wordCloud',   // load-on-demand, don't forget the Magic switch type.
        ],
        function (ec) {
            var myChart = ec.init(document.getElementById('word-count-canvas'));
            var option = {
                title: {
                    text: '词频统计',
                    show: false
                    // textAlign: 'center'
                },
                tooltip: {
                    show: true
                },
                series: [{
                    name: '词频统计',
                    type: 'wordCloud',
                    size: ['100%', '100%'],
                    textRotation : [0, 90],
                    textPadding: 0.5,
                    autoSize: {
                        enable: true,
                        minSize: 12
                    },
                    data: wordCountData
                }]
            };
            myChart.setOption(option);
        }
    );
}

function provinceCanvas(provinceData) {
    require(
        [
            'echarts',
            'echarts/chart/map',   // load-on-demand, don't forget the Magic switch type.
        ],
        function (ec) {
            var myChart = ec.init(document.getElementById('province-canvas'));
            var option = option = {
                title : {
                    text: '各省评论数与情感极性指数',
                    x:'center'
                },
                legend: {
                    orient: 'vertical',
                    x:'left',
                    data:['评论数','正面值','负面值']
                },
                tooltip : {
                    trigger: 'item'
                },
                dataRange: {
                    min: 0,
                    max: 1000,
                    x: 'left',
                    y: 'bottom',
                    text:['活跃','不活跃'],           // 文本，默认为数值文本
                    calculable : true
                },
                toolbox: {
                    show: true,
                    orient : 'vertical',
                    x: 'right',
                    y: 'center',
                    feature : {
                        mark : {show: true},
                        dataView : {show: true, readOnly: false},
                        restore : {show: true},
                        saveAsImage : {show: true}
                    }
                },
                roamController: {
                    show: true,
                    x: 'right',
                    mapTypeControl: {
                        'china': true
                    }
                },
                series : [
                    {
                        name: '评论数',
                        type: 'map',
                        mapType: 'china',
                        roam: false,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        data: provinceData.comment_count
                    },
                    {
                        name: '正面值',
                        type: 'map',
                        mapType: 'china',
                        roam: false,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        data: provinceData.positive
                    },
                    {
                        name: '负面值',
                        type: 'map',
                        mapType: 'china',
                        roam: false,
                        itemStyle:{
                            normal:{label:{show:true}},
                            emphasis:{label:{show:true}}
                        },
                        data: provinceData.negative
                    }
                ]
            };

            myChart.setOption(option);
        }
    );
}

$.get("/api/news/" + newsID + "/analysis_data/", function (result) {
    if (result.result) {
        var updateTime = new Date(result.data.create_time * 1000 + 3600 * 8 * 1000);
        $("#update-time").text(updateTime.getFullYear() + "-" + (updateTime.getMonth() + 1)
            + "-" + updateTime.getDate() + " " + updateTime.getHours() + ":" +
            updateTime.getMinutes() + ":" + updateTime.getSeconds());
        var emotions = result.data.sentiment_value.emotions;
        var emotionsData = [
            emotions.EMOTION_HAPPY,
            emotions.EMOTION_GOOD,
            emotions.EMOTION_ANGER,
            emotions.EMOTION_SORROW,
            emotions.EMOTION_FEAR,
            emotions.EMOTION_EVIL,
            emotions.EMOTION_SURPRISE
        ];
        emotionsCanvas(emotionsData);

        var polarity = result.data.sentiment_value.polarity;
        var polarityData = [
            polarity.positive,
            polarity.neutral,
            polarity.negative
        ];
        polarityCanvas(polarityData);

        var wordCount = result.data.word_count;
        var wordCountData = [];
        for (var i in wordCount) {
            wordCountData.push({
                name: wordCount[i].word,
                value: wordCount[i].count,
                itemStyle: createRandomItemStyle()
            });
        }
        wordCountCanvas(wordCountData);

        var province = result.data.province_statistics;
        var provinceData = {
            comment_count: [],
            positive: [],
            negative: []
        };
        for (var i in province) {
            provinceData.comment_count.push({
                name: i,
                value: province[i].comment_count
            })
            provinceData.positive.push({
                name: i,
                value: province[i].positive
            })
            provinceData.negative.push({
                name: i,
                value: province[i].negative
            })
        }

        provinceCanvas(provinceData);


    } else {

    }
}, "json");