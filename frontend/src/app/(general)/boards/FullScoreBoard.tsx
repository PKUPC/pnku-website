import { FlagTwoTone } from '@ant-design/icons';
import { Alert, Tag, Tooltip } from 'antd';
import { memo, useCallback, useEffect, useRef, useState } from 'react';

import { TimeIcon } from '@/SvgIcons';
import { BoardReloader } from '@/app/(general)/boards/components/BoardReloader';
import { TeamInfo } from '@/app/(general)/boards/components/TeamInfo';
import TopStarPlot from '@/app/(general)/boards/components/TopStarPlot.tsx';
import { useSuccessGameInfo, useTheme, useWindowInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts, format_ts_to_HMS } from '@/utils.ts';

function PassedStatus({ team }: { team: Wish.Game.FullBoardItem }) {
    if (team.g)
        return (
            <div className="inline">
                解出 <b>{team.s}</b> 题
                <br />
                {team.s > 0 && format_ts(team.lts)}
            </div>
        );
    else
        return (
            <div className="inline">
                <div className="inline text-base-content text-opacity-70">未过序章</div>
            </div>
        );
}

function FinishedStatus({ team, gameStartTime }: { team: Wish.Game.FullBoardItem; gameStartTime: number }) {
    const { color } = useTheme();
    const falseColor = color.baseContent + '99';
    if (team.f) {
        return (
            <div className="inline">
                <div className="inline text-success">
                    <FlagTwoTone twoToneColor={[color.success, color.base100]} /> 已完赛
                </div>
                <br />
                用时 {format_ts_to_HMS(team.fts - gameStartTime)}
            </div>
        );
    } else
        return (
            <div className="inline">
                <div className="inline" style={{ color: falseColor }}>
                    <FlagTwoTone twoToneColor={[falseColor, color.base100]} /> 未完赛
                </div>
            </div>
        );
}

function StatusSmall({ team, gameStartTime }: { team: Wish.Game.FullBoardItem; gameStartTime: number }) {
    const { color } = useTheme();
    const falseColor = color.baseContent + '99';
    let finishedStatus;
    if (team.f)
        finishedStatus = (
            <div className="inline">
                <div className="inline text-success">
                    <FlagTwoTone twoToneColor={[color.success, color.base100]} />
                    {' 已完赛 '}
                </div>
                <div className="inline opacity-35">
                    <TimeIcon />
                </div>
            </div>
        );
    else
        finishedStatus = (
            <div className="inline">
                <div className="inline" style={{ color: falseColor }}>
                    <FlagTwoTone twoToneColor={[falseColor, color.base100]} /> 未完赛
                </div>
            </div>
        );

    const toolTipsTitle = (
        <>
            {/*{team.finished && <>{"完赛时间：" + format_ts(team.finished_timestamp_s)}<br/> </>}*/}
            {team.f && (
                <>
                    {'完赛用时：' + format_ts_to_HMS(team.fts - gameStartTime)}
                    <br />{' '}
                </>
            )}
            {team.s > 0 && '最后提交时间：' + format_ts(team.lts)}
        </>
    );

    let pass_text = (
        <>
            解出 <b>{team.s} </b> 题
        </>
    );
    if (!team.g)
        pass_text = (
            <div className="inline" style={{ color: falseColor }}>
                未过序章
            </div>
        );

    return (
        <div>
            <Tooltip title={team.s > 0 && toolTipsTitle} placement={'topRight'} arrow={{ pointAtCenter: true }}>
                {finishedStatus}
                <br />
                <div className="inline">
                    {pass_text}{' '}
                    {team.s > 0 && (
                        <div className="inline opacity-35">
                            <TimeIcon />
                        </div>
                    )}
                </div>
            </Tooltip>
        </div>
    );
}

// eslint-disable-next-line react/display-name
const RowHeader = memo(({ wide }: { wide: boolean }) => {
    const common = 'p-2 items-center border-neutral-content';
    if (wide)
        return (
            <div className="flex text-[0.875rem] rounded-t-box bg-base-200/30 font-bold h-10 border-b-[1px] border-neutral-content">
                <div className={`${common} hidden w640:w-[3.75rem] w640:flex`}>排名</div>
                <div
                    className={`${common} hidden w640:flex`}
                    style={{
                        width: 'calc(100% - 21.75rem)',
                    }}
                >
                    队伍
                </div>
                <div className={`${common} w-32 hidden w640:flex`}>完赛状态</div>
                <div className="p-2 items-center w-40 hidden w640:flex">解出题数</div>
            </div>
        );
    return (
        <div className="flex text-[0.875rem] rounded-t-box bg-base-200/30 font-bold h-10 border-b-[1px] border-neutral-content">
            <div className={`${common} flex w-[2.25rem] w640:hidden`}>#</div>
            <div
                className={`${common} flex w640:hidden`}
                style={{
                    width: 'calc(100% - 9rem)',
                }}
            >
                队伍
            </div>
            <div className="p-2 items-center w-[6.75rem] flex w640:hidden">状态</div>
        </div>
    );
});

// eslint-disable-next-line react/display-name
const RowContent = memo(
    ({ team, gameStartTime, wide }: { team: Wish.Game.FullBoardItem; gameStartTime: number; wide: boolean }) => {
        const common = 'p-2 items-center text-base-content text-opacity-80';
        if (wide)
            return (
                <div className="flex text-[0.875rem] border-b-[1px] hover:bg-base-200/30 border-neutral-content">
                    <div className={`${common} hidden w640:w-[3.75rem] w640:flex`}>{team.g ? team.r : '--'}</div>
                    <div
                        className={`${common} hidden w640:flex`}
                        style={{
                            width: 'calc(100% - 21.75rem)',
                        }}
                    >
                        <TeamInfo team={team} />
                    </div>
                    <div className={`${common} w-32 hidden w640:flex`}>
                        <FinishedStatus team={team} gameStartTime={gameStartTime} />
                    </div>
                    <div className={`${common} w-40 hidden w640:flex`}>
                        <PassedStatus team={team} />
                    </div>
                </div>
            );
        return (
            <div className="flex text-[0.875rem] border-b-[1px] hover:bg-base-200/30 border-neutral-content">
                <div className={`${common} flex w-[2.25rem] w640:hidden`}>{team.g ? team.r : '--'}</div>
                <div
                    className={`${common} flex w640:hidden`}
                    style={{
                        width: 'calc(100% - 9rem)',
                    }}
                >
                    <TeamInfo team={team} maxLength={25} />
                </div>
                <div className={`${common} w-[6.75rem] flex w640:hidden`}>
                    <StatusSmall team={team} gameStartTime={gameStartTime} />
                </div>
            </div>
        );
    },
);

// function RowContent({ team, gameStartTime }: { team: Wish.FullBoardItem; gameStartTime: number })

function BoardList({ data, wide }: { data: Wish.Game.FullBoard; wide: boolean }) {
    const [showCount, setShowCount] = useState(data.list.length > 30 ? 30 : data.list.length);
    const bottomRef = useRef<HTMLDivElement | null>(null);

    const onScrolledToBottom = useCallback(
        (entries: IntersectionObserverEntry[]) => {
            const [entry] = entries;
            if (entry.isIntersecting) {
                setShowCount((pre) => (pre + 15 > data.list.length ? data.list.length : pre + 15));
            }
        },
        [data.list.length],
    );

    useEffect(() => {
        const observer = new IntersectionObserver(onScrolledToBottom, {
            root: null,
            rootMargin: '0px',
            threshold: 0.01,
        });
        const current = bottomRef.current;
        if (current) observer.observe(current);
        return () => {
            if (current) observer.unobserve(current);
        };
    }, [onScrolledToBottom]);

    return (
        <div>
            <RowHeader wide={wide} />
            {data.list.slice(0, showCount).map((item) => (
                <RowContent key={item.id} team={item} gameStartTime={data.time_range[0]} wide={wide} />
            ))}
            <div ref={bottomRef} className="w-full h-4"></div>
        </div>
    );
}

export function FullScoreBoard({ data, reload }: { data: Wish.Game.FullBoard; reload: () => void }) {
    const info = useSuccessGameInfo();
    const { windowWidth } = useWindowInfo();

    const myTeamData = data.list.filter((item) => item.id === info.team?.id);
    let myTeamInfo = null;
    if (myTeamData.length > 0) {
        console.log(myTeamData[0]);
        myTeamInfo = (
            <Alert
                message={
                    <>
                        您的队伍排名为 <Tag color="#87d068">第 {myTeamData[0].r} 名 </Tag>，通过题数为{' '}
                        <Tag color="#2db7f5">{myTeamData[0].s} 题</Tag>。
                    </>
                }
            />
        );
    }

    let hideInfo = null;
    if (info.team?.extra_status === 'hidden')
        hideInfo = <Alert type={'warning'} showIcon={true} message={'您的队伍已经在排行榜上隐藏！'} />;

    return (
        <div>
            <BoardReloader reload={reload} />
            {data.topstars.length > 0 && <TopStarPlot data={data} />}

            <br />
            {myTeamInfo && (
                <>
                    {myTeamInfo}
                    <br />
                </>
            )}
            {hideInfo && (
                <>
                    {hideInfo}
                    <br />
                </>
            )}
            <BoardList data={data} wide={windowWidth >= 650} />
        </div>
    );
}
