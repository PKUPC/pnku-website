import { CheckCircleOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import { Alert, Button, Form, Input, Modal, message } from 'antd';
import Md5 from 'crypto-js/md5';
import { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import FancyCard from '@/components/FancyCard';
import { NeverError } from '@/errors';
import { GameInfoContext } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';

function ChangePasswordForm() {
    const { info, reloadInfo } = useContext(GameInfoContext);
    const [different, setDifferent] = useState(false);
    const [wrongFormat, setWrongFormat] = useState(false);
    const navigate = useNavigate();
    const [modal, contextHolder] = Modal.useModal();
    const [messageApi, messageContextHolder] = message.useMessage();

    if (info.status === 'error') throw new NeverError();

    if (!info.user) {
        return <Alert type="error" showIcon message="未登录" description="请登录后查看" />;
    }

    const form_style = {
        colon: false, // initialValues: info.user.profile,
        labelCol: { span: 6 },
        labelWrap: true,
        wrapperCol: { span: 13 },
    };

    const onFinish = (values: { old_password: string; new_password: string }) => {
        if (wrongFormat) {
            messageApi.error({ content: '密码格式错误！', key: 'CHANGE_PASSWORD', duration: 3 }).then();
            return;
        }
        if (different) {
            messageApi.error({ content: '两次密码不一样！', key: 'CHANGE_PASSWORD', duration: 3 }).then();
            return;
        }
        modal.confirm({
            title: '警告',
            icon: <ExclamationCircleFilled />,
            content: <>确定修改密码</>,
            onOk() {
                if (!info.user) throw new NeverError();

                messageApi.loading({ content: '修改中，请稍候', key: 'CHANGE_PASSWORD', duration: 5 }).then();
                const op = Md5(values.old_password + 'email:' + info.user.profile.email.toLowerCase()).toString();
                const np = Md5(values.new_password + 'email:' + info.user.profile.email.toLowerCase()).toString();

                wish({
                    endpoint: 'user/change_password',
                    payload: {
                        old_password: op,
                        new_password: np,
                    },
                }).then((res) => {
                    if (res.status === 'error') {
                        messageApi.error({ content: res.message, key: 'CHANGE_PASSWORD', duration: 3 }).then();
                    } else {
                        messageApi
                            .success({ content: '修改成功，请重新登录', key: 'CHANGE_PASSWORD', duration: 3 })
                            .then();
                        reloadInfo().then(() => {
                            navigate('/login');
                        });
                    }
                });
            },
            onCancel() {},
        });
    };

    const checkPassword = (p: string) => {
        const regex = /^[a-zA-Z0-9_+\-=&!@#$%^*()]{8,16}$/;
        return regex.test(p);
    };

    const onChange = (
        _changedValues: {
            new_password?: string;
            new_password_2?: string;
            old_password?: string;
        },
        values: {
            new_password: string;
            new_password_2: string;
            old_password: string;
        },
    ) => {
        if (!values.new_password) values.new_password = '';
        if (!values.new_password_2) values.new_password_2 = '';
        if (!values.old_password) values.old_password = '';
        console.log(values);
        setDifferent(values.new_password !== values.new_password_2);
        if (values.new_password !== '') setWrongFormat(!checkPassword(values.new_password));
    };

    // 下面都是 render
    return (
        <div>
            {contextHolder}
            {messageContextHolder}
            <Alert
                showIcon
                message={<b>注意事项</b>}
                description={
                    <>
                        <p>
                            你可以在这里修改你的密码，但是总是使用随机强密码是一个好习惯。网站的登录有效期足够长，并且没有限制单一设备登陆，正常情况下不会需要你输入很多次密码。
                        </p>
                        <p>如果你相信我们不会明文存储你的当前密码和历史使用密码，可以在此修改你的密码。</p>
                        {/*<br/>*/}
                        <p>注意，手动修改密码是立即生效的，修改后只能用新密码登录。</p>
                    </>
                }
            />
            <br />

            <FancyCard title="修改密码">
                <Form name="public" {...form_style} onFinish={onFinish} onValuesChange={onChange}>
                    <Form.Item name="old_password" label="旧密码">
                        <Input.Password maxLength={16} showCount />
                    </Form.Item>
                    <Form.Item
                        name="new_password"
                        label="新密码"
                        extra={
                            <>
                                {'密码应为8到16位，只能包含字母、数字以及 _+-&=!@#$%^*()'}
                                {wrongFormat && (
                                    <>
                                        <br />
                                        <span style={{ color: 'red', fontStyle: 'italic' }}> 密码格式错误 </span>
                                    </>
                                )}
                            </>
                        }
                    >
                        <Input.Password maxLength={16} showCount visibilityToggle={true} />
                    </Form.Item>
                    <Form.Item
                        name="new_password_2"
                        label="新密码确认"
                        extra={different && <span style={{ color: 'red', fontStyle: 'italic' }}> 两次密码不一样 </span>}
                    >
                        <Input.Password maxLength={16} showCount visibilityToggle={true} />
                    </Form.Item>

                    <Button type="primary" size="large" block htmlType="submit">
                        <CheckCircleOutlined /> 修改密码
                    </Button>
                </Form>
            </FancyCard>
            <br />
        </div>
    );
}

export function UserSecurityPage() {
    return <ChangePasswordForm />;
}
