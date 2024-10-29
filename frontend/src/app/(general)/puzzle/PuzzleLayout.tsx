import { useOutlet } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function PuzzleLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!info.user) return <NotFound />;
    else if (info.user.group !== 'staff' && (!info.game.isGameBegin || !info.team?.gaming)) return <NotFound />;

    return outlet;
}
