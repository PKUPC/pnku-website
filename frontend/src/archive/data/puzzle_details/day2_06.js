const data = {
    key: 'day2_06',
    title: '永不消逝的电波',
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
    desc: '<style>\n.margin-y-20px {\n    margin: 20px 0;\n}\n.refresh-icon {\n    display: flex;\n    align-items: center;\n    margin-right: 0.5em;\n}\n</style>\n\n<div class="flavor-text center">\n“时间是纯粹的。而最接近那种纯粹感的收藏品应该是这个收音机。<br>\n无论你有没有留意，时间总是会流动，<br>\n这个收音机总是在发出声音，以十分钟为刻度发生着变迁。”\n</div>\n<p><br>\n<center class="margin-y-20px">\n    <button class="fancy-button" id="refresh">\n        <div class="refresh-icon"><svg width="16" height="16" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M42 8V24" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 24L6 40" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M42 24C42 14.0589 33.9411 6 24 6C18.9145 6 14.3216 8.10896 11.0481 11.5M6 24C6 33.9411 14.0589 42 24 42C28.8556 42 33.2622 40.0774 36.5 36.9519" stroke="#333" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>\n        <div>刷新</div>\n    </button>\n</center></p>\n<div class="center">\n\n\nREPLACEME\n\n<br/>\n(9 4 5) → (11)\n</div>\n\n<hr/>\n<div class="hint center">\n注意：在正式比赛过程中（2024-07-19 20:00 ~ 2024-07-28 20:00），本题每过 10 分钟会换一次音频。\n<br/>\n在这一归档版本中题目仍然是 10 分钟换一次，从 2024-07-19 20:00 开始计算。\n<br/>\n本题存在一定随机要素，在正式比赛中，会以队伍的 id 作为随机种子，在目前的存档环境中，这个种子是固定的。详情请参考解析。\n</div>\n\n<script>\nfunction refresh() {\n    window.puzzleApi.reloadPuzzleDetail();\n    window.messageApi.success({content: "刷新成功！", "key": "REFRESH", duration: 4});\n}\ndocument.getElementById(\'refresh\').addEventListener(\'click\', refresh);\n</script>',
};

export default data;
