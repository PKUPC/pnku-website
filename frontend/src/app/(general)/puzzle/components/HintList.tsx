import { ExclamationCircleFilled, LockTwoTone, UnlockTwoTone } from '@ant-design/icons';
import { Button, Collapse, CollapseProps, Empty, Modal, Tag, Tooltip, message } from 'antd';
import { useContext } from 'react';
import { KeyedMutator } from 'swr';

import { Loading } from '@/components/DaisyUI/Loading.tsx';
import NamedIcon from '@/components/NamedIcon';
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
    const { currencies, syncAllCurrencies } = useContext(GameStatusContext);
    const [cooling, countdown] = useCooldown(hint.effective_after_ts);
    const { color } = useTheme();

    // 处理价格信息
    const processPriceInfo = () => {
        if (!hint.price || hint.price.length === 0) {
            return {
                canPurchase: false,
                reason: '状态异常，请咨询工作人员',
                priceElement: <span>无法购买</span>,
                missingCurrencies: [],
                unknownCurrencies: [],
            };
        }

        const missingCurrencies: string[] = [];
        const unknownCurrencies: string[] = [];
        let canPurchase = true;

        // 检查每种货币
        for (const priceItem of hint.price) {
            const currency = currencies.find((c) => c.type === priceItem.type);
            if (!currency) {
                unknownCurrencies.push(priceItem.type);
                canPurchase = false;
            } else if (currency.balance < priceItem.price) {
                const shortage = priceItem.price - currency.balance;
                missingCurrencies.push(
                    `${currency.name} 缺少 ${(shortage / currency.denominator).toFixed(currency.precision)}`,
                );
                canPurchase = false;
            }
        }

        // 生成价格文本
        const priceElements = hint.price.map((priceItem) => {
            const currency = currencies.find((c) => c.type === priceItem.type);
            if (currency) {
                return (
                    <span key={priceItem.type}>
                        {(priceItem.price / currency.denominator).toFixed(currency.precision)} {currency.name}{' '}
                        <NamedIcon
                            iconName={currency.icon}
                            style={{ color: 'transparent', transform: 'translateY(0.1em)' }}
                        />
                    </span>
                );
            }
            return (
                <span key={priceItem.type}>
                    {priceItem.price} {priceItem.type}
                </span>
            );
        });

        const priceElement =
            priceElements.length === 1 ? (
                priceElements[0]
            ) : (
                <span>
                    {priceElements.map((element, index) => (
                        <span key={index}>
                            {element}
                            {index < priceElements.length - 1 && ' 和 '}
                        </span>
                    ))}
                </span>
            );

        // 生成无法购买的原因
        let reason = '';
        if (unknownCurrencies.length > 0) {
            reason = '需要未知的货币';
        } else if (missingCurrencies.length > 0) {
            reason = missingCurrencies.join('; ');
        }

        return {
            canPurchase,
            reason,
            priceElement,
            missingCurrencies,
            unknownCurrencies,
        };
    };

    const priceInfo = processPriceInfo();

    const showConfirm = (hint: Wish.Puzzle.HintItem) => {
        modalApi.confirm({
            title: '购买提示确认',
            icon: <ExclamationCircleFilled />,
            content: <span>该提示花费：{priceInfo.priceElement}</span>,
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
                        syncAllCurrencies();
                    }
                });
            },
        });
    };

    const buttonText = <span>购买（{priceInfo.priceElement}）</span>;

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
                <Tooltip title={!priceInfo.canPurchase ? priceInfo.reason : ''}>
                    <Button size="small" disabled={!priceInfo.canPurchase || cooling} onClick={() => showConfirm(hint)}>
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
