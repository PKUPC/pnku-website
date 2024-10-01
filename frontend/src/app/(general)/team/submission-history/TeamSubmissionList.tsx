import { InfoCircleTwoTone } from '@ant-design/icons';
import { Tooltip } from 'antd';

import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { useTheme } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

export function TeamSubmissionList({ submissions }: { submissions: Wish.Team.TeamSubmissionInfo[] }) {
    const puzzleTitles = Array.from(new Set(submissions.map((item) => item.puzzle)));
    const puzzleFilters = puzzleTitles.map((item) => ({ text: item, value: item }));
    const users = Array.from(new Set(submissions.map((item) => item.user_name)));
    const userFilters = users.map((item) => ({ text: item, value: item }));
    const subStatus = Array.from(new Set(submissions.map((item) => item.status)));
    const subStatusFilters = subStatus.map((item) => ({ text: item, value: item }));
    const { color } = useTheme();

    const columns: TableColumnsType<Wish.Team.TeamSubmissionInfo> = [
        {
            title: '提交时间',
            dataIndex: 'timestamp_s',
            render: (text) => format_ts(text),
            sorter: (a, b) => a.timestamp_s - b.timestamp_s,
        },
        {
            title: '题目',
            dataIndex: 'puzzle',
            filters: puzzleFilters,
            onFilter: (value, record) => record.puzzle === value,
        },
        {
            title: '提交人',
            dataIndex: 'user_name',
            filters: userFilters,
            onFilter: (value, record) => record.user_name === value,
        },
        {
            title: (
                <Tooltip title={'鼠标悬停查看忽略无关字符后的结果'}>
                    <span>提交内容</span>&nbsp;
                    <InfoCircleTwoTone twoToneColor={[color.warning, color.base100]} className="icon-with-chinese" />
                </Tooltip>
            ),
            dataIndex: 'origin',
            render: (text, record) => <Tooltip title={record.cleaned}>{text}</Tooltip>,
        },
        {
            title: '状态',
            dataIndex: 'status',
            filters: subStatusFilters,
            onFilter: (value, record) => record.status === value,
        },
        { title: '信息', dataIndex: 'info' },
    ];

    return (
        <>
            {/*<h1>提交历史记录</h1>*/}
            <Table<Wish.Team.TeamSubmissionInfo>
                size="small"
                dataSource={submissions}
                rowKey="idx"
                scroll={{
                    x: 'max-content',
                }}
                columns={columns}
                pagination={{
                    defaultPageSize: 20,
                    showQuickJumper: true,
                }}
            />
        </>
    );
}
