import { Alert } from 'antd';

import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { Wish } from '@/types/wish.ts';
import { format_ts_to_HMS } from '@/utils.ts';

type TableItem = Wish.Game.SpeedRunBoardItem & {
    areaName: string;
    puzzleCount: number;
    puzzleIndex: number;
};

function NameAndTime({ team_name, time_cost }: { team_name: string; time_cost: number }) {
    return (
        <div>
            <b>{team_name}</b>
            <br />
            <div style={{ opacity: 0.8 }}>用时 {format_ts_to_HMS(time_cost)}</div>
        </div>
    );
}

export function SpeedRunBoard({ data }: { data: Wish.Game.SpeedRunBoard }) {
    const displayData = data.areas.flatMap((area) =>
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
            className: 'w-[6.4rem] xl:w-[10rem] align-top',
            render: (text) => (
                <div className="text-[1rem] inline">
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
            title: '第一',
            dataIndex: 'first',
            render: (text) =>
                text === null || text === undefined ? (
                    '---'
                ) : (
                    <NameAndTime time_cost={text.time_cost} team_name={text.team_name} />
                ),
        },
        {
            title: '第二',
            dataIndex: 'second',
            render: (text) =>
                text === null || text === undefined ? (
                    '---'
                ) : (
                    <NameAndTime time_cost={text.time_cost} team_name={text.team_name} />
                ),
        },
        {
            title: '第三',
            dataIndex: 'third',
            render: (text) =>
                text === null || text === undefined ? (
                    '---'
                ) : (
                    <NameAndTime time_cost={text.time_cost} team_name={text.team_name} />
                ),
        },
    ];

    return (
        <div>
            {data.desc && (
                <>
                    <Alert showIcon={true} message={data.desc} />
                    <br />
                </>
            )}
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
