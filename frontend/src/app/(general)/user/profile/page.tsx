import { CheckCircleOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, Radio, message } from 'antd';
import { useContext, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { GeneralTag } from '@/components/GeneralTag';
import { ProfileAvatar } from '@/components/ProfileAvatar.tsx';
import { InfoError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';

function UserProfileForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [changed, setChanged] = useState(false);
    const [messageApi, messageContextHolder] = message.useMessage();

    if (info.status !== 'success') throw new InfoError();

    if (!info.user) return <Alert type="error" showIcon message="未登录" description="请登录后修改个人资料" />;

    const form_style = {
        colon: false,
        initialValues: info.user.profile,
        labelCol: { span: 6 },
        labelWrap: true,
        wrapperCol: { span: 13 },
        onValuesChange: (_: any, values: { nickname: string; avatarService: 'cravatar' | 'weavatar' }) => {
            setChanged(
                info.user?.profile.nickname !== values.nickname ||
                    info.user?.profile.avatarService !== values.avatarService,
            );
            console.log(values);
        },
    };

    return (
        <>
            {messageContextHolder}
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
                    messageApi.loading({ content: '正在保存…', key: 'UserProfile', duration: 10 }).then();

                    wish({
                        endpoint: 'user/update_profile',
                        payload: {
                            profile: all_values,
                        },
                    }).then((res) => {
                        if (res.status === 'error') {
                            messageApi.error({ content: res.message, key: 'UserProfile', duration: 3 }).then();
                        } else if (res.status === 'info') {
                            messageApi.info({ content: res.message, key: 'UserProfile', duration: 3 }).then();
                        } else {
                            messageApi.success({ content: '保存成功', key: 'UserProfile', duration: 2 }).then();
                            reloadInfo().then();
                        }
                    });
                    setChanged(false);
                }}
            >
                <FancyCard title="公开资料">
                    <Form name="public" {...form_style}>
                        <Form.Item label="头像">
                            <ProfileAvatar src={info.user.profile.avatar_url} alt={'avatar'} size={'3.5rem'} />
                        </Form.Item>
                        <Form.Item
                            name="avatarService"
                            label="头像服务"
                            extra={
                                <div>
                                    <a
                                        className="dark:text-blue-400/60"
                                        href="https://cravatar.com/"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        Cravatar
                                    </a>{' '}
                                    和{' '}
                                    <a
                                        className="dark:text-blue-400/60"
                                        href="https://weavatar.com/"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        WeAvatar
                                    </a>{' '}
                                    是两个公共头像服务。您可以选择其中一个服务绑定注册用的邮箱并上传自己的头像。
                                </div>
                            }
                        >
                            <Radio.Group>
                                <Radio.Button value="cravatar">Cravatar</Radio.Button>
                                <Radio.Button value="weavatar">Weavatar</Radio.Button>
                            </Radio.Group>
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
        </>
    );
}

export function UserProfilePage() {
    return <UserProfileForm />;
}
