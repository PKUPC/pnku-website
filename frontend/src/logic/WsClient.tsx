import { CarryOutOutlined, MessageOutlined, NotificationOutlined, RocketOutlined } from '@ant-design/icons';
import { MessageInstance } from 'antd/es/message/interface';
import { NotificationInstance } from 'antd/es/notification/interface';
import { ScopedMutator } from 'swr/_internal';

import { WS_ROOT } from '@/constants';
import { GameInfoContextType, GameStatusContextType } from '@/logic/contexts.ts';
import { WsClient } from '@/types/ws.ts';

const PUSH_STARTUP_DELAY_MS = 2000;
const PUSH_RECONNECT_DELAY_MS = 5000;
const PUSH_STABLE_MS = 25000;
const PUSH_RECONNECT_MAX = 8;

export class PushClient {
    private static notification: NotificationInstance;
    private static message: MessageInstance;

    private ws: WebSocket | null;
    private stopped: boolean = false;
    private countReconnect: number = 0;
    private info: GameInfoContextType['info'];
    private readonly reloadInfo: GameInfoContextType['reloadInfo'];
    private readonly setNeedReloadAnnouncement: GameStatusContextType['setNeedReloadAnnouncement'];
    // private setHasNewAnnouncement: GameStatusContextType["setHasNewAnnouncement"];
    private readonly setHasNewMessage: GameStatusContextType['setHasNewMessage'];
    private readonly setNeedReloadArea: GameStatusContextType['setNeedReloadArea'];
    private readonly updateAllCurrencies: GameStatusContextType['updateAllCurrencies'];

    private swrMutate: ScopedMutator;

    constructor(
        info: GameInfoContextType['info'],
        reloadInfo: GameInfoContextType['reloadInfo'],
        setNeedReloadAnnouncement: GameStatusContextType['setNeedReloadAnnouncement'],
        // setHasNewAnnouncement: GameStatusContextType["setHasNewAnnouncement"],
        setHasNewMessage: GameStatusContextType['setHasNewMessage'],
        setNeedReloadArea: GameStatusContextType['setNeedReloadArea'],
        updateAllCurrencies: GameStatusContextType['updateAllCurrencies'],
        swrMutate: ScopedMutator,
    ) {
        this.ws = null;
        this.stopped = false;
        this.countReconnect = 0;
        this.info = info;
        this.reloadInfo = reloadInfo;
        // this.setHasNewAnnouncement = setHasNewAnnouncement;
        this.setNeedReloadAnnouncement = setNeedReloadAnnouncement;
        this.setHasNewMessage = setHasNewMessage;
        this.setNeedReloadArea = setNeedReloadArea;
        this.updateAllCurrencies = updateAllCurrencies;
        this.swrMutate = swrMutate;

        setTimeout(() => {
            this.connect();
        }, PUSH_STARTUP_DELAY_MS);
    }

    static init(notification: NotificationInstance, message: MessageInstance) {
        console.log('ws client: init');
        PushClient.notification = notification;
        PushClient.message = message;
    }

    handleMessage(data: WsClient.WsData) {
        console.log('receive ws data: ' + JSON.stringify(data));
        const key = `notification-${+new Date()}`;
        const notificationConfig = {
            key: key,
            className: 'push-notification',
            duration: null,
        };

        switch (data.type) {
            case 'tick_update': {
                setTimeout(
                    () => {
                        PushClient.notification.info({
                            ...notificationConfig,
                            icon: <CarryOutOutlined />,
                            message: '赛程提醒',
                            description: data.new_tick_name.replace(/;/, '，'),
                        });
                        this.reloadInfo();
                    },
                    200 + Math.random() * 1300,
                ); // add a random delay to flatten the backend load
                break;
            }
            case 'new_announcement': {
                PushClient.notification.info({
                    ...notificationConfig,
                    icon: <NotificationOutlined />,
                    message: '比赛公告',
                    description: `有新的公告【${data.title}】`,
                });
                this.setNeedReloadAnnouncement(true);
                break;
            }
            case 'game_message': {
                PushClient.notification.info({
                    ...notificationConfig,
                    icon: <MessageOutlined />,
                    message: data.title,
                    description: data.message,
                });
                break;
            }
            case 'update_announcements': {
                this.setNeedReloadAnnouncement(true);
                break;
            }
            case 'staff_action': {
                switch (data.action) {
                    case 'modify_currency': {
                        this.updateAllCurrencies();
                        break;
                    }
                }
                PushClient.notification.info({
                    ...notificationConfig,
                    icon: <RocketOutlined />,
                    message: '队伍动态',
                    description: data.message,
                });
                break;
            }
            case 'teammate_action': {
                PushClient.notification.success({
                    ...notificationConfig,
                    icon: <RocketOutlined />,
                    message: '队友动态提醒',
                    description: data.message,
                });
                console.log(data);
                switch (data.action) {
                    case 'buy_normal_hint': {
                        this.swrMutate({
                            endpoint: 'puzzle/get_hints',
                            payload: { puzzle_key: data.puzzle_key },
                        }).then();
                        this.updateAllCurrencies();
                        break;
                    }
                    case 'submission': {
                        this.setNeedReloadArea(true);
                        this.swrMutate({
                            endpoint: 'puzzle/get_detail',
                            payload: { puzzle_key: data.puzzle_key },
                        }).then();
                        this.swrMutate({
                            endpoint: 'puzzle/get_submissions',
                            payload: { puzzle_key: data.puzzle_key },
                        }).then();
                        break;
                    }
                }
                break;
            }
            case 'game_start': {
                this.reloadInfo();
                PushClient.notification.success({
                    ...notificationConfig,
                    icon: <RocketOutlined />,
                    message: '游戏状态更新',
                    description: '你的队伍开始了游戏！',
                });
                break;
            }
            case 'new_message': {
                if (this.info.status !== 'success' || !this.info.user) {
                    break;
                }
                if (data.direction === 'to_staff' && this.info.user.group === 'staff')
                    PushClient.notification.success({
                        ...notificationConfig,
                        icon: <RocketOutlined />,
                        message: '新消息提醒',
                        description: `队伍 [${data.team_name}] 发送了一条站内信。`,
                    });
                else if (
                    data.direction === 'to_staff' &&
                    this.info.user.group === 'player' &&
                    data.sender_id !== this.info.user.id
                )
                    PushClient.notification.success({
                        ...notificationConfig,
                        icon: <RocketOutlined />,
                        message: '新消息提醒',
                        description: `你的队友发送了一条站内信。`,
                    });
                else if (data.direction === 'to_user' && this.info.user.group === 'player')
                    PushClient.notification.success({
                        ...notificationConfig,
                        icon: <RocketOutlined />,
                        message: '新消息提醒',
                        description: `工作人员回复了一条站内信。`,
                    });
                this.setHasNewMessage(true);
                break;
            }
            case 'new_ticket': {
                if (this.info.status !== 'success' || !this.info.user) {
                    break;
                }
                if (this.info.user.group === 'staff') {
                    PushClient.notification.success({
                        ...notificationConfig,
                        icon: <RocketOutlined />,
                        message: '新工单提醒',
                        description: `队伍 [${data.team_name}] 发送了一条工单。类型为 [${data.ticket_type}]。${data.extra_info ?? ''}`,
                    });
                } else if (this.info.user.group === 'player') {
                    if (data.ticket_type === '人工提示') {
                        PushClient.notification.success({
                            ...notificationConfig,
                            icon: <RocketOutlined />,
                            message: '新神谕提醒',
                            description: `你的队友请求了一条神谕。${data.extra_info ?? ''}`,
                        });
                    }
                }
                break;
            }
            case 'new_ticket_message': {
                if (this.info.status !== 'success' || !this.info.user) {
                    break;
                }
                if (data.direction === 'TO_STAFF' && this.info.user.group === 'staff')
                    PushClient.notification.success({
                        ...notificationConfig,
                        icon: <RocketOutlined />,
                        message: '工单回复提醒',
                        description: `队伍 [${data.team_name}] 回复了一条工单，工单类型为 [${data.ticket_type}]。`,
                    });
                else if (
                    data.direction === 'TO_STAFF' &&
                    this.info.user.group === 'player' &&
                    data.sender_id !== this.info.user.id
                ) {
                    if (data.ticket_type === '人工提示')
                        PushClient.notification.success({
                            ...notificationConfig,
                            icon: <RocketOutlined />,
                            message: '神谕提醒',
                            description: `你的队友回复了一条神谕。${data.extra_info ?? ''}`,
                        });
                } else if (data.direction === 'TO_PLAYER' && this.info.user.group === 'player') {
                    if (data.ticket_type === '人工提示') {
                        PushClient.notification.success({
                            ...notificationConfig,
                            icon: <RocketOutlined />,
                            message: '神谕提醒',
                            description: `芈雨回复了一条神谕。${data.extra_info ?? ''}`,
                        });
                    }
                }

                this.setHasNewMessage(true);
                break;
            }
            case 'ticket_status_update': {
                this.setHasNewMessage(true);
                break;
            }
            case 'puzzle_errata': {
                PushClient.notification.success({
                    ...notificationConfig,
                    icon: <RocketOutlined />,
                    message: '谜题勘误提醒',
                    description: data.message,
                });
                break;
            }
        }
    }

    connect() {
        if (this.stopped) return;

        const url = new URL(WS_ROOT + 'push?rem=' + window.rem + '&ram=' + window.ram, window.location.href);
        url.protocol = url.protocol === 'http:' ? 'ws:' : 'wss:';

        this.ws = new WebSocket(url.href);
        console.log(`PushClient: connecting to ${url.href}`);

        let stableWaiter: number | null = null;
        this.ws.onopen = () => {
            console.log('PushClient: socket opened');
            stableWaiter = setTimeout(() => {
                this.countReconnect = 0;
            }, PUSH_STABLE_MS);
        };

        this.ws.onclose = (e) => {
            if (e.code === 4337) {
                console.log('PushClient: socket closed by server, will not retry', e.reason);
                this.stopped = true;
                return;
            }
            console.log('PushClient: socket closed, will reconnect later', e);
            setTimeout(() => {
                if (this.countReconnect < PUSH_RECONNECT_MAX) {
                    this.countReconnect++;
                    this.connect();
                } else {
                    PushClient.message
                        .error({
                            content: '消息推送连接中断',
                            key: 'PushDaemon.Error',
                            duration: 3,
                        })
                        .then();
                    console.log('PushClient: stopped reconnecting');
                }
            }, PUSH_RECONNECT_DELAY_MS);

            if (stableWaiter != null) clearTimeout(stableWaiter);
        };

        this.ws.onmessage = (e) => {
            this.handleMessage(JSON.parse(e.data));
        };
    }

    stop() {
        this.stopped = true;
        if (this.ws !== null) this.ws.close();
    }
}
