const data = {
    key: 'day2_05',
    title: '时光穿梭机',
    actions: [],
    status: 'untouched',
    puzzle_list: [
        {
            name: 'NORMAL',
            puzzles: [
                {
                    puzzle_key: 'day2_01',
                    title: '谜成为谜之前',
                    status: 'untouched',
                    total_passed: 306,
                    total_attempted: 323,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
                {
                    puzzle_key: 'day2_02',
                    title: '时空花园',
                    status: 'untouched',
                    total_passed: 290,
                    total_attempted: 317,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
                {
                    puzzle_key: 'day2_03',
                    title: '下一站，终点站',
                    status: 'untouched',
                    total_passed: 307,
                    total_attempted: 313,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
                {
                    puzzle_key: 'day2_04',
                    title: '谜成为谜之后',
                    status: 'untouched',
                    total_passed: 309,
                    total_attempted: 313,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
                {
                    puzzle_key: 'day2_05',
                    title: '时光穿梭机',
                    status: 'untouched',
                    total_passed: 299,
                    total_attempted: 314,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
                {
                    puzzle_key: 'day2_06',
                    title: '永不消逝的电波',
                    status: 'untouched',
                    total_passed: 294,
                    total_attempted: 301,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
            ],
        },
        {
            name: 'meta',
            puzzles: [
                {
                    puzzle_key: 'day2_meta',
                    title: '乞求春风再临',
                    status: 'untouched',
                    total_passed: 280,
                    total_attempted: 287,
                    difficulty_status: {
                        total_num: 9,
                        green_num: 8,
                        red_num: 1,
                    },
                },
            ],
        },
    ],
    return: '/area/day2',
    area_name: '第二日',
    desc: '<div class="flavor-text center" style="width: 650px; max-width: 100%; margin: auto">\n    “这可是我的压箱底的宝物哦。”<br>\n    秋蝉从各个房间里拼拼凑凑出一堆零件，做出了一台时光穿梭机。<br>\n    不过，它的预览功能好像已经严重损坏了。<br>\n    该如何才能回到那个正确的日期呢……\n</div>\n\n<style>\n.date-input-wrapper {\n    position: relative;\n    display: inline-block;\n}\n\n.date-input-wrapper input[type="date"] {\n    -webkit-appearance: none;\n    -moz-appearance: none;\n    appearance: none;\n    width: 200px;\n    padding: 10px;\n    font-size: 16px;\n    border: 2px solid #ccc;\n    border-radius: 4px;\n    background-color: #fff;\n    outline: none;\n    transition: border-color 0.3s ease, box-shadow 0.3s ease;\n}\n\n.date-input-wrapper input[type="date"]:focus {\n    border-color: #007BFF;\n    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);\n}\n\n.date-input-wrapper input[type="date"]::-webkit-calendar-picker-indicator {\n    position: absolute;\n    right: 10px;\n    top: 50%;\n    transform: translateY(-50%);\n    cursor: pointer;\n}\n\n.date-input-wrapper input[type="date"]::-webkit-clear-button {\n    display: none;\n}\n\n.current-date-digital {\n    width: 400px;\n    max-width: 100%;\n    padding: 10px;\n    margin: 20px auto;\n    background: #000;\n}\n\n</style>\n\n<p><link rel="stylesheet" href="/mion/css/digital-7.css"></p>\n<form class="center" id="time-machine-form">\n<div class="date-input-wrapper">\n<input type="date" id="dateInput" min="1900-01-01" max="2099-12-31">\n</div>\n<button class="fancy-button" type="submit">时光机，启动！</button>\n</form>\n\n<div class="clock-display current-date-digital">\n    <div class="date-field">\n        <div>\n            <p id="year">1900</p>\n            <p class="placeholder">8888</p>\n            <p class="type">年</p>\n        </div>\n        <div>\n            <p id="month">01</p>\n            <p class="placeholder">88</p>\n            <p class="type">月</p>\n        </div>\n        <div>\n            <p id="day">01</p>\n            <p class="placeholder">88</p>\n            <p class="type">日</p>\n        </div>\n    </div>\n</div>\n\n<p><img id="time-machine-image" class="puzzle-image" src="/media/puzzle/day2_05/1900-01-01.webp" alt=""></p>\n<script>\n\nwindow.puzzleApi.setDisableInput(true);\nwindow.puzzleApi.setSubmitAnswer("1900年1月1日");\nwindow.puzzleApi.setInputAnswer("1900年1月1日");\n\nfunction tellMyFortune() {\n    const dateInput = document.getElementById("dateInput").value;\n    if (dateInput) {\n        const [year, month, day] = dateInput.split(\'-\').map(Number);\n        console.log(`年：${year}`);\n        console.log(`月：${month}`);\n        console.log(`日：${day}`);\n\n        window.wish({\n            endpoint: "special/time_machine",\n            payload: { year: year, month: month, day: day },\n        }).then((res) => {\n            if (res.status === "error") {\n                window.messageApi.error({\n                    content: res.message,\n                    key: "TimeMachine",\n                    duration: 3,\n                }).then();\n            } else {\n                window.messageApi.success({\n                    content: res.message,\n                    key: "TimeMachine",\n                    duration: 3,\n                }).then();\n                window.puzzleApi.setSubmitAnswer(`${year}年${month}月${day}日`);\n                window.puzzleApi.setInputAnswer(`${year}年${month}月${day}日`);\n                document.getElementById("time-machine-image").src = res.data;\n                document.getElementById("year").innerText = year.toString().padStart(4, \'0\');\n                document.getElementById("month").innerText = month.toString().padStart(2, \'0\');\n                document.getElementById("day").innerText = day.toString().padStart(2, \'0\');\n            }\n        });\n\n    } else {\n        window.messageApi.warning({\n            content: "请选择一个日期！",\n            key: "TimeMachine",\n            duration: 3,\n        }).then();\n    }\n    console.log(dateInput);\n}\n\nfunction handleEvent(event) {\n    event.preventDefault();\n    tellMyFortune()\n}\n\nconst form = document.getElementById(\'time-machine-form\');\nif (form) {\n    form.onsubmit = handleEvent;\n}\n\n</script>',
};

export default data;
