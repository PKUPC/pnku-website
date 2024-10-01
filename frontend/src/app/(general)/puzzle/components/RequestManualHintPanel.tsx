import { CheckCircleOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import { Button, Form, Input, Modal, message } from 'antd';

import { FORM_STYLE } from '@/app/(general)/user/common_style';
import FancyCard from '@/components/FancyCard';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

export function RequestManualHintPanel({
    puzzleData,
    reloadManualHintList,
}: {
    puzzleData: Wish.Puzzle.PuzzleDetailData;
    reloadManualHintList: () => void;
}) {
    console.log(puzzleData);
    const [requestManualHintForm] = Form.useForm();
    const [confirmModal, modalContextHolder] = Modal.useModal();
    const [messageApi, messageContextHolder] = message.useMessage();

    const request = (content: string) => {
        wish({
            endpoint: 'ticket/request_hint',
            payload: { puzzle_key: puzzleData.key, content },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi
                    .error({
                        content: res.message,
                        key: 'REQUEST_MANUAL_HINT',
                        duration: 5,
                    })
                    .then();
            } else {
                reloadManualHintList();
                messageApi
                    .success({
                        content: '成功',
                        key: 'REQUEST_MANUAL_HINT',
                        duration: 3,
                    })
                    .then();
            }
        });
    };

    const onRequestManualHint = (values: { subject?: string; content?: string }) => {
        console.log('call onRequestManualHint()');
        console.log(values);
        if (!values.content || values.content === '') {
            messageApi.error({ content: '提问内容不能为空！', key: 'REQUEST_MANUAL_HINT', duration: 5 }).then();
            return;
        }
        confirmModal.confirm({
            title: '提交神谕须知',
            icon: <ExclamationCircleFilled />,
            content: (
                <>
                    <p>请注意，在芈雨回复之前，无法再提交新的神谕。</p>
                    <br />
                    <p>
                        作为交换答案的代价，芈雨会要求献祭一定量的注意力。在她给出交换条件后，你可以决定要不要支付这个代价来换取答案。
                    </p>
                </>
            ),
            onOk: () => {
                request(values.content as string);
            },
            onCancel: () => {},
        });
    };

    const onFormValuesChange = (values: object) => {
        console.log(values);
    };

    return (
        <div>
            {modalContextHolder}
            {messageContextHolder}
            <FancyCard title="请求神谕">
                <Form
                    name="recruitment-info"
                    {...FORM_STYLE}
                    onFinish={onRequestManualHint}
                    onValuesChange={onFormValuesChange}
                    form={requestManualHintForm}
                >
                    <Form.Item
                        name="content"
                        label="提问内容"
                        extra={
                            '发起提问后，在芈雨回复之前无法再追问或发起新的神谕，在确认发送前请仔细检查。提问内容不超过 400 个字符。'
                        }
                    >
                        <Input.TextArea maxLength={400} autoSize={{ minRows: 2 }} />
                    </Form.Item>

                    <Button type="primary" size="large" block htmlType="submit">
                        <CheckCircleOutlined /> 请求提示
                    </Button>
                </Form>
            </FancyCard>
        </div>
    );
}
