import React from 'react';

import styles from './FancySlimContainer.module.css';

export function FancySlimContainer({
    title,
    style,
    extraClassName,
    children,
    logoUrl,
}: {
    title: string;
    style?: React.CSSProperties;
    extraClassName?: string;
    children?: React.ReactNode;
    logoUrl?: string;
}) {
    const logoComponent = logoUrl ? (
        <div className={styles.logo}>
            <img src={logoUrl} alt="LOGO" />
        </div>
    ) : (
        <></>
    );

    return (
        <div className={styles.fancySlimContainer + (extraClassName ? ' ' + extraClassName : '')} style={style ?? {}}>
            <div className={styles.title}>
                <span data-text={title}>{title}</span>
            </div>
            <div className={styles.contentContainer}>
                {logoComponent}
                <div className={styles.childrenWrapper}>{children}</div>
            </div>
        </div>
    );
}

// eslint-disable-next-line react/display-name
FancySlimContainer.SubTitle = ({
    subTitle,
    extraClassName,
    style,
}: {
    subTitle: string;
    extraClassName?: string;
    style?: React.CSSProperties;
}) => {
    // 上方横线的宽度是根据这个字体估算的，并不准
    return (
        <div
            className={styles.subTitle + (extraClassName ? ' ' + extraClassName : '')}
            style={{ '--sub-title-width': `${subTitle.length * 2.5}rem`, ...style } as React.CSSProperties}
        >
            {subTitle}
        </div>
    );
};
