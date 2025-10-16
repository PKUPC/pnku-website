import { ExceptionOutlined, TeamOutlined } from '@ant-design/icons';
import { useLocation, useOutlet } from 'react-router';

import { HistoryIcon } from '@/SvgIcons';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';

export function StaffMenuLayout() {
    const outlet = useOutlet();

    const { pathname: loc } = useLocation();

    const items = [
        {
            label: '队伍列表',
            key: '/staff/teams',
            icon: <TeamOutlined />,
        },
        {
            label: '提交列表',
            key: '/staff/submissions',
            icon: <HistoryIcon />,
        },
        {
            label: '工单列表',
            key: '/staff/tickets',
            icon: <ExceptionOutlined />,
        },
    ];

    return (
        <div style={{ maxWidth: 1200, margin: 'auto' }}>
            <TabsNavbar items={items} selectedKeys={[loc]} />
            <br />
            {outlet}
        </div>
    );
}
