import { Suspense, lazy, useEffect, useState } from 'react';

import { AppErrorBoundary } from '@/app/AppErrorBoundary.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

const Line = lazy(() => import('@/components/lazy/Line'));

function minmax(x: number, a: number, b: number) {
    return Math.max(a, Math.min(b, x));
}

type PointItem = {
    timestamp_ms: number;
    score: number;
    idx0: string;
};

export default function TopStarPlot({ data }: { data: Wish.Game.FullBoard }) {
    const [loading, setLoading] = useState(true);
    const [finalData, setFinalData] = useState<PointItem[]>([]);
    const [timeRange, setTimeRange] = useState<[number, number]>([-1, -1]);

    useEffect(() => {
        setLoading(true);
        setFinalData([]);
        setTimeRange([-1, -1]);

        const points: PointItem[] = [];
        const timePoints: { [key: number]: boolean } = {};

        const timeRangeDisplay: [number, number] = [
            data.time_range[0] * 1000,
            minmax(+new Date() + 1000, data.time_range[0] * 1000 + 1000, data.time_range[1] * 1000),
        ];

        data.topstars.forEach((topstar) => {
            topstar.ss.forEach((sub) => {
                timePoints[sub[0]] = true;
            });
        });
        const sortedTimePoints = [
            ...Object.keys(timePoints).map((x) => +x),
            timeRangeDisplay[0],
            timeRangeDisplay[1],
            Infinity,
        ].sort();

        data.topstars.forEach((topstar, idx) => {
            let tot_score = 0;
            let time_idx = 0;

            topstar.ss.forEach((sub) => {
                for (; sortedTimePoints[time_idx] < sub[0]; time_idx++) {
                    points.push({
                        timestamp_ms: sortedTimePoints[time_idx],
                        score: tot_score,
                        idx0: idx + '',
                    });
                }
                tot_score += sub[1];
            });
            for (; time_idx < sortedTimePoints.length - 1; time_idx++) {
                points.push({
                    timestamp_ms: sortedTimePoints[time_idx],
                    score: tot_score,
                    idx0: idx + '',
                });
            }
        });

        setLoading(false);
        setTimeRange(timeRangeDisplay);
        setFinalData(points);
    }, [data]);

    return (
        <AppErrorBoundary>
            <Suspense fallback={<Loading style={{ height: 350 }} />}>
                {loading ? (
                    <Loading style={{ height: 350 }} />
                ) : (
                    <div className={'min-h-[21.875rem]'}>
                        <Line
                            height={350}
                            data={finalData}
                            xField="timestamp_ms"
                            yField="score"
                            seriesField="idx0"
                            colorField="idx0"
                            stepType="hv"
                            axis={{
                                x: {
                                    labelFormatter: (x: number) => format_ts(x / 1000),
                                    grid: false,
                                    minLimit: timeRange[0],
                                    maxLimit: timeRange[1],
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
                                    labelFormatter: (x: number) => data.topstars[x].n,
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
                                title: (d) => format_ts(d.timestamp_ms / 1000),
                                items: [
                                    (d) => ({
                                        name: data.topstars[d.idx0].n,
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
                    </div>
                )}
            </Suspense>
        </AppErrorBoundary>
    );
}
