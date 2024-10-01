import { useContext, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { Intro } from '@/app/area/Intro';
import { ListArea } from '@/app/area/ListArea';
import { GameStatusContext } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

function AreaRouter({ areaName }: { areaName: string }) {
    const { data, mutate } = useWishData({ endpoint: 'game/get_area_detail', payload: { area_name: areaName } });
    const { needReloadArea, setNeedReloadArea } = useContext(GameStatusContext);

    useEffect(() => {
        if (needReloadArea) {
            mutate().then(() => setNeedReloadArea(false));
        }
    }, [mutate, needReloadArea, setNeedReloadArea]);

    if (!data) return <></>;
    if (data.status === 'error') return <NotFound />;

    console.log(data);
    console.log(data.data.type);

    if (data.data.type === 'list') return <ListArea areaData={data.data} />;
    if (data.data.type === 'intro') return <Intro areaData={data.data} />;

    return <NotFound />;
}

export function AreaPage() {
    const [params] = useSearchParams();
    const dst = params.get('dst') ?? '';
    if (dst === '') return <NotFound />;

    return (
        <div className="mt-12 bg-base-300">
            <AreaRouter areaName={dst} />
        </div>
    );
}
