import { LockOutlined } from '@ant-design/icons';
import { Tooltip } from 'antd';

import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

type TableItem = Wish.Game.FirstBloodItem & {
    area_title: string;
    puzzle_count: number;
    puzzle_idx0: number;
};

function UserName({ name }: { name: string }) {
    const idx = name.indexOf(' #');
    if (idx <= 0) return <span className="name-base-part">{name}</span>;
    else {
        const basename = name.substring(0, idx);
        const tag = name.substring(idx);
        return (
            <>
                <span className="name-base-part">{basename}</span>
                <span className="name-tag-part">{tag}</span>
            </>
        );
    }
}

export function FirstBloodBoard({ data }: { data: Wish.Game.FirstBloodBoard }) {
    const displayData = data.list.flatMap((area) =>
        area.list.map((puzzle, idx) => ({
            ...puzzle,
            area_title: area.name,
            puzzle_count: area.list.length,
            puzzle_idx0: idx,
        })),
    );

    const columns: TableColumnsType<TableItem> = [
        {
            className: 'w-[6.4rem] xl:w-[10rem] align-top',
            title: '区域',
            dataIndex: 'area_title',
            render: (text) => {
                if (text === 'unknown')
                    return (
                        <Tooltip title={'你还没有解锁这个区域'}>
                            <div className="text-[1rem] inline opacity-50">
                                <LockOutlined /> <b>未知区域</b>
                            </div>
                        </Tooltip>
                    );
                return (
                    <div className="inline text-[1rem]">
                        <b>{text}</b>
                    </div>
                );
            },
            onCell: (record) => {
                return {
                    rowSpan: record.puzzle_idx0 === 0 ? record.puzzle_count : 0,
                };
            },
        },
        {
            title: '题目',
            dataIndex: 'title',
            render: (text) => {
                if (text === 'unknown')
                    return (
                        <Tooltip title={'你还没有解锁这个题目'}>
                            <div className={'unknown-title'}>
                                <LockOutlined /> <b>未知题目</b>
                            </div>
                        </Tooltip>
                    );
                return <b>{text}</b>;
            },
        },
        {
            title: '首杀队伍',
            dataIndex: 'team_name',
            render: (_text, record: TableItem) => record.team_name !== null && <UserName name={record.team_name} />,
        },
        {
            title: '首杀时间',
            dataIndex: 'timestamp',
            render: (text) => (text === null ? null : format_ts(text)),
        },
    ];

    return (
        <div>
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
