import { FlagOutlined, WarningOutlined } from '@ant-design/icons';
import { Alert, Button, Tooltip } from 'antd';
import { useContext, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { GeneralTag } from '@/components/GeneralTag.tsx';
import { ProfileAvatar } from '@/components/ProfileAvatar.tsx';
import { WishConfirmModal } from '@/components/WishConfirmModal';
import { InfoError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';

export function TeamMemberForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [modalOpen, setModalOpen] = useState(false);
    const [modalConfig, setModalConfig] = useState<Wish.WishConfirmConfig<Wish.WishConfirmParams> | undefined>(
        undefined,
    );
    if (info.status !== 'success') throw new InfoError();

    if (!info.user || !info.team)
        return <Alert type="error" showIcon message="未登录" description="请登录后查看队伍信息" />;

    const isLeader = info.team && info.team.leader_id === info.user.id;
    const curUserId = info.user.id;
    const leader_id = info.team.leader_id;

    const onRemoveUser = (user_id: number, user_name: string) => {
        return () => {
            setModalConfig({
                wishParam: {
                    endpoint: 'team/remove_user',
                    payload: { user_id: user_id },
                },
                confirmTitle: '操作确认',
                confirmContent: `你确定要移除用户 ${user_name} 吗？\n注意，该操作不可撤销。`,
                onSuccessContentRender: () => '操作成功，点击确定刷新',
                onFinish: (res) => {
                    if (res.status === 'success') {
                        reloadInfo().then();
                    }
                },
            });
            setModalOpen(true);
        };
    };

    const onChangeLeader = (user_id: number, user_name: string) => {
        return () => {
            setModalConfig({
                wishParam: {
                    endpoint: 'team/change_leader',
                    payload: { user_id: user_id },
                },
                confirmTitle: '操作确认',
                confirmContent: `你确定要将队长转移给用户 ${user_name} 吗？\n注意，该操作不可撤销。`,
                onSuccessContentRender: () => '操作成功，点击确定刷新',
                onFinish: (res) => {
                    if (res.status === 'success') {
                        reloadInfo().then();
                    }
                },
            });
            setModalOpen(true);
        };
    };

    const onLeaveTeam = () => {
        const tmp = isLeader ? '解散队伍' : '退出队伍';

        setModalConfig({
            wishParam: {
                endpoint: 'team/leave_team',
            },
            confirmTitle: '操作确认',
            confirmContent: `你确定要${tmp}吗？\n注意，该操作不可撤销。`,
            onSuccessContentRender: () => '操作成功，点击确定刷新',
            onFinish: (res) => {
                if (res.status === 'success') {
                    reloadInfo().then();
                }
            },
        });
        setModalOpen(true);
    };

    const leaderIcon = (
        <Tooltip placement="top" title={'队长'}>
            <FlagOutlined />
        </Tooltip>
    );

    return (
        <div>
            {!!modalConfig && <WishConfirmModal open={modalOpen} setOpen={setModalOpen} {...modalConfig} />}
            <FancyCard title="队伍成员列表">
                <div>
                    {info.team.members.map((item) => (
                        <div key={item.id} className="not-last:border-b-[1px] py-3 px-1 text-sm flex">
                            <div className="flex items-center gap-2 flex-grow">
                                <ProfileAvatar src={item.avatar_url} alt={item.nickname} size={'2rem'} />
                                {item.nickname}
                                {leader_id === item.id && leaderIcon}
                                <GeneralTag color="blue" bordered={false}>{`UID ${item.id}`}</GeneralTag>
                            </div>
                            {isLeader && item.id !== curUserId && info.team?.id !== 0 && (
                                <div className="flex gap-2">
                                    <Button
                                        type={'link'}
                                        style={{ padding: 0 }}
                                        key={'delete-user'}
                                        onClick={onRemoveUser(item.id, item.nickname)}
                                    >
                                        移出队伍
                                    </Button>
                                    <Button
                                        type={'link'}
                                        style={{ padding: 0 }}
                                        key={'change_leader'}
                                        onClick={onChangeLeader(item.id, item.nickname)}
                                    >
                                        转移队长
                                    </Button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                <br />
                {info.team.id !== 0 && (
                    <Button danger size="large" block onClick={onLeaveTeam} disabled={info.team.status !== 'preparing'}>
                        <WarningOutlined />{' '}
                        {isLeader
                            ? info.team.status === 'preparing'
                                ? '解散队伍'
                                : '游戏中不能解散队伍'
                            : info.team.status === 'preparing'
                              ? '退出队伍'
                              : '游戏中不能退出队伍'}
                    </Button>
                )}
            </FancyCard>
        </div>
    );
}
