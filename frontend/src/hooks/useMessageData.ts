import { useCallback, useContext, useEffect, useState } from 'react';

import { GameStatusContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

export function useMessageData(
    teamId: number,
): [Wish.Message.MessageInfo[], Wish.ErrorRes | null, () => void, () => void] {
    const [error, setError] = useState<Wish.ErrorRes | null>(null);
    const [messages, setMessages] = useState<Wish.Message.MessageInfo[]>([]);
    const { hasNewMessage, setHasNewMessage } = useContext(GameStatusContext);

    const reloadMessage = useCallback(() => {
        // console.log("reloading messages, team_id=" + team_id);
        wish({
            endpoint: 'message/get_message',
            payload: {
                team_id: teamId,
                start_id: 0,
            },
        }).then((res) => {
            if (res.status === 'error') {
                setError(res);
            } else {
                setError(null);
                setMessages(res.data);
                if (window.messageStorage === undefined) window.messageStorage = {};
                window.messageStorage[`team#${teamId}`] = res.data;
            }
        });
    }, [teamId]);

    const updateMessage = useCallback(() => {
        // console.log("updating messages, team_id=" + team_id);
        if (messages === undefined || messages === null || messages.length === 0) return reloadMessage();
        const lastMessageId = messages[messages.length - 1].id;

        wish({
            endpoint: 'message/get_message',
            payload: {
                team_id: teamId,
                start_id: lastMessageId,
            },
        }).then((res) => {
            if (res.status === 'error') {
                setError(res);
            } else {
                setError(null);
                if (res.data.length > 0) {
                    const newMessages = messages.concat(res.data);
                    setMessages(newMessages);
                    if (window.messageStorage === undefined) window.messageStorage = {};
                    window.messageStorage[`team#${teamId}`] = newMessages;
                }
            }
        });
    }, [messages, reloadMessage, teamId]);

    useEffect(() => {
        // console.log("init messages for team#" + team_id);
        // console.log(window.messageStorage);
        let localCache = window.messageStorage !== undefined ? window.messageStorage[`team#${teamId}`] : undefined;
        if (Array.isArray(localCache)) {
            if (localCache.length === 0) return reloadMessage();
            // console.log("found local cache!");
            const lastMessageId = localCache[localCache.length - 1].id;
            wish({
                endpoint: 'message/get_message',
                payload: {
                    team_id: teamId,
                    start_id: lastMessageId,
                },
            }).then((res) => {
                if (res.status === 'error') {
                    setError(res);
                } else {
                    setError(null);
                    // make ts happy
                    if (localCache === undefined) localCache = [];
                    const newMessages = localCache.concat(res.data);
                    setMessages(newMessages);
                    // make ts happy
                    if (!window.messageStorage) window.messageStorage = {};

                    window.messageStorage[`team#${teamId}`] = newMessages;
                }
            });
        } else {
            reloadMessage();
        }
    }, [reloadMessage, teamId]);

    useEffect(() => {
        if (hasNewMessage) {
            updateMessage();
            setHasNewMessage(false);
        }
    }, [hasNewMessage, setHasNewMessage, updateMessage]);

    return [messages, error, reloadMessage, updateMessage];
}
