import { ARCHIVE_MODE, TEMPLATE_ROOT, WISH_ROOT } from '@/constants';
import { Wish } from '@/types/wish.ts';

export const WISH_VER = 'wish.2023.v6';

export function wish<T extends Wish.WishParams>({
    endpoint,
    payload,
}: T): Promise<Wish.ResponseMapping[T['endpoint']]> {
    console.log(endpoint, payload);
    console.log(WISH_ROOT + endpoint);

    if (ARCHIVE_MODE) {
        return new Promise((resolve) => {
            import('@/archive/archiveWish').then((module) => {
                const result = module.archiveWish({ endpoint, payload });
                // @ts-ignore
                resolve(result);
            });
        });
    }

    return fetch(WISH_ROOT + endpoint + (endpoint.includes('?') ? '&' : '?') + `rem=${window.rem}&ram=${window.ram}`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'X-Wish-Version': WISH_VER,
            'Content-Type': 'application/json',
        },
        body: payload ? JSON.stringify(payload) : '{}',
    })
        .then((res) => {
            if (res.status === 200) return res.json();
            else if (res.status === 429)
                return {
                    status: 'error',
                    title: '请求频率过快',
                    message: '请求频率太快了，让服务器休息一会吧。',
                };
            else
                return {
                    status: 'error',
                    title: 'HTTP_ERROR',
                    message: `HTTP ${res.status} 错误，服务暂时不可用，请稍后重试`,
                };
        })
        .catch((e) => {
            return {
                status: 'error',
                title: 'HTTP_REQ_FAILED',
                message: `网络错误 ${e}，请稍后重试`,
            };
        });
}

export function fetchTemplateFile(fileName: string): Promise<string> {
    if (ARCHIVE_MODE) {
        return new Promise((resolve) => {
            import('@/archive/archiveWish').then((module) => {
                const result = module.archiveFetchTemplateFile(fileName);
                // @ts-ignore
                resolve(result);
            });
        });
    }

    if (window.template) window.template(fileName);

    return fetch(TEMPLATE_ROOT + fileName, {
        method: 'GET',
        credentials: 'include',
    })
        .then((res) => {
            if (res.status !== 200) {
                throw new Error(`HTTP错误 ${res.status}`);
            } else {
                return res.text();
            }
        })
        .catch((e) => {
            throw new Error(`错误：${e.message}`);
        });
}
