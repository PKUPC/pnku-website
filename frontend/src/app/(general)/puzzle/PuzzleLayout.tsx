import { useLocation, useOutlet } from 'react-router';

import NotFound from '@/app/NotFound.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function PuzzleLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname } = useLocation();
    const isPublicPage = pathname.startsWith('/puzzle/public/');

    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!info.user) return <NotFound />;
    else if (info.user.group !== 'staff' && !isPublicPage && (!info.game.isGameBegin || !info.team?.gaming))
        return <NotFound />;

    return outlet;
}
