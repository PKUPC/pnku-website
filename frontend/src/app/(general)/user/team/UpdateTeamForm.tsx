import { CheckCircleOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, message } from 'antd';
import { useContext, useState } from 'react';

import { FORM_STYLE } from '@/app/(general)/user/common_style';
import FancyCard from '@/components/FancyCard';
import { TeamStatusTag } from '@/components/TeamStatusTag';
import { NeverError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { random_str } from '@/utils.ts';

export function UpdateTeamForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [updateTeamForm] = Form.useForm<{ teamId: number; teamName: string; teamInfo: string; teamSecret: string }>();
    const [changed, setChanged] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();
    if (info.status !== 'success') throw new NeverError();

    const onTeamInfoChange = (
        _1: any,
        values: { teamId: number; teamName: string; teamInfo: string; teamSecret: string },
    ) => {
        setChanged(
            values.teamId !== info.team?.id ||
                values.teamName !== info.team?.team_name ||
                values.teamInfo !== info.team?.team_info ||
                values.teamSecret !== info.team?.team_secret,
        );
    };

    const onUpdateTeamInfo = (values: { teamName: string; teamInfo: string; teamSecret: string }) => {
        wish({
            endpoint: 'team/update_team',
            payload: {
                team_name: values.teamName ? values.teamName : '',
                team_info: values.teamInfo ? values.teamInfo : '',
                team_secret: values.teamSecret ? values.teamSecret : '',
            },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'TeamInfo', duration: 3 }).then();
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'TeamInfo', duration: 3 }).then();
            } else {
                messageApi.success({ content: '保存成功', key: 'TeamInfo', duration: 2 }).then();
                reloadInfo().then(() => {
                    setChanged(false);
                });
            }
        });
    };

    const onFreshTeamSecretInUpdateTeam = () => {
        if (!changed) setChanged(true);
        const newTeamSecret = random_str(16);
        if (newTeamSecret !== info.team?.team_secret) {
            setChanged(true);
        }
        updateTeamForm.setFieldsValue({ teamSecret: newTeamSecret });
    };

    if (!info.user || !info.team)
        return <Alert type="error" showIcon message="未登录" description="请登录后查看队伍信息" />;

    const isLeader = info.team && info.team.leader_id === info.user.id;

    return (
        <FancyCard title="所在队伍信息">
            {contextHolder}
            <Form
                name="team-info"
                {...FORM_STYLE}
                onFinish={onUpdateTeamInfo}
                onValuesChange={onTeamInfoChange}
                form={updateTeamForm}
            >
                <Form.Item label="队伍状态">
                    {info.team.disp_list.length > 0 &&
                        info.team.disp_list.map((v) => <TeamStatusTag key={v.text} data={v} />)}
                </Form.Item>
                <Form.Item
                    name="teamId"
                    label="队伍 ID"
                    initialValue={info.team.id}
                    extra={'注意：加入队伍时需要填写的是这个 ID 而不是队名。'}
                >
                    <Input maxLength={20} disabled={true} />
                </Form.Item>
                <Form.Item
                    name="teamName"
                    label="队名"
                    extra={
                        isLeader
                            ? '队伍名称应至少包含2个非空白字符，如包含不适宜内容可能会被强制修改、封禁账号或追究责任。'
                            : ''
                    }
                    initialValue={info.team.team_name}
                >
                    <Input
                        maxLength={20}
                        showCount
                        disabled={!isLeader || info.team.status !== 'preparing' || info.team.id === 0}
                    />
                </Form.Item>
                <Form.Item name="teamInfo" label="简介" initialValue={info.team.team_info}>
                    <Input.TextArea maxLength={200} showCount disabled={!isLeader || info.team.id === 0} />
                </Form.Item>
                <Form.Item
                    name="teamSecret"
                    label="队伍邀请码"
                    initialValue={info.team.team_secret}
                    extra="队伍邀请码长度应该在10到20之间，建议随机生成。"
                >
                    <Input.Search
                        style={{ width: '100%' }}
                        onSearch={onFreshTeamSecretInUpdateTeam}
                        enterButton="随机"
                        disabled={!isLeader || info.team.id === 0}
                    />
                </Form.Item>

                {isLeader && info.team.id !== 0 && (
                    <Button
                        type="primary"
                        size="large"
                        block
                        htmlType="submit"
                        disabled={!changed || info.team.id === 0}
                    >
                        <CheckCircleOutlined /> 修改队伍信息
                    </Button>
                )}
            </Form>
        </FancyCard>
    );
}
