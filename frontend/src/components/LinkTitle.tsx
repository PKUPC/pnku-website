import React from 'react';
import { Link } from 'react-router-dom';

import styles from './LinkTitle.module.css';

export function LinkTitle({
    icon,
    title,
    url,
}: {
    icon: React.ReactNode;
    title: string | React.ReactNode;
    url: string;
}) {
    return (
        <div className={styles.linkTitle}>
            <Link to={url}>
                {icon} {title}
            </Link>
        </div>
    );
}

export function ClickTitle({
    icon,
    title,
    onClick,
}: {
    icon: React.ReactNode;
    title: string | React.ReactNode;
    onClick: () => void;
}) {
    return (
        <div className={styles.clickTitle} onClick={onClick}>
            {icon} {title}
        </div>
    );
}
