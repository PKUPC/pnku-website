import { Alert } from 'antd';

import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { NeverError } from '@/errors';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { Wish } from '@/types/wish.ts';
import { format_ms } from '@/utils.ts';

function ApChangeHistory() {
    const { data } = useWishData({
        endpoint: 'team/get_ap_change_history',
        payload: undefined,
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    const columns: TableColumnsType<Wish.Team.TeamApHistorySingleRecord> = [
        { title: '时间', dataIndex: 'timestamp_ms', render: (text) => format_ms(text) },
        {
            title: '变动',
            dataIndex: 'change',
            render: (text) => {
                if (text > 0) return '+' + text;
                else if (text < 0) return text;
                else return '--';
            },
        },
        { title: '变动后数量', dataIndex: 'cur_ap' },
        { title: '备注', dataIndex: 'info' },
    ];

    return (
        <>
            {/*<h1>注意力变动记录</h1>*/}
            <Table
                size="small"
                dataSource={data.history.reverse()}
                rowKey="timestamp_ms"
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

export function ApHistoryPage() {
    const info = useSuccessGameInfo();

    if (info.status !== 'success' || !info.user) throw new NeverError();

    if (!info.team) {
        return <Alert type="error" showIcon message="无队伍" description="请先创建或加入队伍" />;
    }

    return (
        <>
            <ApChangeHistory />
        </>
    );
}
