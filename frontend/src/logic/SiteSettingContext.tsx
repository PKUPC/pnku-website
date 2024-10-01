import { ReactNode, useEffect, useState } from 'react';

import { PuzzleListConfig, SiteSettingContext, SiteSettingContextType, useSuccessGameInfo } from '@/logic/contexts.ts';
import { decodeBase64ToObject, encodeObjectToBase64 } from '@/utils.ts';

export function GameSettingContextProvider({ children }: { children: ReactNode }) {
    const info = useSuccessGameInfo();
    const [usePuzzleList, setUsePuzzleList] = useState<SiteSettingContextType['usePuzzleList']>('off');

    const setDefaultContext = (key: string) => {
        localStorage.setItem(key, encodeObjectToBase64({ usePuzzleList: 'off' }));
    };

    const userId = info.user?.id;
    const key = userId ? userId + '_setting' : 'default_setting';

    useEffect(() => {
        const valueBase64 = localStorage.getItem(key);
        if (!valueBase64) {
            // 没有设置，则存储一份默认设置
            setDefaultContext(key);
            return;
        }
        // 尝试解析
        const obj = decodeBase64ToObject(valueBase64);
        if (!obj) {
            setDefaultContext(key);
            return;
        }
        console.log(obj);
        //@ts-ignore
        setUsePuzzleList(obj.usePuzzleList);
    }, [key]);

    return (
        <SiteSettingContext.Provider
            value={{
                usePuzzleList,
                setUsePuzzleList: (value: string) => {
                    localStorage.setItem(
                        key,
                        encodeObjectToBase64({
                            usePuzzleList: value,
                        }),
                    );
                    if (['off', 'drawer', 'show'].includes(value)) setUsePuzzleList(value as PuzzleListConfig);
                    else setUsePuzzleList('off');
                    const storageValue = localStorage.getItem(key);
                    console.log(storageValue ? decodeBase64ToObject(storageValue) : 'no localstorage value');
                },
            }}
        >
            {children}
        </SiteSettingContext.Provider>
    );
}
