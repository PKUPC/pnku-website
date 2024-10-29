const data = {
    key: 'day2_02',
    title: '时空花园',
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
    return: '/area?dst=day2',
    area_name: '第二日',
    desc: '<div class="flavor-text center" style="width: 650px; max-width: 100%; margin: auto">\n    “这块花园里的花会随着时间而改变。<br>\n    但是因为我操纵时间的能力也需要冷却……所以每隔十五分钟才能带你穿梭一次哦。”\n</div>\n\n<p><br></p>\n<style>\n.time-input-wrapper {\n    position: relative;\n    display: inline-block;\n}\n\n.time-input-wrapper input[type="time"] {\n    -webkit-appearance: none;\n    -moz-appearance: none;\n    appearance: none;\n    width: 200px;\n    padding: 10px;\n    font-size: 16px;\n    border: 2px solid #ccc;\n    border-radius: 4px;\n    background-color: #fff;\n    outline: none;\n    transition: border-color 0.3s ease, box-shadow 0.3s ease;\n}\n\n.time-input-wrapper input[type="time"]:focus {\n    border-color: #007BFF;\n    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);\n}\n\n.time-input-wrapper input[type="time"]::-webkit-calendar-picker-indicator {\n    position: absolute;\n    right: 10px;\n    top: 50%;\n    transform: translateY(-50%);\n    cursor: pointer;\n}\n\n.time-input-wrapper input[type="time"]::-webkit-clear-button {\n    display: none;\n}\n.current-time-digital {\n    width: 400px;\n    max-width: 100%;\n    padding: 10px;\n    margin: 20px auto;\n    background: #000;\n}\n.margin-y-20px {\n    margin: 20px 0;\n}\n.refresh-icon {\n    display: flex;\n    align-items: center;\n    margin-right: 0.5em;\n}\n</style>\n\n<p><link rel="stylesheet" href="/mion/css/digital-7.css"></p>\n<form class="center margin-y-20px" id="garden-form">\n<div class="time-input-wrapper">\n<input type="time" id="timeInput">\n</div>\n<button class="fancy-button" type="submit" >逛花园</button>\n</form>\n<hr>\n<p><center class="margin-y-20px">\n    <button class="fancy-button" id="refresh">\n        <div class="refresh-icon"><svg width="16" height="16" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M42 8V24" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 24L6 40" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M42 24C42 14.0589 33.9411 6 24 6C18.9145 6 14.3216 8.10896 11.0481 11.5M6 24C6 33.9411 14.0589 42 24 42C28.8556 42 33.2622 40.0774 36.5 36.9519" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>\n        <div>刷新</div>\n    </button>\n</center></p>\n<div class="clock-display current-time-digital">\n    <div class="clock-field">\n        <div class="number">\n            <p id="hour">HOURNUM</p>\n            <p class="placeholder">88</p>\n            <p class="type">时</p>\n        </div>\n        <div class="colon">\n            <p>:</p>\n        </div>\n        <div class="number">\n            <p id="minute">MINUTENUM</p>\n            <p class="placeholder">88</p>\n            <p class="type">分</p>\n        </div>\n    </div>\n</div>\n\n<p><br></p>\n<p>REPLACEME</p>\n<script>\nfunction tellMyFortune() {\n    const timeInput = document.getElementById("timeInput").value;\n    if (timeInput) {\n        const [hour, minute] = timeInput.split(\':\').map(Number);\n        console.log(`小时数：${hour}`);\n        console.log(`分钟数：${minute}`);\n        window.wish({\n            endpoint: "special/time_garden",\n            payload: { hour: hour, minute: minute },\n        }).then((res) => {\n            if (res.status === "error") {\n                window.messageApi.error({\n                    content: res.message,\n                    key: "TimeGarden",\n                    duration: 3,\n                }).then();\n            } else {\n                window.messageApi.success({\n                    content: res.message,\n                    key: "TimeGarden",\n                    duration: 3,\n                }).then();\n                window.puzzleApi.reloadPuzzleDetail();\n            }\n        });\n\n    } else {\n        window.messageApi.warning({\n            content: "请选择一个时间！",\n            key: "TimeGarden",\n            duration: 3,\n        }).then();\n    }\n    console.log(timeInput);\n}\nfunction refresh() {\n    window.puzzleApi.reloadPuzzleDetail();\n    window.messageApi.success({content: "刷新成功！", "key": "REFRESH", duration: 4});\n}\ndocument.getElementById(\'refresh\').addEventListener(\'click\', refresh);\n\nconst form = document.getElementById(\'garden-form\');\nif (form) {\n    form.onsubmit = function() {\n        event.preventDefault();\n        tellMyFortune();\n    }\n}\n\n</script>',
};

export default data;
