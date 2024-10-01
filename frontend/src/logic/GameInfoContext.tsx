import React from 'react';

import { useWishContext } from '@/logic/swrWrappers';

import { GameInfoContext } from './contexts';

export function GameInfoContextProvider({ children }: { children: React.ReactNode }) {
    const { data: info, mutate: reloadInfo } = useWishContext({ endpoint: 'game/game_info' });
    if (info) {
        return <GameInfoContext.Provider value={{ info, reloadInfo }}>{children}</GameInfoContext.Provider>;
    } else {
        return <></>;
    }
}
