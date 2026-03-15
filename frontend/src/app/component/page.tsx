import { useMemo } from 'react';
import { useSearchParams } from 'react-router';

import { RemoteComponent } from '@/remote/RemoteComponent';

import NotFound from '../NotFound';

interface ComponentData {
    name: string;
    url: string;
    props: Record<string, unknown>;
}

export function ComponentPage() {
    const [searchParams] = useSearchParams();
    const key = searchParams.get('key');

    const data = useMemo<ComponentData | null>(() => {
        if (!key) {
            return null;
        }

        try {
            // 解码base64字符串
            const base64Decoded = atob(key);

            // 将二进制字符串转换为Uint8Array
            const bytes = new Uint8Array(base64Decoded.length);
            for (let i = 0; i < base64Decoded.length; i++) {
                bytes[i] = base64Decoded.charCodeAt(i);
            }

            // 使用TextDecoder解码UTF-8字符串
            const utf8String = new TextDecoder('utf-8').decode(bytes);

            // 解析JSON
            const parsedData: Record<string, unknown> = JSON.parse(utf8String);

            // 检查是否有name和url字段
            if (!parsedData.name || !parsedData.url) {
                return null;
            }

            // 提取name和url，剩余字段作为props
            const { name, url, ...props } = parsedData;

            return {
                name: name as string,
                url: url as string,
                props: props as Record<string, unknown>,
            };
        } catch (error) {
            // 如果解码或解析失败，返回null
            console.error('Failed to decode or parse key:', error);
            return null;
        }
    }, [key]);

    if (!data) {
        return <NotFound />;
    }

    return (
        <div className="mt-12 w-full">
            <RemoteComponent componentName={data.name} componentUrl={data.url} {...data.props} />
        </div>
    );
}
