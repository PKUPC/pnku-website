import { useCallback, useMemo, useState } from 'react';

import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { wish } from '@/logic/wish';
import { Adhoc } from '@/types/wish';
import { calcCurrentBalance, getCurrentIncrease } from '@/utils';

type CurrencyData = {
    balance: number;
    currentIncrease: number;
    increasePolicy: [number, number][];
};

export function useCurrencies() {
    const info = useSuccessGameInfo();
    const currencies = useMemo(() => {
        return info.game?.currencies ?? [];
    }, [info.game?.currencies]);

    const [currencyData, setCurrencyData] = useState<Partial<Record<Adhoc.CurrencyType, CurrencyData>>>({});

    // 同步单个货币
    const syncCurrency = useCallback(async (currencyType: Adhoc.CurrencyType) => {
        try {
            const res = await wish({
                endpoint: 'game/team_currency_detail',
                payload: { currency_type: currencyType },
            });

            if (res.status !== 'error') {
                const { balance, increase_policy } = res.data;
                const currentIncrease = getCurrentIncrease(increase_policy);
                const currentBalance = calcCurrentBalance(balance, increase_policy);

                setCurrencyData((prev) => ({
                    ...prev,
                    [currencyType]: {
                        balance: currentBalance,
                        currentIncrease,
                        increasePolicy: increase_policy,
                    },
                }));

                console.log(`update current balance for ${currencyType}: ${balance}`);
            }
        } catch (error) {
            console.error(`Failed to sync currency ${currencyType}:`, error);
        }
    }, []);

    // 同步所有货币
    const syncAllCurrencies = useCallback(() => {
        currencies.forEach((currency) => {
            syncCurrency(currency.type);
        });
    }, [currencies, syncCurrency]);

    // 更新单个货币余额（基于本地数据重新计算）
    const updateCurrency = useCallback((currencyType: Adhoc.CurrencyType) => {
        setCurrencyData((prev) => {
            const data = prev[currencyType];
            if (data) {
                return {
                    ...prev,
                    [currencyType]: {
                        ...data,
                        balance: calcCurrentBalance(data.balance, data.increasePolicy),
                    },
                };
            }
            return prev;
        });
    }, []);

    // 更新所有货币余额
    const updateAllCurrencies = useCallback(() => {
        currencies.forEach((currency) => {
            updateCurrency(currency.type);
        });
    }, [currencies, updateCurrency]);

    // 获取格式化的货币数据
    const formattedCurrencies = currencies.map((currency) => ({
        type: currency.type,
        name: currency.name,
        icon: currency.icon,
        denominator: currency.denominator,
        precision: currency.precision,
        balance: currencyData[currency.type]?.balance ?? 0,
        currentIncrease: currencyData[currency.type]?.currentIncrease ?? 0,
        syncCurrency: () => syncCurrency(currency.type),
        updateCurrency: () => updateCurrency(currency.type),
    }));

    return {
        currencies: formattedCurrencies,
        syncAllCurrencies,
        updateAllCurrencies,
    };
}
