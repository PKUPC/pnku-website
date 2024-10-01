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

export function TeamApCard({ data, reloadData }: { data: Wish.Staff.StaffTeamDetail; reloadData: () => void }) {
    const [form] = Form.useForm();
    const [changed, setChanged] = useState(false);

    useEffect(() => {
        form.setFieldsValue({
            ap_change: data.ap_change,
            cur_ap: data.cur_ap,
        });
    }, [form, data]);

    const [apChangeNumber, setApChangeNumber] = useState(0);
    const [apChangeReason, setApChangeReason] = useState('');
    const [confirmModalOpen, setConfirmModalOpen] = useState(false);

    const onSubmit = (value: { new_ap_change: number; reason: string }) => {
        setApChangeNumber(value.new_ap_change);
        setApChangeReason(value.reason);
        setConfirmModalOpen(true);
    };

    return (
        <div>
            <FancyCard title="队伍注意力信息">
                <Form
                    form={form}
                    name="change-ap-panel"
                    {...form_style}
                    onValuesChange={(_changedValues, values) => {
                        console.log(values);
                        if (!values.new_ap_change) setChanged(false);
                        else if (values.reason === '' || !values.reason) setChanged(false);
                        else setChanged(true);
                    }}
                    onFinish={onSubmit}
                    validateMessages={{
                        types: {
                            number: '请输入一个数字',
                        },
                    }}
                >
                    <Form.Item name="cur_ap" label="当前注意力">
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>

                    <Form.Item name="ap_change" label="当前注意力变动">
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>

                    <Form.Item name="new_ap_change" label="新增变动" rules={[{ type: 'number' }]}>
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
                        team_id: data.team_id,
                        ap_change: apChangeNumber,
                        reason: apChangeReason,
                    },
                }}
                open={confirmModalOpen}
                setOpen={setConfirmModalOpen}
                confirmContent={'修改数量：' + apChangeNumber}
                onFinish={() => {
                    reloadData();
                }}
            />
        </div>
    );
}
