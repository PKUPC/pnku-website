import { CheckCircleOutlined } from '@ant-design/icons';
import { Button, Form, Input, message } from 'antd';
import { useContext } from 'react';

import { FORM_STYLE } from '@/app/(general)/user/common_style';
import FancyCard from '@/components/FancyCard';
import { InfoError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { random_str } from '@/utils.ts';

export function CreateTeamForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [createTeamForm] = Form.useForm();
    const [messageApi, contextHolder] = message.useMessage();

    if (info.status !== 'success') throw new InfoError();

    const onCreateTeam = (values: { team_name: string; team_info: string; team_secret: string }) => {
        wish({
            endpoint: 'team/create_team',
            payload: {
                team_name: values.team_name ? values.team_name : '',
                team_info: values.team_info ? values.team_info : '',
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
    const onFreshTeamSecretInCreateTeam = () => {
        createTeamForm.setFieldsValue({ team_secret: random_str(16) });
    };

    return (
        <FancyCard title="想新建一个新队伍？">
            {contextHolder}
            <Form
                name="new-team"
                {...FORM_STYLE}
                form={createTeamForm}
                onFinish={onCreateTeam}
                initialValues={{ team_secret: random_str(15) }}
            >
                <Form.Item
                    name="team_name"
                    label="队名"
                    extra="队伍名称应至少包含2个非空白字符，如包含不适宜内容可能会被强制修改、封禁账号或追究责任"
                >
                    <Input maxLength={20} showCount placeholder="（将显示在排行榜上）" />
                </Form.Item>
                <Form.Item name="team_info" label="队伍信息">
                    <Input.TextArea
                        maxLength={200}
                        showCount
                        placeholder="（将显示在排行榜上，可以下拉右下角从而增大显示区域）"
                    />
                </Form.Item>
                <Form.Item name="team_secret" label="队伍邀请码" extra="队伍邀请码长度应该在10到20之间，建议随机生成">
                    <Input.Search
                        style={{ width: '100%' }}
                        onSearch={onFreshTeamSecretInCreateTeam}
                        enterButton="随机"
                    />
                </Form.Item>

                <Button type="primary" size="large" block htmlType="submit">
                    <CheckCircleOutlined /> 创建队伍
                </Button>
            </Form>
        </FancyCard>
    );
}
