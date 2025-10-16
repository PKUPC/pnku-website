import {
    AppstoreOutlined,
    DisconnectOutlined,
    FileTextOutlined,
    LoginOutlined,
    NotificationOutlined,
    SettingOutlined,
} from '@ant-design/icons';
import { ConfigProvider, Menu } from 'antd';
import type { MenuProps } from 'antd';
import { useCallback, useMemo } from 'react';
import { BiNavigation } from 'react-icons/bi';
import { Link, useLocation, useNavigate } from 'react-router';

import { EveryUserIcon, HomeIcon, IdCardIcon, PlazaIcon, RankingIcon } from '@/SvgIcons.tsx';
import { ImageWithSkeleton } from '@/components/ImageWithSkeleton.tsx';
import { GAME_LOGO, GAME_SHORT_TITLE, GAME_TITLE } from '@/constants.tsx';
import { ARCHIVE_MODE } from '@/constants.tsx';
import { useSuccessGameInfo, useTheme, useWindowInfo } from '@/logic/contexts.ts';
import { make_auth_url } from '@/utils.ts';

function genHeaderMenu(info: ReturnType<typeof useSuccessGameInfo>, compact: boolean = false) {
    const items: MenuProps['items'] = [];
    const compactItems: MenuProps['items'] = [];

    // 主页，在序章开放后并且组队之后就能看到区域列表
    if (!ARCHIVE_MODE && (!info.user || (info.user.group !== 'staff' && (!info.team || !info.game.isPrologueUnlock)))) {
        items.push({ label: '主页', key: '/home', icon: <HomeIcon /> });
    } else {
        const submenuItems: MenuProps['items'] = [{ label: '主页', key: '/home' }];
        submenuItems.push({ type: 'divider' });
        info.areas.forEach((area) => {
            submenuItems.push({
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
            submenuItems.push({ label: '谜题一览', key: '/puzzle-list' });
            submenuItems.push({ label: '情报一览', key: '/story-list' });
        }
        items.push({
            type: 'submenu',
            label: '区域',
            key: '_/area',
            icon: <AppstoreOutlined />,
            children: submenuItems,
        });
    }
    const aboutItem = {
        label: '关于',
        key: '_/about',
        icon: <FileTextOutlined />,
    };

    if (compact) compactItems.push(aboutItem);
    else items.push(aboutItem);

    // 如果是存档模式可以看到排行榜、信息和浏览设置
    if (ARCHIVE_MODE) {
        if (info.game.boards.length > 0) {
            const boardItem = {
                label: '排行榜',
                key: '_/boards',
                icon: <RankingIcon />,
            };
            if (compact) compactItems.push(boardItem);
            else items.push(boardItem);
        }

        const infoItem = {
            label: '信息',
            key: '/info/announcements',
            icon: <NotificationOutlined />,
        };
        if (compact) compactItems.push(infoItem);
        else items.push(infoItem);

        const settingItem = {
            icon: <SettingOutlined />,
            label: '浏览设置',
            key: '/setting',
        };

        if (compact) compactItems.push(settingItem);
        else items.push(settingItem);

        if (compact) {
            items.push({
                type: 'submenu',
                key: '_/nav',
                label: '导航',
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
                label: '关于',
                key: '_/about',
                icon: <FileTextOutlined />,
            });
        items.push({
            label: '登录',
            key: '/login',
            icon: <LoginOutlined />,
        });
    }
    // 登陆后的按钮
    else {
        if (info.game.boards.length > 0) {
            const boardItem = {
                label: '排行榜',
                key: '_/boards',
                icon: <RankingIcon />,
            };
            if (compact) compactItems.push(boardItem);
            else items.push(boardItem);
        }

        const infoItem = {
            label: '信息',
            key: '/info/announcements',
            icon: <NotificationOutlined />,
        };
        if (compact) compactItems.push(infoItem);
        else items.push(infoItem);

        const plazaItem = {
            label: '队伍广场',
            key: '/plaza',
            icon: <PlazaIcon />,
        };

        if (compact) compactItems.push(plazaItem);
        else items.push(plazaItem);

        if (compact) {
            items.push({
                type: 'submenu',
                key: '_/nav',
                label: '导航',
                icon: <BiNavigation />,
                children: compactItems,
            });
        }

        const submenuItems: MenuProps['items'] = [];
        submenuItems.push({
            icon: <IdCardIcon />,
            label: '个人中心',
            key: '/user/profile',
        });

        if (info.user.group === 'staff') {
            submenuItems.push({
                icon: <EveryUserIcon />,
                label: '比赛管理',
                key: '/staff/teams',
            });
        }

        // 正式开赛并且队伍开始游戏后才能看到队伍动态
        if (info.team?.gaming && info.game.isGameBegin) {
            submenuItems.push({
                icon: <EveryUserIcon />,
                label: '队伍动态',
                key: '/team/submission-history',
            });
        }

        submenuItems.push({
            icon: <SettingOutlined />,
            label: '网站设置',
            key: '/setting',
        });

        submenuItems.push({
            icon: <DisconnectOutlined />,
            label: '注销',
            key: '_/user/logout',
            danger: true,
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
            children: submenuItems,
        });
    }

    return items;
}

function NavigationMenu() {
    const { windowWidth } = useWindowInfo();
    const info = useSuccessGameInfo();
    const navigate = useNavigate();
    const headerItems = useMemo(() => genHeaderMenu(info, windowWidth < 640), [info, windowWidth]);
    const { color } = useTheme();
    const { pathname } = useLocation();

    const onClick = useCallback<NonNullable<MenuProps['onClick']>>(
        (e) => {
            if (e.key.startsWith('/')) {
                navigate(e.key);
            } else if (e.key.startsWith('_/boards')) {
                navigate(`/boards/${info.game.boards[0]}`);
            } else if (e.key.startsWith('_/about')) {
                navigate('/about/introduction');
            }
        },
        [navigate, info],
    );

    const selectedKeys = useMemo<string[]>(() => {
        let result: string[] = [pathname];
        if (pathname.startsWith('/boards')) {
            result.push('_/boards');
        }
        if (pathname.startsWith('/about')) {
            result.push('_/about');
        }
        return result;
    }, [pathname]);

    return (
        <ConfigProvider
            theme={{
                token: {
                    colorText: color.neutralContent,
                    colorSplit: color.neutralContent,
                },
                components: {
                    Menu: {
                        popupBg: color.neutral,
                        darkItemBg: color.neutral,
                        darkItemSelectedBg: color.neutral,
                    },
                },
            }}
        >
            <Menu
                items={headerItems}
                theme="dark"
                mode="horizontal"
                onClick={onClick}
                style={{
                    minWidth: 0,
                    flex: 'auto',
                    justifyContent: 'flex-end',
                }}
                selectedKeys={selectedKeys}
            />
        </ConfigProvider>
    );
}

export function Header() {
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
                <NavigationMenu />
            </div>
        </div>
    );
}
