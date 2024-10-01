import { useContext, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

import { TicketDetail } from '@/app/(general)/ticket-detail/TicketDetail.tsx';
import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { GameStatusContext, useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';

function TicketBody({ tid }: { tid: number }) {
    const { data, mutate } = useWishData({
        endpoint: 'ticket/get_ticket_detail',
        payload: { ticket_id: tid },
    });
    const { hasNewMessage, setHasNewMessage } = useContext(GameStatusContext);

    useEffect(() => {
        if (hasNewMessage) {
            mutate().then();
            setHasNewMessage(false);
        }
    }, [hasNewMessage, mutate, setHasNewMessage]);

    if (!data) return <Loading />;
    if (data.status !== 'success') return <WishError res={data} reload={mutate} />;

    return <TicketDetail ticketDetail={data.data} reloadTicketDetail={() => mutate()} />;
}

export function TicketDetailPage() {
    const info = useSuccessGameInfo();
    const [searchParams] = useSearchParams();

    if (!info.user) return <NotFound />;
    if (info.user?.group !== 'staff' && (!info.team?.gaming || !info.game.isGameBegin)) return <NotFound />;
    const tid = searchParams.get('id');
    if (!tid || isNaN(+tid)) return <NotFound />;

    return <TicketBody tid={parseInt(tid)} />;
}
