import { createContext, useContext } from 'react';
import { KeyedMutator } from 'swr';

import { InfoError } from '@/errors.ts';
import { Wish } from '@/types/wish.ts';

type PuzzleListConfig = 'off' | 'show' | 'drawer';

type SiteSettingContextType = {
    usePuzzleList: PuzzleListConfig;
    setUsePuzzleList: (value: PuzzleListConfig) => void;
};

// @ts-ignore
const SiteSettingContext = createContext<SiteSettingContextType>(undefined);

type GameStatusContextType = {
    currentAp: number;
    currentApIncrease: number;
    updateCurrentAp: () => void;
    needReloadAnnouncement: boolean;
    setNeedReloadAnnouncement: React.Dispatch<React.SetStateAction<boolean>>;
    needReloadPuzzle: boolean;
    setNeedReloadPuzzle: React.Dispatch<React.SetStateAction<boolean>>;
    needReloadArea: boolean;
    setNeedReloadArea: React.Dispatch<React.SetStateAction<boolean>>;
    hasNewAnnouncement: boolean;
    setHasNewAnnouncement: React.Dispatch<React.SetStateAction<boolean>>;
    staffUnreadOnly: boolean;
    setStaffUnreadOnly: React.Dispatch<React.SetStateAction<boolean>>;
    staffTimeDesc: boolean;
    setStaffTimeDesc: React.Dispatch<React.SetStateAction<boolean>>;
    hasNewMessage: boolean;
    setHasNewMessage: React.Dispatch<React.SetStateAction<boolean>>;
};

// @ts-ignore
const GameStatusContext = createContext<GameStatusContextType>(undefined);

type GameInfoContextType = {
    info: Wish.Game.GameInfoApi['response'];
    reloadInfo: KeyedMutator<Wish.Game.GameInfoApi['response']>;
};

// @ts-ignore
const GameInfoContext = createContext<GameInfoContextType>(undefined);

type WindowInfoContextType = {
    viewportHeight: number;
    documentWidth: number;
    windowWidth: number;
    hasScrollbar: boolean;
    scrollbarWidth: number;
    updateWindowInfo: () => void;
};
// @ts-ignore
const WindowInfoContext = createContext<WindowInfoContextType>(undefined);

type SiteThemeType = 'light' | 'cupcake' | 'dark' | 'dracula' | 'corporate' | 'luxury';

export const enabledThemes: SiteThemeType[] = ['light', 'cupcake', 'corporate', 'dark', 'dracula', 'luxury'];

type ThemeContextType = {
    theme: SiteThemeType;
    setTheme: (value: SiteThemeType) => void;
    color: {
        primary: string;
        primaryContent: string;
        secondary: string;
        secondaryContent: string;
        accent: string;
        accentContent: string;
        neutral: string;
        neutralContent: string;
        base100: string;
        base200: string;
        base300: string;
        baseContent: string;
        info: string;
        infoContent: string;
        success: string;
        successContent: string;
        warning: string;
        warningContent: string;
        error: string;
        errorContent: string;
    };
    style: {
        roundedBoxPx: number;
        roundedBtnPx: number;
        roundedBadgePx: number;
    };
};
// @ts-ignore
const ThemeContext = createContext<ThemeContextType>(undefined);

export function useGameInfo() {
    const { info } = useContext(GameInfoContext);
    return info;
}

export function useSuccessGameInfo() {
    const info = useGameInfo();
    if (info.status !== 'success') throw new InfoError();
    return info;
}

export function useWindowInfo() {
    return useContext(WindowInfoContext);
}

export function useTheme() {
    return useContext(ThemeContext);
}

export { GameInfoContext, GameStatusContext, SiteSettingContext, WindowInfoContext, ThemeContext };
export type {
    SiteSettingContextType,
    SiteThemeType,
    PuzzleListConfig,
    GameInfoContextType,
    GameStatusContextType,
    WindowInfoContextType,
    ThemeContextType,
};
