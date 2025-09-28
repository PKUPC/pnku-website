import { CheckCircleTwoTone, ExclamationCircleTwoTone, SyncOutlined } from '@ant-design/icons';
import { Button, Space, Switch, message } from 'antd';
import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';

import { TableLoader as Table, type TableColumnsType } from '@/components/lazy/TableLoader';
import { useReloadButton } from '@/hooks/useReloadButton';
import { GameStatusContext, useTheme } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';

type TeamInfoStaff = Wish.Staff.TeamInfoStaff;

export function TeamTable({ teamIntoList, reload }: { teamIntoList: TeamInfoStaff[]; reload: () => void }) {
    const navigate = useNavigate();
    const { staffUnreadOnly, setStaffUnreadOnly, staffTimeDesc, setStaffTimeDesc } = useContext(GameStatusContext);
    const [_lastReload, markReload, reloadButtonRef] = useReloadButton(3);
    const [messageApi, contextHolder] = message.useMessage();
    const { color } = useTheme();

    const columns: TableColumnsType<TeamInfoStaff> = [
        { title: 'id', dataIndex: 'team_id', key: 'team_id' },
        {
            title: '队名',
            dataIndex: 'team_name',
            key: 'team_name',
            filters: teamIntoList.map((item) => ({
                text: `[${item.team_id}]${item.team_name}`,
                value: item.team_name,
            })),
            onFilter: (value, record) => (value as string) === record.team_name,
            filterSearch: true,
        },
        {
            title: '最后一次消息',
            dataIndex: 'last_msg_ts',
            key: 'last_msg_ts',
            render: (t: number, record) => {
                return (
                    <span>
                        {record.unread ? (
                            <ExclamationCircleTwoTone twoToneColor={[color.error, color.base100]} />
                        ) : (
                            <CheckCircleTwoTone twoToneColor={[color.success, color.base100]} />
                        )}
                        &nbsp;&nbsp;
                        {t === null ? '---' : new Date(t * 1000).toLocaleString()}
                    </span>
                );
            },
        },
        {
            title: '操作',
            key: 'action',
            render: (_: undefined, record) => {
                return (
                    <Space.Compact>
                        <Button onClick={() => navigate(`/staff/message?tid=${record.team_id}`)}>回复站内信</Button>
                        <Button onClick={() => navigate(`/staff/team-detail?tid=${record.team_id}`)}>队伍详情</Button>
                    </Space.Compact>
                );
            },
        },
    ];

    return (
        <div>
            {contextHolder}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <div>
                    <span style={{ display: 'flex', alignItems: 'center' }}>
                        &nbsp;仅显示未回复信息：
                        <Switch
                            defaultChecked={staffUnreadOnly}
                            onChange={() => setStaffUnreadOnly(!staffUnreadOnly)}
                        />
                        <>
                            &nbsp;&nbsp;&nbsp;时间降序：
                            <Switch defaultChecked={staffTimeDesc} onChange={() => setStaffTimeDesc(!staffTimeDesc)} />
                        </>
                    </span>
                </div>

                <Button
                    type="link"
                    ref={reloadButtonRef}
                    onClick={() => {
                        messageApi.success({ content: '已刷新', key: 'TeamManage.LoadData', duration: 1 }).then();
                        markReload();
                        reload();
                    }}
                >
                    <SyncOutlined /> 刷新
                </Button>
            </div>

            <Table
                size="small"
                bordered
                columns={columns}
                scroll={{
                    x: 'max-content',
                }}
                dataSource={teamIntoList
                    .sort(staffTimeDesc ? (a, b) => b.last_msg_ts - a.last_msg_ts : (a, b) => a.team_id - b.team_id)
                    .filter((v) => (staffUnreadOnly ? v.unread : true))
                    .map((v) => {
                        return {
                            key: v.team_id,
                            ...v,
                        };
                    })}
            />
        </div>
    );
}
