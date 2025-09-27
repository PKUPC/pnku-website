import { Tag } from 'antd';
import { useContext } from 'react';

import NamedIcon from '@/components/NamedIcon';
import { CurrencyDetail, GameStatusContext } from '@/logic/contexts.ts';

export default function CurrencyStatus({ currencyDetail }: { currencyDetail: CurrencyDetail }) {
    return (
        <div>
            <Tag>
                <span>
                    {`当前${currencyDetail.name}`} :{' '}
                    {(currencyDetail.balance / currencyDetail.denominator).toFixed(currencyDetail.precision)}{' '}
                    <NamedIcon
                        iconName={currencyDetail.icon}
                        style={{ color: 'transparent', transform: 'translateY(0.1em)' }}
                    />
                </span>
                <span>
                    {' '}
                    (+{(currencyDetail.currentIncrease / currencyDetail.denominator).toFixed(
                        currencyDetail.precision,
                    )}{' '}
                    <NamedIcon
                        iconName={currencyDetail.icon}
                        style={{ color: 'transparent', transform: 'translateY(0.1em)' }}
                    />{' '}
                    / min)
                </span>
            </Tag>
        </div>
    );
}

export function CurrencyStatusList() {
    const { currencies } = useContext(GameStatusContext);
    return (
        <div>
            {currencies.map((currency) => (
                <CurrencyStatus key={currency.type} currencyDetail={currency} />
            ))}
        </div>
    );
}
