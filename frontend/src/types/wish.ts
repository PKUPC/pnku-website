import React from 'react';

// ADHOC: 在这里修改各种 adhoc 类型定义
export namespace Adhoc {
    // api 交互时统一为小写，大写字母形式显示在 url 中很怪
    export type CurrencyType = 'hint_point';
}

export namespace Wish {
    export type ErrorRes = { status: 'error'; message: string; title: string };
    export type InfoRes = { status: 'info'; message: string; title: string };
    export type SuccessRes = { status: 'success'; message?: string; title?: string };
    export type NormalRes = ErrorRes | InfoRes | SuccessRes;

    export namespace Game {
        export type SimpleBoardItem = {
            bs: { text: string; color: string }[];
            lts: number;
            r: number;
            s: number;
            in: string;
            n: string;
            ms: string[];
            detail_url?: string;
        };

        export type SimpleBoard = { type: 'simple'; list: SimpleBoardItem[] };

        export type FullBoardItem = {
            bs: { text: string; color: string }[]; // badges
            lts: number; // last_success_submission_ts
            r: number; // rank
            s: number; // score
            id: number; // id
            in: string; // info
            n: string; // name
            ms: string[]; // members
            f: boolean; // finished
            fts: number; // finished ts
            g: boolean; // g
        };

        export type FullBoard = {
            type: 'full';
            list: FullBoardItem[];
            time_range: [number, number];
            // n: team_name ss: submissions
            topstars: { n: string; ss: [number, number][] }[];
        };

        export type FirstBloodItem = {
            key: string;
            team_name: string;
            timestamp: number;
            title: string;
        };

        export type FirstBloodBoard = {
            type: 'firstblood';
            list: { name: string; list: FirstBloodItem[] }[];
        };

        export type SpeedRunBoardItem = {
            key: string;
            title: string;
            first?: { team_name: string; time_cost: number };
            second?: { team_name: string; time_cost: number };
            third?: { team_name: string; time_cost: number };
        };

        export type SpeedRunBoard = {
            type: 'speed_run';
            desc?: string;
            areas: { name: string; puzzles: SpeedRunBoardItem[] }[];
        };

        export type GetBoardApi = {
            request: {
                endpoint: 'game/get_board';
                payload: { board_key: string };
            };
            response: ErrorRes | (SuccessRes & { data: SimpleBoard | FullBoard | FirstBloodBoard | SpeedRunBoard });
        };

        export type ScheduleInfo = {
            timestamp_s: number;
            name: string;
            status: 'prs' | 'ftr' | 'pst';
        };

        export type GetScheduleApi = {
            request: {
                endpoint: 'game/get_schedule';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: ScheduleInfo[] });
        };

        export type AnnouncementInfo = {
            id: number;
            publish_at: number;
            category: string;
            sorting_index: number;
            title: string;
            content: string;
        };

        export type GetAnnouncementsApi = {
            request: {
                endpoint: 'game/get_announcements';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: AnnouncementInfo[] });
        };

        export type PuzzleInfo = {
            puzzle_key: string;
            status: 'untouched' | 'partial' | 'passed' | 'found' | 'public';
            title: string;
            location?: [number, number, number, number];
            found_msg?: string;
            difficulty_status: {
                total_num: number;
                green_num: number;
                red_num: number;
            };
            total_attempted: number;
            total_passed: number;
            image?: string;
            tags?: { text: string; color: string }[];
        };

        export type PuzzleGroupInfo = { name: string; puzzles: PuzzleInfo[] };

        export type MapArea = {
            type: 'map';
            puzzle_groups: PuzzleGroupInfo[];
            bash_url: string;
            blocks: number[][];
            map_image: string;
            bg_image: string;
            items: {
                location: [number, number];
                image: string;
            };
        };

        export type ListAreaExtra = {
            areaImage: string /* backend_static URL */;
            areaLogoImage: string;
            areaTitle: string /* 素青 */;
            areaSubtitle: string /* 第一天 */;
            bgFocusPositionX: number /* image focus X */;
            bgFocusPositionY: number /* image focus X */;
            mainColor: string;
            subColor: string;
        };

        export type ListArea = {
            type: 'list';
            template: string;
            puzzle_groups: PuzzleGroupInfo[];
            extra: ListAreaExtra;
        };

        export type IntroAreaExtra = ListAreaExtra;

        export type IntroArea = {
            type: 'intro';
            template: string;
            extra: IntroAreaExtra;
        };

        export type GetAreaDetailApi = {
            request: {
                endpoint: 'game/get_area_detail';
                payload: { area_name: string };
            };
            response: ErrorRes | (SuccessRes & { data: MapArea | IntroArea | ListArea });
        };

        export type HomeAreaData = {
            bgUrl: string;
            title: string;
            subtitle: string;
            buttonText: string;
            buttonLink: string;
            align: 'left' | 'right';
            topPercentage?: number;
            leftPercentage?: number;
            rightPercentage?: number;
            bottomPercentage?: number;
            bgFocusPositionX: number;
            bgFocusPositionY: number;
            mainColor: string;
            subColor: string;
        };

        export type CurrencyInfo = {
            type: Adhoc.CurrencyType;
            name: string;
            icon: string;
            denominator: number;
            precision: number;
        };

        export type GameInfoApi = {
            request: {
                endpoint: 'game/game_info';
                payload?: undefined;
            };
            response:
                | ErrorRes
                | (SuccessRes & {
                      status: 'success';
                      game: {
                          login: boolean;
                          boards: { key: string; name: string; icon: string }[];
                          aboutTemplates: { key: string; title: string; icon: string }[];
                          isPrologueUnlock: boolean;
                          isGameBegin: boolean;
                          isGameEnd: boolean;
                          currencies: CurrencyInfo[];
                      };
                      feature: {
                          push: boolean;
                          debug: boolean;
                          recaptcha: boolean;
                          playground: boolean;
                          email_login: boolean;
                          sso_login: boolean;
                      };
                      user: null | {
                          group: 'staff' | 'player' | 'banned';
                          admin?: boolean;
                          group_disp: string;
                          id: number;
                          profile: {
                              nickname: string;
                              email: string;
                              avatar_url: string;
                          };
                      };
                      team: null | {
                          id: number;
                          team_name: string;
                          team_info: string;
                          team_secret: string;
                          status: string;
                          extra_status: 'normal' | 'hidden';
                          leader_id: number;
                          members: { id: number; nickname: string; avatar_url: string }[];
                          disp_list: { text: string; color: string }[];
                          recruiting: boolean;
                          recruiting_contact: string;
                          gaming: boolean;
                          ban_list: {
                              ban_message_until: number;
                              ban_manual_hint_until: number;
                              ban_recruiting_until: number;
                          };
                      };
                      areas: HomeAreaData[];
                  });
        };

        export type GetPuzzleListApi = {
            request: {
                endpoint: 'game/get_puzzle_list';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: ListArea[] });
        };

        // ADHOC: 根据需求修改可选的货币类型
        export type GetTeamCurrencyDetailApi = {
            request: {
                endpoint: 'game/team_currency_detail';
                payload: { currency_type: Adhoc.CurrencyType };
            };
            response:
                | ErrorRes
                | (SuccessRes & {
                      data: {
                          type: string;
                          name: string;
                          icon: string;
                          denominator: number;
                          precision: number;
                          balance: number;
                          increase_policy: [number, number][];
                      };
                  });
        };

        export type GameStartApi = {
            request: {
                endpoint: 'game/game_start';
                payload: { content: string };
            };
            response: NormalRes & { need_reload_info?: boolean };
        };

        export type TeamInfo = {
            team_id: number;
            team_info: string;
            team_name: string;
            recruiting: boolean;
            recruiting_contact: string;
            team_members: {
                avatar_url: string;
                nickname: string;
                type: string;
            }[];
        };

        export type GetTeamListApi = {
            request: {
                endpoint: 'game/get_team_list';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { team_list: TeamInfo[] });
        };

        export type StoryGroup = { subtitle: string; list: { title: string; template: string }[] };

        export type GetStoryListApi = {
            request: {
                endpoint: 'game/get_story_list';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: StoryGroup[] });
        };

        // 所有 Api
        export type GameApis =
            | GameInfoApi
            | GameStartApi
            | GetAnnouncementsApi
            | GetAreaDetailApi
            | GetBoardApi
            | GetPuzzleListApi
            | GetScheduleApi
            | GetStoryListApi
            | GetTeamCurrencyDetailApi
            | GetTeamListApi;
    }

    export namespace Message {
        export type SendMessageApi = {
            request: {
                endpoint: 'message/send_message';
                payload: { team_id: number; type: string; content: string };
            };
            response: NormalRes;
        };

        export type ReadMessageApi = {
            request: {
                endpoint: 'message/read_message';
                payload: { team_id: number; msg_id: number };
            };
            response: NormalRes;
        };

        export type MessageInfo = {
            id: number;
            user_name: string;
            team_name: string;
            direction: string;
            content_type: string;
            content: string;
            timestamp_s: number;
            player_unread: boolean;
            staff_unread: boolean;
        };

        export type GetMessageApi = {
            request: {
                endpoint: 'message/get_message';
                payload: { team_id: number; start_id: number };
            };
            response: ErrorRes | (SuccessRes & { data: MessageInfo[] });
        };

        export type MessageApis = GetMessageApi | ReadMessageApi | SendMessageApi;
    }

    export namespace Puzzle {
        export type SubmitAnswerApi = {
            request: {
                endpoint: 'puzzle/submit_answer';
                payload: { puzzle_key: string; content: string };
            };
            response: NormalRes & { need_reload?: boolean };
        };

        export type SubmitPublicAnswerApi = {
            request: {
                endpoint: 'puzzle/submit_public_answer';
                payload: { puzzle_key: string; content: string };
            };
            response: NormalRes & { need_reload?: boolean };
        };

        export type SubmissionRecordData = {
            idx: number;
            team_name: string;
            user_name: string;
            origin: string;
            cleaned: string;
            status: string;
            info: string;
            timestamp_s: number;
        };

        export type GetSubmissionsApi = {
            request: {
                endpoint: 'puzzle/get_submissions';
                payload: { puzzle_key: string };
            };
            response: ErrorRes | (SuccessRes & { submissions: SubmissionRecordData[] });
        };

        export type PuzzleActionData =
            | { type: 'webpage'; name: string; url: string; noreferrer?: boolean }
            | { type: 'media'; name: string; media_url: string };

        export type ClipboardData = { type: string; idx: number };

        export type PuzzleGroupInfo = Game.PuzzleGroupInfo;

        export type PuzzleDetailData = {
            key: string;
            title: string;
            desc: string;
            actions: PuzzleActionData[];
            clipboard?: ClipboardData[];
            status: string;
            puzzle_list: PuzzleGroupInfo[];
            unlock_ts?: number;
            pass_ts?: number;
            cold_down_ts?: number;
            special_list?: object;
            correct_answers?: string[];
            answer_display?: string;
            return?: string;
            area_name?: string;
            stories?: string[];
        };

        export type GetDetailApi = {
            request: {
                endpoint: 'puzzle/get_detail';
                payload: { puzzle_key: string };
            };
            response: ErrorRes | (SuccessRes & { data: PuzzleDetailData });
        };

        export type GetClipboardApi = {
            request: {
                endpoint: 'puzzle/get_clipboard';
                payload: { puzzle_key: string; clipboard_idx: number; clipboard_type: string };
            };
            response: ErrorRes | (SuccessRes & { data: string });
        };

        export type GetPublicDetailApi = {
            request: {
                endpoint: 'puzzle/get_public_detail';
                payload: { puzzle_key: string };
            };
            response: ErrorRes | (SuccessRes & { data: PuzzleDetailData });
        };

        export type HintPrice = { type: Adhoc.CurrencyType; price: number };

        export type HintItem = {
            id: number;
            question: string;
            answer: string;
            type: string;
            price: HintPrice[];
            unlock: boolean;
            effective_after_ts: number;
        };

        export type HintRecordData = { list: HintItem[] };

        export type GetHintsApi = {
            request: {
                endpoint: 'puzzle/get_hints';
                payload: { puzzle_key: string };
            };
            response: ErrorRes | (SuccessRes & { data: HintRecordData });
        };

        export type BuyHintApi = {
            request: {
                endpoint: 'puzzle/buy_hint';
                payload: { puzzle_key: string; hint_id: number };
            };
            response: NormalRes;
        };

        export type PuzzleApis =
            | SubmitAnswerApi
            | SubmitPublicAnswerApi
            | GetSubmissionsApi
            | GetDetailApi
            | GetClipboardApi
            | GetPublicDetailApi
            | GetHintsApi
            | BuyHintApi;
    }

    export namespace Staff {
        export type TeamInfoStaff = {
            team_id: number;
            team_name: string;
            last_msg_ts: number;
            unread: boolean;
        };

        export type GetGameInfoApi = {
            request: {
                endpoint: 'staff/get_game_info';
                payload?: undefined;
            };
            response:
                | ErrorRes
                | (SuccessRes & {
                      data: {
                          teams: TeamInfoStaff[];
                          puzzles: { key: string; title: string }[];
                          puzzle_status: string[];
                          ticket_status: string[];
                          ticket_num: number;
                          submission_num: number;
                      };
                  });
        };

        export type StaffTeamDetailSubmission = {
            idx: string;
            puzzle: string;
            user_name: string;
            origin: string;
            cleaned: string;
            status: string;
            info: string;
            timestamp_s: number;
        };

        export type StaffTeamDetailPassedPuzzles = { title: string; timestamp_s: number };

        export type StaffTeamDetailCurrencyHistory = {
            timestamp_s: number;
            change: string;
            time_based_change: string;
            info: string;
        };

        export type StaffTeamDetailCurrency = {
            type: Adhoc.CurrencyType;
            name: string;
            icon: string;
            denominator: number;
            precision: number;
            current: number;
            change: number;
            history: StaffTeamDetailCurrencyHistory[];
        };

        export type StaffTeamDetail = {
            team_id: number;
            team_name: string;
            team_info: string;
            disp_list: { text: string; color: string }[];
            leader_id: number;
            members: {
                id: number;
                nickname: string;
                avatar_url: string;
            }[];
            currency_status: StaffTeamDetailCurrency[];
            submissions: StaffTeamDetailSubmission[];
            passed_puzzles: StaffTeamDetailPassedPuzzles[];
            ban_list: {
                ban_message_until: number;
                ban_manual_hint_until: number;
                ban_recruiting_until: number;
            };
        };

        export type GetTeamDetailApi = {
            request: {
                endpoint: 'staff/get_team_detail';
                payload: { team_id: number };
            };
            response: ErrorRes | (SuccessRes & StaffTeamDetail);
        };

        export type VMe50Api = {
            request: {
                endpoint: 'staff/v_me_50';
                payload: { team_id: number; type: Adhoc.CurrencyType; change: number; reason: string };
            };
            response: NormalRes;
        };

        export type GetTeamListApi = {
            request: {
                endpoint: 'staff/get_team_list';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: TeamInfoStaff[] });
        };

        export type StaffSubmissionInfo = {
            idx: number;
            puzzle: string;
            puzzle_key: string;
            team: string;
            team_id: number;
            user: string;
            origin: string;
            cleaned: string;
            status: string;
            info: string;
            timestamp_s: number;
        };

        export type GetSubmissionListApi = {
            request: {
                endpoint: 'staff/get_submission_list';
                payload: {
                    start_idx: number;
                    count: number;
                    team_id: number[] | null;
                    puzzle_key: string[] | null;
                    puzzle_status: string[] | null;
                    sort_field: string | null;
                    sort_order: 'ascend' | 'descend' | null | undefined;
                };
            };
            response: ErrorRes | (SuccessRes & { data: { total_num: number; list: StaffSubmissionInfo[] } });
        };

        export type StaffTicketInfo = {
            ticket_id: number;
            team_id: number;
            team_name: string;
            last_message_ts: number;
            staff_replied: boolean;
            status: string;
            subject: string;
            ticket_type: string;
        };

        export type GetTicketsApi = {
            request: {
                endpoint: 'staff/get_tickets';
                payload: {
                    team_id: number[] | null;
                    status: string[] | null;
                    staff_replied: boolean[] | null;
                    sort_field: string | null;
                    sort_order: 'ascend' | 'descend' | null | undefined;
                    start_idx: number;
                    count: number;
                };
            };

            response: ErrorRes | (SuccessRes & { data: { total_num: number; list: StaffTicketInfo[] } });
        };

        export type UpdateExtraTeamInfoApi = {
            request: {
                endpoint: 'staff/update_extra_team_info';
                payload: {
                    team_id: number;
                    type: 'ban_list';
                    data: {
                        ban_message_until: string;
                        ban_manual_hint_until: string;
                        ban_recruiting_until: string;
                    };
                };
            };
            response: NormalRes;
        };

        export type StaffApis =
            | GetGameInfoApi
            | GetTeamDetailApi
            | VMe50Api
            | GetTeamListApi
            | GetSubmissionListApi
            | GetTicketsApi
            | UpdateExtraTeamInfoApi;
    }

    export namespace Team {
        export type CreateTeamApi = {
            request: {
                endpoint: 'team/create_team';
                payload: { team_name: string; team_info: string; team_secret: string };
            };
            response: NormalRes;
        };

        export type UpdateTeamApi = {
            request: {
                endpoint: 'team/update_team';
                payload: { team_name: string; team_info: string; team_secret: string };
            };
            response: NormalRes;
        };

        export type LeaveTeamApi = {
            request: {
                endpoint: 'team/leave_team';
                payload?: undefined;
            };
            response: NormalRes;
        };

        export type RemoveUserApi = {
            request: {
                endpoint: 'team/remove_user';
                payload: { user_id: number };
            };
            response: NormalRes;
        };

        export type UpdateExtraTeamInfoApi = {
            request: {
                endpoint: 'team/update_extra_team_info';
                payload: { type: string; data: { recruiting: boolean; recruiting_contact: string } };
            };
            response: NormalRes;
        };

        export type JoinTeamApi = {
            request: {
                endpoint: 'team/join_team';
                payload: { team_id: string; team_secret: string };
            };
            response: NormalRes;
        };

        export type ChangeLeaderApi = {
            request: {
                endpoint: 'team/change_leader';
                payload: { user_id: number };
            };
            response: NormalRes;
        };

        export type TeamCurrencyHistorySingleRecord = {
            timestamp_s: number;
            change: string;
            time_based_change: string;
            current: string;
            info: string;
        };

        export type TeamCurrencyHistory = { history: TeamCurrencyHistorySingleRecord[] };

        export type GetCurrencyChangeHistoryApi = {
            request: {
                endpoint: 'team/get_currency_change_history';
                payload: { currency_type: Adhoc.CurrencyType };
            };
            response: ErrorRes | (SuccessRes & TeamCurrencyHistory);
        };

        export type TeamPuzzleStatisticsItem = {
            key: string;
            title: string;
            unlock_ts: number;
            passed_ts?: number;
            time_cost?: number;
            pass: number;
            wrong: number;
            milestone: number;
        };
        export type TeamPuzzleStatisticsAreaItem = {
            name: string;
            puzzles: TeamPuzzleStatisticsItem[];
        };

        export type GetPuzzleStatisticsApi = {
            request: {
                endpoint: 'team/get_puzzle_statistics';
                payload?: undefined;
            };
            response: ErrorRes | (SuccessRes & { data: TeamPuzzleStatisticsAreaItem[] });
        };
        export type TeamSubmissionInfo = {
            idx: number;
            puzzle: string;
            user_name: string;
            origin: string;
            cleaned: string;
            status: string;
            info: string;
            timestamp_s: number;
        };

        export type TeamPassedSubmission = { timestamp_s: number; gained_score: number };

        export type GetSubmissionHistoryApi = {
            request: {
                endpoint: 'team/get_submission_history';
                payload?: undefined;
            };
            response:
                | ErrorRes
                | (SuccessRes & {
                      data: { submissions: TeamSubmissionInfo[]; passed_submissions: TeamPassedSubmission[] };
                  });
        };

        export type TeamApis =
            | CreateTeamApi
            | UpdateTeamApi
            | LeaveTeamApi
            | RemoveUserApi
            | UpdateExtraTeamInfoApi
            | JoinTeamApi
            | ChangeLeaderApi
            | GetCurrencyChangeHistoryApi
            | GetPuzzleStatisticsApi
            | GetSubmissionHistoryApi;
    }

    export namespace Ticket {
        export type TicketInfo = {
            ticket_id: number;
            last_message_ts: number;
            staff_replied: boolean;
            status: string;
            subject: string;
        };

        export type TicketHintInfo = {
            list: TicketInfo[];
            hints_open?: string[];
            disabled?: boolean;
            disabled_reason?: string;
            effective_after_ts: number;
        };

        export type GetManualHintsApi = {
            request: {
                endpoint: 'ticket/get_manual_hints';
                payload: { puzzle_key: string };
            };

            response: ErrorRes | (SuccessRes & { data: TicketHintInfo });
        };

        export type TicketMessageInfo = {
            id: number;
            user_name: string;
            team_name: string;
            direction: string;
            content: string;
            timestamp_s: number;
        };

        export type TicketDetailInfo = {
            ticket_id: number;
            subject: string;
            ticket_status: 'OPEN' | 'CLOSED';
            staff_replied: boolean;
            disabled?: boolean;
            disabled_reason?: string;
            messages: TicketMessageInfo[];
        };

        export type GetTicketDetailApi = {
            request: { endpoint: 'ticket/get_ticket_detail'; payload: { ticket_id: number } };
            response: ErrorRes | (SuccessRes & { data: TicketDetailInfo });
        };

        export type RequestHintApi = {
            request: { endpoint: 'ticket/request_hint'; payload: { content: string } };
            response: NormalRes;
        };

        export type SendMessageApi = {
            request: {
                endpoint: 'ticket/send_message';
                payload: { ticket_id: number; content: string };
            };
            response: NormalRes;
        };

        export type SetTicketStatusApi = {
            request: {
                endpoint: 'ticket/set_ticket_status';
                payload: { ticket_id: number; ticket_status: 'OPEN' | 'CLOSED' };
            };
            response: NormalRes;
        };

        export type TicketApis =
            | GetManualHintsApi
            | GetTicketDetailApi
            | RequestHintApi
            | SendMessageApi
            | SetTicketStatusApi;
    }
    export namespace Upload {
        export type UploadedImageItem = { url: string };

        export type GetUploadedImagesApi = {
            request: { endpoint: 'upload/get_uploaded_images'; payload?: undefined };
            response:
                | ErrorRes
                | (SuccessRes & { data: { list: UploadedImageItem[]; disabled?: boolean; disable_reason?: string } });
        };

        export type UploadApis = GetUploadedImagesApi;
    }

    export namespace User {
        export type UpdateProfileApi = {
            request: { endpoint: 'user/update_profile'; payload: { profile: object } };
            response: NormalRes;
        };

        export type ChangePasswordApi = {
            request: { endpoint: 'user/change_password'; payload: { old_password: string; new_password: string } };
            response: NormalRes;
        };

        export type UserApis = UpdateProfileApi | ChangePasswordApi;
    }

    export type WishApis =
        | Game.GameApis
        | Message.MessageApis
        | Puzzle.PuzzleApis
        | Staff.StaffApis
        | Team.TeamApis
        | Ticket.TicketApis
        | Upload.UploadApis
        | User.UserApis;

    export type WishConfirmApis =
        | Team.RemoveUserApi
        | Team.ChangeLeaderApi
        | Team.LeaveTeamApi
        | Puzzle.SubmitAnswerApi
        | Puzzle.SubmitPublicAnswerApi
        | Puzzle.BuyHintApi
        | Game.GameStartApi
        | Staff.VMe50Api
        | Staff.UpdateExtraTeamInfoApi;

    type ExtractParam<T> = T extends { request: infer P } ? P : never;

    export type WishParams = ExtractParam<WishApis>;
    export type WishConfirmParams = ExtractParam<WishConfirmApis>;

    type ExtractResponseMapping<T> = T extends {
        request: { endpoint: infer P };
        response: infer V;
    }
        ? { [K in P & string]: V }
        : never;

    type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;

    export type ResponseMapping = UnionToIntersection<ExtractResponseMapping<WishApis>>;

    export type WishConfirmConfig<T extends WishConfirmParams> = {
        wishParam: T;
        confirmTitle?: string;
        confirmContent?: string | React.ReactNode;
        onError?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
        onErrorContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onErrorTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onSuccess?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
        onSuccessContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onSuccessTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onInfo?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
        onInfoContentRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onInfoTitleRender?: (res: Wish.ResponseMapping[T['endpoint']]) => React.ReactNode;
        onFinish?: (res: Wish.ResponseMapping[T['endpoint']]) => void;
    };
}
