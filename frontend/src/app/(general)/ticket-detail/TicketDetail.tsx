import { ExclamationCircleFilled } from '@ant-design/icons';
import { Button, Modal, Tag, message } from 'antd';
import { Dispatch, SetStateAction } from 'react';
import { useNavigate } from 'react-router-dom';

import { LeftCircleIcon } from '@/SvgIcons';
import { ChatBox } from '@/components/ChatBox';
import { ClickTitle } from '@/components/LinkTitle';
import { NeverError } from '@/errors';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

export function TicketDetail({
    ticketDetail,
    reloadTicketDetail,
}: {
    ticketDetail: Wish.Ticket.TicketDetailInfo;
    reloadTicketDetail: () => void;
}) {
    const info = useSuccessGameInfo();
    const navigate = useNavigate();
    if (!info.user) throw new NeverError();

    const [messageApi, contextHolder] = message.useMessage();
    const [modalApi, modalContextHolder] = Modal.useModal();

    const chatData = {
        title: ticketDetail.subject,
        messageLengthLimit: 400,
        messageList: ticketDetail.messages.map((v) => ({
            ...v,
            content_type: 'text',
        })),
    };

    const sendMessage = (
        content: string,
        setInputMessage: Dispatch<SetStateAction<string>>,
        setSending: Dispatch<SetStateAction<boolean>>,
    ) => {
        setSending(true);
        wish({
            endpoint: 'ticket/send_message',
            payload: { ticket_id: ticketDetail.ticket_id, content: content },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'SEND_TICKET_MESSAGE', duration: 5 }).then();
                setSending(false);
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'SEND_TICKET_MESSAGE', duration: 5 }).then();
                setSending(false);
            } else {
                messageApi.success({ content: '发送成功', key: 'SEND_TICKET_MESSAGE', duration: 3 }).then();
                setInputMessage('');
                reloadTicketDetail();
                setSending(false);
            }
        });
    };

    const setTicketStatus = (targetStats: 'OPEN' | 'CLOSED') => {
        wish({
            endpoint: 'ticket/set_ticket_status',
            payload: { ticket_id: ticketDetail.ticket_id, ticket_status: targetStats },
        }).then((res) => {
            if (res.status === 'error') {
                messageApi.error({ content: res.message, key: 'SEND_TICKET_MESSAGE', duration: 5 }).then();
            } else if (res.status === 'info') {
                messageApi.info({ content: res.message, key: 'SEND_TICKET_MESSAGE', duration: 5 }).then();
            } else {
                messageApi.success({ content: '发送成功', key: 'SEND_TICKET_MESSAGE', duration: 3 }).then();
                // console.log(res);
                reloadTicketDetail();
            }
        });
    };

    const onConfirm = (targetStatus: 'OPEN' | 'CLOSED') => {
        let text = '';
        if (info.user?.group === 'staff') text = targetStatus === 'OPEN' ? '确认重新打开工单吗？' : '确认关闭工单吗？';
        else if (info.user?.group === 'player' && targetStatus === 'CLOSED') text = '确认结束神谕吗？';

        modalApi.confirm({
            title: '警告',
            icon: <ExclamationCircleFilled />,
            content: text,
            onOk() {
                setTicketStatus(targetStatus);
            },
            onCancel() {},
        });
    };

    let customToolBar = undefined;
    if (info.user.group === 'staff') {
        if (ticketDetail.ticket_status === 'CLOSED')
            customToolBar = (
                <Button block={true} onClick={() => onConfirm('OPEN')}>
                    重新打开工单
                </Button>
            );
        else
            customToolBar = (
                <Button danger={true} block={true} onClick={() => onConfirm('CLOSED')}>
                    关闭工单
                </Button>
            );
    }
    // else if (info.user.group === "player" && ticketDetail.staff_replied) {
    //     customToolBar = <Button danger={true} block={true}
    //                             onClick={() => onConfirm("CLOSED")}
    //                             disabled={ticketDetail.ticket_status === "CLOSED"}
    //     >结束神谕</Button>;
    // }

    console.log(ticketDetail);

    let statusTag = ticketDetail.staff_replied ? <Tag color="green">已回复</Tag> : <Tag color="gold">未回复</Tag>;
    if (ticketDetail.ticket_status == 'CLOSED') {
        statusTag = <Tag color="red">已关闭</Tag>;
    }

    return (
        <div>
            {contextHolder}
            {modalContextHolder}
            <div className={'slim-container'}>
                <ClickTitle icon={<LeftCircleIcon />} title={'返回'} onClick={() => navigate(-1)} />
                <div className="mx-2.5 my-0">
                    <h3 className="text-2xl font-semibold">{ticketDetail.subject}</h3>
                    {statusTag}
                </div>

                <ChatBox
                    data={chatData}
                    sendMessage={sendMessage}
                    disabled={ticketDetail.disabled}
                    disabledReason={ticketDetail.disabled_reason}
                    customToolBar={customToolBar}
                />
            </div>
        </div>
    );
}
