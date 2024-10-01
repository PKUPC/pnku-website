import { CheckCircleOutlined } from '@ant-design/icons';
import { Button, Form, Input, InputNumber, message } from 'antd';
import { useContext } from 'react';

import { FORM_STYLE } from '@/app/(general)/user/common_style';
import FancyCard from '@/components/FancyCard';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';

export function JoinTeamForm() {
    const { reloadInfo } = useContext(GameInfoContext);
    const [messageApi, contextHolder] = message.useMessage();

    const onJoinTeam = (values: { team_id: string; team_secret: string }) => {
        // console.log(values);
        wish({
            endpoint: 'team/join_team',
            payload: {
                team_id: values.team_id,
                team_secret: values.team_secret ? values.team_secret : '',
            },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'TeamInfo', duration: 3 }).then();
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'TeamInfo', duration: 3 }).then();
            } else {
                messageApi.success({ content: '保存成功', key: 'TeamInfo', duration: 2 }).then();
                reloadInfo().then();
            }
        });
    };

    return (
        <FancyCard title="想加入一个现有队伍？">
            {contextHolder}
            <Form name="join-team" {...FORM_STYLE} onFinish={onJoinTeam}>
                <Form.Item name="team_id" label="队伍 ID" extra={'注意，你应该让队长告诉你队伍 ID 而不是队名'}>
                    <InputNumber style={{ width: '100%' }} controls={false} placeholder="请联系队长获取队伍 ID" />
                </Form.Item>
                <Form.Item name="team_secret" label="队伍邀请码">
                    <Input maxLength={20} showCount placeholder="请联系队长获取队伍邀请码" />
                </Form.Item>

                <Button type="primary" size="large" block htmlType="submit">
                    {/* TODO: 这里也找一个图标 */}
                    <CheckCircleOutlined /> 加入队伍
                </Button>
            </Form>
        </FancyCard>
    );
}
