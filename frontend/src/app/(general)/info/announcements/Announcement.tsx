import { NotificationOutlined } from '@ant-design/icons';
import { Tag } from 'antd';
import React from 'react';
import { redirect } from 'react-router-dom';

import { SimpleTemplateStr } from '@/components/Template';
import TimestampAgo from '@/components/TimestampAgo';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo, useTheme } from '@/logic/contexts.ts';
import { Wish } from '@/types/wish.ts';
import { mixColor } from '@/utils.ts';

export function Announcement({
    announcement,
    style,
}: {
    announcement: Wish.Game.AnnouncementInfo;
    style?: React.CSSProperties;
}) {
    const info = useSuccessGameInfo();
    const { color } = useTheme();

    const borderColor = mixColor(color.base300, color.info, 0.5);
    const headerBgColor = mixColor(color.base200, color.info, 0.3);
    const headerTextColor = mixColor(color.baseContent, color.info, 0.3);
    const contentBgColor = mixColor(color.base100, color.info, 0.05);

    if (!ARCHIVE_MODE && !info.game.login) redirect('/home');
    return (
        <div
            className="rounded-box border-[1px] overflow-hidden"
            id={`announcement-${announcement.id}`}
            style={{
                borderColor,
                ...style,
            }}
        >
            <div className="py-2 px-4 text-[0.875rem]" style={{ backgroundColor: headerBgColor }}>
                <>
                    {announcement.sorting_index >= 0 && <Tag color={'volcano'}>置顶</Tag>}
                    {announcement.category !== '通用' && <Tag color={'green'}>{announcement.category}</Tag>}
                    <span className="font-bold" style={{ color: headerTextColor }}>
                        <NotificationOutlined /> {announcement.title}
                    </span>
                    <span className="text-[0.75rem] ml-2 text-base-content text-opacity-60">
                        {' '}
                        发布于 <TimestampAgo ts={announcement.publish_at} />
                    </span>
                </>
            </div>
            <div className=" h-full w-full p-3" style={{ backgroundColor: contentBgColor }}>
                <SimpleTemplateStr name="announcement">{announcement.content}</SimpleTemplateStr>
            </div>
        </div>
    );
}
