import { Navigate, useLocation, useOutlet, useParams } from 'react-router';

import NotFound from '@/app/NotFound.tsx';
import NamedIcon from '@/components/NamedIcon';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

function BoardLayoutBody() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const params = useParams();
    const curKey = params.boardName;
    const { pathname } = useLocation();

    if (!curKey || !info.game.boards.map((item) => item.key).includes(curKey))
        if (info.game.boards.length > 0) return <Navigate to={`/boards/${info.game.boards[0].key}`} replace={true} />;
        else return <NotFound />;

    const items = info.game.boards.map((item) => ({
        label: item.name,
        key: `/boards/${item.key}`,
        icon: <NamedIcon iconName={item.icon} />,
    }));

    return (
        <div>
            <TabsNavbar items={items} selectedKeys={[pathname]} />
            <br />
            {outlet}
        </div>
    );
}

export function BoardLayout() {
    const info = useSuccessGameInfo();
    // 只有游戏正式开始后以及队伍开始游戏后才可见
    if (ARCHIVE_MODE) {
        /* empty */
    } else if (!info.user || (info.user.group !== 'staff' && (!info.game.isPrologueUnlock || !info.team?.gaming)))
        return <NotFound />;
    return <BoardLayoutBody />;
}
