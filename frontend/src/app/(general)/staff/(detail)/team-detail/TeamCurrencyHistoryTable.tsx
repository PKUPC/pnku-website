import FancyCard from '@/components/FancyCard';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import styles from './TeamCurrencyHistoryTable.module.css';

export function TeamCurrencyHistoryTable({ currencyDetail }: { currencyDetail: Wish.Staff.StaffTeamDetailCurrency }) {
    const columns: TableColumnsType<Wish.Staff.StaffTeamDetailCurrencyHistory> = [
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
        { title: '备注', dataIndex: 'info' },
    ];
    const data = currencyDetail.history.slice().reverse();
    return (
        <div className={styles.teamCurrencyHistoryTable}>
            <FancyCard title={`队伍${currencyDetail.name}变动记录`}>
                <Table
                    size="small"
                    dataSource={data}
                    rowKey="timestamp_s"
                    scroll={{
                        x: 'max-content',
                    }}
                    columns={columns}
                />
            </FancyCard>
        </div>
    );
}
