import { gameStartReply } from '@/archive/gameStartApi';
import { cleanSubmission } from '@/utils';

import * as day201 from './day201';
import * as day202 from './day202';
import * as day203 from './day203';
import * as day205 from './day205';
import * as day206 from './day206';
import * as day320 from './day320';

export function archiveWish({ endpoint, payload }) {
    return new Promise((resolve) => {
        console.log([endpoint, payload]);
        const notFound = { status: 'error', title: 'NOT FOUND', message: 'NOT FOUND!' };
        switch (endpoint) {
            case 'game/game_info':
                import('./data/gameInfoData.js').then((data) => {
                    let gameInfoData = data.default;
                    let resultData = { status: 'success', ...gameInfoData };
                    resolve(resultData);
                });
                break;
            case 'game/get_area_detail':
                import('./data/areaDetailData.js').then((data) => {
                    let areaDetailData = data.default;
                    if (payload.area_name in areaDetailData)
                        resolve({ status: 'success', data: areaDetailData[payload.area_name] });
                    else resolve(notFound);
                });
                break;
            case 'game/get_announcements':
                import('./data/miscData.js').then((data) => {
                    resolve({ status: 'success', data: data.default['announcements'] });
                });
                break;
            case 'game/get_schedule':
                import('./data/miscData.js').then((data) => {
                    resolve({ status: 'success', data: data.default['schedule'] });
                });
                break;
            case 'game/get_puzzle_list':
                import('./data/puzzleList.js').then((data) => {
                    resolve({ status: 'success', data: data.default });
                });
                break;
            case 'game/get_story_list':
                import('./data/storyList.js').then((data) => {
                    resolve({ status: 'success', data: data.default });
                });
                break;
            case 'puzzle/get_detail': {
                let puzzleKey = payload.puzzle_key;
                import(`./data/puzzle_details/${puzzleKey}.js`)
                    .then((data) => {
                        if (puzzleKey === 'day2_01')
                            resolve({ status: 'success', data: day201.makeCurrentState(data.default) });
                        else if (puzzleKey === 'day3_20')
                            resolve({ status: 'success', data: day320.makeCurrentState(data.default) });
                        else if (puzzleKey === 'day2_03')
                            resolve({ status: 'success', data: day203.makeCurrentState(data.default) });
                        else if (puzzleKey === 'day2_06')
                            resolve({ status: 'success', data: day206.makeCurrentState(data.default) });
                        else if (puzzleKey === 'day2_02')
                            resolve({ status: 'success', data: day202.makeCurrentState(data.default) });
                        else resolve({ status: 'success', data: data.default });
                    })
                    .catch(() => {
                        resolve({ status: 'error', message: '题目信息获取失败' });
                    });
                break;
            }
            case 'puzzle/get_hints':
                import('./data/puzzleHints.js').then((data) => {
                    let puzzleHints = data.default;
                    if (payload.puzzle_key in puzzleHints)
                        resolve({ status: 'success', data: { list: puzzleHints[payload.puzzle_key] } });
                    else resolve(notFound);
                });
                break;
            case 'game/get_board':
                import('./data/boardsData.js').then((data) => {
                    let boardsData = data.default;
                    if (payload.board_key in boardsData)
                        resolve({ status: 'success', data: boardsData[payload.board_key] });
                    else resolve(notFound);
                });
                break;
            case 'special/time_garden':
                resolve(day202.apiCall(payload.hour, payload.minute));
                break;
            case 'special/time_machine':
                resolve(day205.apiCall(payload.year, payload.month, payload.day));
                break;
            case 'game/game_start':
                resolve(gameStartReply(payload.content));
                break;
            case 'puzzle/submit_answer':
                import('./data/puzzleTriggers.js').then((data) => {
                    let puzzleTriggers = data.default;
                    let cleanedSub = cleanSubmission(payload.content);
                    if (payload.puzzle_key === 'day2_01') resolve(day201.checkAndUpdate(cleanedSub));
                    if (payload.puzzle_key === 'day3_20') resolve(day320.checkAndUpdate(cleanedSub));
                    if (payload.puzzle_key === 'day3_premeta') {
                        if (
                            cleanedSub === 'cdegklmqsv'.toUpperCase() ||
                            cleanedSub === 'afghijlmnprstv'.toUpperCase() ||
                            cleanedSub === 'bcefhjkorsu'.toUpperCase()
                        )
                            resolve({
                                status: 'success',
                                title: '答案正确',
                                message: '精妙的选择！这是一组正确的组合！',
                            });
                        else
                            resolve({
                                status: 'success',
                                title: '答案错误',
                                message: '这是什么？你没有得到任何信息！',
                            });
                    }
                    if (payload.puzzle_key in puzzleTriggers) {
                        if (cleanedSub in puzzleTriggers[payload.puzzle_key]) {
                            let trigger = puzzleTriggers[payload.puzzle_key][cleanedSub];
                            if (trigger.type === 'answer') {
                                resolve({ status: 'success', title: '答案正确', message: trigger.info });
                            } else if (trigger.type === 'milestone') {
                                resolve({ status: 'info', title: '里程碑', message: trigger.info });
                            } else {
                                resolve({
                                    status: 'error',
                                    title: '答案错误',
                                    message: '答案错误！你没有得到任何信息！',
                                });
                            }
                        } else {
                            resolve({ status: 'error', title: '答案错误', message: '答案错误！你没有得到任何信息！' });
                        }
                    } else resolve({ status: 'error', title: '出错了！', message: '题目不存在！你是怎么做到的？' });
                });
                break;
            default:
                resolve({ status: 'error', title: 'ARCHIVED', message: '归档模式不支持该请求。' });
        }
    });
}

export function archiveFetchTemplateFile(fileName) {
    return new Promise((resolve) => {
        import('./data/templatesData.js').then((data) => {
            let templatesData = data.default;
            if (fileName in templatesData) return resolve(templatesData[fileName]);
            else return resolve('暂无内容');
        });
    });
}
