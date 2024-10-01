import { CheckCircleOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, Switch, message } from 'antd';
import { useContext, useState } from 'react';

import { FORM_STYLE } from '@/app/(general)/user/common_style';
import FancyCard from '@/components/FancyCard';
import { NeverError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { format_ts } from '@/utils.ts';

export function UpdateRecruitmentInfoForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [updateRecruitmentInfoForm] = Form.useForm();
    const [changed, set_changed] = useState(false);
    if (info.status !== 'success' || !info.team) throw new NeverError();
    const [checked, setChecked] = useState(info.team ? info.team.recruiting : false);
    const [messageApi, contextHolder] = message.useMessage();

    const onUpdateRecruitmentInfo = (values: { recruiting_contact: string }) => {
        wish({
            endpoint: 'team/update_extra_team_info',
            payload: {
                type: 'recruitment',
                data: {
                    recruiting: checked,
                    recruiting_contact: values.recruiting_contact,
                },
            },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'TeamExtraInfo', duration: 3 }).then();
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'TeamExtraInfo', duration: 3 }).then();
            } else {
                messageApi.success({ content: '保存成功', key: 'TeamExtraInfo', duration: 2 }).then();
                reloadInfo().then();
            }
        });
    };

    const onInfoChange = () => {
        // console.log(updateRecruitmentInfoForm.getFieldValue("switch"));
        if (!changed) set_changed(true);
    };

    const banned = info.team.ban_list.ban_recruiting_until > new Date().getTime() / 1000;
    const bannedText = `您的队伍的成员招募功能被禁用至 ${format_ts(info.team.ban_list.ban_recruiting_until)}。`;

    return (
        <FancyCard title="成员招募设置">
            {contextHolder}
            <Alert
                type={'warning'}
                showIcon
                message={'注意'}
                description={
                    <>
                        招募功能是方便玩家组队使用，请确定您有真实的招聘需求后再开启。
                        <br />
                        请在招募信息中给出<strong>有效的联系方式</strong>
                        ，也可以写上招募要求等。如果已经无需再招人，请及时取消公开招募状态。
                        <br />
                        如果启用了招募状态但是没有提供<strong>有效的联系方式</strong>，会禁用公开招募权限。
                    </>
                }
            />
            <br />
            {banned && <Alert type={'error'} showIcon={true} description={bannedText} />}

            {!banned && (
                <Form
                    name="recruitment-info"
                    {...FORM_STYLE}
                    onFinish={onUpdateRecruitmentInfo}
                    onValuesChange={onInfoChange}
                    form={updateRecruitmentInfoForm}
                >
                    <Form.Item label="公开招募" extra={'启用此选项后会在队伍广场中发布招募启示'}>
                        <Switch
                            onChange={(e) => {
                                setChecked(e);
                                onInfoChange();
                            }}
                            checked={checked}
                        />
                    </Form.Item>
                    <Form.Item
                        name="recruiting_contact"
                        label="招募信息"
                        extra={'给想加入的玩家提供一个联系方式吧！'}
                        initialValue={info.team.recruiting_contact}
                    >
                        <Input.TextArea maxLength={100} showCount />
                    </Form.Item>

                    <Button type="primary" size="large" block htmlType="submit" disabled={!changed}>
                        <CheckCircleOutlined /> 修改招募设置
                    </Button>
                </Form>
            )}
        </FancyCard>
    );
}
