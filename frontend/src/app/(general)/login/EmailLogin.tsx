import { Button, Form, Input, message } from 'antd';
import Md5 from 'crypto-js/md5';
import { useRef, useState } from 'react';

import { useSuccessGameInfo } from '@/logic/contexts.ts';

import styles from './EmailLogin.module.css';
import { ReCaptchaPanel } from './components/ReCaptchaPanel';

export interface CaptchaPanelRef {
    reset: () => void;
}

export function EmailLogin() {
    // 默认为注册
    const [isSingIn, setIsSingIn] = useState(true);

    const captchaPanelRef = useRef<CaptchaPanelRef>(null);
    const [captchaData, setCaptchaData] = useState<Record<string, string>>({});
    const [messageApi, messageContextHolder] = message.useMessage();
    const info = useSuccessGameInfo();

    const onChangeStatus = () => {
        setIsSingIn(!isSingIn);
    };

    const signIn = (values: { email: string; password: string }) => {
        // console.log("sign_up");
        fetch(`/service/auth/email/login?rem=${window.rem}&ram=${window.ram}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: values.email,
                password: Md5(values.password + 'email:' + values.email.toLowerCase()).toString(),
                captcha: captchaData,
            }),
        })
            .then((res) => {
                if (res.status !== 200) {
                    messageApi.error({ content: `HTTP 错误 ${res.body}`, key: 'HTTP_ERROR', duration: 3 }).then();
                    return;
                }
                if (res.redirected) {
                    const redirectedURL = new URL(res.url);
                    if (redirectedURL.pathname === '/login/error') {
                        const msgValue = redirectedURL.searchParams.get('msg');
                        messageApi.error({ content: msgValue, key: 'EMAIL_SIGN_IN', duration: 3 }).then();
                        return {
                            status: 'error',
                            message: msgValue,
                        };
                    } else {
                        window.location.href = res.url;
                    }
                } else return res.json();
            })
            .then((res) => {
                console.log(res);
                if (res.status === 'error') {
                    messageApi.error({ content: res.message, key: 'EMAIL_SIGN_IN', duration: 3 }).then();
                }
                if (captchaPanelRef.current) captchaPanelRef.current.reset();
            });
    };

    const signUp = (values: { email: string }) => {
        // console.log("sign_up");
        messageApi.loading({ content: '注册中，请稍后', key: 'EMAIL_SIGN_IN', duration: 10 }).then();
        fetch(`/service/auth/email/register?rem=${window.rem}&ram=${window.ram}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: values.email,
                captcha: captchaData,
            }),
        })
            .then((res) => {
                if (res.status !== 200) {
                    return {
                        status: 'error',
                        message: `HTTP 错误 ${res.body}`,
                    };
                }
                if (res.redirected) {
                    const redirectedURL = new URL(res.url);
                    if (redirectedURL.pathname === '/login/error') {
                        const msgValue = redirectedURL.searchParams.get('msg');
                        messageApi.error({ content: msgValue, key: 'EMAIL_SIGN_IN', duration: 3 }).then();
                        return {
                            status: 'error',
                            message: msgValue,
                        };
                    } else {
                        window.location.href = res.url;
                    }
                }
                return res.json();
            })
            .then((res) => {
                if (res.status === 'success') {
                    messageApi.success({ content: '注册成功，请查收邮件', key: 'EMAIL_SIGN_IN', duration: 5 }).then();
                    if (captchaPanelRef.current) captchaPanelRef.current.reset();
                    setIsSingIn(!isSingIn);
                } else {
                    messageApi
                        .error({
                            content: res.message,
                            key: 'EMAIL_SIGN_IN',
                            duration: 3,
                        })
                        .then();
                }
            })
            .then(() => {
                if (captchaPanelRef.current) {
                    captchaPanelRef.current.reset();
                }
            });
    };

    const onFinish = (values: { email: string; password: string } | { email: string }) => {
        // 不强制要求进行人机身份验证，后端处理，用于豁免某些邮箱
        isSingIn ? signIn(values as { email: string; password: string }) : signUp(values);
    };

    return (
        <div>
            {messageContextHolder}
            <p>
                <b>账号密码登录</b>
            </p>
            <br />
            <Form name="email-login" wrapperCol={{ span: 10 }} onFinish={onFinish} className={styles.main}>
                <Form.Item
                    className={'submit-form-item'}
                    label="邮箱"
                    name="email"
                    rules={[{ required: true, message: '请输入邮箱' }]}
                >
                    <Input />
                </Form.Item>
                {isSingIn && (
                    <Form.Item
                        className={'submit-form-item'}
                        label="密码"
                        name="password"
                        rules={[{ required: true, message: '请输入密码' }]}
                    >
                        <Input.Password />
                    </Form.Item>
                )}

                {info.feature.captcha === 'recaptcha' && (
                    <ReCaptchaPanel setCaptchaData={setCaptchaData} ref={captchaPanelRef} />
                )}

                <Form.Item className={'submit-form-item'}>
                    <Button htmlType="submit">{isSingIn ? '登录' : '注册 / 重置'}</Button>
                    &nbsp;
                    <Button type="link" htmlType="button" onClick={onChangeStatus}>
                        {isSingIn ? '注册或重置密码' : '已有帐号，我要登录'}
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
}
