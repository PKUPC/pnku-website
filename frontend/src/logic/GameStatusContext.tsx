import { ReactNode, useCallback, useEffect, useRef, useState } from 'react';

import { GameStatusContext, useSuccessGameInfo } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { calcCurrentActionPoints, getCurrentApIncrease } from '@/utils.ts';

export function GameStatusContextProvider({ children }: { children: ReactNode }) {
    const [needReloadAnnouncement, setNeedReloadAnnouncement] = useState<boolean>(false);
    const [needReloadPuzzle, setNeedReloadPuzzle] = useState<boolean>(false);
    const [needReloadArea, setNeedReloadArea] = useState<boolean>(false);
    const [hasNewAnnouncement, setHasNewAnnouncement] = useState<boolean>(false);
    const [staffUnreadOnly, setStaffUnreadOnly] = useState<boolean>(false);
    const [staffTimeDesc, setStaffTimeDesc] = useState<boolean>(false);
    const [hasNewMessage, setHasNewMessage] = useState<boolean>(false);
    const [currentAp, setCurrentAp] = useState<number>(0);
    const [currentApIncrease, setCurrentApIncrease] = useState<number>(0);
    const [currentApChange, setCurrentApChange] = useState<number>(0);
    const [currentApIncreasePolicy, setCurrentApIncreasePolicy] = useState<[number, number][]>([[0, 0]]);
    const info = useSuccessGameInfo();

    const updateCurrentAp = useCallback(() => {
        wish({ endpoint: 'game/team_ap_detail' }).then((res) => {
            if (res.status !== 'error') {
                const teamApChange = res.data.team_ap_change;
                const apIncreasePolicy = res.data.ap_increase_policy;
                if (JSON.stringify(apIncreasePolicy) !== JSON.stringify(currentApIncreasePolicy))
                    setCurrentApIncreasePolicy(apIncreasePolicy);
                setCurrentApChange(teamApChange);
                const tCurrentAp = calcCurrentActionPoints(apIncreasePolicy, teamApChange);
                setCurrentAp(tCurrentAp);
                setCurrentApIncrease(getCurrentApIncrease(apIncreasePolicy));
                console.log('update current ap: ' + tCurrentAp);
            }
        });
    }, [currentApIncreasePolicy]);

    const updateCurrentApWithTime = useCallback(() => {
        if (currentApIncreasePolicy) setCurrentAp(calcCurrentActionPoints(currentApIncreasePolicy, currentApChange));
    }, [currentApChange, currentApIncreasePolicy]);

    const initUpdateCurrentRef = useRef(updateCurrentAp);

    useEffect(() => {
        if (!info.user || !info.team || info.user.group === 'staff') return;
        initUpdateCurrentRef.current();
    }, [info, initUpdateCurrentRef]);

    useEffect(() => {
        if (!info.user || !info.team || info.user.group === 'staff') return;
        console.log('set update ap interval');
        const interval = setInterval(updateCurrentApWithTime, 20 * 1000);
        return () => {
            console.log('clear update ap interval');
            clearInterval(interval);
        };
    }, [info, updateCurrentApWithTime]);

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
                currentAp,
                currentApIncrease,
                updateCurrentAp,
            }}
        >
            {children}
        </GameStatusContext.Provider>
    );
}
