import FancyCard from '@/components/FancyCard';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import styles from './TeamPassedPuzzleTable.module.css';

type StaffTeamDetailPassedPuzzles = Wish.Staff.StaffTeamDetailPassedPuzzles;

export function TeamPassedPuzzleTable({ data }: { data: StaffTeamDetailPassedPuzzles[] }) {
    const columns: TableColumnsType<StaffTeamDetailPassedPuzzles> = [
        { title: '时间', dataIndex: 'timestamp_s', render: (text) => format_ts(text) },
        { title: '标题', dataIndex: 'title' },
    ];

    return (
        <div className={styles.teamPassedPuzzleTable}>
            <FancyCard title="队伍通过题目">
                <Table
                    size="small"
                    dataSource={data.sort((a, b) => b.timestamp_s - a.timestamp_s)}
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
