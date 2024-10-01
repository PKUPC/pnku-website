import { Alert } from 'antd';
import { redirect } from 'react-router-dom';

import { DevLogin } from '@/app/(general)/login/DevLogin.tsx';
import { EmailLogin } from '@/app/(general)/login/EmailLogin.tsx';
import NotFound from '@/app/NotFound.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';

import styles from './page.module.scss';

export function LoginBody() {
    const info = useSuccessGameInfo();
    if (info.user) redirect('/home');

    return (
        <div className={'slim-container ' + styles.main}>
            <Alert
                showIcon
                message={<b>注意事项</b>}
                description={
                    <>
                        <p>
                            使用邮箱注册后，服务器会自动向邮箱发送一个随机密码，登陆后可以修改密码。
                            <br />
                            如果你忘记密码，可以再次点击注册进行密码重置，重新注册后原密码仍然可以使用，直到你使用新密码登录。
                            <br />
                            短时间内发送到同一邮箱的邮件可能会无法收到，可以等待一段时间后重试。
                            <br />
                            如果您还有其他问题，请联系 <a href="mailto:winfridx@163.com">winfridx@163.com</a> 获取帮助。
                        </p>
                    </>
                }
            />
            <br />
            <div className="login-instruction">
                {/*<p><b>选择登录方式</b></p>*/}
                {/*<br/>*/}
                {info.feature.email_login && <EmailLogin />}
                {info.feature.debug && <DevLogin />}
            </div>
        </div>
    );
}

export function LoginPage() {
    if (import.meta.env.VITE_ARCHIVE_MODE === 'true') return <NotFound />;

    return <LoginBody />;
}
