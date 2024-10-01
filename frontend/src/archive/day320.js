function isValidState(state) {
    return Number.isInteger(state) && state >= 1 && state <= 8;
}

function getState() {
    const state = parseInt(sessionStorage.getItem('day3_20_state'), 10);
    if (isValidState(state)) return state;
    else return 1;
}

function setState(state) {
    if (isValidState(state)) sessionStorage.setItem('day3_20_state', state);
    else sessionStorage.setItem('day3_20_state', 1);
}

function makeCurrentState(puzzleDetail) {
    console.log(puzzleDetail);
    const curState = getState();
    console.log(curState);
    let result = JSON.parse(JSON.stringify(puzzleDetail));
    let imageStr = '';
    if (curState >= 1)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/1.webp" alt=""></p>';
    if (curState >= 2)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/2_v2.webp" alt=""></p>';
    if (curState >= 3)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/3.webp" alt=""></p>';
    if (curState >= 4)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/4.webp" alt=""></p>';
    if (curState >= 5)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/5.webp" alt=""></p>';
    if (curState >= 6)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/6.webp" alt=""></p>';
    if (curState >= 7)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/7.webp" alt=""></p>';
    if (curState >= 8)
        imageStr += '<p><img style="width: 400px; max-width: 100%;" src="media/puzzle/day3_20/8.webp" alt=""></p>';

    result.desc = result.desc.replace('<p>REPLACEME</p>', imageStr);
    return result;
}

function checkAndUpdate(submission) {
    const curState = getState();
    const ansByState = { 1: '相', 2: '力', 3: 'SAND', 4: '乏力', 5: '锦', 6: 'TUBEROSE', 7: '巫', 8: 'HANDS' };
    if (submission === ansByState[curState]) {
        if (curState < 8) {
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
