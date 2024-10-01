import { DownloadOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import { PuzzleStatisticsTable } from '@/app/(general)/team/puzzle-statistics/PuzzleStatisticsTable';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';
import { Wish } from '@/types/wish.ts';
import { format_ts, format_ts_to_HMS } from '@/utils.ts';

function genCSV(data: Wish.Team.TeamPuzzleStatisticsAreaItem[]) {
    const flatData = data.flatMap((area) =>
        area.puzzles.map((puzzle) => ({
            ...puzzle,
            areaName: area.name,
        })),
    );
    const header =
        ['区域', '题目', '解锁时间', '通过时间', '花费时间', '错误提交数', '里程碑提交数', '正确提交数'].join(',') +
        '\n';
    const rows = flatData
        .map((item) => {
            const passedTimeStr = item.passed_ts ? format_ts(item.passed_ts) : '---';
            const unlockedTimeStr = item.unlock_ts ? format_ts(item.unlock_ts) : '---';
            const timeCostStr = item.time_cost ? format_ts_to_HMS(item.time_cost) : '---';

            return [
                item.areaName,
                item.title,
                unlockedTimeStr,
                passedTimeStr,
                timeCostStr,
                item.wrong + '',
                item.milestone + '',
                item.pass + '',
            ].join(',');
        })
        .join('\n');
    return header + rows;
}

export function PuzzleStatisticsPage() {
    const { data } = useWishData({ endpoint: 'team/get_puzzle_statistics' });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    return (
        <div>
            <PuzzleStatisticsTable data={data.data} />
            <br />
            <div style={{ textAlign: 'right' }}>
                <Button
                    onClick={() => {
                        const csvContent = genCSV(data.data);
                        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.setAttribute('href', url);
                        link.setAttribute('download', 'puzzle-statistics.csv');
                        link.style.visibility = 'hidden';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }}
                >
                    <DownloadOutlined />
                    存储为 csv 文件
                </Button>
            </div>
        </div>
    );
}
