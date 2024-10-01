import { InfoCircleTwoTone } from '@ant-design/icons';
import { Tooltip } from 'antd';

import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { useSuccessGameInfo, useTheme } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

export function SubmissionList({ puzzleKey }: { puzzleKey: string }) {
    const { color } = useTheme();
    const { data } = useWishData({
        endpoint: 'puzzle/get_submissions',
        payload: {
            puzzle_key: puzzleKey,
        },
    });
    const info = useSuccessGameInfo();

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    const columns: TableColumnsType<Wish.Puzzle.SubmissionRecordData> = [
        {
            title: '提交时间',
            dataIndex: 'timestamp_s',
            render: (text) => format_ts(text),
        },
        { title: '提交人', dataIndex: 'user_name' },
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
        { title: '状态', dataIndex: 'status' },
        { title: '信息', dataIndex: 'info' },
    ];
    if (!!info.user && info.user.group === 'staff') columns.splice(1, 0, { title: '队伍', dataIndex: 'team_name' });

    return (
        <>
            {/*<h1>提交历史记录</h1>*/}
            <Table<Wish.Puzzle.SubmissionRecordData>
                size="small"
                dataSource={data.submissions}
                rowKey="idx"
                scroll={{
                    x: 'max-content',
                }}
                columns={columns}
            />
        </>
    );
}
