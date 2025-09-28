import { CheckCircleOutlined } from '@ant-design/icons';
import { Alert, Button, Empty, Input, Tag, message } from 'antd';
import { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import FancyCard from '@/components/FancyCard.tsx';
import { SimpleTemplateStr } from '@/components/Template';
import { WishError } from '@/components/WishError.tsx';
import { NeverError } from '@/errors';
import { useMessageData } from '@/hooks/useMessageData';
import { GameStatusContext, useGameInfo } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

export function Message({ message }: { message: Wish.Message.MessageInfo }) {
    return (
        <FancyCard
            className="mb-4"
            title={
                <>
                    {message.direction === 'to_staff' ? (
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

export function MessageBox({ teamId }: { teamId: number }) {
    const info = useGameInfo();
    if (info.status !== 'success' || !info.user || !info.team) {
        throw new NeverError();
    }
    const [messages, error, reloadMessage] = useMessageData(teamId);
    const [inputMsg, setInputMsg] = useState('');
    const [messageApi, contextHolder] = message.useMessage();
    const [sending, setSending] = useState(false);

    const { setHasNewMessage } = useContext(GameStatusContext);
    const banned = info.team.ban_list.ban_message_until > new Date().getTime() / 1000;
    const bannedText = `您的队伍的站内信功能被禁用至 ${format_ts(info.team.ban_list.ban_message_until)}。`;

    useEffect(() => {
        if (info.status !== 'success' || !info.user) {
            return;
        }
        if (!!info.user && info.user.group === 'staff') return;
        if (!messages) return;
        if (!!messages && messages.length === 0) return;
        if (!messages[messages.length - 1].player_unread) return;
        // console.log("read message");
        wish({
            endpoint: 'message/read_message',
            payload: {
                team_id: teamId,
                msg_id: messages[messages.length - 1].id,
            },
        }).then((res) => {
            if (res.status === 'error') {
                message.error({ content: '似乎出了点错误', key: 'Message', duration: 3 }).then();
            }
            setHasNewMessage(false);
            reloadMessage();
        });
    }, [info.status, info.user, messages, reloadMessage, setHasNewMessage, teamId]);

    if (error) return <WishError res={error} reload={reloadMessage} />;

    const send_msg = () => {
        setSending(true);
        wish({
            endpoint: 'message/send_message',
            payload: {
                team_id: teamId,
                type: 'text',
                content: inputMsg,
            },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'send-msg-error', duration: 3 }).then();
                setSending(false);
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'send-msg-error', duration: 3 }).then();
                setSending(false);
            } else {
                messageApi.success({ content: '发送成功', key: 'send-msg-success', duration: 1 }).then();
                // console.log(res);
                setInputMsg('');
                setSending(false);
            }
        });
    };

    if (messages === null || messages === undefined) throw new NeverError();

    return (
        <div className="message-list">
            {contextHolder}
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

            {banned && (
                <>
                    <Alert type={'error'} showIcon={true} description={bannedText} />
                    <br />
                </>
            )}
            {!banned && (
                <div className="border-base-300 rounded-box bordered border-[1px] p-4 mb-4 bg-base-200/30">
                    <Input.TextArea
                        value={banned ? bannedText : inputMsg}
                        onChange={(e) => setInputMsg(e.target.value)}
                        placeholder="要发送的信息"
                        autoSize={{ minRows: 3, maxRows: 5 }}
                        disabled={banned}
                        maxLength={400}
                        style={{ display: 'block' }}
                    />
                    <br />
                    <Button
                        type="primary"
                        size="large"
                        block
                        disabled={inputMsg === '' || banned}
                        onClick={send_msg}
                        loading={sending}
                    >
                        <CheckCircleOutlined /> 发送
                    </Button>
                </div>
            )}

            {Array.from(messages)
                .reverse()
                .map((msg) => (
                    <Message key={msg.id} message={msg} />
                ))}
            {messages.length === 0 && <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无消息" />}
        </div>
    );
}
