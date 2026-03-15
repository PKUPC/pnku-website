import { ReactNode } from 'react';

import { useLocalStorageKeyValue } from '@/hooks/useLocalStorageKeyValue';
import { SiteSettingContext } from '@/logic/contexts.ts';

export function GameSettingContextProvider({ children }: { children: ReactNode }) {
    const baseKey = 'website:setting';

    const [theme, setTheme] = useLocalStorageKeyValue(`${baseKey}:theme`, 'system', ['light', 'dark', 'system']);
    const [usePuzzleList, setUsePuzzleList] = useLocalStorageKeyValue(`${baseKey}:usePuzzleList`, 'show', [
        'off',
        'show',
    ]);

    return (
        <SiteSettingContext.Provider
            value={{
                theme: theme as 'light' | 'dark' | 'system',
                setTheme,
                usePuzzleList: usePuzzleList as 'off' | 'show',
                setUsePuzzleList,
            }}
        >
            {children}
        </SiteSettingContext.Provider>
    );
}
