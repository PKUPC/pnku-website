import React from 'react';

import styles from './InfoBox.module.css';

export default function InfoBox({
    title,
    backgroundColor,
    children,
}: {
    title?: string | React.ReactNode;
    children?: string | React.ReactNode;
    backgroundColor: string;
}) {
    return (
        <div className={styles.infoBox}>
            <div className={'wrapper'}>
                <div
                    className={'info-title-wrapper'}
                    style={{
                        backgroundColor: backgroundColor,
                    }}
                >
                    <div className={'info-title'}>{title}</div>
                </div>
                <div className={'info-content'}>{children}</div>
            </div>
        </div>
    );
}
