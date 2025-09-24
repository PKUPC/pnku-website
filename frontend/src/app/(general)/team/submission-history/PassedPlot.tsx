import { Suspense, lazy } from 'react';

import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

const Line = lazy(() => import('@/components/lazy/Line'));

type PointItem = {
    timestamp_s: number;
    score: number;
    idx0: string;
};

export default function PassedPlot({ passedSubmissions }: { passedSubmissions: Wish.Team.TeamPassedSubmission[] }) {
    const points: PointItem[] = [];

    const timeRange = [
        passedSubmissions[0].timestamp_s,
        passedSubmissions[passedSubmissions.length - 1].timestamp_s + 60,
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
                    height={250}
                    data={points}
                    xField="timestamp_s"
                    yField="score"
                    seriesField="idx0"
                    colorField="idx0"
                    stepType="hv"
                    axis={{
                        x: {
                            labelFormatter: (x: number) => format_ts(x),
                            grid: false,
                        },
                        y: {
                            gridLineDash: [0, 0],
                            gridStrokeOpacity: 0.5,
                        },
                    }}
                    interaction={{
                        tooltip: {
                            position: 'top-right',
                            sort: (x: PointItem) => -x.score,
                            showMarkers: false,
                        },
                    }}
                    legend={{
                        color: {
                            labelFormatter: () => '我的队伍',
                            itemMarker: 'circle',
                            itemMarkerSize: 12,
                            itemLabelFontSize: 10,
                            navPageNumFontSize: 10,
                            itemSpacing: 0,
                            colPadding: 6,
                            navControllerSpacing: 12,
                            itemLabelFillOpacity: 1,
                            itemLabelFontWeight: 'bold',
                            navLoop: true,
                            navPageNumFillOpacity: 0.65,
                            layout: {
                                justifyContent: 'center',
                            },
                        },
                    }}
                    tooltip={{
                        title: (d) => format_ts(d.timestamp_s),
                        items: [
                            (d) => ({
                                name: '我的队伍',
                                value: d.score,
                            }),
                        ],
                    }}
                    scale={{
                        y: {
                            nice: true,
                        },
                        x: {
                            type: 'time',
                            domainMin: timeRange[0],
                            domainMax: timeRange[1],
                        },
                    }}
                    style={{
                        lineWidth: 2,
                    }}
                />
            </Suspense>
        </AppErrorBoundary>
    );
}
