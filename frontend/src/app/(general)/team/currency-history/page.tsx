import { Alert } from 'antd';
import { useSearchParams } from 'react-router';

import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { NeverError } from '@/errors';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { Adhoc, Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

function CurrencyChangeHistory({ currencyType }: { currencyType: Adhoc.CurrencyType }) {
    const { data } = useWishData({
        endpoint: 'team/get_currency_change_history',
        payload: { currency_type: currencyType as Adhoc.CurrencyType },
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    const columns: TableColumnsType<Wish.Team.TeamCurrencyHistorySingleRecord> = [
        { title: '时间', dataIndex: 'timestamp_s', render: (text) => format_ts(text) },
        {
            title: '变动',
            dataIndex: 'change',
            render: (text) => {
                if (text > 0) return '+' + text;
                else if (text < 0) return text;
                else return '--';
            },
        },
        { title: '随时间增长', dataIndex: 'time_based_change' },
        { title: '当前余额', dataIndex: 'current' },
        { title: '备注', dataIndex: 'info' },
    ];

    return (
        <>
            <Table
                size="small"
                dataSource={data.history.slice().reverse()}
                rowKey="timestamp_s"
                scroll={{
                    x: 'max-content',
                }}
                style={{ marginTop: '16px' }}
                pagination={{
                    defaultPageSize: 20,
                    showQuickJumper: true,
                }}
                columns={columns}
            />
        </>
    );
}

export function CurrencyHistoryPage() {
    const info = useSuccessGameInfo();
    const [params] = useSearchParams();
    const currencyType = params.get('type');

    if (info.status !== 'success' || !info.user) throw new NeverError();

    if (!info.team) {
        return <Alert type="error" showIcon message="无队伍" description="请先创建或加入队伍" />;
    }

    const hasCurrencyType = info.game.currencies.some((currency) => currency.type === currencyType);
    if (!hasCurrencyType) return <NotFound />;

    return (
        <>
            <CurrencyChangeHistory currencyType={currencyType as Adhoc.CurrencyType} />
        </>
    );
}
