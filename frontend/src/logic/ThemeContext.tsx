import { default as Color } from 'colorjs.io';
import { ReactNode, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from 'react';

import { SiteSettingContext, ThemeContext, ThemeContextType } from '@/logic/contexts.ts';

function getColorFromCssVar(cssVar: string) {
    const color = getComputedStyle(document.documentElement).getPropertyValue(cssVar).trim();
    if (color === '') return '#ffffff';
    const colorObj = new Color(`${color}`);
    return colorObj.to('srgb').toString({ format: 'hex' });
}

function getCurrentColor(): ThemeContextType['color'] {
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
    return {
        radiusSelector: getCssVariableAsPx('--radius-selector'),
        radiusField: getCssVariableAsPx('--radius-field'),
        radiusBox: getCssVariableAsPx('--radius-box'),
    };
}

function deepEqual<T>(a: T, b: T): boolean {
    if (a === b) return true;
    if (typeof a !== 'object' || a === null || typeof b !== 'object' || b === null) return false;
    const keysA = Object.keys(a) as Array<keyof T>;
    const keysB = Object.keys(b) as Array<keyof T>;
    if (keysA.length !== keysB.length) return false;
    for (const key of keysA) {
        if (!keysB.includes(key) || !deepEqual(a[key], b[key])) return false;
    }
    return true;
}

export function ThemeContextProvider({ children }: { children: ReactNode }) {
    const { theme } = useContext(SiteSettingContext);
    const [color, setColor] = useState<ThemeContextType['color']>(getCurrentColor());
    const [style, setStyle] = useState<ThemeContextType['style']>(getCurrentStyle());
    const observerRef = useRef<MutationObserver | null>(null);

    const getActualTheme = useCallback((themeValue: 'light' | 'dark' | 'system'): 'light' | 'dark' => {
        if (themeValue === 'system') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return themeValue;
    }, []);

    const updateThemeValues = useCallback(() => {
        const newColor = getCurrentColor();
        const newStyle = getCurrentStyle();

        setColor((prevColor) => {
            if (!deepEqual(prevColor, newColor)) {
                console.log('color changed, updating color!');
                return newColor;
            }
            return prevColor;
        });

        setStyle((prevStyle) => {
            if (!deepEqual(prevStyle, newStyle)) {
                console.log('style changed, updating style!');
                return newStyle;
            }
            return prevStyle;
        });
    }, []);

    // 监听主题变化并更新 data-theme 属性
    useLayoutEffect(() => {
        const actualTheme = getActualTheme(theme);
        document.documentElement.setAttribute('data-theme', actualTheme);
    }, [theme, getActualTheme]);

    // 监听系统主题变化（仅在 theme === 'system' 时）
    useEffect(() => {
        if (theme !== 'system') return;

        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = () => {
            const actualTheme = getActualTheme('system');
            document.documentElement.setAttribute('data-theme', actualTheme);
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => {
            mediaQuery.removeEventListener('change', handleChange);
        };
    }, [theme, getActualTheme]);

    useEffect(() => {
        observerRef.current = new MutationObserver((mutations) => {
            const hasRelevantChange = mutations.some((mutation) => {
                if (mutation.type === 'attributes') {
                    const attributeName = mutation.attributeName;
                    return attributeName === 'data-theme' || attributeName === 'style';
                }
                return false;
            });

            if (hasRelevantChange) {
                console.log('document observer got style change!');
                updateThemeValues();
            }
        });

        // 开始观察 document.documentElement 的属性变化
        observerRef.current.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme', 'style'],
        });

        // 初始化时也更新一次
        updateThemeValues();

        return () => {
            if (observerRef.current) {
                observerRef.current.disconnect();
                observerRef.current = null;
            }
        };
    }, [updateThemeValues]);

    return <ThemeContext.Provider value={{ color, style }}>{children}</ThemeContext.Provider>;
}
