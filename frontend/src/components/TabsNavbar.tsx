import { ReactNode } from 'react';
import { Link } from 'react-router';

import { cn } from '@/utils';

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
                                className={cn(
                                    'relative inline-block p-2',
                                    'after:content-[""] after:absolute after:-bottom-0.5 after:left-1 after:right-1 after:border-b-2 after:border-b-base-200',
                                    selectedKeys?.includes(item.key)
                                        ? 'after:border-b-base-content hover:after:border-b-base-content'
                                        : 'after:border-b-base-content/0 hover:after:border-b-base-content/60',
                                )}
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
                            className={cn(
                                'cursor-pointer relative inline-block p-2',
                                'after:content-[""] after:absolute after:-bottom-0.5 after:left-1 after:right-1 after:border-b-2 after:border-b-base-200',
                                selectedKeys?.includes(item.key)
                                    ? 'after:border-b-base-content hover:after:border-b-base-content'
                                    : 'after:border-b-base-content/0 hover:after:border-b-base-content/60',
                            )}
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
