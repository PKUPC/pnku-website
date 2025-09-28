import { BarChartOutlined } from '@ant-design/icons';
import { useLocation, useOutlet, useSearchParams } from 'react-router-dom';

import { HistoryIcon } from '@/SvgIcons';
import NotFound from '@/app/NotFound.tsx';
import NamedIcon from '@/components/NamedIcon';
import { TabsNavbar } from '@/components/TabsNavbar.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

export function TeamLayout() {
    const outlet = useOutlet();
    const info = useSuccessGameInfo();
    const { pathname: loc } = useLocation();
    const [params] = useSearchParams();

    if (!info.user || !info.team || !info.team.gaming || !info.game.isGameBegin) return <NotFound />;

    const items = [
        {
            type: 'link',
            label: '队伍提交记录',
            key: '/team/submission-history',
            icon: <HistoryIcon />,
        },
        ...info.game.currencies.map((currency) => ({
            type: 'link',
            label: `${currency.name}变动记录`,
            key: `/team/currency-history?type=${currency.type}`,
            icon: <NamedIcon iconName={currency.icon} />,
        })),
        {
            type: 'link',
            label: '题目数据统计',
            key: '/team/puzzle-statistics',
            icon: <BarChartOutlined />,
        },
    ];

    const selectedKey = loc !== '/team/currency-history' ? loc : loc + '?type=' + (params.get('type') ?? '');

    return (
        <div className={'slim-container'}>
            <TabsNavbar items={items} selectedKeys={[selectedKey]} />
            <br />
            {outlet}
        </div>
    );
}
