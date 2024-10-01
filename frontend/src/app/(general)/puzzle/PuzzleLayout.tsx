import { useOutlet } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function PuzzleLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true') {
        /* empty */
    } else if (!info.user) return <NotFound />;
    else if (info.user.group !== 'staff' && (!info.game.isGameBegin || !info.team?.gaming)) return <NotFound />;

    return outlet;
}
