import useSWR from 'swr';

import { wish } from '@/logic/wish';
import { Wish } from '@/types/wish.ts';

export function useWishContext<T extends Wish.WishParams>(key: T) {
    const { data, mutate } = useSWR(key, (key: T) => wish(key), { refreshInterval: 30 * 60 * 1000 });

    return { data, mutate };
}

export function useWishData<T extends Wish.WishParams>(key: T) {
    const { data, mutate } = useSWR(key, (key: T) => wish(key), {});
    return { data, mutate };
}
