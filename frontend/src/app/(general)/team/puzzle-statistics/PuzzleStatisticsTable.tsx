import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts, format_ts_to_HMS } from '@/utils.ts';

import styles from './PuzzleStatisticsTable.module.css';

type TableItem = Wish.Team.TeamPuzzleStatisticsItem & {
    areaName: string;
    puzzleCount: number;
    puzzleIndex: number;
};

export function PuzzleStatisticsTable({ data }: { data: Wish.Team.TeamPuzzleStatisticsAreaItem[] }) {
    const displayData = data.flatMap((area) =>
        area.puzzles.map((puzzle, idx) => ({
            ...puzzle,
            areaName: area.name,
            puzzleCount: area.puzzles.length,
            puzzleIndex: idx,
        })),
    );

    const columns: TableColumnsType<TableItem> = [
        {
            title: '区域',
            dataIndex: 'areaName',
            className: styles.areaTd,
            render: (text) => (
                <div className={styles.areaTitle}>
                    <b>{text}</b>
                </div>
            ),
            onCell: (record: TableItem) => {
                return {
                    rowSpan: record.puzzleIndex === 0 ? record.puzzleCount : 0,
                };
            },
        },
        { title: '题目', dataIndex: 'title', render: (text) => <b>{text}</b> },
        {
            title: '解锁时间',
            dataIndex: 'unlock_ts',
            render: (text) => (text === null ? null : format_ts(text)),
        },
        {
            title: '通过时间',
            dataIndex: 'passed_ts',
            render: (text) => (text === null || text === undefined ? '---' : format_ts(text)),
        },
        {
            title: '花费时间',
            dataIndex: 'time_cost',
            render: (text) => (text === null || text === undefined ? '---' : format_ts_to_HMS(text)),
        },
        {
            title: '错误/里程碑/正确',
            key: 'submission_count',
            render: (_, record) => (
                <span>
                    {record.wrong} / {record.milestone} / {record.pass}
                </span>
            ),
        },
    ];

    return (
        <div className={styles.puzzleStatisticsTable}>
            <Table<TableItem>
                size="small"
                dataSource={displayData}
                pagination={false}
                rowKey="key"
                scroll={{
                    x: 'max-content',
                }}
                columns={columns}
            />
        </div>
    );
}
