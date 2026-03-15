import { CheckCircleOutlined } from '@ant-design/icons';
import { Button, Form, InputNumber, message } from 'antd';
import { useCallback, useState } from 'react';

import FancyCard from '@/components/FancyCard';

export function Sucard() {
    const [form] = Form.useForm();
    const [changed, setChanged] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();

    const onSubmit = useCallback(
        (value: { uid: string }) => {
            console.log(value);
            fetch(`/service/auth/su?rem=${window.rem}&ram=${window.ram}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    uid: value.uid,
                }),
            })
                .then((res) => {
                    if (res.status !== 200) {
                        messageApi.error({ content: `HTTP 错误 ${res.body}`, key: 'HTTP_ERROR', duration: 3 }).then();
                        return;
                    }
                    if (res.redirected) {
                        const url = new URL(res.url);
                        if (url.pathname === '/login/error') {
                            const params = Object.fromEntries(url.searchParams);
                            if (params.msg) {
                                messageApi.error({ content: params.msg, key: 'LOGIN_ERROR', duration: 3 }).then();
                            } else {
                                messageApi.error({ content: '切换失败！', key: 'LOGIN_ERROR', duration: 3 }).then();
                            }
                        } else {
                            window.location.href = res.url;
                        }
                    } else return res.json();
                })
                .then((res) => {
                    console.log(res);
                });
        },
        [messageApi],
    );

    return (
        <FancyCard title="用户切换">
            {contextHolder}
            <Form
                form={form}
                name="su-panel"
                colon={false}
                labelCol={{ span: 6 }}
                labelWrap={true}
                wrapperCol={{ span: 13 }}
                onValuesChange={(_changedValues, values) => {
                    if (values.uid) setChanged(true);
                    else setChanged(false);
                }}
                onFinish={onSubmit}
                validateMessages={{
                    types: {
                        number: '请输入一个数字',
                    },
                }}
            >
                <Form.Item name="uid" label={'用户 ID'}>
                    <InputNumber style={{ width: '100%' }} controls={false} />
                </Form.Item>

                <Button type="primary" size="middle" htmlType="submit" block disabled={!changed}>
                    <CheckCircleOutlined /> 确认切换
                </Button>
            </Form>
        </FancyCard>
    );
}
