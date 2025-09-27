import { CheckCircleOutlined } from '@ant-design/icons';
import { Button, Form, Input, InputNumber } from 'antd';
import { useEffect, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { WishConfirmModal } from '@/components/WishConfirmModal';
import { Wish } from '@/types/wish.ts';

const form_style = {
    colon: false,
    // initialValues: info.user.profile,
    labelCol: { span: 6 },
    labelWrap: true,
    wrapperCol: { span: 13 },
};

export function TeamCurrencyCard({
    team_id,
    data,
    reloadData,
}: {
    team_id: number;
    data: Wish.Staff.StaffTeamDetailCurrency;
    reloadData: () => void;
}) {
    const [form] = Form.useForm();
    const [changed, setChanged] = useState(false);

    useEffect(() => {
        form.setFieldsValue({
            change: data.change,
            current: data.current,
        });
    }, [form, data]);

    const [changeNumber, setChangeNumber] = useState(0);
    const [changeReason, setChangeReason] = useState('');
    const [confirmModalOpen, setConfirmModalOpen] = useState(false);

    const onSubmit = (value: { new_change: number; reason: string }) => {
        setChangeNumber(value.new_change);
        setChangeReason(value.reason);
        setConfirmModalOpen(true);
    };

    return (
        <div>
            <FancyCard title={`队伍${data.name}信息`}>
                <Form
                    form={form}
                    name="change-currency-panel"
                    {...form_style}
                    onValuesChange={(_changedValues, values) => {
                        if (values.new_change && values.reason) setChanged(true);
                        else setChanged(false);
                    }}
                    onFinish={onSubmit}
                    validateMessages={{
                        types: {
                            number: '请输入一个数字',
                        },
                    }}
                >
                    <Form.Item name="current" label={`当前${data.name}`}>
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>

                    <Form.Item name="change" label={'当前变动'}>
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>

                    <Form.Item name="new_change" label="新增变动" rules={[{ type: 'number' }]}>
                        <InputNumber style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item name="reason" label="变动原因">
                        <Input.TextArea maxLength={100} showCount />
                    </Form.Item>

                    <Button type="primary" size="middle" htmlType="submit" block disabled={!changed}>
                        <CheckCircleOutlined /> 提交更改
                    </Button>
                </Form>
            </FancyCard>
            <WishConfirmModal
                wishParam={{
                    endpoint: 'staff/v_me_50',
                    payload: {
                        team_id: team_id,
                        type: data.type,
                        change: changeNumber,
                        reason: changeReason,
                    },
                }}
                open={confirmModalOpen}
                setOpen={setConfirmModalOpen}
                confirmContent={'修改数量：' + changeNumber}
                onFinish={() => {
                    reloadData();
                }}
            />
        </div>
    );
}
