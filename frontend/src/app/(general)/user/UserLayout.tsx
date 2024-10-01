import { LockOutlined } from '@ant-design/icons';
import { redirect, useLocation, useOutlet } from 'react-router-dom';

import { EveryUserIcon, IdCardIcon } from '@/SvgIcons';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export default function UserLayout() {
    const info = useSuccessGameInfo();
    if (!info.user) redirect('/login');

    const outlet = useOutlet();
    const { pathname: loc } = useLocation();

    const items = [];

    items.push({
        type: 'link',
        label: '个人资料',
        key: '/user/profile',
        icon: <IdCardIcon />,
    });

    items.push({
        type: 'link',
        label: '队伍信息',
        key: '/user/team',
        icon: <EveryUserIcon />,
    });

    items.push({
        type: 'link',
        label: '安全设置',
        key: '/user/security',
        icon: <LockOutlined />,
    });

    return (
        <div className={'slim-container'}>
            <TabsNavbar items={items} selectedKeys={[loc]} />
            <br />
            {outlet}
        </div>
    );
}
