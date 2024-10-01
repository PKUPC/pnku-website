import { ClockCircleOutlined } from '@ant-design/icons';
import { Empty, Timeline } from 'antd';
import React from 'react';

import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useTheme } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { format_ts } from '@/utils.ts';

function WithStatus({ status, children }: { status: string; children: React.ReactNode }) {
    const { color } = useTheme();
    let style = {};
    if (status === 'pst') style = { color: color.baseContent + 'aa' };
    else if (status === 'prs') style = { color: color.info, fontWeight: 'bold' };
    else if (status === 'ftr') style = { color: color.baseContent };

    return <span style={style}>{children}</span>;
}

function Splitter({ children }: { children: string }) {
    const split = children.split(';');
    return (
        <div>
            {split.map((frag, idx) => (
                <p className="m-0" key={idx}>
                    {frag}
                </p>
            ))}
        </div>
    );
}

function Schedule() {
    const { data, mutate } = useWishData({ endpoint: 'game/get_schedule' });
    const { color } = useTheme();

    if (!data) return <Loading />;
    if (data.status !== 'success') return <WishError res={data} reload={mutate} />;

    const items = data.data.map((trigger) => ({
        label: (
            <WithStatus status={trigger.status}>
                {trigger.timestamp_s === 0 ? '--' : format_ts(trigger.timestamp_s)}
            </WithStatus>
        ),
        color: { pst: color.baseContent + '99', prs: color.info, ftr: color.baseContent }[trigger.status],
        dot: { pst: null, prs: <ClockCircleOutlined />, ftr: null }[trigger.status],
        children: (
            <WithStatus status={trigger.status}>
                <Splitter>{trigger.name}</Splitter>
            </WithStatus>
        ),
    }));

    return (
        <div>
            <br />
            <Timeline mode="left" items={items} />
            {data.data.length === 0 && <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无赛程" />}
        </div>
    );
}

export function SchedulePage() {
    return (
        <div>
            <Schedule />
        </div>
    );
}
