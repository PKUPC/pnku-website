import { CloseCircleOutlined } from '@ant-design/icons';
import { message, notification } from 'antd';
import React, { useContext, useEffect } from 'react';
import { useSWRConfig } from 'swr';

import { InfoError, NeverError } from '@/errors';
import { PushClient } from '@/logic/WsClient';
import { GameInfoContext, GameInfoContextType, GameStatusContext } from '@/logic/contexts.ts';

export function PushDaemon({ info, reloadInfo }: GameInfoContextType) {
    const { setNeedReloadAnnouncement, setHasNewMessage, setNeedReloadArea, updateAllCurrencies } =
        useContext(GameStatusContext);
    const [wsNotification, contextHolder] = notification.useNotification({
        stack: { threshold: 3 },
        placement: 'topRight',
        top: 70,
    });
    const [wsMessage] = message.useMessage();
    const { mutate } = useSWRConfig();

    if (info.status !== 'success') throw new NeverError();

    useEffect(() => {
        notification.config({
            closeIcon: <CloseCircleOutlined />,
        });
        PushClient.init(wsNotification, wsMessage);
    }, [wsMessage, wsNotification]);

    useEffect(() => {
        if (info !== null && info.feature.push) {
            const client = new PushClient(
                info,
                reloadInfo,
                setNeedReloadAnnouncement,
                setHasNewMessage,
                setNeedReloadArea,
                updateAllCurrencies,
                mutate,
            );
            return () => {
                client.stop();
            };
        }
    }, [
        info,
        mutate,
        reloadInfo,
        setHasNewMessage,
        setNeedReloadAnnouncement,
        setNeedReloadArea,
        updateAllCurrencies,
        wsNotification,
    ]);

    return <>{contextHolder}</>;
}

export function PushDaemonWrapper({ children }: { children: React.ReactNode }) {
    const { info, reloadInfo } = useContext(GameInfoContext);
    if (info.status !== 'success') throw new InfoError();

    return (
        <>
            {info.feature.push ? <PushDaemon info={info} reloadInfo={reloadInfo} /> : null}
            {children}
        </>
    );
}
