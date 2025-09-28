import { Navigate, useOutlet, useSearchParams } from 'react-router-dom';

import NotFound from '@/app/NotFound.tsx';
import NamedIcon from '@/components/NamedIcon';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

function BoardLayoutBody() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const [searchParams] = useSearchParams();
    const cur_key = searchParams.get('key');

    console.log(cur_key);

    if (!cur_key || !info.game.boards.map((item) => item.key).includes(cur_key))
        if (info.game.boards.length > 0)
            return <Navigate to={`/boards?key=${info.game.boards[0].key}`} replace={true} />;
        else return <NotFound />;

    const items = info.game.boards.map((item) => ({
        type: 'link',
        href: `/boards?key=${item.key}`,
        label: item.name,
        key: item.key,
        icon: <NamedIcon iconName={item.icon} />,
    }));

    return (
        <div>
            <TabsNavbar items={items} selectedKeys={[cur_key ?? 'NONE']} />
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
