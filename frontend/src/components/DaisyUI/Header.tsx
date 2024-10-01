import { useRef } from 'react';
import { Link } from 'react-router-dom';

import { GAME_LOGO, GAME_SHORT_TITLE, GAME_TITLE } from '@/constants.tsx';
import { ButtonMenuItem, LinkMenuItem, SubMenuItem, useHeaderMenu } from '@/hooks/useHeaderMenu.tsx';
import { blurActivateElement } from '@/utils.ts';

function HeaderMenuButton({ item }: { item: ButtonMenuItem }) {
    return (
        <button
            className={
                'btn btn-neutral justify-start px-3 md:px-4 font-normal' +
                (item.buttonType === 'danger' ? ' text-error' : '')
            }
            onClick={() => {
                item.onClick();
                blurActivateElement();
            }}
        >
            {item.icon}
            {item.label}
        </button>
    );
}

function HeaderMenuLink({ item }: { item: LinkMenuItem }) {
    return (
        <Link
            className="btn btn-neutral justify-start px-3 md:px-4 font-normal"
            to={item.href}
            onClick={() => blurActivateElement()}
        >
            {item.icon}
            {item.label}
        </Link>
    );
}

function DropdownSubmenu({ submenuItem, position }: { submenuItem: SubMenuItem; position?: 'start' | 'end' }) {
    const buttonRef = useRef<HTMLDivElement>(null);
    return (
        <div
            className={`dropdown dropdown-hover ${position === 'end' ? 'dropdown-end' : 'dropdown-start'}`}
            onMouseLeave={() => {
                if (buttonRef.current) buttonRef.current.blur();
            }}
        >
            <div
                tabIndex={0}
                role="button"
                className="btn btn-neutral rounded-btn px-3 md:px-4 font-normal"
                ref={buttonRef}
            >
                {submenuItem.icon}
                {submenuItem.label}
            </div>
            <div tabIndex={0} className="dropdown-content z-40 pt-2" style={{ width: submenuItem.width + 'rem' }}>
                <div className="menu bg-neutral text-neutral-content rounded-box">
                    {submenuItem.children.map((child, index) => {
                        if (child.type === 'link') return <HeaderMenuLink item={child} key={child.key} />;
                        else if (child.type === 'button') return <HeaderMenuButton item={child} key={child.key} />;
                        else if (child.type === 'divider')
                            return <div key={`divider-${index}`} className="border-t border-neutral-content"></div>;
                    })}
                </div>
            </div>
        </div>
    );
}

function MenuHorizontal({ compact }: { compact?: boolean }) {
    const headerItems = useHeaderMenu(compact ?? false);
    return (
        <div role="list" className="menu menu-horizontal p-0">
            {headerItems.map((item, index, items) => {
                if (item.type === 'submenu') {
                    return (
                        <DropdownSubmenu
                            key={item.key}
                            submenuItem={item}
                            position={index === items.length - 1 ? 'end' : 'start'}
                        />
                    );
                } else if (item.type === 'link') return <HeaderMenuLink item={item} key={item.key} />;
                else if (item.type === 'button') return <HeaderMenuButton item={item} key={item.key} />;
            })}
        </div>
    );
}

export function Header() {
    const headerItems = useHeaderMenu();
    console.log(headerItems);

    return (
        <div className="fixed top-0 left-0 w-full z-50 h-12 bg-neutral">
            <div className="navbar bg-neutral text-neutral-content min-h-12 h-12 max-w-[75rem] m-auto">
                <div className="flex-1">
                    <Link to={'/home'}>
                        <div className="text-[1.1rem] font-semibold lg:w-64 md:w-32 flex flex-row items-center cursor-pointer">
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
                </div>
                <div className="flex-none hidden w640:flex">
                    <MenuHorizontal compact={false} />
                </div>
                <div className="flex-none w640:hidden">
                    <MenuHorizontal compact={true} />
                </div>
            </div>
        </div>
    );
}
