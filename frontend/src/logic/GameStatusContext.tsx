import { ReactNode, useEffect, useRef, useState } from 'react';

import { useCurrencies } from '@/hooks/useCurrency';
import { GameStatusContext, useSuccessGameInfo } from '@/logic/contexts.ts';

export function GameStatusContextProvider({ children }: { children: ReactNode }) {
    const [needReloadAnnouncement, setNeedReloadAnnouncement] = useState<boolean>(false);
    const [needReloadPuzzle, setNeedReloadPuzzle] = useState<boolean>(false);
    const [needReloadArea, setNeedReloadArea] = useState<boolean>(false);
    const [hasNewAnnouncement, setHasNewAnnouncement] = useState<boolean>(false);
    const [staffUnreadOnly, setStaffUnreadOnly] = useState<boolean>(false);
    const [staffTimeDesc, setStaffTimeDesc] = useState<boolean>(false);
    const [hasNewMessage, setHasNewMessage] = useState<boolean>(false);

    const { currencies, syncAllCurrencies, updateAllCurrencies } = useCurrencies();

    const info = useSuccessGameInfo();

    const initUpdateCurrentRef = useRef(syncAllCurrencies);

    useEffect(() => {
        if (!info.user || !info.team || info.user.group === 'staff') return;
        initUpdateCurrentRef.current();
    }, [info, initUpdateCurrentRef]);

    useEffect(() => {
        if (!info.user || !info.team || info.user.group === 'staff') return;
        console.log('set update currency interval');
        const interval = setInterval(updateAllCurrencies, 20 * 1000);
        return () => {
            console.log('clear update currency interval');
            clearInterval(interval);
        };
    }, [info, updateAllCurrencies]);

    return (
        <GameStatusContext.Provider
            value={{
                needReloadAnnouncement,
                setNeedReloadAnnouncement,
                hasNewAnnouncement,
                setHasNewAnnouncement,
                staffUnreadOnly,
                setStaffUnreadOnly,
                staffTimeDesc,
                setStaffTimeDesc,
                hasNewMessage,
                setHasNewMessage,
                needReloadPuzzle,
                setNeedReloadPuzzle,
                needReloadArea,
                setNeedReloadArea,
                currencies,
                syncAllCurrencies,
                updateAllCurrencies,
            }}
        >
            {children}
        </GameStatusContext.Provider>
    );
}
