import { SyncOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router';

import { TableParams, getFromSessionStorage, saveToSessionStorage } from '@/app/(general)/staff/(menu)/common';
import {
    TableLoader as Table,
    type TableColumnsType,
    type TablePaginationConfig,
    type TableProps,
} from '@/components/lazy/TableLoader';
import { useReloadButton } from '@/hooks/useReloadButton';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

type StaffTicketInfo = Wish.Staff.StaffTicketInfo;

export function TicketTable({
    status_filters,
    team_filters,
}: {
    status_filters?: { text: string; value: string }[];
    team_filters?: { text: string; value: number }[];
}) {
    const [data, setData] = useState<StaffTicketInfo[]>([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const [_lastReload, markReload, reloadButtonRef] = useReloadButton(3);
    let oldTableParams = getFromSessionStorage('staffTicketsTableParams');
    if (oldTableParams.pagination === undefined) {
        oldTableParams = { pagination: { current: 1, pageSize: 50 } };
    } else {
        if (oldTableParams.pagination.current === undefined) oldTableParams.pagination.current = 1;
        if (oldTableParams.pagination.pageSize === undefined) oldTableParams.pagination.pageSize = 50;
    }
    const [tableParams, setTableParams] = useState<TableParams>(oldTableParams);
    const [messageApi, contextHolder] = message.useMessage();
    // 单独存储 totalNum，避免 totalNum 的更新触发重新请求数据
    const [totalNum, setTotalNum] = useState(0);

    const loadData = useCallback(() => {
        setLoading(true);
        const team_id = tableParams.filters?.team_id as number[] | null;
        const status = tableParams.filters?.status as string[] | null;
        const staff_replied = tableParams.filters?.staff_replied as boolean[] | null;
        const startPage = tableParams.pagination?.current ?? 1;
        const pageSize = tableParams.pagination?.pageSize ?? 50;
        const sort_field = tableParams.sortField as string | null;
        wish({
            endpoint: 'staff/get_tickets',
            payload: {
                team_id,
                status,
                staff_replied,
                sort_field,
                sort_order: tableParams.sortOrder,
                start_idx: (startPage - 1) * pageSize + 1,
                count: pageSize,
            },
        }).then((res) => {
            if (res.status !== 'success') {
                messageApi.error({ content: res.message, key: res.title }).then();
            } else {
                setData(res.data.list);
                setLoading(false);
                setTotalNum(res.data.total_num);
            }
        });
    }, [messageApi, tableParams]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleTableChange = useCallback<NonNullable<TableProps<StaffTicketInfo>['onChange']>>(
        (pagination, filters, sorter) => {
            console.log(pagination);
            console.log(filters);
            console.log(sorter);
            if (pagination.pageSize !== tableParams.pagination?.pageSize) setData([]);
            const nextTableParams = {
                pagination,
                filters,
                sortOrder: Array.isArray(sorter) ? undefined : sorter.order,
                sortField: Array.isArray(sorter) ? undefined : sorter.field,
            };
            if (JSON.stringify(tableParams) !== JSON.stringify(nextTableParams)) {
                saveToSessionStorage('staffTicketsTableParams', nextTableParams);
                setTableParams(nextTableParams);
                console.log(nextTableParams);
            }
        },
        [tableParams],
    );

    const columns: TableColumnsType<StaffTicketInfo> = useMemo(
        () => [
            { title: 'id', dataIndex: 'ticket_id' },
            {
                title: '队伍',
                dataIndex: 'team_name',
                key: 'team_id',
                render: (value, item) => <Link to={`/staff/team-detail/${item.team_id}`}>{value}</Link>,
                filters: team_filters,
                filterSearch: true,
                filteredValue: tableParams.filters?.team_id ? tableParams.filters.team_id : undefined,
            },
            {
                title: '最后回复时间',
                dataIndex: 'last_message_ts',
                render: (value) => format_ts(value),
                sorter: true,
                sortOrder: tableParams.sortField === 'last_message_ts' ? tableParams.sortOrder : undefined,
            },
            { title: '类型', dataIndex: 'ticket_type' },
            { title: '主题', dataIndex: 'subject' },
            {
                title: '状态',
                dataIndex: 'status',
                filters: status_filters,
                filteredValue: tableParams.filters?.status ? tableParams.filters.status : undefined,
            },
            {
                title: '已回复',
                dataIndex: 'staff_replied',
                render: (value) => (value ? '是' : '否'),
                filters: [
                    { text: '否', value: false },
                    { text: '是', value: true },
                ],
                filteredValue: tableParams.filters?.staff_replied ? tableParams.filters.staff_replied : undefined,
            },
            {
                title: '操作',
                key: 'action',
                render: (_, record: StaffTicketInfo) => (
                    <Button onClick={() => navigate(`/ticket-detail/${record.ticket_id}`)}>查看详情</Button>
                ),
            },
        ],
        [team_filters, status_filters, tableParams, navigate],
    );

    const paginationConfig = useMemo<TablePaginationConfig>(() => {
        return {
            ...tableParams.pagination,
            total: totalNum,
            position: ['topLeft'],
        };
    }, [tableParams.pagination, totalNum]);

    return (
        <>
            {contextHolder}
            <div style={{ position: 'relative', top: -16 }}>
                <div style={{ position: 'absolute', display: 'inline-block', zIndex: 3, right: 0, top: 16 }}>
                    <Button
                        type="link"
                        ref={reloadButtonRef}
                        onClick={() => {
                            messageApi.success({ content: '已刷新', key: 'TeamManage.LoadData', duration: 1 }).then();
                            markReload();
                            loadData();
                        }}
                    >
                        <SyncOutlined /> 刷新
                    </Button>
                </div>

                {
                    /* 没有数据时不会显示分页，提供一个占位 div */
                    totalNum === 0 && <div className="h-[56px] w-full"></div>
                }

                <Table<StaffTicketInfo>
                    size="small"
                    bordered
                    columns={columns}
                    rowKey="ticket_id"
                    dataSource={data}
                    pagination={paginationConfig}
                    loading={loading}
                    onChange={handleTableChange}
                    scroll={{
                        x: 'max-content',
                    }}
                />
            </div>
        </>
    );
}
