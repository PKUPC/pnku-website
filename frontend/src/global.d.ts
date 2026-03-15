import type { Button, Image, Input, InputNumber, Modal, Slider } from 'antd';
import type { MessageInstance } from 'antd/es/message/interface';
import type { useLocation, useParams } from 'react-router';

import type { Loading } from './components/Loading';
import type { SyncTextarea } from './components/SyncTextarea';
import type { WishError } from './components/WishError';
import type { useYArray, useYClient, useYMap, useYText } from './hooks/useYClient';
import type { YClient } from './logic/YClient';
import type { useSuccessGameInfo } from './logic/contexts';
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
        };
        exports: {
            React: typeof import('react');
        };
        components: {
            Loading: typeof Loading;
            WishError: typeof WishError;
            SyncTextarea: typeof SyncTextarea;
            Button: typeof Button;
            Image: typeof Image;
            Modal: typeof Modal;
            Popconfirm: typeof Popconfirm;
            Input: typeof Input;
            InputNumber: typeof InputNumber;
            Slider: typeof Slider;
        };
    }
}

export {};
