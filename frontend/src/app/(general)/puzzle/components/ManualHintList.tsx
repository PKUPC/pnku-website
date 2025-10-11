import { DeliveredProcedureOutlined, FieldTimeOutlined, SelectOutlined } from '@ant-design/icons';
import { Button, Col, Empty, Row, Tag } from 'antd';
import { useNavigate } from 'react-router';

import styles from '@/app/(general)/puzzle/ManualHintTab.module.css';
import FancyCard from '@/components/FancyCard';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

function ManualHintItem({ hintData }: { hintData: Wish.Ticket.TicketInfo }) {
    const navigate = useNavigate();
    let statusTag = hintData.staff_replied ? <Tag color="green">已回复</Tag> : <Tag color="gold">未回复</Tag>;
    if (hintData.status == '已关闭') {
        statusTag = <Tag color="red">已关闭</Tag>;
    }
    return (
        <Col md={12} xs={24}>
            <FancyCard
                title={<span>{hintData.subject}</span>}
                extra={
                    <Button
                        icon={<SelectOutlined />}
                        type="link"
                        onClick={() => navigate(`/ticket-detail?id=${hintData.ticket_id}`)}
                    >
                        查看
                    </Button>
                }
                className={styles.manualHintCard}
            >
                <p>
                    <DeliveredProcedureOutlined /> 状态：{statusTag}{' '}
                </p>
                <p>
                    <FieldTimeOutlined /> 最后活动时间：{format_ts(hintData.last_message_ts)}
                </p>
            </FancyCard>
        </Col>
    );
}

export function ManualHintList({ ticketHintInfo }: { ticketHintInfo: Wish.Ticket.TicketHintInfo }) {
    const sortedList = ticketHintInfo.list.sort((a, b) => b.last_message_ts - a.last_message_ts);
    const manualHintList =
        sortedList.length > 0 ? (
            <Row gutter={16}>
                {sortedList.map((v) => (
                    <ManualHintItem key={v.ticket_id} hintData={v} />
                ))}
            </Row>
        ) : (
            <Empty description={'暂无神谕'} />
        );

    return <div style={{ paddingTop: 20 }}>{manualHintList}</div>;
}
