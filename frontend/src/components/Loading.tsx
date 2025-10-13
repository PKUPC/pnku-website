import { CSSProperties, ReactNode } from 'react';

export function Loading({
    className,
    style,
    text,
}: {
    className?: string;
    style?: CSSProperties;
    text?: ReactNode | string;
}) {
    const extraClassName = className ? ' ' + className : '';
    const mixedStyle = !className && !style ? { height: 350 } : style;
    return (
        <div className={'flex justify-center flex-col items-center' + extraClassName} style={mixedStyle}>
            <span className="loading loading-infinity loading-lg"></span>
            {text ? text : '加载中'}
        </div>
    );
}
