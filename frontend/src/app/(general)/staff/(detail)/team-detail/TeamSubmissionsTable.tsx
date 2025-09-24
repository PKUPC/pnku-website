import { InfoCircleTwoTone } from '@ant-design/icons';
import { Tooltip } from 'antd';

import FancyCard from '@/components/FancyCard';
import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { useTheme } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

import styles from './TeamSubmissionTable.module.css';

type StaffTeamDetailSubmission = Wish.Staff.StaffTeamDetailSubmission;

export function TeamSubmissionsTable({ data }: { data: StaffTeamDetailSubmission[] }) {
    const { color } = useTheme();

    const submissionColumns: TableColumnsType<StaffTeamDetailSubmission> = [
        {
            title: '提交时间',
            key: 'timestamp_s',
            dataIndex: 'timestamp_s',
            render: (text) => format_ts(text),
        },
        {
            title: '题目',
            key: 'puzzle',
            dataIndex: 'puzzle',
        },
        {
            title: '提交人',
            key: 'user_name',
            dataIndex: 'user_name',
        },
        {
            title: (
                <Tooltip title={'鼠标悬停查看忽略无关字符后的结果'}>
                    提交内容{' '}
                    <InfoCircleTwoTone twoToneColor={[color.warning, color.base100]} className="icon-with-chinese" />
                </Tooltip>
            ),
            key: 'origin',
            dataIndex: 'origin',
            render: (text, record) => <Tooltip title={record.cleaned}>{text}</Tooltip>,
        },
        {
            title: '状态',
            key: 'status',
            dataIndex: 'status',
        },
        {
            title: '信息',
            key: 'info',
            dataIndex: 'info',
        },
    ];
    return (
        <>
            <div className={styles.teamSubmissionTable}>
                <FancyCard title="队伍提交记录">
                    <Table
                        className={'team-detail-submission-table'}
                        size="small"
                        columns={submissionColumns}
                        dataSource={data}
                        rowKey="idx"
                        scroll={{
                            x: 'max-content',
                        }}
                    />
                </FancyCard>
            </div>
        </>
    );
}
