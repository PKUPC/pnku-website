import React from 'react';

import styles from './FancierCard.module.css';

export function FancierCard({
    title,
    subTitle,
    style,
    extraClassName,
    children,
    logoUrl,
}: {
    title: string;
    subTitle?: string;
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

    const subTitleComponent = subTitle ? <span className={styles.subTitle}>{subTitle}</span> : <></>;

    return (
        <div className={styles.fancierCard + (extraClassName ? ' ' + extraClassName : '')} style={style ?? {}}>
            <div className={styles.title}>
                <span data-text={title}>{title}</span>
                {subTitleComponent}
            </div>
            <div className={styles.contentContainer}>
                {logoComponent}
                <div className={styles.childrenWrapper}>{children}</div>
            </div>
        </div>
    );
}
