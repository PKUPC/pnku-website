import { useEffect, useState } from 'react';

export function useCooldown(targetTs: number): [boolean, number] {
    const [cooling, setCooling] = useState(new Date().getTime() / 1000 < targetTs);
    const [countdown, setCountdown] = useState(0);

    useEffect(() => {
        const update = () => {
            if (!cooling) return;
            const currentSeconds = Math.floor(new Date().getTime() / 1000);
            if (currentSeconds > targetTs) setCooling(false);
            else setCountdown(targetTs - currentSeconds);
        };
        update();
        const intervalId = setInterval(update, 1000);
        return () => clearInterval(intervalId);
    }, [cooling, targetTs]);

    useEffect(() => {
        if (targetTs && new Date().getTime() / 1000 < targetTs) setCooling(true);
    }, [targetTs]);
    return [cooling, countdown];
}
