import { BarChartOutlined, StockOutlined } from '@ant-design/icons';
import { useLocation, useOutlet } from 'react-router';

import { HistoryIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function TeamLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname: loc } = useLocation();

    if (!info.user || !info.team || !info.team.gaming || !info.game.isGameBegin) return <NotFound />;

    const items = [
        {
            type: 'link',
            label: '注意力变动记录',
            key: '/team/ap-history',
            icon: <StockOutlined />,
        },
        {
            type: 'link',
            label: '队伍提交记录',
            key: '/team/submission-history',
            icon: <HistoryIcon />,
        },
        {
            type: 'link',
            label: '题目数据统计',
            key: '/team/puzzle-statistics',
            icon: <BarChartOutlined />,
        },
    ];

    return (
        <div className={'slim-container'}>
            <TabsNavbar items={items} selectedKeys={[loc]} />
            <br />
            {outlet}
        </div>
    );
}
