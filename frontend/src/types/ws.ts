export namespace WsClient {
    export type TeammateActionData = {
        type: 'teammate_action';
        action: 'submission' | 'buy_normal_hint';
        puzzle_key: string;
        message: string;
    };

    export type GameMessageData = {
        type: 'game_message';
        title: string;
        message: string;
    };
    export type GameStartData = {
        type: 'game_start';
    };

    export type TickUpdateData = {
        type: 'tick_update';
        new_tick_name: string;
    };

    export type NewAnnouncementData = {
        type: 'new_announcement';
        title: string;
    };

    export type NewMessageData = {
        type: 'new_message';
        direction: 'to_staff' | 'to_user';
        team_id: number;
        team_name: string;
        sender_id: number;
    };

    export type UpdateAnnouncements = {
        type: 'update_announcements';
    };

    export type StaffActionData = {
        type: 'staff_action';
        action: 'modify_currency';
        message: string;
    };

    export type NewTicketData = {
        type: 'new_ticket';
        team_id: number;
        team_name: string;
        ticket_type: '人工提示';
        extra_info?: string;
    };

    export type NewTicketMessageData = {
        type: 'new_ticket_message';
        direction: 'TO_PLAYER' | 'TO_STAFF';
        team_id: number;
        team_name: string;
        type_name: string;
        sender_id: number;
        ticket_type: '人工提示';
        extra_info?: string;
    };

    export type TicketStatusUpdate = {
        type: 'ticket_status_update';
        status: 'OPEN' | 'CLOSED';
    };

    export type WsData =
        | NewAnnouncementData
        | UpdateAnnouncements
        | NewMessageData
        | TickUpdateData
        | GameStartData
        | GameMessageData
        | TeammateActionData
        | StaffActionData
        | NewTicketData
        | NewTicketMessageData
        | TicketStatusUpdate;
}
