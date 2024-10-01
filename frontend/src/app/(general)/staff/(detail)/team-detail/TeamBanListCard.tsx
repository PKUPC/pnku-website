import { CheckCircleOutlined } from '@ant-design/icons';
import { Button, DatePicker, Form } from 'antd';
import dayjs from 'dayjs';
import { useEffect, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { WishConfirmModal } from '@/components/WishConfirmModal';
import { Wish } from '@/types/wish.ts';

export function TeamBanListCard({ data, reloadData }: { data: Wish.Staff.StaffTeamDetail; reloadData: () => void }) {
    const [form] = Form.useForm();
    const [changed, setChanged] = useState(false);

    useEffect(() => {
        console.log(data.ban_list.ban_message_until);
        form.setFieldsValue({
            ban_message_until: dayjs(data.ban_list.ban_message_until * 1000),
            ban_manual_hint_until: dayjs(data.ban_list.ban_manual_hint_until * 1000),
            ban_recruiting_until: dayjs(data.ban_list.ban_recruiting_until * 1000),
        });
    }, [form, data]);

    const [banMessageUntil, setBanMessageUntil] = useState('');
    const [banManualHintUntil, setBanManualHintUntil] = useState('');
    const [banRecruitingUntil, setBanRecruitingUntil] = useState('');
    const [confirmModalOpen, setConfirmModalOpen] = useState(false);

    const onSubmit = (value: {
        ban_message_until: dayjs.Dayjs;
        ban_manual_hint_until: dayjs.Dayjs;
        ban_recruiting_until: dayjs.Dayjs;
    }) => {
        setBanMessageUntil(value.ban_message_until.format('YYYY-MM-DD HH:mm'));
        setBanManualHintUntil(value.ban_manual_hint_until.format('YYYY-MM-DD HH:mm'));
        setBanRecruitingUntil(value.ban_recruiting_until.format('YYYY-MM-DD HH:mm'));
        setConfirmModalOpen(true);
    };

    return (
        <div>
            <FancyCard title="队伍禁用列表">
                <Form
                    form={form}
                    name="ban-list-form"
                    colon={false}
                    labelCol={{ span: 6 }}
                    labelWrap={true}
                    wrapperCol={{ span: 13 }}
                    onValuesChange={(_, values) => {
                        if (
                            values.ban_message_until &&
                            values.ban_message_until.valueOf() === data.ban_list.ban_message_until * 1000 &&
                            values.ban_manual_hint_until &&
                            values.ban_manual_hint_until.valueOf() !== data.ban_list.ban_manual_hint_until * 1000 &&
                            values.ban_recruiting_until &&
                            values.ban_recruiting_until.valueOf() !== data.ban_list.ban_recruiting_until * 1000
                        )
                            setChanged(false);
                        else if (
                            !values.ban_message_until ||
                            !values.ban_manual_hint_until ||
                            !values.ban_recruiting_until
                        )
                            setChanged(false);
                        else setChanged(true);
                        if (!values.ban_message_until)
                            form.setFieldValue('ban_message_until', dayjs(data.ban_list.ban_message_until * 1000));
                        if (!values.ban_manual_hint_until)
                            form.setFieldValue(
                                'ban_manual_hint_until',
                                dayjs(data.ban_list.ban_manual_hint_until * 1000),
                            );
                        if (!values.ban_recruiting_until)
                            form.setFieldValue(
                                'ban_recruiting_until',
                                dayjs(data.ban_list.ban_recruiting_until * 1000),
                            );
                    }}
                    onFinish={onSubmit}
                >
                    <Form.Item name="ban_message_until" label="禁用站内信至">
                        <DatePicker format={'YYYY-MM-DD HH:mm'} showTime={true} allowClear={false} />
                    </Form.Item>
                    <Form.Item name="ban_manual_hint_until" label="禁用人工提示至">
                        <DatePicker format={'YYYY-MM-DD HH:mm'} showTime={true} allowClear={false} />
                    </Form.Item>
                    <Form.Item name="ban_recruiting_until" label="禁用招募功能至">
                        <DatePicker format={'YYYY-MM-DD HH:mm'} showTime={true} allowClear={false} />
                    </Form.Item>
                    <Button type="primary" size="middle" htmlType="submit" block disabled={!changed}>
                        <CheckCircleOutlined /> 提交更改
                    </Button>
                </Form>
            </FancyCard>
            <WishConfirmModal
                wishParam={{
                    endpoint: 'staff/update_extra_team_info',
                    payload: {
                        team_id: data.team_id,
                        type: 'ban_list',
                        data: {
                            ban_manual_hint_until: banManualHintUntil,
                            ban_message_until: banMessageUntil,
                            ban_recruiting_until: banRecruitingUntil,
                        },
                    },
                }}
                open={confirmModalOpen}
                setOpen={setConfirmModalOpen}
                confirmContent={
                    <>
                        禁用站内信至：{banMessageUntil}
                        <br />
                        禁用人工提示至：{banManualHintUntil}
                        <br />
                        禁用招募功能至：{banRecruitingUntil}
                    </>
                }
                onFinish={() => {
                    reloadData();
                }}
            />
        </div>
    );
}
