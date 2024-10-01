/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_ARCHIVE_MODE?: string;
    readonly VITE_RECAPTCHA_KEY?: string;
    readonly VITE_APP_BUILD_INFO: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
