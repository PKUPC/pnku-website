import { FileDoneOutlined } from '@ant-design/icons';
import { useState } from 'react';

import { HintIcon, HistoryIcon, SearchIcon, TextIcon } from '@/SvgIcons';
import { HintTab } from '@/app/(general)/puzzle/HintTab.tsx';
import { ManualHintTab } from '@/app/(general)/puzzle/ManualHintTab.tsx';
import { SolutionTab } from '@/app/(general)/puzzle/SolutionTab.tsx';
import { SubmissionTab } from '@/app/(general)/puzzle/SubmissionTab.tsx';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import { PuzzleTab } from './PuzzleTab';
import styles from './TabContainer.module.scss';

type TabKeyItem = 'body' | 'submissions' | 'hints' | 'manual-hints' | 'solution';

export function TabContainer({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const info = useSuccessGameInfo();
    const [tabKey, setTabKey] = useState<TabKeyItem>('body');

    const items = [
        {
            type: 'button',
            label: '题目',
            icon: <TextIcon />,
            key: 'body',
            onClick: () => setTabKey('body'),
        },
    ];

    if (!ARCHIVE_MODE)
        items.push({
            type: 'button',
            label: '提交记录',
            icon: <HistoryIcon />,
            key: 'submissions',
            onClick: () => setTabKey('submissions'),
        });

    items.push({
        type: 'button',
        label: '观测',
        icon: <SearchIcon />,
        key: 'hints',
        onClick: () => setTabKey('hints'),
    });

    if (!ARCHIVE_MODE && info.user?.group === 'player' && !info.feature.playground)
        items.push({
            type: 'button',
            label: '神谕',
            icon: <HintIcon />,
            key: 'manual-hints',
            onClick: () => setTabKey('manual-hints'),
        });

    if (ARCHIVE_MODE || info.user?.group === 'staff')
        items.push({
            type: 'button',
            label: '解析',
            icon: <FileDoneOutlined />,
            key: 'solution',
            onClick: () => setTabKey('solution'),
        });

    let children;
    if (tabKey === 'body') children = <PuzzleTab puzzleData={puzzleData} />;
    else if (tabKey === 'submissions') children = <SubmissionTab puzzleData={puzzleData} />;
    else if (tabKey === 'hints') children = <HintTab puzzleData={puzzleData} />;
    else if (tabKey === 'manual-hints') children = <ManualHintTab puzzleData={puzzleData} />;
    else if (tabKey == 'solution') children = <SolutionTab puzzleData={puzzleData} />;

    return (
        <div className={styles.tabContainer}>
            <div className={styles.puzzleTitle}>
                <div className={styles.titleContent}>{puzzleData.title}</div>
                {puzzleData.unlock_ts && (
                    <div className={styles.unlockTime}>解锁于 {format_ts(puzzleData.unlock_ts)}</div>
                )}
            </div>

            <TabsNavbar items={items} selectedKeys={[tabKey]} />
            <br />
            {children}
        </div>
    );
}
