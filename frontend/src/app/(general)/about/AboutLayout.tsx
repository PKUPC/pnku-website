import { useLocation, useOutlet } from 'react-router-dom';

import { FaqIcon, IntroductionIcon, ToolsIcon } from '@/SvgIcons';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';

export function AboutLayout() {
    const { pathname: loc } = useLocation();
    const outlet = useOutlet();

    const items = [
        {
            type: 'link',
            label: '游戏简介',
            key: '/about/introduction',
            icon: <IntroductionIcon />,
        },
        {
            type: 'link',
            label: '常见问题',
            key: '/about/faq',
            icon: <FaqIcon />,
        },
        {
            type: 'link',
            label: '常用工具',
            key: '/about/tools',
            icon: <ToolsIcon />,
        },
    ];

    return (
        <>
            <div className={'slim-container'}>
                <TabsNavbar items={items} selectedKeys={[loc]} />
                <br />
                {outlet}
            </div>
        </>
    );
}
