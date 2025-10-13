import { Empty, FloatButton } from 'antd';
import React, { useRef } from 'react';

import { BookIcon, PuzzlePieceIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { PuzzleList } from '@/app/area/components/PuzzleList';
import { FancySlimContainer } from '@/components/FancySlimContainer';
import { Footer } from '@/components/Footer.tsx';
import { TemplateFile } from '@/components/Template';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';

export function ListArea({ areaData }: { areaData: Wish.Game.ListArea }) {
    const info = useSuccessGameInfo();

    const storyRef = useRef<HTMLDivElement>(null);
    const puzzleRef = useRef<HTMLDivElement>(null);

    const scrollToParagraph = (ref: React.RefObject<HTMLDivElement>) => {
        if (!ref.current) return;
        const elementPosition = ref.current.getBoundingClientRect().top;
        // header 固定 48px，-10 是为了和谜题上边的横条对齐
        const offsetPosition = elementPosition + window.scrollY - 48 - 10;
        window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
    };

    const areaDataExtra = areaData.extra;

    const containerBgStyles: React.CSSProperties = {
        backgroundImage: `url(${areaDataExtra.areaImage})`,
        backgroundPositionX: `${areaDataExtra.bgFocusPositionX}%`,
        backgroundPositionY: `${areaDataExtra.bgFocusPositionY}%`,
    };

    const themeColors = {
        '--main-color': areaDataExtra.mainColor,
        '--sub-color': areaDataExtra.subColor,
    } as React.CSSProperties;

    console.log(areaData);

    if (!ARCHIVE_MODE && (!info.user || (info.user.group !== 'staff' && !info.game.isGameBegin))) return <NotFound />;

    return (
        <div className="relative w-full" style={themeColors}>
            <div
                className="relative w-full h-[80vh] z-0"
                style={{
                    ...containerBgStyles,
                    backgroundSize: 'cover',
                    pointerEvents: 'none',
                }}
            />
            <FancySlimContainer
                title={areaDataExtra.areaTitle}
                extraClassName="relative -mt-[40vh] z-1"
                logoUrl={areaDataExtra.areaLogoImage}
            >
                <div ref={storyRef}></div>
                <FancySlimContainer.SubTitle subTitle={areaDataExtra.areaSubtitle} />
                <TemplateFile name={areaData.template} />
                <br />
                <div ref={puzzleRef}></div>
                <FancySlimContainer.SubTitle subTitle={'谜题'} />
                {areaData.puzzle_groups.length === 0 ? (
                    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无题目" />
                ) : (
                    areaData.puzzle_groups.map((group, idx) => <PuzzleList puzzleList={group.puzzles} key={idx} />)
                )}
            </FancySlimContainer>

            <FloatButton.Group shape="square" style={{ right: 5 }}>
                <FloatButton
                    icon={<BookIcon style={{ color: 'transparent' }} />}
                    onClick={() => scrollToParagraph(storyRef)}
                />
                <FloatButton
                    icon={<PuzzlePieceIcon style={{ color: 'transparent' }} />}
                    onClick={() => scrollToParagraph(puzzleRef)}
                />
            </FloatButton.Group>
            <Footer />
        </div>
    );
}
