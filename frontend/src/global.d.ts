interface Window {
    recaptchaOptions?: { useRecaptchaNet: boolean };
    rem?: string;
    ram?: string;
    logout?: () => void;
    template?: (v: string) => void;
    messageStorage?: { [key: `team#${string}`]: Wish.MessageInfo[] };
    wish: <T extends Wish.WishParam>(args: T) => Promise<Wish.ResponseMapping[T['endpoint']]>;
    messageApi: MessageInstance;
    puzzleApi?: {
        setDisableInput: (v: boolean) => void;
        setSubmitAnswer: (v: string) => void;
        setInputAnswer: (v: string) => void;
        reloadPuzzleDetail: () => void;
    };
}
