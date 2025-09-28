import { SyncOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { TableParams, getFromSessionStorage, saveToSessionStorage } from '@/app/(general)/staff/(menu)/common';
import { TableLoader as Table, type TableColumnsType, type TableProps } from '@/components/lazy/TableLoader';
import { useReloadButton } from '@/hooks/useReloadButton';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

type StaffSubmissionInfo = Wish.Staff.StaffSubmissionInfo;

export function SubmissionTable({
    puzzle_filters,
    team_filters,
    status_filters,
}: {
    puzzle_filters?: { text: string; value: string }[];
    team_filters?: { text: string; value: number }[];
    status_filters?: { text: string; value: string }[];
}) {
    const [data, setData] = useState<StaffSubmissionInfo[]>([]);
    const [loading, setLoading] = useState(false);
    const [_lastReload, markReload, reloadButtonRef] = useReloadButton(3);
    let oldTableParams = getFromSessionStorage('staffSubmissionsTableParams');
    if (oldTableParams.pagination === undefined) {
        oldTableParams = { pagination: { current: 1, pageSize: 50 }, sortOrder: 'descend', sortField: 'timestamp_s' };
    } else {
        if (oldTableParams.pagination.current === undefined) oldTableParams.pagination.current = 1;
        if (oldTableParams.pagination.pageSize === undefined) oldTableParams.pagination.pageSize = 50;
    }
    const [tableParams, setTableParams] = useState<TableParams>(oldTableParams);
    const [messageApi, contextHolder] = message.useMessage();

    const loadData = useCallback(() => {
        setLoading(true);
        const startPage = tableParams.pagination?.current ?? 1;
        const pageSize = tableParams.pagination?.pageSize ?? 50;
        const team_id = tableParams.filters?.team_id as number[] | null;
        const puzzle_key = tableParams.filters?.puzzle as string[] | null;
        const puzzle_status = tableParams.filters?.status as string[] | null;
        const sort_field = tableParams.sortField as string | null;
        wish({
            endpoint: 'staff/get_submission_list',
            payload: {
                start_idx: (startPage - 1) * pageSize + 1,
                count: pageSize,
                team_id,
                puzzle_key,
                puzzle_status,
                sort_field,
                sort_order: tableParams.sortOrder,
            },
        }).then((res) => {
            if (res.status !== 'success') {
                messageApi.error({ content: res.message }).then();
            } else {
                setData(res.data.list);
                setLoading(false);
                const nextConfig = {
                    ...tableParams,
                    pagination: {
                        ...tableParams.pagination,
                        total: res.data.total_num,
                    },
                };
                if (JSON.stringify(nextConfig) !== JSON.stringify(tableParams)) setTableParams(nextConfig);
            }
        });
    }, [tableParams, messageApi]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleTableChange: TableProps<StaffSubmissionInfo>['onChange'] = (pagination, filters, sorter) => {
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
            saveToSessionStorage('staffSubmissionsTableParams', nextTableParams);
            setTableParams(nextTableParams);
        }
    };

    console.log(tableParams);

    const columns: TableColumnsType<StaffSubmissionInfo> = [
        { title: 'id', dataIndex: 'idx' },
        {
            title: '提交时间',
            dataIndex: 'timestamp_s',
            render: (value) => format_ts(value),
            sorter: true,
            sortOrder: tableParams.sortField === 'timestamp_s' ? tableParams.sortOrder : undefined,
        },
        {
            title: '题目',
            dataIndex: 'puzzle',
            render: (value, item) => <Link to={`/puzzle?key=${item.puzzle_key}`}>{value}</Link>,
            filters: puzzle_filters,
            filterSearch: true,
            filteredValue: tableParams.filters?.puzzle ? tableParams.filters.puzzle : undefined,
        },
        {
            title: '队伍',
            dataIndex: 'team',
            key: 'team_id',
            render: (value, item) => <Link to={`/staff/team-detail?tid=${item.team_id}`}>{value}</Link>,
            filters: team_filters,
            filterSearch: true,
            filteredValue: tableParams.filters?.team_id ? tableParams.filters.team_id : undefined,
        },
        { title: '提交人', dataIndex: 'user' },
        { title: '提交内容', dataIndex: 'origin' },
        {
            title: '状态',
            dataIndex: 'status',
            filters: status_filters,
            filteredValue: tableParams.filters?.status ? tableParams.filters.status : undefined,
        },
        { title: '信息', dataIndex: 'info' },
    ];

    return (
        <>
            {contextHolder}
            <div style={{ position: 'relative', top: -16 }}>
                <div style={{ position: 'absolute', display: 'inline-block', zIndex: 3, right: 0, top: 16 }}>
                    <Button
                        type="link"
                        ref={reloadButtonRef}
                        onClick={() => {
                            loadData();
                            messageApi.success({ content: '已刷新', key: 'TeamManage.LoadData', duration: 2 }).then();
                            markReload();
                        }}
                    >
                        <SyncOutlined /> 刷新
                    </Button>
                </div>
                <Table<StaffSubmissionInfo>
                    size="small"
                    bordered
                    columns={columns}
                    rowKey="idx"
                    dataSource={data}
                    pagination={{
                        ...tableParams.pagination,
                        position: ['topLeft'],
                    }}
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
