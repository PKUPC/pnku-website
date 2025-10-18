import { BarChartOutlined } from '@ant-design/icons';
import { useLocation, useOutlet } from 'react-router';

import { HistoryIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import NamedIcon from '@/components/NamedIcon';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function TeamLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname } = useLocation();
    if (!info.user || !info.team || !info.team.gaming || !info.game.isGameBegin) return <NotFound />;

    const items = [
        {
            label: '队伍提交记录',
            key: '/team/submission-history',
            icon: <HistoryIcon />,
        },
        ...info.game.currencies.map((currency) => ({
            label: `${currency.name}变动记录`,
            key: `/team/currency-history/${currency.type}`,
            icon: <NamedIcon iconName={currency.icon} />,
        })),
        {
            label: '题目数据统计',
            key: '/team/puzzle-statistics',
            icon: <BarChartOutlined />,
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
