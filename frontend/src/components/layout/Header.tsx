import { NavigationMenu } from 'radix-ui';
import { forwardRef, useCallback, useState } from 'react';
import { Link } from 'react-router';

import { GAME_LOGO, GAME_SHORT_TITLE, GAME_TITLE } from '@/constants.tsx';
import { ButtonMenuItem, LinkMenuItem, SubMenuItem, useHeaderMenu } from '@/hooks/useHeaderMenu.tsx';
import { cn } from '@/utils.ts';

function HeaderMenuButton({ item, closeMenu }: { item: ButtonMenuItem; closeMenu?: () => void }) {
    return (
        <button
            className={cn(
                'flex h-10 w-full items-center gap-2 px-3 md:px-4 py-2 text-sm font-normal rounded-md bg-neutral hover:bg-neutral-hover transition-colors active:scale-97',
                item.buttonType === 'danger' ? ' text-error' : '',
            )}
            onClick={() => {
                item.onClick();
                if (closeMenu) {
                    closeMenu();
                }
            }}
        >
            {item.icon}
            {item.label}
        </button>
    );
}

const HeaderMenuLink = forwardRef<HTMLAnchorElement, { item: LinkMenuItem; closeMenu?: () => void }>(
    ({ item, closeMenu }, ref) => {
        return (
            <Link
                className={cn(
                    'text-neutral-content bg-neutral hover:bg-neutral-hover',
                    'flex h-10 items-center gap-2 px-3 md:px-4 py-2 text-sm font-normal rounded-md    transition-colors active:scale-97',
                )}
                to={item.href}
                ref={ref}
                onClick={() => {
                    if (closeMenu) {
                        closeMenu();
                    }
                }}
            >
                {item.icon}
                {item.label}
            </Link>
        );
    },
);
HeaderMenuLink.displayName = 'HeaderMenuLink';

function NavigationSubmenu({
    submenuItem,
    position,
    closeMenu,
}: {
    submenuItem: SubMenuItem;
    position?: 'start' | 'end';
    closeMenu?: () => void;
}) {
    return (
        <>
            <NavigationMenu.Trigger className="flex items-center gap-2 px-3 md:px-4 py-2 text-sm font-normal rounded-md bg-neutral text-neutral-content hover:bg-neutral-hover transition-colors cursor-pointer active:scale-97">
                {submenuItem.icon}
                {submenuItem.label}
            </NavigationMenu.Trigger>
            <NavigationMenu.Content
                className={cn(
                    'absolute top-full z-40 mt-2 rounded-lg bg-neutral shadow-lg p-2',
                    position === 'end' ? 'right-0' : 'left-0',
                )}
                style={{ width: submenuItem.width + 'rem' }}
            >
                {submenuItem.children.map((child, index) => {
                    if (child.type === 'link') {
                        return (
                            <NavigationMenu.Link asChild key={child.key}>
                                <HeaderMenuLink item={child} closeMenu={closeMenu} />
                            </NavigationMenu.Link>
                        );
                    } else if (child.type === 'button') {
                        return <HeaderMenuButton item={child} key={child.key} closeMenu={closeMenu} />;
                    } else if (child.type === 'divider') {
                        return <div key={`divider-${index}`} className="my-1 border-t border-neutral-600"></div>;
                    }
                    return null;
                })}
            </NavigationMenu.Content>
        </>
    );
}

function RadixNavigationMenu({ compact }: { compact?: boolean }) {
    const headerItems = useHeaderMenu(compact ?? false);
    const [currentValue, setCurrentValue] = useState('');
    const closeMenu = useCallback(() => {
        setCurrentValue('');
    }, []);

    return (
        <NavigationMenu.Root
            className="relative"
            delayDuration={50}
            value={currentValue}
            onValueChange={setCurrentValue}
        >
            <NavigationMenu.List className="flex items-center gap-2">
                {headerItems.map((item, index, items) => {
                    if (item.type === 'submenu') {
                        return (
                            <NavigationMenu.Item key={item.key}>
                                <NavigationSubmenu
                                    submenuItem={item}
                                    position={index === items.length - 1 ? 'end' : 'start'}
                                    closeMenu={closeMenu}
                                />
                            </NavigationMenu.Item>
                        );
                    } else if (item.type === 'link') {
                        return (
                            <NavigationMenu.Item key={item.key}>
                                <NavigationMenu.Link asChild>
                                    <HeaderMenuLink item={item} />
                                </NavigationMenu.Link>
                            </NavigationMenu.Item>
                        );
                    } else if (item.type === 'button') {
                        return (
                            <NavigationMenu.Item key={item.key}>
                                <HeaderMenuButton item={item} />
                            </NavigationMenu.Item>
                        );
                    }
                    return null;
                })}
            </NavigationMenu.List>

            {/* Viewport for positioning content */}
            <NavigationMenu.Viewport className="absolute top-full left-0 w-full" />
        </NavigationMenu.Root>
    );
}

export function Header() {
    const headerItems = useHeaderMenu();
    console.log(headerItems);

    return (
        <div className="fixed top-0 left-0 w-full z-50 h-12 bg-neutral">
            <div className="flex items-center justify-between h-12 max-w-300 mx-auto px-2">
                {/* <div className="flex-1"> */}
                <Link to={'/home'}>
                    <div className="text-[1.1rem] font-semibold lg:w-64 md:w-32 flex flex-row items-center cursor-pointer text-neutral-100">
                        <div
                            className="w-7 inline-block ml-[0.2rem] mr-[0.3rem]"
                            style={{
                                filter: 'invert(100%)',
                                transform: 'translateY(0rem) scale(1.4)',
                            }}
                        >
                            {GAME_LOGO}
                        </div>
                        <div className="hidden lg:flex">{GAME_TITLE}</div>
                        <div className="flex lg:hidden">{GAME_SHORT_TITLE}</div>
                    </div>
                </Link>
                {/* </div> */}

                <div className="flex-none hidden w640:flex">
                    <RadixNavigationMenu compact={false} />
                </div>
                <div className="flex-none w640:hidden">
                    <RadixNavigationMenu compact={true} />
                </div>
            </div>
        </div>
    );
}
