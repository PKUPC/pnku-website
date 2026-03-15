import { Tag } from 'antd';
import { useContext } from 'react';

import NamedIcon from '@/components/NamedIcon';
import { CurrencyDetail, GameStatusContext } from '@/logic/contexts.ts';

export default function CurrencyStatus({ currencyDetail }: { currencyDetail: CurrencyDetail }) {
    return (
        <div className="inline-block">
            <Tag>
                <span>
                    {`当前${currencyDetail.name}`} :{' '}
                    {(currencyDetail.balance / currencyDetail.denominator).toFixed(currencyDetail.precision)}{' '}
                    <NamedIcon iconName={currencyDetail.icon} />
                </span>
                {currencyDetail.currentIncrease !== 0 && (
                    <span>
                        {' '}
                        (+
                        {(currencyDetail.currentIncrease / currencyDetail.denominator).toFixed(
                            currencyDetail.precision,
                        )}{' '}
                        <NamedIcon iconName={currencyDetail.icon} /> / min)
                    </span>
                )}
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
