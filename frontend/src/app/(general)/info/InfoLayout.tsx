import { CarryOutOutlined, NotificationOutlined } from '@ant-design/icons';
import { useMemo } from 'react';
import { useLocation, useOutlet } from 'react-router';

import { MailIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

function InfoLayoutBody() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname: loc } = useLocation();

    const items = useMemo(() => {
        let items = [
            {
                key: '/info/announcements',
                label: '比赛公告',
                icon: <NotificationOutlined />,
            },
            {
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
                key: '/info/message',
                label: '站内信',
                icon: <MailIcon />,
            });
        }
        return items;
    }, [info]);

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
