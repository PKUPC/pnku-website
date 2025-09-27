import { CheckCircleOutlined, FlagOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, Tooltip, message } from 'antd';
import { useEffect, useState } from 'react';

import FancyCard from '@/components/FancyCard';
import { GeneralTag } from '@/components/GeneralTag';
import { ProfileAvatar } from '@/components/ProfileAvatar.tsx';
import { TeamStatusTag } from '@/components/TeamStatusTag';
import { Wish } from '@/types/wish.ts';

import styles from './TeamInfoCard.module.css';

type StaffTeamDetail = Wish.Staff.StaffTeamDetail;
const form_style = {
    colon: false,
    // initialValues: info.user.profile,
    labelCol: { span: 6 },
    labelWrap: true,
    wrapperCol: { span: 13 },
};

export function TeamInfoCard({ data }: { data: StaffTeamDetail; reloadData: () => void }) {
    const [form] = Form.useForm();
    const [edit, set_edit] = useState(false);

    // form.in

    useEffect(() => {
        if (!edit) {
            form.setFieldsValue({
                team_id: data.team_id,
                team_name: data.team_name,
                team_info: data.team_info,
            });
        }
    }, [form, data, edit]);

    const onEditStatusChange = () => {
        set_edit(!edit);
    };

    const onUpdateTeamInfo = () => {
        message.error('NOT IMPLEMENT').then();
    };

    return (
        <div className={styles.teamInfoCard}>
            <FancyCard title="队伍基本信息">
                <Form form={form} name="team-info" {...form_style}>
                    <Form.Item name="team_id" label="队伍ID" initialValue={data.team_id}>
                        <Input maxLength={20} disabled={true} />
                    </Form.Item>
                    <Form.Item label="队伍状态">
                        {data.disp_list.length > 0 &&
                            data.disp_list.map((v) => <TeamStatusTag key={v.text} data={v} />)}
                    </Form.Item>
                    <Form.Item name="team_name" label="队名">
                        <Input maxLength={20} showCount disabled={!edit} />
                    </Form.Item>
                    <Form.Item name="team_info" label="简介">
                        <Input.TextArea maxLength={200} showCount disabled={!edit} />
                    </Form.Item>

                    {edit && (
                        <Form.Item name="reason" label="修改理由">
                            <Input.TextArea maxLength={100} showCount disabled={!edit} />
                        </Form.Item>
                    )}

                    <Alert type={'warning'} showIcon={true} description={'如需修改队伍信息，请直接在后台修改'} />

                    {/*{!edit && <Button type="primary" size="middle" block onClick={onEditStatusChange}>*/}
                    {/*    <CheckCircleOutlined/> 修改队伍信息*/}
                    {/*</Button>}*/}

                    {edit && (
                        <Button
                            danger
                            size="middle"
                            block
                            onClick={onEditStatusChange}
                            style={{ marginBottom: '24px' }}
                        >
                            <CheckCircleOutlined /> 取消
                        </Button>
                    )}

                    {edit && (
                        <Button type="primary" size="middle" block onClick={onUpdateTeamInfo}>
                            <CheckCircleOutlined /> 确认修改
                        </Button>
                    )}
                </Form>
            </FancyCard>
            <br />

            <FancyCard title="队伍成员列表">
                {data.members.map((item) => (
                    <div key={item.id} className="not-last:border-b-[1px] py-3 px-1 text-sm flex">
                        <div className="flex items-center gap-2 flex-grow">
                            <ProfileAvatar src={item.avatar_url} alt={item.nickname} size={'2rem'} />
                            {item.nickname}
                            {data.leader_id === item.id && (
                                <Tooltip placement="top" title={'队长'}>
                                    <FlagOutlined />
                                </Tooltip>
                            )}
                            <GeneralTag color="blue" bordered={false}>{`UID ${item.id}`}</GeneralTag>
                        </div>
                    </div>
                ))}
            </FancyCard>
        </div>
    );
}
