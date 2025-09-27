import React from 'react';

import { Loading } from '@/components/DaisyUI/Loading';
import { WishError } from '@/components/WishError';
import { useWishContext } from '@/logic/swrWrappers';

import { GameInfoContext } from './contexts';

export function GameInfoContextProvider({ children }: { children: React.ReactNode }) {
    const { data: info, mutate: reloadInfo } = useWishContext({ endpoint: 'game/game_info' });
    console.log(info);
    if (info) {
        if (info.status === 'error') {
            return <WishError res={info} reload={reloadInfo} />;
        }
        return <GameInfoContext.Provider value={{ info, reloadInfo }}>{children}</GameInfoContext.Provider>;
    } else {
        return <Loading />;
    }
}
