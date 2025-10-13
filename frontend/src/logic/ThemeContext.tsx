import { default as Color } from 'colorjs.io';
import { ReactNode, useCallback, useEffect, useLayoutEffect, useState } from 'react';

import { SiteThemeType, ThemeContext, ThemeContextType, enabledThemes } from '@/logic/contexts.ts';

function getColorFromCssVar(cssVar: string) {
    const color = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
    if (color === '') return '#ffffff';
    const colorObj = new Color(`${color}`);
    return colorObj.to('srgb').toString({ format: 'hex' });
}

function getCurrentColor() {
    return {
        primary: getColorFromCssVar('--color-primary'),
        primaryContent: getColorFromCssVar('--color-primary-content'),
        secondary: getColorFromCssVar('--color-secondary'),
        secondaryContent: getColorFromCssVar('--color-secondary-content'),
        accent: getColorFromCssVar('--color-accent'),
        accentContent: getColorFromCssVar('--color-accent-content'),
        neutral: getColorFromCssVar('--color-neutral'),
        neutralContent: getColorFromCssVar('--color-neutral-content'),
        base100: getColorFromCssVar('--color-base-100'),
        base200: getColorFromCssVar('--color-base-200'),
        base300: getColorFromCssVar('--color-base-300'),
        baseContent: getColorFromCssVar('--color-base-content'),
        info: getColorFromCssVar('--color-info'),
        infoContent: getColorFromCssVar('--color-info-content'),
        success: getColorFromCssVar('--color-success'),
        successContent: getColorFromCssVar('--color-success-content'),
        warning: getColorFromCssVar('--color-warning'),
        warningContent: getColorFromCssVar('--color-warning-content'),
        error: getColorFromCssVar('--color-error'),
        errorContent: getColorFromCssVar('--color-error-content'),
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
        radiusSelector: getCssVariableAsPx('--radius-selector'),
        radiusField: getCssVariableAsPx('--radius-field'),
        radiusBox: getCssVariableAsPx('--radius-box'),
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
