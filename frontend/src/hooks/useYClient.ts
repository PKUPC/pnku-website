import diff from 'fast-diff';
import { useEffect, useMemo, useState } from 'react';
import { YKeyValue } from 'y-utility/y-keyvalue';
import * as Y from 'yjs';

import { YClient } from '@/logic/YClient';

interface UseYClientOptions {
    roomId: string;
    statusHandler?: (event: { status: string }) => void;
    syncHandler?: (isSynced: boolean) => void;
}

export function useYClient({ roomId, statusHandler, syncHandler }: UseYClientOptions) {
    const [client, setClient] = useState<YClient | null>(null);
    const [synced, setSynced] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    useEffect(() => {
        console.log(`[useYClient] Init YClient for room: ${roomId}`);
        const yClient = new YClient(roomId);
        yClient.provider.on('sync', (isSynced: boolean) => {
            setSynced(isSynced);
        });
        yClient.provider.on('connection-close', (event: CloseEvent | null) => {
            if (event) {
                if (event.code === 4337) {
                    setClient(null);
                    setErrorMessage(`协作服务器拒绝了连接，原因是：${event.reason}。`);
                } else if (event.code !== 1000) {
                    setClient(null);
                    setErrorMessage(`连接协作服务器失败，请稍后尝试刷新页面。如果您一直遇到此问题，请联系工作人员。`);
                }
            }
        });
        setClient(yClient);
        yClient.provider.awareness.setLocalState({});

        if (statusHandler) {
            console.log('[useYClient] Add custom status handler');
            yClient.provider.on('status', statusHandler);
        }
        if (syncHandler) {
            console.log('[useYClient] Add custom sync handler');
            yClient.provider.on('sync', syncHandler);
        }

        const cleanBeforeUnload = () => {
            console.log(`[useYClient] [BeforeUnload] Disconnecting from room: ${roomId}`);
            yClient.provider.awareness.setLocalState(null);
            yClient.destroy();
            setClient(null);
        };

        window.addEventListener('beforeunload', cleanBeforeUnload);
        console.log(`[useYClient] Connecting to room: ${roomId}`);
        yClient.connect();

        return () => {
            if (statusHandler) {
                yClient.provider.off('status', statusHandler);
            }
            if (syncHandler) {
                yClient.provider.off('sync', syncHandler);
            }
            window.removeEventListener('beforeunload', cleanBeforeUnload);
            console.log(`[useYClient] Disconnecting from room: ${roomId}`);
            yClient.destroy();
            setClient(null);
        };
    }, [roomId, statusHandler, syncHandler]);

    return { client, synced, errorMessage };
}

/**
 * 计算并应用文本差异到 Y.Text
 * @param yText Y.Text 实例
 * @param oldContent 旧文本内容
 * @param newContent 新文本内容
 * @param cursorPos 可选的光标位置，用于优化 diff 计算
 */
export function applyTextDiff(yText: Y.Text, oldContent: string, newContent: string, cursorPos: number = 0) {
    const diffs = diff(oldContent, newContent, cursorPos);
    let pos = 0;

    const doc = yText.doc;
    if (!doc) {
        throw new Error('Y.Text must be bound to a Y.Doc');
    }

    doc.transact(() => {
        for (let i = 0; i < diffs.length; i++) {
            const d = diffs[i];
            if (d[0] === 0) {
                // EQUAL - 跳过相同部分
                pos += d[1].length;
            } else if (d[0] === -1) {
                // DELETE - 删除
                console.log('delete', pos, d[1].length);
                yText.delete(pos, d[1].length);
            } else {
                // INSERT - 插入
                console.log('insert', pos, d[1]);
                yText.insert(pos, d[1]);
                pos += d[1].length;
            }
        }
    });
}

export type YTextBind = {
    value: string;
    setText: (newValue: string) => void;
    updateTextWithCursor: (newValue: string, cursorPos: number) => void;
};

export function useYText({ client, name }: { client: YClient; name: string }): { yText: Y.Text; text: YTextBind } {
    const yText = useMemo(() => client.doc.getText(name), [client, name]);
    const [value, setValue] = useState('');

    useEffect(() => {
        setValue(yText.toString());

        const observer = () => {
            setValue(yText.toString());
        };

        yText.observe(observer);

        return () => {
            yText.unobserve(observer);
        };
    }, [yText]);

    const setText = (newValue: string) => {
        const oldValue = yText.toString();
        applyTextDiff(yText, oldValue, newValue);
    };

    const updateTextWithCursor = (newValue: string, cursorPos: number = 0) => {
        const oldValue = yText.toString();
        applyTextDiff(yText, oldValue, newValue, cursorPos);
    };

    return {
        yText,
        text: {
            value,
            setText,
            updateTextWithCursor,
        },
    };
}

export type YMapBind<T = any> = {
    value: Record<string, T>;
    set: (key: string, val: T) => void;
    get: (key: string) => T | undefined;
    delete: (key: string) => void;
    clear: () => void;
};

export function useYMap<T = any>({
    client,
    name,
}: {
    client: YClient;
    name: string;
}): {
    yMap: Y.Map<T>;
    map: YMapBind<T>;
} {
    const yMap = useMemo(() => client.doc.getMap<T>(name), [client, name]);
    const [value, setValue] = useState<Record<string, T>>({});

    useEffect(() => {
        const initialValue: Record<string, T> = {};
        yMap.forEach((val, key) => {
            initialValue[key] = val;
        });
        setValue(initialValue);

        const observer = (_event: Y.YMapEvent<T>) => {
            const newValue: Record<string, T> = {};
            yMap.forEach((val, key) => {
                newValue[key] = val;
            });
            setValue(newValue);
        };

        yMap.observe(observer);

        return () => {
            yMap.unobserve(observer);
        };
    }, [yMap]);

    const set = (key: string, val: T) => {
        yMap.set(key, val);
    };

    const get = (key: string): T | undefined => {
        return yMap.get(key);
    };

    const deleteKey = (key: string) => {
        yMap.delete(key);
    };

    const clear = () => {
        yMap.clear();
    };

    return {
        yMap,
        map: {
            value,
            set,
            get,
            delete: deleteKey,
            clear,
        },
    };
}

export type YArrayBind<T = any> = {
    value: T[];
    push: (...items: T[]) => void;
    insert: (index: number, ...items: T[]) => void;
    removeAt: (index: number, length: number) => void;
    setAt: (index: number, item: T) => void;
    getAt: (index: number) => T | undefined;
    clear: () => void;
};

export function useYArray<T = any>({
    client,
    name,
}: {
    client: YClient;
    name: string;
}): {
    yArray: Y.Array<T>;
    array: YArrayBind<T>;
} {
    const yArray = useMemo(() => client.doc.getArray<T>(name), [client, name]);
    const [value, setValue] = useState<T[]>([]);

    useEffect(() => {
        setValue(yArray.toArray());

        const observer = (_event: Y.YArrayEvent<T>) => {
            setValue(yArray.toArray());
        };

        yArray.observe(observer);

        return () => {
            yArray.unobserve(observer);
        };
    }, [yArray]);

    const push = (...items: T[]) => {
        yArray.push(items);
    };

    const insert = (index: number, ...items: T[]) => {
        yArray.insert(index, items);
    };

    const removeAt = (index: number, length: number = 1) => {
        yArray.delete(index, length);
    };

    const setAt = (index: number, item: T) => {
        // Y.Array 没有原生 set；通过 delete+insert 实现
        const doc = yArray.doc;
        if (!doc) {
            throw new Error('Y.Array must be bound to a Y.Doc');
        }
        doc.transact(() => {
            yArray.delete(index, 1);
            yArray.insert(index, [item]);
        });
    };

    const getAt = (index: number): T | undefined => {
        return yArray.get(index);
    };

    const clear = () => {
        if (yArray.length > 0) {
            yArray.delete(0, yArray.length);
        }
    };

    return {
        yArray,
        array: {
            value,
            push,
            insert,
            removeAt,
            setAt,
            getAt,
            clear,
        },
    };
}

export type YKeyValueBind<T = any> = {
    value: Record<string, T>;
    set: (key: string, val: T) => void;
    get: (key: string) => T | undefined;
    delete: (key: string) => void;
    clear: () => void;
};

export function useYKeyValue<T = any>({
    client,
    name,
}: {
    client: YClient;
    name: string;
}): {
    yKeyValue: YKeyValue<T>;
    keyValue: YKeyValueBind<T>;
} {
    const yKeyValue = useMemo(
        () => new YKeyValue(client.doc.getArray<{ key: string; val: T }>(name)),
        [client.doc, name],
    );

    const [value, setValue] = useState<Record<string, T>>({});

    useEffect(() => {
        const initialValue: Record<string, T> = {};
        yKeyValue.map.forEach((val, key) => {
            initialValue[key] = val.val;
        });
        setValue(initialValue);

        const observer = () => {
            const newValue: Record<string, T> = {};
            yKeyValue.map.forEach((val, key) => {
                newValue[key] = val.val;
            });
            setValue(newValue);
        };

        yKeyValue.on('change', observer);

        return () => {
            yKeyValue.off('change', observer);
        };
    }, [yKeyValue]);

    const set = (key: string, val: T) => {
        yKeyValue.set(key, val);
    };

    const get = (key: string): T | undefined => {
        return yKeyValue.get(key);
    };

    const deleteKey = (key: string) => {
        yKeyValue.delete(key);
    };

    const clear = () => {
        yKeyValue.doc.transact(() => {
            for (const key of yKeyValue.map.keys()) {
                yKeyValue.delete(key);
            }
        });
    };

    return {
        yKeyValue,
        keyValue: {
            value,
            set,
            get,
            delete: deleteKey,
            clear,
        },
    };
}
