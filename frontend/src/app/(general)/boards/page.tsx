import { useSearchParams } from 'react-router-dom';

import { FirstBloodBoard } from '@/app/(general)/boards/FirstBloodBoard.tsx';
import { FullScoreBoard } from '@/app/(general)/boards/FullScoreBoard.tsx';
import { SimpleScoreBoard } from '@/app/(general)/boards/SimpleScoreBoard.tsx';
import { SpeedRunBoard } from '@/app/(general)/boards/SpeedRunBoard.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';

export function BoardPage() {
    const [searchParams] = useSearchParams();
    const cur_key = searchParams.get('key');
    const { data, mutate } = useWishData({ endpoint: 'game/get_board', payload: { board_key: cur_key ?? '' } });

    if (!data)
        if (!data)
            return (
                // 空出刷新排行榜那一栏的距离 height 9 + margin 3 (1/4 rem)
                <div className="pt-12">
                    <Loading style={{ height: 350 }} />
                </div>
            );
    if (data.status !== 'success') return <WishError res={data} reload={mutate} />;

    let board = <></>;

    if (data.data.type === 'full') board = <FullScoreBoard data={data.data} reload={mutate} />;
    else if (data.data.type === 'firstblood') board = <FirstBloodBoard data={data.data} />;
    else if (data.data.type === 'simple') board = <SimpleScoreBoard data={data.data} />;
    else if (data.data.type === 'speed_run') board = <SpeedRunBoard data={data.data} />;
    return <div>{board}</div>;
}
