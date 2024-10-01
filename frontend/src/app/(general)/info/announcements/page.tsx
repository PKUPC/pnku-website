import { Empty } from 'antd';
import { useContext, useEffect } from 'react';

import { Announcement } from '@/app/(general)/info/announcements/Announcement';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { GameStatusContext } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

function AnnouncementList() {
    const { data, mutate } = useWishData({
        endpoint: 'game/get_announcements',
    });
    const { needReloadAnnouncement, setNeedReloadAnnouncement } = useContext(GameStatusContext);

    useEffect(() => {
        setNeedReloadAnnouncement(false);
    }, [setNeedReloadAnnouncement]);

    useEffect(() => {
        if (needReloadAnnouncement) {
            mutate().then();
            setNeedReloadAnnouncement(false);
        }
    }, [mutate, needReloadAnnouncement, setNeedReloadAnnouncement]);

    if (!data) return <Loading />;

    if (data.status !== 'success') return <WishError res={data} reload={mutate} />;

    const announcements =
        data.data.length > 0 ? (
            data.data.map((item) => <Announcement announcement={item} key={item.id} style={{ marginBottom: '24px' }} />)
        ) : (
            <Empty description={'暂无公告'} />
        );

    return <div>{announcements}</div>;
}

export function AnnouncementPage() {
    return (
        <div>
            <AnnouncementList />
        </div>
    );
}
