import { Suspense, lazy } from 'react';

import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

const Line = lazy(() => import('@/components/lazy/Line'));

export default function PassedPlot({ passedSubmissions }: { passedSubmissions: Wish.Team.TeamPassedSubmission[] }) {
    const points: { timestamp_s: number; score: number; idx0: string }[] = [];

    const timeRange = [
        passedSubmissions[0].timestamp_s,
        passedSubmissions[passedSubmissions.length - 1].timestamp_s + 60 * 5,
    ];

    let totalScore = 0;
    passedSubmissions.forEach((item) => {
        totalScore += item.gained_score;
        points.push({
            timestamp_s: item.timestamp_s,
            score: totalScore,
            idx0: '我的队伍',
        });
    });

    return (
        <AppErrorBoundary>
            <Suspense fallback={<Loading />}>
                <Line
                    height={350}
                    data={points}
                    xField="timestamp_s"
                    yField="score"
                    seriesField="idx0"
                    stepType="hv"
                    legend={{
                        layout: 'horizontal',
                        position: 'top',
                    }}
                    meta={{
                        timestamp_s: {
                            type: 'linear',
                            minLimit: timeRange[0],
                            maxLimit: timeRange[1],
                            formatter: (x: number) => format_ts(x),
                        },
                    }}
                />
            </Suspense>
        </AppErrorBoundary>
    );
}
