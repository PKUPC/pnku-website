function getMediaName(seconds) {
    const numMap = [4, 9, 3, 5, 13, 17, 14, 2, 15, 16, 7, 11, 12, 10, 6, 8, 18, 1];
    const nameMap = ['music', 'road', 'question', 'weather'];
    const numIndex = Math.floor(seconds / 600) % 18;
    const num = numMap[numIndex];
    const nameIndex = (111 * 10000 + Math.floor(seconds / 600) + 3) % 4;
    const name = nameMap[nameIndex];
    return name + num;
}

function makeCurrentState(puzzleDetail) {
    console.log(puzzleDetail);
    const currentSeconds = Math.floor(Date.now() / 1000);
    const gameStartSeconds = Math.floor(new Date('2024-07-19T20:00:00+08:00').getTime() / 1000);
    const secondDifference = currentSeconds - gameStartSeconds;
    const mediaName = getMediaName(secondDifference);
    const mediaUrl = `media/puzzle/day2_06/32k_${mediaName}.m4a`;
    let result = JSON.parse(JSON.stringify(puzzleDetail));
    result.desc = result.desc.replace(
        'REPLACEME',
        `<audio controls><source src="${mediaUrl}" type="audio/mp4"/>您的浏览器不支持 audio 元素，请更换较新的浏览器！</audio>`,
    );
    result.actions = [{ type: 'media', name: '音频文件', media_url: mediaUrl }];

    return result;
}

export { makeCurrentState };
