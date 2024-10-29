import { useContext, useEffect } from 'react';

import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Footer } from '@/components/Footer.tsx';
import { WishError } from '@/components/WishError.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { GameStatusContext, useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

import { FullPuzzleList } from './FullPuzzleList';

function PuzzleListBody() {
    const { data, mutate } = useWishData({ endpoint: 'game/get_puzzle_list' });
    const { needReloadArea, setNeedReloadArea } = useContext(GameStatusContext);

    useEffect(() => {
        if (needReloadArea) {
            mutate().then(() => setNeedReloadArea(false));
        }
    }, [mutate, needReloadArea, setNeedReloadArea]);

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;
    return <FullPuzzleList areaDataList={data.data} />;
}

export function PuzzleListPage() {
    const gameInfo = useSuccessGameInfo();

    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!gameInfo.user) return NotFound();
    else if (gameInfo.user.group !== 'staff' && (!gameInfo.game.isGameBegin || !gameInfo.team?.gaming))
        return <NotFound />;

    return (
        <div className="mt-12 bg-base-300 w-full" style={{ minHeight: 'calc(100vh - 3rem)' }}>
            <PuzzleListBody />
            <Footer />
        </div>
    );
}
