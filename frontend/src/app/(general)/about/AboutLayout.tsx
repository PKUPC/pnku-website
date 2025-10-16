import { useLocation, useOutlet } from 'react-router';

import { FaqIcon, IntroductionIcon, ToolsIcon } from '@/SvgIcons';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';

export function AboutLayout() {
    const { pathname: loc } = useLocation();
    const outlet = useOutlet();

    const items = [
        {
            label: '游戏简介',
            key: '/about/introduction',
            icon: <IntroductionIcon />,
        },
        {
            label: '常见问题',
            key: '/about/faq',
            icon: <FaqIcon />,
        },
        {
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
