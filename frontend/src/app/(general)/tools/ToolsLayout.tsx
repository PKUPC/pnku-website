import { CloudUploadOutlined } from '@ant-design/icons';
import { useLocation, useNavigate, useOutlet } from 'react-router-dom';

import { LeftCircleIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { ClickTitle } from '@/components/LinkTitle';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function ToolsLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();

    const { pathname: loc } = useLocation();
    const navigate = useNavigate();

    if (import.meta.env.VITE_ARCHIVE_MODE === 'true' || !info.user) return <NotFound />;

    const items = [
        {
            type: 'link',
            label: '图片上传',
            key: '/tools/upload-image',
            icon: <CloudUploadOutlined />,
        },
    ];

    return (
        <div className={'slim-container'}>
            <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
            <TabsNavbar items={items} selectedKeys={[loc]} />
            <br />
            {outlet}
        </div>
    );
}
