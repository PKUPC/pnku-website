import { FileDoneOutlined } from '@ant-design/icons';
import { useMemo } from 'react';
import { LuBookHeart } from 'react-icons/lu';
import { useLocation, useParams } from 'react-router';

import { HintIcon, HistoryIcon, SearchIcon, TextIcon } from '@/SvgIcons';
import { HintTab } from '@/app/(general)/puzzle/HintTab.tsx';
import { ManualHintTab } from '@/app/(general)/puzzle/ManualHintTab.tsx';
import { SolutionTab } from '@/app/(general)/puzzle/SolutionTab.tsx';
import { SubmissionTab } from '@/app/(general)/puzzle/SubmissionTab.tsx';
import NotFound from '@/app/NotFound';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import { PuzzleTab } from './PuzzleTab';
import { StoryTab } from './StoryTab';
import styles from './TabContainer.module.css';

export function TabContainer({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const info = useSuccessGameInfo();
    const { pathname } = useLocation();
    const params = useParams();
    const component = params.component;
    const puzzleKey = params.puzzleKey;

    const items = useMemo(() => {
        let items = [];
        if (puzzleData.stories?.length ?? 0 > 0)
            items.push({
                label: '剧情',
                icon: <LuBookHeart />,
                key: '/puzzle/stories/' + puzzleKey,
            });

        items.push({
            label: '题目',
            icon: <TextIcon />,
            key: '/puzzle/body/' + puzzleKey,
        });

        if (!ARCHIVE_MODE)
            items.push({
                label: '提交记录',
                icon: <HistoryIcon />,
                key: '/puzzle/submissions/' + puzzleKey,
            });

        items.push({
            label: '观测',
            icon: <SearchIcon />,
            key: '/puzzle/hints/' + puzzleKey,
        });

        if (!ARCHIVE_MODE && info.user?.group === 'player' && !info.feature.playground)
            items.push({
                label: '神谕',
                icon: <HintIcon />,
                key: '/puzzle/manual-hints/' + puzzleKey,
            });

        if (ARCHIVE_MODE || info.user?.group === 'staff')
            items.push({
                label: '解析',
                icon: <FileDoneOutlined />,
                key: '/puzzle/solution/' + puzzleKey,
            });

        return items;
    }, [info, puzzleKey, puzzleData]);

    console.log(pathname);

    let children = <NotFound />;
    if (component === 'body') children = <PuzzleTab puzzleData={puzzleData} />;
    else if (component === 'submissions') children = <SubmissionTab puzzleData={puzzleData} />;
    else if (component === 'hints') children = <HintTab puzzleData={puzzleData} />;
    else if (component === 'manual-hints') children = <ManualHintTab puzzleData={puzzleData} />;
    else if (component == 'solution') children = <SolutionTab puzzleData={puzzleData} />;
    else if (component == 'stories') children = <StoryTab puzzleData={puzzleData} />;

    return (
        <div className={styles.tabContainer}>
            <div className={styles.puzzleTitle}>
                <div className={styles.titleContent}>{puzzleData.title}</div>
                {puzzleData.unlock_ts && (
                    <div className={styles.unlockTime}>解锁于 {format_ts(puzzleData.unlock_ts)}</div>
                )}
            </div>

            <TabsNavbar items={items} selectedKeys={[pathname]} />
            <br />
            {children}
        </div>
    );
}

export function PublicTabContainer({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const { pathname } = useLocation();
    const params = useParams();
    const puzzleKey = params.puzzleKey;

    const items = useMemo(() => {
        let items = [
            {
                label: '题目',
                icon: <TextIcon />,
                key: '/puzzle/public/' + puzzleKey,
            },
        ];
        return items;
    }, [puzzleKey]);

    return (
        <div className={styles.tabContainer}>
            <div className={styles.puzzleTitle}>
                <div className={styles.titleContent}>{puzzleData.title}</div>
                {puzzleData.unlock_ts && (
                    <div className={styles.unlockTime}>解锁于 {format_ts(puzzleData.unlock_ts)}</div>
                )}
            </div>

            <TabsNavbar items={items} selectedKeys={[pathname]} />
            <br />
            <PuzzleTab puzzleData={puzzleData} />
        </div>
    );
}
