import TimeAgo from 'react-timeago';
// @ts-ignore
import buildFormatter from 'react-timeago/lib/formatters/buildFormatter';

import { format_ts } from '@/utils.ts';

const timeAgoFormat = buildFormatter({
    prefixAgo: null,
    prefixFromNow: '',
    suffixAgo: (_val: number, delta: number) => {
        return delta < 59500 ? '刚刚' : '前';
    },
    suffixFromNow: (_val: number, delta: number) => {
        return -delta < 59500 ? '1 分钟之内' : '后';
    },
    seconds: '\u200b', // ZWSP, not '' because TimeAgo will fall back to default
    minute: '1 分钟',
    minutes: '%d 分钟',
    hour: '1 小时',
    hours: '%d 小时',
    day: '1 天',
    days: '%d 天',
    month: '1 个月',
    months: '%d 月',
    year: '1 年',
    years: '%d 年',
    wordSeparator: '',
});

export default function TimestampAgo({ ts, delta }: { ts: number; delta?: number }) {
    return <TimeAgo date={(ts + (delta ?? 0)) * 1000} formatter={timeAgoFormat} title={format_ts(ts)} />;
}
