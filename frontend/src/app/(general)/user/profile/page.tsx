import { CheckCircleOutlined, InfoCircleTwoTone } from '@ant-design/icons';
import { Alert, Button, Form, Input, Tooltip, message } from 'antd';
import { useContext, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { GeneralTag } from '@/components/GeneralTag';
import { ProfileAvatar } from '@/components/ProfileAvatar.tsx';
import { InfoError } from '@/errors';
import { GameInfoContext, useTheme } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';

function UserProfileForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [changed, set_changed] = useState(false);
    const { color } = useTheme();

    if (info.status !== 'success') throw new InfoError();

    if (!info.user) return <Alert type="error" showIcon message="未登录" description="请登录后修改个人资料" />;

    const form_style = {
        colon: false,
        initialValues: info.user.profile,
        labelCol: { span: 6 },
        labelWrap: true,
        wrapperCol: { span: 13 },
        onValuesChange: () => {
            set_changed(true);
        },
    };

    return (
        <Form.Provider
            onFormFinish={(name, { forms }) => {
                if (name !== 'submit')
                    // submit events in other forms are redirected to `submit_btn.click()` in `onValuesChange`
                    return;
                if (!changed) return;

                const all_values = {};
                Object.values(forms).forEach((f) => {
                    Object.assign(all_values, f.getFieldsValue());
                });
                message.loading({ content: '正在保存…', key: 'UserProfile', duration: 10 }).then();

                wish({
                    endpoint: 'user/update_profile',
                    payload: {
                        profile: all_values,
                    },
                }).then((res) => {
                    if (res.status === 'error') {
                        message.error({ content: res.message, key: 'UserProfile', duration: 3 }).then();
                    } else if (res.status === 'info') {
                        message.info({ content: res.message, key: 'UserProfile', duration: 3 }).then();
                    } else {
                        message.success({ content: '保存成功', key: 'UserProfile', duration: 2 }).then();
                        reloadInfo().then();
                    }
                });
            }}
        >
            <FancyCard title="公开资料">
                <Form name="public" {...form_style}>
                    <Form.Item
                        label={
                            <Tooltip
                                title={
                                    <>
                                        前往{' '}
                                        <a target={'_blank'} rel="noopener noreferrer" href={'https://cravatar.com/'}>
                                            https://cravatar.com/
                                        </a>{' '}
                                        绑定邮箱
                                    </>
                                }
                            >
                                头像&nbsp;
                                <InfoCircleTwoTone
                                    twoToneColor={[color.warning, color.base100]}
                                    className="icon-with-chinese"
                                />
                            </Tooltip>
                        }
                    >
                        <ProfileAvatar src={info.user.profile.avatar_url} alt={'avatar'} size={'3.5rem'} />
                    </Form.Item>
                    <Form.Item name="user_id" label="用户 ID" initialValue={info.user.id}>
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>
                    {info.user.profile.nickname !== undefined && (
                        <Form.Item
                            name="nickname"
                            label="昵称"
                            extra="如包含不适宜内容可能会被强制修改、封禁账号或追究责任"
                        >
                            <Input maxLength={20} showCount placeholder="（将显示在排行榜上）" />
                        </Form.Item>
                    )}
                    <Form.Item label="用户组">
                        <GeneralTag color={info.user.group === 'player' ? 'blue' : 'green'}>
                            {info.user.group_disp}
                        </GeneralTag>
                    </Form.Item>
                </Form>
                {info.user.group === 'banned' && (
                    <>
                        <br />
                        <Alert
                            type="error"
                            showIcon
                            message="由于违反规则，你的参赛资格已被取消。如有疑问请联系工作人员。"
                        />
                    </>
                )}
            </FancyCard>
            <br />
            <FancyCard title="联系方式">
                <Form name="contact" {...form_style}>
                    {info.user.profile.email !== undefined && (
                        <Form.Item name="email" label="邮箱">
                            <Input disabled={true} />
                        </Form.Item>
                    )}
                </Form>
            </FancyCard>
            <br />
            <Form name="submit">
                <Button type="primary" size="large" block htmlType="submit" disabled={!changed}>
                    <CheckCircleOutlined /> 保存
                </Button>
            </Form>
        </Form.Provider>
    );
}

export function UserProfilePage() {
    return <UserProfileForm />;
}
