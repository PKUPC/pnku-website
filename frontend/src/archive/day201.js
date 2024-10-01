function isValidState(state) {
    return Number.isInteger(state) && state >= 1 && state <= 5;
}

function getState() {
    const state = parseInt(sessionStorage.getItem('day2_01_state'), 10);
    if (isValidState(state)) return state;
    else return 1;
}

function setState(state) {
    if (isValidState(state)) sessionStorage.setItem('day2_01_state', state);
    else sessionStorage.setItem('day2_01_state', 1);
}

function makeCurrentState(puzzleDetail) {
    console.log(puzzleDetail);
    const curState = getState();
    console.log(curState);
    let result = JSON.parse(JSON.stringify(puzzleDetail));
    let imageStr = '';
    if (curState >= 1)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day2_01/1.webp" alt=""></p>';
    if (curState >= 2)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day2_01/2.webp" alt=""></p>';
    if (curState >= 3)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day2_01/3.webp" alt=""></p>';
    if (curState >= 4)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day2_01/4_v3.webp" alt=""></p>';
    if (curState >= 5)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day2_01/5.webp" alt=""></p>';

    result.desc = result.desc.replace('<p>REPLACEME</p>', imageStr);
    return result;
}

function checkAndUpdate(submission) {
    const curState = getState();
    const ansByState = { 1: '韭菜盒子', 2: '花', 3: '密西西比', 4: '一目十行', 5: '乔治盖莫夫' };
    if (submission === ansByState[curState]) {
        if (curState < 5) {
            setState(curState + 1);
            return {
                status: 'success',
                title: '答案正确',
                message: '答案正确！请继续回答下一个小题。',
                need_reload: true,
            };
        } else return { status: 'success', title: '答案正确', message: '答案正确！这是本题的最终答案！' };
    }
    return { status: 'error', title: '答案错误', message: '答案错误！你没有得到任何信息！' };
}

export { checkAndUpdate, makeCurrentState };
