import { default as Color } from 'colorjs.io';
import { ReactNode, useCallback, useEffect, useLayoutEffect, useState } from 'react';

import { SiteThemeType, ThemeContext, ThemeContextType, enabledThemes } from '@/logic/contexts.ts';

function getColorFromCssVar(cssVar: string) {
    const color = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
    if (color === '') return '#ffffff';
    const colorObj = new Color(`oklch(${color})`);
    return colorObj.to('srgb').toString({ format: 'hex' });
}

function getCurrentColor() {
    return {
        primary: getColorFromCssVar('--p'),
        primaryContent: getColorFromCssVar('--pc'),
        secondary: getColorFromCssVar('--s'),
        secondaryContent: getColorFromCssVar('--sc'),
        accent: getColorFromCssVar('--a'),
        accentContent: getColorFromCssVar('--ac'),
        neutral: getColorFromCssVar('--n'),
        neutralContent: getColorFromCssVar('--nc'),
        base100: getColorFromCssVar('--b1'),
        base200: getColorFromCssVar('--b2'),
        base300: getColorFromCssVar('--b3'),
        baseContent: getColorFromCssVar('--bc'),
        info: getColorFromCssVar('--in'),
        infoContent: getColorFromCssVar('--inc'),
        success: getColorFromCssVar('--su'),
        successContent: getColorFromCssVar('--suc'),
        warning: getColorFromCssVar('--wa'),
        warningContent: getColorFromCssVar('--wac'),
        error: getColorFromCssVar('--er'),
        errorContent: getColorFromCssVar('--erc'),
    };
}

function getCurrentTheme(): SiteThemeType {
    const storedTheme = localStorage.getItem('themeName');
    if (storedTheme && enabledThemes.includes(storedTheme as SiteThemeType)) {
        return storedTheme as SiteThemeType;
    }
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDarkMode ? 'dark' : 'light';
}

function getCssVariableAsPx(variableName: string): number {
    const cssValue = getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
    if (cssValue.endsWith('rem')) {
        const remValue = parseFloat(cssValue);
        const rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        return remValue * rootFontSize;
    } else if (cssValue.endsWith('px')) {
        return parseFloat(cssValue);
    } else {
        return 8;
    }
}

function getCurrentStyle(): ThemeContextType['style'] {
    console.log(window.getComputedStyle(document.documentElement).fontSize);
    return {
        roundedBoxPx: getCssVariableAsPx('--rounded-box'),
        roundedBtnPx: getCssVariableAsPx('--rounded-btn'),
        roundedBadgePx: getCssVariableAsPx('--rounded-badge'),
    };
}

export function ThemeContextProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<ThemeContextType['theme']>(getCurrentTheme());
    const [color, setColor] = useState<ThemeContextType['color']>(getCurrentColor());
    const [style, setStyle] = useState<ThemeContextType['style']>(getCurrentStyle());

    const innerSetTheme = useCallback((theme: SiteThemeType) => {
        localStorage.setItem('themeName', theme);
        setTheme(theme);
    }, []);

    useLayoutEffect(() => {
        const oldTheme = document.documentElement.getAttribute('data-theme');
        document.documentElement.setAttribute('data-theme', theme);
        return () => {
            if (oldTheme) document.documentElement.setAttribute('data-theme', oldTheme);
        };
    }, [theme]);

    useEffect(() => {
        const currentColor = getCurrentColor();
        const currentStyle = getCurrentStyle();
        if (JSON.stringify(currentColor) !== JSON.stringify(color)) setColor(currentColor);
        if (JSON.stringify(currentStyle) !== JSON.stringify(style)) setStyle(currentStyle);
    }, [color, style, theme]);

    console.log(color);
    console.log(style);

    return (
        <ThemeContext.Provider value={{ color, style, theme, setTheme: innerSetTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}
