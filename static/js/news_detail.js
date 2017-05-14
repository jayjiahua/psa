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
                fontSize: 26
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

// function polarityCanvas(polarityData) {
//     var config = {
//         type: 'doughnut',
//         data: {
//             datasets: [{
//                 data: polarityData,
//                 backgroundColor: [
//                     window.chartColors.orange,
//                     window.chartColors.green,
//                     window.chartColors.blue,
//                 ],
//                 label: 'Dataset 1'
//             }],
//             labels: [
//                 "正面",
//                 "中性",
//                 "负面",
//             ]
//         },
//         options: {
//             responsive: true,
//             legend: {
//                 position: 'top',
//             },
//             title: {
//                 display: true,
//                 text: '情感极性',
//                 fontSize: 20
//             },
//             animation: {
//                 animateScale: true,
//                 animateRotate: true
//             }
//         }
//     };
//
//     var ctx = document.getElementById("polarity-canvas").getContext("2d");
//     return new Chart(ctx, config);
// }


function polarityCanvas(polarityData) {
        require(
        [
            'echarts',
            'echarts/chart/pie',   // load-on-demand, don't forget the Magic switch type.
        ],
        function (ec) {
            var myChart = ec.init(document.getElementById("polarity-canvas"));
            var option = {
                title: {
                    text: "情感极性",
                    show: true,
                    x: "center",
                    textStyle: {
                        fontSize: 26,
                    }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    x: 'right',
                    data: ['正面', '中性', '负面']
                },

                calculable: true,
                series: [
                    {
                        name: '情感极性',
                        type: 'pie',
                        radius: ['50%', '70%'],
                        itemStyle: {
                            normal: {
                                label: {
                                    show: false
                                },
                                labelLine: {
                                    show: false
                                }
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    position: 'center',
                                    textStyle: {
                                        fontSize: '30',
                                        fontWeight: 'bold'
                                    },
                                    formatter: function (params) {
                                        return params.name + "\n" + params.percent + "%";
                                    }
                                }

                            }
                        },
                        data: polarityData
                    }
                ]
            };
            myChart.setOption(option);
        }
    );
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


function wordCloudCanvas(dom, title, data) {
    require(
        [
            'echarts',
            'echarts/chart/wordCloud',   // load-on-demand, don't forget the Magic switch type.
        ],
        function (ec) {
            var myChart = ec.init(dom);
            var option = {
                title: {
                    text: title,
                    show: true,
                    x: "center",
                    textStyle: {
                        fontSize: 26,
                        color: "#ffffff"
                    }
                    // textAlign: 'center'
                },
                tooltip: {
                    show: true
                },
                // toolbox: {
                // 　　show: true,
                // 　　feature: {
                // 　　　　saveAsImage: {
                //     　　　　show:true,
                //     　　　　excludeComponents :['toolbox'],
                //     　　　　pixelRatio: 2
                // 　　　　}
                // 　　}
                // },
                series: [{
                    name: title,
                    type: 'wordCloud',
                    size: ['100%', '100%'],
                    textRotation : [0, 90],
                    textPadding: 1,
                    autoSize: {
                        enable: true,
                        minSize: 12
                    },
                    data: data
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

function timeCanvas(timeData) {
    require(
        [
            'echarts',
            'echarts/chart/line',   // load-on-demand, don't forget the Magic switch type.
        ],
        function (ec) {
            var myChart = ec.init(document.getElementById('time-canvas'));
            var option = {
            // title: {
            //     text: "情感极性变化趋势",
            //     show: true,
            //     x: "center",
            //     textStyle: {
            //         fontSize: 26,
            //     }
            // },
            tooltip : {
                trigger: 'axis'
            },
            legend: {
                data:['正面值','中性值', '负面值', '交互数']
            },
            toolbox: {
                show : true,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            calculable : true,
            xAxis : [
                {
                    type : 'category',
                    boundaryGap : false,
                    data : timeData.x,
                }
            ],
            yAxis : [
                {
                    type : 'value'
                }
            ],
            series : [
                {
                    name:'交互数',
                    type:'line',
                    // stack: '总量',
                    data: timeData.total
                },
                {
                    name:'正面值',
                    type:'line',
                    // stack: '总量',
                    data: timeData.positive
                },
                {
                    name:'中性值',
                    type:'line',
                    // stack: '总量',
                    data: timeData.neutral
                },
                {
                    name:'负面值',
                    type:'line',
                    // stack: '总量',
                    data: timeData.negative
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
            emotions.EMOTION_HAPPY + 100,
            emotions.EMOTION_GOOD,
            emotions.EMOTION_ANGER + 300,
            emotions.EMOTION_SORROW + 80,
            emotions.EMOTION_FEAR + 50,
            emotions.EMOTION_EVIL,
            emotions.EMOTION_SURPRISE + 200,
        ];
        emotionsCanvas(emotionsData);

        var polarity = result.data.sentiment_value.polarity;
        var polarityData = [
            {value: polarity.positive, name: "正面"},
            {value: polarity.neutral, name: "中性"},
            {value: polarity.negative, name: "负面"}
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
        wordCloudCanvas(document.getElementById("word-count-canvas"), "词频统计", wordCountData);

        var keywords = result.data.keywords;
        var keywordsData = [];
        for (var i in keywords) {
            keywordsData.push({
                name: keywords[i].keyword,
                value: keywords[i].rank,
                itemStyle: createRandomItemStyle()
            });

        }
        wordCloudCanvas(document.getElementById("keywords-canvas"), "关键词统计", keywordsData);

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
            });
            provinceData.positive.push({
                name: i,
                value: province[i].positive
            });
            provinceData.negative.push({
                name: i,
                value: province[i].negative
            })
        }

        provinceCanvas(provinceData);


    } else {

    }
}, "json");

$.get("/api/news_time_data/" + newsID + "/", function (result) {
    if (result.result) {
        timeCanvas(result.data);
    } else {

    }
}, "json");