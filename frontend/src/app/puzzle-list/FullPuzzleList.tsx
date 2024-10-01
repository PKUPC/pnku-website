import { Empty } from 'antd';
import React from 'react';

import { PuzzleList } from '@/app/area/components/PuzzleList';
import { FancierCard } from '@/components/FancierCard.tsx';
import { Wish } from '@/types/wish.ts';

function AreaPuzzleList({ areaData }: { areaData: Wish.Game.ListArea }) {
    const areaDataExtra = areaData.extra;

    const themeColors = {
        '--main-color': areaDataExtra.mainColor,
        '--sub-color': areaDataExtra.subColor,
    } as React.CSSProperties;

    console.log(areaData);

    return (
        <FancierCard
            title={areaDataExtra.areaTitle}
            subTitle={areaDataExtra.areaSubtitle}
            // logoUrl={areaDataExtra.areaLogoImage} 会影响难度状态的 tooltip
            style={themeColors}
        >
            {areaData.puzzle_groups.length === 0 ? (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无题目" />
            ) : (
                areaData.puzzle_groups.map((group, idx) => <PuzzleList puzzleList={group.puzzles} key={idx} />)
            )}
        </FancierCard>
    );
}

export function FullPuzzleList({ areaDataList }: { areaDataList: Wish.Game.ListArea[] }) {
    return (
        <>
            {/*<Header/>*/}
            <div
                style={{
                    maxWidth: 850,
                    margin: 'auto',
                    display: 'flex',
                    gap: '16px',
                    flexDirection: 'column',
                    paddingTop: '16px',
                    paddingBottom: '16px',
                }}
            >
                {areaDataList.map((areaData) => (
                    <AreaPuzzleList areaData={areaData} key={areaData.template} />
                ))}
            </div>
        </>
    );
}
