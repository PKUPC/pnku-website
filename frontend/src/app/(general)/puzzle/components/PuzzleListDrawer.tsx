import { UnorderedListOutlined } from '@ant-design/icons';
import { Drawer, Empty, FloatButton } from 'antd';
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { PuzzleListSider } from '@/app/(general)/puzzle/components/PuzzleListSider';
import { Wish } from '@/types/wish.ts';

export default function PuzzleListDrawer({ data }: { data: { data: Wish.Puzzle.PuzzleDetailData } }) {
    const [showPuzzleList, setShowPuzzleList] = useState(false);
    const closeDrawer = () => setShowPuzzleList(false);
    const [params] = useSearchParams();
    const curKey = params.get('key') ?? 'none';

    return (
        <>
            <Drawer
                open={showPuzzleList}
                onClose={closeDrawer}
                placement={'right'}
                title={<span>{data.data.area_name}</span>}
            >
                <div>
                    {data.data.puzzle_list.length === 0 ? (
                        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无题目" />
                    ) : (
                        data.data.puzzle_list.map((group, idx) => (
                            <PuzzleListSider puzzleList={group.puzzles} key={idx} currentKey={curKey} />
                        ))
                    )}
                </div>
            </Drawer>
            <FloatButton
                shape={'square'}
                onClick={() => setShowPuzzleList(true)}
                icon={<UnorderedListOutlined />}
                style={{ right: 0, bottom: '90%', transform: 'translate(0, 50%)' }}
            />
        </>
    );
}
