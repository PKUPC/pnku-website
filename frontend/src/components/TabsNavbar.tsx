import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

import styles from './TabsNavbar.module.css';

export type MenuItem = {
    type: string;
    href?: string;
    label: string | ReactNode;
    key: string;
    icon?: ReactNode;
    onClick?: () => void;
};

export function TabsNavbar({ selectedKeys, items }: { selectedKeys?: string[]; items: MenuItem[] }) {
    return (
        <div role="tablist" className={'flex border-b-base-200 border-b-2 relative gap-2 text-[0.875rem]'}>
            {items.map((item) => {
                if (item.type === 'link') {
                    return (
                        <Link to={item.href ?? item.key} key={item.key}>
                            <div
                                role="tab"
                                className={
                                    styles.tab + (selectedKeys?.includes(item.key) ? ' ' + styles.tabActive : '')
                                }
                            >
                                {item.icon}
                                <span className="ml-1">{item.label}</span>
                            </div>
                        </Link>
                    );
                } else if (item.type === 'button') {
                    return (
                        <div
                            key={item.key}
                            role="tab"
                            className={
                                'cursor-pointer ' +
                                styles.tab +
                                (selectedKeys?.includes(item.key) ? ' ' + styles.tabActive : '')
                            }
                            onClick={item.onClick}
                        >
                            {item.icon}
                            <span className="ml-1">{item.label}</span>
                        </div>
                    );
                }
                return <></>;
            })}
        </div>
    );
}
