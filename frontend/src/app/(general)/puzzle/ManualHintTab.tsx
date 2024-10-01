import { Alert } from 'antd';

import ApStatus from '@/app/(general)/puzzle/components/ApStatus';
import { ManualHintList } from '@/app/(general)/puzzle/components/ManualHintList.tsx';
import { RequestManualHintPanel } from '@/app/(general)/puzzle/components/RequestManualHintPanel.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useCooldown } from '@/hooks/useCooldown';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { Wish } from '@/types/wish.ts';
import { format_ts, format_ts_to_HMS } from '@/utils.ts';

function DisabledInfo({ disabledReason }: { disabledReason: string }) {
    return <Alert type={'warning'} message={disabledReason} />;
}

function ManualHintContent({
    ticketHintInfo,
    puzzleData,
    reloadManualHintList,
}: {
    ticketHintInfo: Wish.Ticket.TicketHintInfo;
    puzzleData: Wish.Puzzle.PuzzleDetailData;
    reloadManualHintList: () => void;
}) {
    const [cooling, countdown] = useCooldown(ticketHintInfo.effective_after_ts);

    let requestManualComponent;
    if (cooling) {
        requestManualComponent = <DisabledInfo disabledReason={`本题神谕解锁倒计时：${format_ts_to_HMS(countdown)}`} />;
    } else if (ticketHintInfo.disabled) {
        let activeHintsReason = '';
        if (ticketHintInfo.hints_open && ticketHintInfo.hints_open.length > 0) {
            activeHintsReason =
                '当前 ' + ticketHintInfo.hints_open.map((s) => `【${s}】`) + '题目的神谕处于未完成状态。';
        }
        requestManualComponent = (
            <DisabledInfo disabledReason={(ticketHintInfo.disabled_reason ?? '请求神谕已禁用！') + activeHintsReason} />
        );
    } else
        requestManualComponent = (
            <RequestManualHintPanel puzzleData={puzzleData} reloadManualHintList={reloadManualHintList} />
        );
    return requestManualComponent;
}

export function ManualHintTab({ puzzleData }: { puzzleData: Wish.Puzzle.PuzzleDetailData }) {
    const { data, mutate } = useWishData({
        endpoint: 'ticket/get_manual_hints',
        payload: { puzzle_key: puzzleData.key },
    });
    const info = useSuccessGameInfo();

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;
    const banned = info.team!.ban_list.ban_manual_hint_until > new Date().getTime() / 1000;
    const bannedText = `您的队伍的神谕功能被禁用至 ${format_ts(info.team!.ban_list.ban_manual_hint_until)}。`;

    return (
        <div>
            <ApStatus />
            <br />
            {banned && <Alert type={'error'} showIcon={true} description={bannedText} />}
            {!banned && (
                <ManualHintContent
                    ticketHintInfo={data.data}
                    puzzleData={puzzleData}
                    reloadManualHintList={() => mutate()}
                />
            )}
            {data.data.list.length > 0 && (
                <div className="mt-5">
                    <h2 className="text-3xl font-medium">神谕列表</h2>
                    <ManualHintList ticketHintInfo={data.data} />
                </div>
            )}
        </div>
    );
}
