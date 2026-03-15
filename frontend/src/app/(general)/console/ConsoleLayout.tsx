import { FileTextOutlined, UserOutlined } from '@ant-design/icons';
import { useLocation, useOutlet } from 'react-router';

import NotFound from '@/app/NotFound.tsx';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function ConsoleLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();

    const { pathname } = useLocation();

    if (ARCHIVE_MODE) return <NotFound />;
    if (!info.user || info.user.admin !== true) return <NotFound />;

    const items = [
        {
            label: '用户管理',
            key: '/console/user',
            icon: <UserOutlined />,
        },
        {
            label: '管理员文档',
            key: '/console/document',
            icon: <FileTextOutlined />,
        },
    ];

    return (
        <div className={'slim-container'}>
            <TabsNavbar items={items} selectedKeys={[pathname]} />
            <br />
            {outlet}
        </div>
    );
}
