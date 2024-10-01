import { ReactNode, useCallback, useLayoutEffect, useState } from 'react';

import { WindowInfoContext } from '@/logic/contexts.ts';

export function WindowInfoContextProvider({ children }: { children: ReactNode }) {
    const [documentWidth, setDocumentWidth] = useState(document.documentElement.clientWidth);
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);
    const [viewportHeight, setViewportHeight] = useState(window.innerHeight * 0.01);
    const [hasScrollbar, setHasScrollbar] = useState(false);
    const [scrollbarWidth, setScrollbarWidth] = useState(0);

    const updateWindowInfo = useCallback(() => {
        console.log('calling updateWindowInfo');
        console.log([window.innerWidth, document.documentElement.clientWidth]);
        const currentScrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        if (currentScrollbarWidth != scrollbarWidth) {
            setScrollbarWidth(currentScrollbarWidth);
            setHasScrollbar(currentScrollbarWidth > 1e-7);
        }
        if (document.documentElement.clientWidth != documentWidth)
            setDocumentWidth(document.documentElement.clientWidth);
    }, [documentWidth, scrollbarWidth]);

    useLayoutEffect(() => {
        const handleResize = () => {
            if (document.documentElement.clientWidth != documentWidth)
                setDocumentWidth(document.documentElement.clientWidth);
            if (window.innerWidth != windowWidth) setWindowWidth(window.innerWidth);
        };
        setDocumentWidth(document.documentElement.clientWidth);
        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [documentWidth, windowWidth]);

    useLayoutEffect(() => {
        const setFullVisibleHeight = () => {
            if (window.innerHeight != viewportHeight) {
                setViewportHeight(window.innerHeight);
            }
            const vh = window.innerHeight * 0.01;
            document.body.style.setProperty('--vh', `${vh}px`);
            document.body.style.setProperty('--full-vh', `${window.innerHeight}px`);
        };
        setFullVisibleHeight();
        window.addEventListener('resize', setFullVisibleHeight);
        return () => {
            window.removeEventListener('resize', setFullVisibleHeight);
        };
    }, [viewportHeight]);

    useLayoutEffect(() => {
        updateWindowInfo();
        window.addEventListener('resize', updateWindowInfo);
        return () => {
            window.removeEventListener('resize', updateWindowInfo);
        };
    }, [updateWindowInfo]);

    console.log([viewportHeight, documentWidth, hasScrollbar, scrollbarWidth]);

    return (
        <WindowInfoContext.Provider
            value={{
                viewportHeight,
                documentWidth,
                windowWidth,
                hasScrollbar,
                scrollbarWidth,
                updateWindowInfo,
            }}
        >
            {children}
        </WindowInfoContext.Provider>
    );
}
