import { CheckCircleOutlined } from '@ant-design/icons';
import { Alert, Button, Empty, Input, Tag } from 'antd';
import React, { Dispatch, SetStateAction, useState } from 'react';
import { Link } from 'react-router-dom';

import FancyCard from '@/components/FancyCard.tsx';
import { SimpleTemplateStr } from '@/components/Template';

type MessageInfo = {
    id: number;
    user_name: string;
    team_name: string;
    direction: string;
    content_type: string;
    content: string;
    timestamp_s: number;
};

type ChatData = {
    title: string;
    messageLengthLimit: number;
    messageList: MessageInfo[];
};

export function Message({ message }: { message: MessageInfo }) {
    return (
        <FancyCard
            className="mb-4"
            title={
                <>
                    {message.direction.toUpperCase() === 'TO_STAFF' ? (
                        <Tag style={{ fontSize: '1em', fontWeight: 'bold' }} color="blue">
                            【玩家】{message.user_name}
                        </Tag>
                    ) : (
                        <Tag style={{ fontSize: '1em', fontWeight: 'bold' }} color="green">
                            {' '}
                            【工作人员】{message.user_name}{' '}
                        </Tag>
                    )}
                </>
            }
        >
            <SimpleTemplateStr name="message">{message.content}</SimpleTemplateStr>
            <div className="italic text-sm text-base-content text-opacity-60">
                {' '}
                发送于 {new Date(message.timestamp_s * 1000).toLocaleString()}
            </div>
        </FancyCard>
    );
}

export function ChatBox({
    data,
    sendMessage,
    disabled,
    disabledReason,
    customToolBar,
}: {
    data: ChatData;
    sendMessage?: (
        content: string,
        setInputMessage: Dispatch<SetStateAction<string>>,
        setSending: Dispatch<SetStateAction<boolean>>,
    ) => void;
    disabled?: boolean;
    disabledReason?: string;
    customToolBar?: React.ReactNode;
}) {
    const [inputMessage, setInputMessage] = useState('');
    const [sending, setSending] = useState(false);

    const sendMessageWrapper = () => {
        if (sendMessage) sendMessage(inputMessage, setInputMessage, setSending);
    };
    console.log(disabled, disabledReason);

    return (
        <div>
            <Alert
                message="提示："
                description={
                    <>
                        你可以在这里向工作人员发送站内信，站内信支持部分 Markdown 语法（不支持表格）。如果你想发送图片，
                        可以将图片上传到其他图片站或者使用我们提供的
                        <Link className="link link-hover link-info" to={'/tools/upload-image'}>
                            图片上传功能
                        </Link>
                        。之后直接发送链接或者用 Markdown 的图片语法发送即可。
                    </>
                }
                className="message-info"
                type="info"
            />
            <br />

            <div className="border-base-300 rounded-box bordered border-[1px] p-4 mb-4 bg-base-200/30">
                <Input.TextArea
                    value={disabled ? (disabledReason ?? '已禁用') : inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="要发送的信息"
                    autoSize={{ minRows: 3, maxRows: 5 }}
                    maxLength={data.messageLengthLimit}
                    showCount={true}
                    disabled={disabled}
                    style={{ display: 'block' }}
                />
                <br />
                <div className="flex justify-end gap-4 w-full">
                    {customToolBar}
                    <Button
                        type="primary"
                        size="middle"
                        disabled={inputMessage === '' || disabled}
                        onClick={() => sendMessageWrapper()}
                        block={true}
                        loading={sending}
                    >
                        <CheckCircleOutlined /> 发送
                    </Button>
                </div>
            </div>

            {Array.from(data.messageList)
                .reverse()
                .map((msg) => (
                    <Message key={msg.id} message={msg} />
                ))}
            {data.messageList.length === 0 && <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无消息" />}
        </div>
    );
}
