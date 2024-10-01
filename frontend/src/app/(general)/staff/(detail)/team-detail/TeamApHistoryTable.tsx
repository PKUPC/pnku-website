import FancyCard from '@/components/FancyCard';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ms } from '@/utils.ts';

import styles from './TeamApHistoryTable.module.scss';

export function TeamApHistoryTable({ history }: { history: Wish.Staff.StaffTeamDetailApChangeHistory[] }) {
    const columns: TableColumnsType<Wish.Staff.StaffTeamDetailApChangeHistory> = [
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
        { title: '备注', dataIndex: 'info' },
    ];
    return (
        <div className={styles.teamApHistoryTable}>
            <FancyCard title="队伍注意力变动记录">
                <Table
                    size="small"
                    dataSource={history.reverse()}
                    rowKey="timestamp_ms"
                    scroll={{
                        x: 'max-content',
                    }}
                    columns={columns}
                />
            </FancyCard>
        </div>
    );
}
