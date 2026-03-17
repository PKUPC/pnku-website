import { Image as AntdImage, ConfigProvider, Skeleton } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { CSSProperties, useLayoutEffect, useRef, useState } from 'react';

import { cn } from '@/utils';

import styles from './TemplateImage.module.css';

export function TemplateImage({
    src,
    alt,
    aspectRatio,
    className,
    preview,
    style,
}: {
    src: string;
    alt?: string;
    aspectRatio?: string;
    className?: string;
    preview?: boolean;
    style?: CSSProperties;
}) {
    const [loaded, setLoaded] = useState(false);
    const imageRef = useRef<HTMLImageElement | null>(null);

    // 直接给 AntdImage 传 Loading 样式会一坨，又拿不到 Image 的 load 状态，只能出此下策
    useLayoutEffect(() => {
        const image = new Image();
        imageRef.current = image;

        imageRef.current.src = src;
        if (image.complete) {
            setLoaded(true);
        }
        image.onload = () => {
            setLoaded(true);
        };
        image.onerror = () => {
            setLoaded(true);
        };

        return () => {
            if (imageRef.current === image) {
                imageRef.current = null;
            }
            image.onload = null;
            image.onerror = null;
        };
    }, [src]);

    return (
        <div
            className={cn(styles.templateImageContainer, className)}
            style={{ aspectRatio: aspectRatio, lineHeight: 0, ...style }}
        >
            {loaded ? (
                <ConfigProvider locale={zhCN}>
                    <AntdImage src={src} alt={alt || 'image'} preview={preview === undefined ? false : preview} />
                </ConfigProvider>
            ) : (
                <Skeleton.Image active={true} className={styles.skeleton} />
            )}
        </div>
    );
}
