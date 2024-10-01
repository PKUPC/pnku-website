import { RefObject, useRef, useState } from 'react';

export function useReloadButton(interval_s: number): [number, () => void, RefObject<HTMLButtonElement>] {
    const [lastReloadedMs, setLastReloadedMs] = useState(+new Date());
    const reloadButtonRef = useRef<HTMLButtonElement>(null);

    function markReload() {
        if (reloadButtonRef.current) reloadButtonRef.current.disabled = true;
        setLastReloadedMs(+new Date());

        setTimeout(() => {
            if (+new Date() - lastReloadedMs >= interval_s * 1000 - 200)
                if (reloadButtonRef.current) reloadButtonRef.current.disabled = false;
        }, interval_s * 1000);
    }

    return [lastReloadedMs / 1000, markReload, reloadButtonRef];
}
