import {
    Alert,
    Button,
    Checkbox,
    ConfigProvider,
    Image,
    Input,
    InputNumber,
    Modal,
    Popconfirm,
    Select,
    Slider,
    Switch,
    Tag,
    Tooltip,
    message,
} from 'antd';
import type { MessageInstance } from 'antd/es/message/interface';
import type { useLocation, useParams } from 'react-router';

import type { Loading } from './components/Loading';
import type { SyncTextarea } from './components/SyncTextarea';
import type { WishError } from './components/WishError';
import type { useYArray, useYClient, useYMap, useYText } from './hooks/useYClient';
import type { YClient } from './logic/YClient';
import type { useSuccessGameInfo, useWindowInfo } from './logic/contexts';
import type { useWishData } from './logic/swrWrappers';
import type { Wish } from './types/wish';

declare global {
    interface Window {
        recaptchaOptions?: { useRecaptchaNet: boolean };
        rem?: string;
        ram?: string;
        logout?: () => void;
        template?: (v: string) => void;
        messageStorage?: { [key: `team#${string}`]: Wish.Message.MessageInfo[] };
        wish: <T extends Wish.WishParams>(args: T) => Promise<Wish.ResponseMapping[T['endpoint']]>;
        messageApi: MessageInstance;
        puzzleApi?: {
            setDisableInput: (v: boolean) => void;
            setSubmitAnswer: (v: string) => void;
            setInputAnswer: (v: string) => void;
            reloadPuzzleDetail: () => void;
        };
        websiteUtils: {
            wish: <T extends Wish.WishParams>(args: T) => Promise<Wish.ResponseMapping[T['endpoint']]>;
            messageApi: MessageInstance;
            useWishData: typeof useWishData;
            YClient: typeof YClient;
            useYClient: typeof useYClient;
            useYText: typeof useYText;
            useYMap: typeof useYMap;
            useYArray: typeof useYArray;
            useParams: typeof useParams;
            useLocation: typeof useLocation;
            useSuccessGameInfo: typeof useSuccessGameInfo;
            useWindowInfo: typeof useWindowInfo;
        };
        exports: {
            React: typeof import('react');
            AntDesign: {
                Alert: typeof Alert;
                Button: typeof Button;
                Checkbox: typeof Checkbox;
                ConfigProvider: typeof ConfigProvider;
                Image: typeof Image;
                Input: typeof Input;
                InputNumber: typeof InputNumber;
                Modal: typeof Modal;
                Popconfirm: typeof Popconfirm;
                Select: typeof Select;
                Slider: typeof Slider;
                Switch: typeof Switch;
                Tag: typeof Tag;
                Tooltip: typeof Tooltip;
                message: typeof message;
            };
        };
        components: {
            Loading: typeof Loading;
            WishError: typeof WishError;
            SyncTextarea: typeof SyncTextarea;
        };
        adhoc: {};
    }
}

export {};
