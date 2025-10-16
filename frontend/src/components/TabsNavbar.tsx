import { ConfigProvider, Menu, MenuProps } from 'antd';
import { ReactNode, useCallback } from 'react';
import { useNavigate } from 'react-router';

import { useTheme } from '@/logic/contexts';

export type MenuItem = {
    label: string | ReactNode;
    key: string;
    icon?: ReactNode;
};

export function TabsNavbar({
    items,
    selectedKeys,
    onClick,
}: {
    items: MenuItem[];
    selectedKeys?: string[];
    onClick?: NonNullable<MenuProps['onClick']>;
}) {
    const navigate = useNavigate();
    const { color } = useTheme();

    const defaultOnClick = useCallback<NonNullable<MenuProps['onClick']>>(
        (e) => {
            if (e.key.startsWith('/')) {
                navigate(e.key);
            }
        },
        [navigate],
    );

    return (
        <ConfigProvider
            theme={{
                components: {
                    Menu: {
                        horizontalItemSelectedColor: color.baseContent,
                        horizontalLineHeight: '36px',
                        iconMarginInlineEnd: 4,
                        itemPaddingInline: 10,
                    },
                },
            }}
        >
            <Menu items={items} mode="horizontal" selectedKeys={selectedKeys} onClick={onClick ?? defaultOnClick} />
        </ConfigProvider>
    );
}
