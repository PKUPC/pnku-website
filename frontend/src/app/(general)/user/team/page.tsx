import { Alert } from 'antd';
import { useContext } from 'react';

import { CreateTeamForm } from '@/app/(general)/user/team/CreateTeamForm';
import { JoinTeamForm } from '@/app/(general)/user/team/JoinTeamForm';
import { TeamMemberForm } from '@/app/(general)/user/team/TeamMemberForm';
import { UpdateRecruitmentInfoForm } from '@/app/(general)/user/team/UpdateRecruitmentInfoForm';
import { UpdateTeamForm } from '@/app/(general)/user/team/UpdateTeamForm';
import { InfoError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';

function TeamInfoForm() {
    const { info } = useContext(GameInfoContext);
    if (info.status !== 'success') throw new InfoError();

    if (!info.user) return <Alert type="error" showIcon message="未登录" description="请登录后查看队伍信息" />;

    // 下面都是 render
    if (info.user.group === 'banned')
        return <Alert type="error" showIcon message="由于违反规则，你的参赛资格已被取消。如有疑问请联系工作人员。" />;
    // 还没有队伍信息
    if (!info.team) {
        return (
            <div>
                <CreateTeamForm />
                <br />
                <JoinTeamForm />
            </div>
        );
    }
    // 已经在队伍中
    else {
        const isLeader = info.team && info.team.leader_id === info.user.id;
        return (
            <div>
                <UpdateTeamForm />
                <br />
                <TeamMemberForm />
                {isLeader && info.team.id !== 0 && (
                    <>
                        <br />
                        <UpdateRecruitmentInfoForm />
                    </>
                )}
            </div>
        );
    }
}

export function UserTeamPage() {
    return <TeamInfoForm />;
}
