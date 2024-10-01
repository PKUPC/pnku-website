import { Button, Col, Input, Row, message } from 'antd';
import { useState } from 'react';

export function DevLogin() {
    const [identity, setIdentity] = useState('');
    const [loading, setLoading] = useState(false);

    const onFinish = () => {
        setLoading(true);
        fetch(`/service/auth/manual?rem=${window.rem}&ram=${window.ram}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                identity: identity,
            }),
        })
            .then((res) => {
                if (res.redirected) {
                    setLoading(false);
                    window.location.href = res.url;
                }
                if (res.status !== 200) {
                    message.error({ content: `HTTP 错误 ${res.body}`, key: 'HTTP_ERROR', duration: 3 }).then();
                    return;
                }
                return res.json();
            })
            .then((res) => {
                if (!res.ok) {
                    message
                        .error({
                            content: `服务器报告了一个错误： ${res.error_msg}`,
                            key: 'BAD_REQUEST',
                            duration: 3,
                        })
                        .then();
                } else window.location.href = res.redirect;
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <>
            <br />
            <hr />
            <br />
            <p>
                <b>开发者登录</b>
            </p>
            <br />
            <Row gutter={{ sm: 8, md: 16 }} align="top">
                <Col xs={24} sm={8} className="flex sm:justify-end mb-2 sm:mb-0 h-8 items-center">
                    ID
                </Col>
                <Col xs={24} sm={10}>
                    <Input size="middle" onChange={(e) => setIdentity(e.target.value)} />
                    <div className="text-left text-opacity-70 text-base-content mt-1">
                        测试用账号的 ID，只要用同一个 ID 登录就是同一个账号。
                    </div>
                </Col>
            </Row>
            <br />
            <div className="flex justify-center">
                <Button loading={loading} onClick={() => onFinish()}>
                    登录
                </Button>
            </div>
        </>
    );
}
