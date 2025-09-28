import { Alert, Empty, FloatButton } from 'antd';
import { useContext } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { LeftCircleIcon } from '@/SvgIcons';
import { TabContainer } from '@/app/(general)/puzzle/TabContainer.tsx';
import PuzzleListDrawer from '@/app/(general)/puzzle/components/PuzzleListDrawer.tsx';
import { PuzzleListSider } from '@/app/(general)/puzzle/components/PuzzleListSider.tsx';
import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { ClickTitle } from '@/components/LinkTitle';
import { WishError } from '@/components/WishError.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { SiteSettingContext, useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

import styles from './page.module.css';

export function PuzzlePage() {
    const [params] = useSearchParams();
    const info = useSuccessGameInfo();
    const { usePuzzleList } = useContext(SiteSettingContext);
    const navigate = useNavigate();

    let hideInfo = null;
    if (info.team?.extra_status === 'hidden')
        hideInfo = <Alert type={'warning'} showIcon={true} message={'您的队伍已经在排行榜上隐藏！'} />;

    const curKey = params.get('key') ?? 'none';

    const { data } = useWishData({
        endpoint: 'puzzle/get_detail',
        payload: { puzzle_key: curKey },
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    console.log(data);

    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!info.user) return <NotFound />;
    else if (info.user.group !== 'staff' && (!info.game.isGameBegin || !info.team?.gaming)) return <NotFound />;

    if (usePuzzleList == 'show')
        return (
            <div className={styles.puzzleWithListContainer}>
                <div className="puzzle-sidebar">
                    {/*<LinkTitle icon={<LeftCircleIcon/>} title={"区域页"} url={data.data.return}/>*/}
                    <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
                    <br />
                    <div className="puzzle-lists">
                        {data.data.puzzle_list.length === 0 ? (
                            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无题目" />
                        ) : (
                            data.data.puzzle_list.map((group, idx) => (
                                <PuzzleListSider puzzleList={group.puzzles} key={idx} currentKey={curKey} />
                            ))
                        )}
                    </div>
                </div>
                <div className="puzzle-content-container">
                    {hideInfo && (
                        <div>
                            {hideInfo}
                            <br />
                        </div>
                    )}
                    <TabContainer puzzleData={data.data} />
                </div>
                <FloatButton.BackTop />
            </div>
        );
    else
        return (
            <>
                <div className={'slim-container'}>
                    {/*<LinkTitle icon={<LeftCircleIcon/>} title={"区域页"} url={data.data.return}/>*/}
                    <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
                    <br />
                    {hideInfo && (
                        <>
                            {hideInfo}
                            <br />
                        </>
                    )}
                    <TabContainer puzzleData={data.data} />
                    <FloatButton.BackTop />
                </div>
                {usePuzzleList == 'drawer' && <PuzzleListDrawer data={data} />}
            </>
        );
}
