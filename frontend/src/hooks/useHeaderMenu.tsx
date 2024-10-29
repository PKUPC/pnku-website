import {
    AppstoreOutlined,
    DisconnectOutlined,
    FileTextOutlined,
    LoginOutlined,
    NotificationOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import { ReactNode } from 'react';
import { BiNavigation } from 'react-icons/bi';

import { EveryUserIcon, HomeIcon, IdCardIcon, PlazaIcon, RankingIcon } from '@/SvgIcons.tsx';
import { ImageWithSkeleton } from '@/components/ImageWithSkeleton.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo } from '@/logic/contexts.ts';
import { make_auth_url } from '@/utils.ts';

type LinkMenuItem = {
    type: 'link';
    label: string | ReactNode;
    href: string;
    key: string;
    icon?: ReactNode;
};

type ButtonMenuItem = {
    type: 'button';
    label: string | ReactNode;
    key: string;
    icon?: ReactNode;
    onClick: () => void;
    buttonType: 'normal' | 'danger';
};

type DividerMenuItem = {
    type: 'divider';
};

type SubMenuItem = {
    type: 'submenu';
    label: string | ReactNode;
    key: string;
    width: number;
    icon?: ReactNode;
    children: MenuItem[];
};

type MenuItem = LinkMenuItem | DividerMenuItem | ButtonMenuItem;
type MenuItems = (MenuItem | SubMenuItem)[];

export function useHeaderMenu(compact: boolean = false) {
    const info = useSuccessGameInfo();

    const items: MenuItems = [];
    const compactItems: MenuItem[] = [];
    // 主页，在序章开放后并且组队之后就能看到区域列表
    if (ARCHIVE_MODE && (!info.user || (info.user.group !== 'staff' && (!info.team || !info.game.isPrologueUnlock)))) {
        items.push({ type: 'link', label: '主页', href: '/home', key: '/home', icon: <HomeIcon /> });
    } else {
        const submenuItems: MenuItem[] = [{ type: 'link', label: '主页', key: '/home', href: '/home' }];
        submenuItems.push({ type: 'divider' });
        info.areas.forEach((area) => {
            submenuItems.push({
                type: 'link',
                href: area.buttonLink,
                label: area.title === 'P&KU 3' ? '序章' : area.title,
                key: area.buttonLink,
            });
        });
        // 对于普通玩家，只有在游戏开始后且队伍开始游戏后能看到谜题一览和情报一览
        if (
            (info.user?.group === 'player' && info.game.isGameBegin && info.team?.gaming) ||
            info.user?.group == 'staff' ||
            ARCHIVE_MODE
        ) {
            submenuItems.push({ type: 'divider' });
            submenuItems.push({ type: 'link', href: '/puzzle-list', label: '谜题一览', key: '/puzzle-list' });
            submenuItems.push({ type: 'link', href: '/story-list', label: '情报一览', key: '/story-list' });
        }
        items.push({
            type: 'submenu',
            label: '区域',
            key: '_/area',
            icon: <AppstoreOutlined />,
            children: submenuItems,
            width: 8,
        });
    }
    const aboutItem = {
        type: 'link',
        href: '/about/introduction',
        label: '关于',
        key: '/about/introduction',
        icon: <FileTextOutlined />,
    } as LinkMenuItem;

    if (compact) compactItems.push(aboutItem);
    else items.push(aboutItem);

    // 如果是存档模式可以看到排行榜、信息和浏览设置
    if (ARCHIVE_MODE) {
        if (info.game.boards.length > 0) {
            const boardItem = {
                type: 'link',
                href: `/boards?name=${info.game.boards[0]}`,
                label: '排行榜',
                key: '/boards',
                icon: <RankingIcon />,
            } as LinkMenuItem;
            if (compact) compactItems.push(boardItem);
            else items.push(boardItem);
        }

        const infoItem = {
            type: 'link',
            href: '/info/announcements',
            label: '信息',
            key: '/info/announcements',
            icon: <NotificationOutlined />,
        } as LinkMenuItem;
        if (compact) compactItems.push(infoItem);
        else items.push(infoItem);

        const settingItem = {
            type: 'link',
            href: '/setting',
            icon: <SettingOutlined />,
            label: '浏览设置',
            key: '/setting',
        } as LinkMenuItem;

        if (compact) compactItems.push(settingItem);
        else items.push(settingItem);

        if (compact) {
            items.push({
                type: 'submenu',
                key: '_/nav',
                label: '导航',
                width: 8,
                icon: <BiNavigation />,
                children: compactItems,
            });
        }
    }
    // 否则，如果未登录，只能看见登录按钮
    else if (!info.user) {
        // 如果未登录并且是 compact 模式，把关于页面也在这里加上
        if (compact)
            items.push({
                type: 'link',
                href: '/about/introduction',
                label: '关于',
                key: '/about/introduction',
                icon: <FileTextOutlined />,
            });
        items.push({
            type: 'link',
            href: '/login',
            label: '登录',
            key: '/login',
            icon: <LoginOutlined />,
        });
    }
    // 登陆后的按钮
    else {
        if (info.game.boards.length > 0) {
            const boardItem = {
                type: 'link',
                href: `/boards?name=${info.game.boards[0]}`,
                label: '排行榜',
                key: '/boards',
                icon: <RankingIcon />,
            } as LinkMenuItem;
            if (compact) compactItems.push(boardItem);
            else items.push(boardItem);
        }

        const infoItem = {
            type: 'link',
            href: '/info/announcements',
            label: '信息',
            key: '/info/announcements',
            icon: <NotificationOutlined />,
        } as LinkMenuItem;
        if (compact) compactItems.push(infoItem);
        else items.push(infoItem);

        const plazaItem = {
            type: 'link',
            href: '/plaza',
            label: '队伍广场',
            key: '/plaza',
            icon: <PlazaIcon />,
        } as LinkMenuItem;

        if (compact) compactItems.push(plazaItem);
        else items.push(plazaItem);

        if (compact) {
            items.push({
                type: 'submenu',
                key: '_/nav',
                label: '导航',
                width: 8,
                icon: <BiNavigation />,
                children: compactItems,
            });
        }

        const submenuItems: MenuItem[] = [];
        submenuItems.push({
            type: 'link',
            href: '/user/profile',
            icon: <IdCardIcon />,
            label: '个人中心',
            key: '/user/profile',
        });

        if (info.user.group === 'staff') {
            submenuItems.push({
                type: 'link',
                href: '/staff/teams',
                icon: <EveryUserIcon />,
                label: '比赛管理',
                key: '/staff/teams',
            });
        }

        // 正式开赛并且队伍开始游戏后才能看到队伍动态
        if (info.team?.gaming && info.game.isGameBegin) {
            submenuItems.push({
                type: 'link',
                href: '/team/ap-history',
                icon: <EveryUserIcon />,
                label: '队伍动态',
                key: '/team/ap-history',
            });
        }

        submenuItems.push({
            type: 'link',
            href: '/setting',
            icon: <SettingOutlined />,
            label: '网站设置',
            key: '/setting',
        });

        submenuItems.push({
            type: 'button',
            icon: <DisconnectOutlined />,
            label: '注销',
            key: '_/user/logout',
            buttonType: 'danger',
            onClick: () => {
                sessionStorage.clear();
                try {
                    if (window.logout) window.logout();
                } catch {
                    /* empty */
                }
                window.location.href = make_auth_url(`logout?rem=${window.rem}&ram=${window.ram}`);
            },
        });

        items.push({
            type: 'submenu',
            label: (
                <div className="avatar">
                    <div className="rounded-xl">
                        <ImageWithSkeleton
                            src={info.user.profile.avatar_url}
                            alt="avatar"
                            width="1.75rem"
                            height="1.75rem"
                        />
                    </div>
                </div>
            ),
            key: '_/user',
            // icon: <UserOutlined />,
            children: submenuItems,
            width: 9,
        });
    }

    return items;
}

export type { MenuItem, SubMenuItem, MenuItems, LinkMenuItem, ButtonMenuItem, DividerMenuItem };
