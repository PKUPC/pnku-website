import { ExclamationCircleFilled, LockTwoTone, UnlockTwoTone } from '@ant-design/icons';
import { Button, Collapse, CollapseProps, Empty, Modal, Tag, Tooltip, message } from 'antd';
import { useContext } from 'react';
import { KeyedMutator } from 'swr';

import { EyeIcon } from '@/SvgIcons';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useCooldown } from '@/hooks/useCooldown';
import { GameStatusContext, useTheme } from '@/logic/contexts.ts';
import { useWishData } from '@/logic/swrWrappers';
import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';
import { format_ts_to_HMS } from '@/utils.ts';

import styles from './HintList.module.css';

function LockedHint({
    puzzleKey,
    hint,
    mutate,
}: {
    puzzleKey: string;
    hint: Wish.Puzzle.HintItem;
    mutate: KeyedMutator<Wish.Puzzle.GetHintsApi['response']>;
}) {
    const [messageApi, messageContextHolder] = message.useMessage();
    const [modalApi, modalContextHolder] = Modal.useModal();
    const { currentAp, updateCurrentAp } = useContext(GameStatusContext);
    const [cooling, countdown] = useCooldown(hint.effective_after_ts);
    const { color } = useTheme();

    const showConfirm = (hint: Wish.Puzzle.HintItem) => {
        modalApi.confirm({
            title: '购买提示确认',
            icon: <ExclamationCircleFilled />,
            content: (
                <span>
                    该提示花费： {hint.cost} 注意力 <EyeIcon style={{ color: 'transparent' }} /> 。
                </span>
            ),
            onOk() {
                wish({
                    endpoint: 'puzzle/buy_hint',
                    payload: { puzzle_key: puzzleKey, hint_id: hint.id },
                }).then((res) => {
                    if (res.status === 'error') {
                        messageApi.error({ content: res.message, key: 'BuyHint', duration: 3 }).then();
                    } else {
                        messageApi.success({ content: '购买成功', key: 'BuyHint', duration: 2 }).then();
                        mutate().then();
                        updateCurrentAp();
                    }
                });
            },
        });
    };

    const hintTooExpensive = currentAp < hint.cost;
    const hintExpensiveNotice = '注意力数量不足，请获取更多注意力再来解锁';

    // const buttonText = cooling ? format_ts_to_HMS(countdown) :
    //     <span>购买（ {hint.cost} {<EyeIcon style={{color: "transparent"}}/>}）</span>;
    const buttonText = (
        <span>
            购买（ {hint.cost} {<EyeIcon style={{ color: 'transparent' }} />}）
        </span>
    );

    const collapseItem: CollapseProps['items'] = [
        {
            key: `hint-${hint.id}`,
            collapsible: 'disabled',
            label: (
                <span>
                    {<LockTwoTone twoToneColor={[color.error, color.base100]} />}&nbsp;
                    {hint.question}&nbsp;&nbsp;
                    <Tag style={{ color: '#bbb' }}>{hint.type}</Tag>
                    {cooling && <Tag color={'orange'}>{format_ts_to_HMS(countdown)}</Tag>}
                </span>
            ),
            extra: (
                <Tooltip title={hintTooExpensive ? hintExpensiveNotice : ''}>
                    <Button size="small" disabled={hintTooExpensive || cooling} onClick={() => showConfirm(hint)}>
                        {buttonText}
                    </Button>
                </Tooltip>
            ),
            children: hint.answer,
        },
    ];
    return (
        <>
            {modalContextHolder}
            {messageContextHolder}
            <Collapse items={collapseItem} key={`hint-collapse-${hint.id}`} />
        </>
    );
}

function UnlockedHint({ hint }: { hint: Wish.Puzzle.HintItem }) {
    const { color } = useTheme();
    const collapseItem: CollapseProps['items'] = [
        {
            key: `hint-${hint.id}`,
            label: (
                <span>
                    <UnlockTwoTone twoToneColor={[color.success, color.base100]} />
                    &nbsp;
                    {hint.question}&nbsp;&nbsp;
                    <Tag>{hint.type}</Tag>
                </span>
            ),
            children: hint.answer,
        },
    ];
    return <Collapse items={collapseItem} key={`hint-collapse-${hint.id}`} />;
}

export function HintList({ puzzleKey }: { puzzleKey: string }) {
    const { data, mutate } = useWishData({
        endpoint: 'puzzle/get_hints',
        payload: { puzzle_key: puzzleKey },
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    let component;
    if (data.data.list.length === 0)
        component = <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={'暂时没有可用的观测。'} />;
    else
        component = data.data.list.map((hint) =>
            hint.unlock ? (
                <UnlockedHint key={hint.id} hint={hint} />
            ) : (
                <LockedHint key={hint.id} puzzleKey={puzzleKey} hint={hint} mutate={mutate} />
            ),
        );

    return <div className={styles.hintsList}>{component}</div>;
}
