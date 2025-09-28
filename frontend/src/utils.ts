import { default as Color } from 'colorjs.io';
import Md5 from 'crypto-js/md5';
import seedrandom from 'seedrandom';

import { AUTH_ROOT } from '@/constants';

export function make_auth_url(url: string): string {
    return AUTH_ROOT + url;
}

function pad2(x: number) {
    return x < 10 ? '0' + x : '' + x;
}

export function stringToHue(input: string): number {
    let hash = 0;
    const inputMd5 = Md5(input).toString();

    for (let i = 0; i < inputMd5.length; i++) {
        const char = inputMd5.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash |= 0;
        hash %= 361;
    }

    return Math.abs(hash);
}

export function format_ts(ts: number) {
    const time = new Date(ts * 1000);
    return (
        `${time.getFullYear()}-${pad2(time.getMonth() + 1)}-${pad2(time.getDate())}` +
        // `${pad2(time.getMonth() + 1)}-${pad2(time.getDate())}`
        ` ${pad2(time.getHours())}:${pad2(time.getMinutes())}:${pad2(time.getSeconds())}`
    );
}

export function format_ms(ms: number) {
    const time = new Date(ms);
    return (
        `${time.getFullYear()}-${pad2(time.getMonth() + 1)}-${pad2(time.getDate())}` +
        // `${pad2(time.getMonth() + 1)}-${pad2(time.getDate())}`
        ` ${pad2(time.getHours())}:${pad2(time.getMinutes())}:${pad2(time.getSeconds())}`
    );
}

// by ChatGPT
export function format_ts_to_HMS(ts: number) {
    let prefix = '';
    if (ts < 0) {
        ts = -ts;
        prefix = '-';
    }
    const hours = Math.floor(ts / 3600);
    let minutes: number | string = Math.floor((ts - hours * 3600) / 60);
    let seconds: number | string = ts - hours * 3600 - minutes * 60;

    if (minutes < 10) {
        minutes = '0' + minutes;
    }
    if (seconds < 10) {
        seconds = '0' + seconds;
    }

    return prefix + hours + ':' + minutes + ':' + seconds;
}

export function random_str(len: number) {
    const alphabet = 'qwertyuiopasdfghjkzxcvbnmQWERTYUPASDFGHJKLZXCVBNM23456789';
    let out = '';
    for (let i = 0; i < len; i++) out += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
    return out;
}

export function shuffleArray<T>(array: T[], seed?: number): T[] {
    const shuffledArray = [...array]; // 创建一个新的数组，以避免修改原始数组
    let rng;
    if (seed !== null && seed !== undefined) {
        rng = seedrandom(seed + '');
    } else {
        rng = seedrandom(Math.random() + '');
    }

    for (let i = shuffledArray.length - 1; i > 0; i--) {
        // 随机选取小于当前元素的一个索引
        const j = Math.floor(rng() * (i + 1));
        // 交换当前元素和随机选取的元素
        [shuffledArray[i], shuffledArray[j]] = [shuffledArray[j], shuffledArray[i]];
    }
    return shuffledArray;
}

export function truncateString(inputString: string, maxLength: number): string {
    if (inputString.length <= maxLength) {
        return inputString;
    } else {
        return inputString.slice(0, maxLength - 2) + '...';
    }
}

export function calcHashForCravatar(input: string): string {
    // 去除首尾两边的空格
    const trimmed = input.trim();
    // 所有字母转小写
    const lowercase = trimmed.toLowerCase();
    // 计算MD5值
    return Md5(lowercase).toString();
}

export const detectZoom = (): number => {
    let ratio = 0;
    const screen = window.screen;
    const ua = navigator.userAgent.toLowerCase();

    if (window.devicePixelRatio !== undefined) {
        ratio = window.devicePixelRatio;
    } else if (~ua.indexOf('msie')) {
        // @ts-expect-error fine
        if (screen.deviceXDPI && screen.logicalXDPI) {
            // @ts-expect-error fine
            ratio = screen.deviceXDPI / screen.logicalXDPI;
        }
    } else if (window.outerWidth !== undefined && window.innerWidth !== undefined) {
        ratio = window.outerWidth / window.innerWidth;
    }

    if (ratio) {
        ratio = Math.round(ratio * 100) / 100;
    }

    return ratio;
};

export function hslaToRgba(h: number, s: number, l: number, a: number): [number, number, number, number] {
    let r: number, g: number, b: number;

    if (s === 0) {
        r = g = b = l; // achromatic
    } else {
        const hue2rgb = (p: number, q: number, t: number): number => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
        };

        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;

        r = hue2rgb(p, q, h + 1 / 3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255), a];
}

export function mixRgbaWithWhite(r: number, g: number, b: number, a: number): [number, number, number] {
    const resultingRed = (1 - a) * 255 + a * r;
    const resultingGreen = (1 - a) * 255 + a * g;
    const resultingBlue = (1 - a) * 255 + a * b;
    return [Math.round(resultingRed), Math.round(resultingGreen), Math.round(resultingBlue)];
}

// ADHOC
// p 是一个特殊参数，用于给 team_id 为 0 的整点花活
// decade: 222, 202, 222
export function mixHslaWithWhite(h: number, s: number, l: number, a: number, p?: number): [number, number, number] {
    const [r, g, b, alpha] = hslaToRgba(h, s, l, a);
    const m = p === 0 ? 0 : 1;
    const resultingRed = ((1 - alpha) * 255 + alpha * r) * m + 222 * (1 - m);
    const resultingGreen = ((1 - alpha) * 255 + alpha * g) * m + 202 * (1 - m);
    const resultingBlue = ((1 - alpha) * 255 + alpha * b) * m + 222 * (1 - m);
    return [Math.round(resultingRed), Math.round(resultingGreen), Math.round(resultingBlue)];
}

export function encodeObjectToBase64(obj: object): string {
    const jsonString = JSON.stringify(obj);
    return btoa(jsonString);
}

export function decodeBase64ToObject(encoded: string): object | undefined {
    try {
        const jsonString = atob(encoded);
        return JSON.parse(jsonString);
    } catch (e) {
        console.error(e);
        return undefined;
    }
}

/**
 * 新版货币计算方案中，不再从头到尾算，直接用当前余额 + 随时间的总增长计算
 */

export function calcCurrentBalance(base_balance: number, increase_policy: [number, number][]) {
    const curMin = Math.floor(Date.now() / 1000 / 60);
    let balance = base_balance;
    for (let i = 0; i < increase_policy.length - 1; i++) {
        if (curMin > increase_policy[i + 1][0])
            balance += (increase_policy[i + 1][0] - increase_policy[i][0]) * increase_policy[i][1];
        else if (curMin <= increase_policy[i][0]) break;
        else {
            balance += (curMin - increase_policy[i][0]) * increase_policy[i][1];
            break;
        }
    }
    const lastIdx = increase_policy.length - 1;
    if (curMin > increase_policy[lastIdx][0])
        balance += (curMin - increase_policy[lastIdx][0]) * increase_policy[lastIdx][1];
    // console.log(balance);
    console.log(increase_policy, balance);
    return balance;
}

export function getCurrentIncrease(increase_policy: [number, number][]) {
    const curMin = Math.floor(Date.now() / 1000 / 60);
    if (increase_policy.length === 0) return 0;
    if (curMin < increase_policy[0][0]) return 0;
    for (let i = 0; i < increase_policy.length - 1; i++) {
        if (curMin < increase_policy[i + 1][0] && curMin >= increase_policy[i][0]) return increase_policy[i][1];
    }
    // 这里应该恒成立
    if (curMin >= increase_policy[increase_policy.length - 1][0]) return increase_policy[increase_policy.length - 1][1];
    return 0;
}

export function cleanSubmission(origin: string): string {
    let rst = '';
    for (const x of origin) {
        if ('\u4e00' <= x && x <= '\u9fff') {
            rst += x;
        } else if ('0' <= x && x <= '9') {
            rst += x;
        } else if ('a' <= x.toLowerCase() && x.toLowerCase() <= 'z') {
            rst += x.toUpperCase();
        }
    }
    return rst;
}

export function blurActivateElement() {
    const focusedElement: HTMLElement | null = document.activeElement as HTMLElement | null;
    if (focusedElement && typeof focusedElement.blur === 'function') focusedElement.blur();
}

export function capitalizeFirstLetter(str: string): string {
    if (str.length === 0) return str;
    return str.charAt(0).toUpperCase() + str.slice(1);
}

export function mixColor(color1: string, color2: string, ratio: number) {
    return Color.mix(color1, color2, ratio, { space: 'srgb', outputSpace: 'srgb' })
        .to('srgb')
        .toString({ format: 'hex' });
}
