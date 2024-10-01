function isValidState(state) {
    return Number.isInteger(state) && state >= 0 && state < 1440;
}

function getCurrentTime() {
    const now = new Date();
    const time = now.getHours() * 60 + now.getMinutes();
    return time;
}

function getState() {
    const state = parseInt(sessionStorage.getItem('day2_02_state'), 10);
    if (isValidState(state)) return state;
    else return getCurrentTime();
}

function setState(state) {
    if (isValidState(state)) sessionStorage.setItem('day2_02_state', state);
    else sessionStorage.setItem('day2_02_state', getCurrentTime());
}

function makeCurrentState(puzzleDetail) {
    let result = JSON.parse(JSON.stringify(puzzleDetail));
    const curState = getState();
    const hour = Math.floor(curState / 60);
    const minute = curState % 60;
    let questionString =
        '<img class="puzzle-image" src="media/puzzle/day2_02/meta/day2_02_meta_v2.webp" style="width: 800px;" alt="">\n<br>\n<center>将最长寿的花对准右上的“2”，然后顺时针缓缓流动……</center>';
    if (hour == 2) {
        questionString = '<img class="puzzle-image" src="media/puzzle/day2_02/02/1.webp" style="width: 400px;" alt="">';
    } else if (hour == 4) {
        questionString =
            '<img class="puzzle-image" src="media/puzzle/day2_02/04/1_v2.webp" style="width: 400px;" alt="">\n<br>\n<div class="center">\n<p>巴拿马开始沦为西班牙殖民地</p>\n<p>“僰道”改称宜宾</p>\n<p>蔡伦被封为龙亭候</p>\n<p>奥斯曼帝国统治阿尔巴尼亚</p>\n<p>发起非暴力不合作运动</p>\n<p>黑羊王朝占领巴格达</p>\n<p>《街头霸王4》发行</p>\n<p>《警钟日报》被查封</p>\n<p>莱比锡大学建校</p>\n<p>李善长诞生于世</p>\n<p>梁武帝天监十三年</p>\n<p>萨克森王朝建立</p>\n<p>蜀太子王元膺被杀害</p>\n<p>宋朝建成龙图阁</p>\n<p>宗喀巴逝世</p>\n</div>';
    } else if (hour == 5) {
        questionString = '<img class="puzzle-image" src="media/puzzle/day2_02/05/1.webp" alt="">';
    } else if (hour == 6) {
        questionString = `<img class=\"puzzle-image\" src=\"media/puzzle/day2_02/06/06${minute.toString().padStart(2, '0')}.webp\" alt=\"\">`;
    } else if (hour == 7) {
        questionString =
            '<div class="flavor-text center" style="width: 650px; max-width: 100%; margin: auto">\n这是一份写在这个月 <b><i>日历</i></b> 上的备忘录，记录着一些毫无关联的事情。\n</div>\n\n<br>\n\n<ul>\n<li>2022年11月6日下午，在美国旧金山举办的？？？全球总决赛终于落下了帷幕</li>\n<li>在2023年2月的三星GALAXY新品发布会上，宣布了其推出的最新款旗舰手机？？？</li>\n<li>家里键盘最上面一行左数第三个按键？？没反应了，得找个电脑店修理一下</li>\n<li>《GODS》是？？？全球总决赛的主题曲，由女子组合NEW JEANS演唱</li>\n<li>？？？钢由于含碳量高，按耐磨性和硬度适于制作车床、铣刀、钻头等</li>\n<li>2023年3月30日，从成都出发至德阳的？？？线正式开工建设</li>\n<li>工业上可作为火箭燃料中氧化剂的淡黄色有毒气体的化学式为？？</li>\n<li>一个长、宽、高都等于1米的立方体的体积为1？？</li>\n<li>？？？说过：火力就是战斗的本钱，鱼雷则是大豪赌！</li>\n<li>宏观经济里流通中的现金也叫作狭义货币供应量？？</li>\n</ul>\n';
    } else if (hour == 10) {
        questionString =
            '<div class="flavor-text center" style="width: 650px; max-width: 100%; margin: auto">\n谁还没个时间系技能啊？\n</div>\n\n<img class="puzzle-image" src="media/puzzle/day2_02/10/4.webp" alt="">';
    } else if (hour == 12) {
        let formatted_angle = Math.floor(minute / 5) * 30;
        questionString = `<img class=\"puzzle-image\" src=\"media/puzzle/day2_02/12/image_${formatted_angle}.webp\" alt=\"\">`;
    } else if (hour == 15) {
        questionString = '<img class="puzzle-image" src="media/puzzle/day2_02/15/1.webp" alt="">';
    } else if (hour == 17) {
        let formatted_angle = Math.floor(minute / 5) * 30;
        questionString = `<img class=\"puzzle-image\" src=\"media/puzzle/day2_02/17/image_${formatted_angle}.webp\" style=\"width: 350px;\" alt=\"\">`;
    } else if (hour == 18) {
        questionString =
            '<div class="flavor-text center" style="width: 650px; max-width: 100%; margin: auto">\n    一些支离破碎的诗句，似乎已经无法查看 <b><i>上下文</i></b> 了。\n</div>\n\n<p>汉口夕阳斜渡鸟，月笛烟莎世不知</p>\n<p>玉琯吹灰夜色残，海内无如此地闲</p>\n<p><font color="red">回看</font>巧技未旋踵，<font color="red">岁岁</font>年年人不同</p>\n<p>（5）&nbsp;&nbsp;&nbsp;&nbsp;（5）+（4）</p>';
    } else if (hour == 19) {
        questionString =
            '<p>最近看了好多好多的书（虽然都没怎么看完），但还是在这里浅浅做一份读书笔记吧。</p>\n<p><br></p>\n<p>我看的第一本书是一本共 37 章的长篇小说，讲述了主人公温福瑞格（一位中国绅士）和朋友打赌要在规定的时间内环游 puzzlehunt 星球并回到 P&amp;KU ，他和观测者克服了一路上的艰难险阻，顺利完成了赌约。作者在介绍了各大 PUZZLE HUNT 的特点和解谜知识的同时，还以强烈的人道主义精神，对各种难题孬题自嗨题进行了批判和鞭笞。比较遗憾的是，这本书我只看了四分之一就被家里的宠物狗吃了。</p>\n<p>我看的第二本书是出自国内非常著名的蔡姓悬疑小说家，讲述了黑天鹅般迷人的芈雨，被关进了二十层烂尾楼的露天围墙里，在这些被囚禁的日子里发生了很多的事情，饥饿和寒冷险些要了她的命，同时她的胎儿也不幸幸离世，就在她奄奄一息的绝望之际，她发现竟然一直有一名观测者在观察着自己......这本书我只是浅浅翻了几章，大概有八分之一吧，打算以后有时间再看。</p>\n<p>我看的第三本书也是一本悬疑小说，它的作者叫什么来着，好像是勒迈特。听说这部小说还有同名的电影，可我并没有看过，小说主要围绕了一个法国小镇上的六岁孩童失踪案进行展开，它阐述了孩子眼中的罪恶和孩子犯下的罪恶，始终是需要自己背负的，而这种背负可能终其一生。这本书我看的比较多，大概有三分之二吧，剩下的留到暑假再说。</p>\n<p>我看的第四本书是一部非常有教育意义的自传体小说，讲述了作者在变成了盲聋人之后所经历的凄惨生活：虽然吃饭，娱乐，甚至解谜都变得十分困难，但是作者身残志坚，精通了盲文密码的使用，在丰富多彩的解谜生活中走向了巅峰。这本书我看了三分之一，因为后来要准备期末考试就暂时搁置了。</p>\n<p>我看的第五本书是芈伯庸创作的长篇历史小说，讲述了一个小捕快、一个女医生、一个芝麻官和一个当朝太子的心灵之旅，描绘了一幅明代大运河沿岸风情的鲜活画卷。可惜我对历史的题材实在是提不起兴趣，所以只看了五分之一就作罢了，听说现在已经有它的同名电视剧了，找个时间可以看一下。</p>\n<p>我看的第六本书是一部非常经典的短篇小说集，它或许比你现在着手玩的东西还要长三天。书中的故事讲述了一群年轻人因为机缘巧合而聚在一起，没日没夜地在山上的小别墅里出题，从基本粒子出到自然的力，从黑暗的教会出到高尚的爱情。他们出各种各样的题，一天每人出十道题，那么最终就能出一百道题。这本书我也只是读了前百分之三十，希望以后有机会可以把它读完。</p>\n<p>我看的最后一本书是一本很黄很暴力的带有争议的作品，是作者被关在巴士底狱时所写下的。这部小说讲述了法国专制旧王朝时期一群人在城堡中度过的一段极度荒淫，残暴的时光。这部小说的情节似乎参考了我刚刚读过的另一本小说，不过这实在是不忍直视，我只读了八分之一就弃坑了。</p>\n<p>希望我还能有更多的时间用来看书。</p>\n';
    } else if (hour == 20) {
        questionString =
            '<img class="puzzle-image" src="media/puzzle/day2_02/20/8.webp" style="width: 800px;" alt="">\n\n<div style="text-align: center; font-size: 1.5em; font-weight: bold">（10）</div>';
    } else if (hour == 21) {
        questionString = '<img class="puzzle-image" src="media/puzzle/day2_02/21/1.webp" style="width: 800px;" alt="">';
    }
    result.desc = result.desc
        .replace('REPLACEME', questionString)
        .replace('HOURNUM', hour.toString().padStart(2, '0'))
        .replace('MINUTENUM', minute.toString().padStart(2, '0'));
    return result;
}

function apiCall(hour, minute) {
    if (
        !(Number.isInteger(hour) && 0 <= hour && hour <= 23 && Number.isInteger(minute) && 0 <= minute && minute <= 59)
    ) {
        return {
            status: 'error',
            title: 'BAD_REQUEST',
            message: '不合法的时间！请选择 00:00 至 23:59 中的合法时间。',
        };
    }
    setState(hour * 60 + minute);
    return {
        status: 'success',
        title: '成功！',
        message: '花园的时间被改变了！',
    };
}

export { apiCall, makeCurrentState };
