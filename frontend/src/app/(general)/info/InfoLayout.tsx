import { CarryOutOutlined, NotificationOutlined } from '@ant-design/icons';
import { useLocation, useOutlet } from 'react-router-dom';

import { MailIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

function InfoLayoutBody() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname: loc } = useLocation();

    const items = [
        {
            type: 'link',
            key: '/info/announcements',
            label: '比赛公告',
            icon: <NotificationOutlined />,
        },
        {
            type: 'link',
            key: '/info/schedule',
            label: '赛程安排',
            icon: <CarryOutOutlined />,
        },
    ];

    // 序章开放后并且组队了并且不是 playground 模式
    if (
        !ARCHIVE_MODE &&
        info.user &&
        info.user.group !== 'staff' &&
        info.team &&
        info.game.isPrologueUnlock &&
        !info.feature.playground
    ) {
        items.push({
            type: 'link',
            key: '/info/message',
            label: '站内信',
            icon: <MailIcon />,
        });
    }

    return (
        <div className={'slim-container'}>
            <TabsNavbar items={items} selectedKeys={[loc]} />
            <br />
            {outlet}
        </div>
    );
}

export function InfoLayout() {
    const info = useSuccessGameInfo();
    if (!ARCHIVE_MODE && !info.user) return <NotFound />;
    return <InfoLayoutBody />;
}
