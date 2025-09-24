import { Button, Form, Input, message } from 'antd';
import Md5 from 'crypto-js/md5';
import React, { useState } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';

import { useSuccessGameInfo } from '@/logic/contexts.ts';

import styles from './EmailLogin.module.css';

export function EmailLogin() {
    // 默认为注册
    const [sign_in, setState] = useState(true);
    const [captchaToken, setCaptchaToken] = useState<string>('');
    const recaptchaRef: React.RefObject<ReCAPTCHA> = React.createRef();
    const [recaptchaLoaded, setRecaptchaLoaded] = useState(false);
    const info = useSuccessGameInfo();

    const onChangeStatus = () => {
        setState(!sign_in);
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
                captcha: captchaToken,
            }),
        })
            .then((res) => {
                if (res.status !== 200) {
                    message.error({ content: `HTTP 错误 ${res.body}`, key: 'HTTP_ERROR', duration: 3 }).then();
                    return;
                }
                if (res.redirected) {
                    window.location.href = res.url;
                } else return res.json();
            })
            .then((res) => {
                console.log(res);
                if (recaptchaRef.current) recaptchaRef.current.reset();
            });
    };

    const signUp = (values: { email: string }) => {
        // console.log("sign_up");
        message.loading({ content: '注册中，请稍后', key: 'EMAIL_SIGN_IN', duration: 10 }).then();
        fetch(`/service/auth/email/register?rem=${window.rem}&ram=${window.ram}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: values.email,
                captcha: captchaToken,
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
                        message.error({ content: msgValue, key: 'EMAIL_SIGN_IN', duration: 3 }).then();
                        return {
                            status: 'error',
                            message: msgValue,
                        };
                    } else {
                        return {
                            status: 'error',
                            message: '未知错误，请联系网站管理员。',
                        };
                    }
                }
                return res.json();
            })
            .then((res) => {
                if (res.status === 'success') {
                    message.success({ content: '注册成功，请查收邮件', key: 'EMAIL_SIGN_IN', duration: 5 }).then();
                    if (recaptchaRef.current) recaptchaRef.current.reset();
                    setState(!sign_in);
                } else {
                    message
                        .error({
                            content: res.message,
                            key: 'EMAIL_SIGN_IN',
                            duration: 3,
                        })
                        .then();
                }
            })
            .then(() => {
                if (recaptchaRef.current) {
                    recaptchaRef.current.reset();
                }
            });
    };

    const onFinishCaptcha = (value: string | null) => {
        setCaptchaToken(value ?? '');
    };

    const onFinish = (values: { email: string; password: string } | { email: string }) => {
        if (info.feature.recaptcha && captchaToken === '') message.error('请进行人机身份验证').then();
        else {
            sign_in ? signIn(values as { email: string; password: string }) : signUp(values);
        }
        // recaptchaRef.current.reset();
    };

    // TODO: 换掉 antd 的 Form 组件
    return (
        <div>
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
                {sign_in && (
                    <Form.Item
                        className={'submit-form-item'}
                        label="密码"
                        name="password"
                        rules={[{ required: true, message: '请输入密码' }]}
                    >
                        <Input.Password />
                    </Form.Item>
                )}

                {info.feature.recaptcha && (
                    <div className="flex justify-center mb-6">
                        <ReCAPTCHA
                            ref={recaptchaRef}
                            sitekey={import.meta.env.VITE_RECAPTCHA_KEY ?? ''}
                            onChange={onFinishCaptcha}
                            hl={navigator.language === 'zh-CN' ? 'zh-CN' : 'en'}
                            size={'normal'}
                            asyncScriptOnLoad={() => {
                                console.log('recaptcha loaded!!');
                                setRecaptchaLoaded(true);
                            }}
                        />
                    </div>
                )}
                {/* TODO: 想办法优化一下这里的加载 */}
                {!recaptchaLoaded && info.feature.recaptcha && <div>人机验证加载中</div>}

                <Form.Item className={'submit-form-item'}>
                    <Button htmlType="submit">{sign_in ? '登录' : '注册 / 重置'}</Button>
                    &nbsp;
                    <Button type="link" htmlType="button" onClick={onChangeStatus}>
                        {sign_in ? '注册或重置密码' : '已有帐号，我要登录'}
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
}
