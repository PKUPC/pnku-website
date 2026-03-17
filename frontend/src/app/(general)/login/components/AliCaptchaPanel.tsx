import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef } from 'react';

import { CaptchaPanelRef } from '../EmailLogin';
import styles from './AliCaptchaPanel.module.css';

export interface AliCaptchaPanelProps {
    setCaptchaData: (value: Record<string, string>) => void;
}

export const AliCaptchaPanel = forwardRef<CaptchaPanelRef, AliCaptchaPanelProps>(({ setCaptchaData }, ref) => {
    const captchaRef = useRef<any>(null);

    function getInstance(instance: any) {
        captchaRef.current = instance;
        console.log(instance);
    }

    const reset = useCallback(() => {
        setCaptchaData({ response: '' });
        console.log(captchaRef.current);
        if (captchaRef.current && typeof captchaRef.current.refresh === 'function') {
            captchaRef.current.refresh();
        }
    }, [setCaptchaData]);

    useImperativeHandle(ref, () => ({
        reset,
    }));

    const onSuccess = useCallback(
        (param: string) => {
            console.log(param);
            setCaptchaData({ response: param });
        },
        [setCaptchaData],
    );

    useEffect(() => {
        if (!window.initAliyunCaptcha) {
            return;
        }
        window.initAliyunCaptcha({
            SceneId: import.meta.env.VITE_ALIYUN_CAPTCHA_SCENE_ID,
            mode: 'embed',
            element: '#aliyun-captcha-element',
            button: '#aliyun-captcha-button',
            success: onSuccess,
            getInstance,
            slideStyle: { width: 360, height: 40 },
            language: navigator.language === 'zh-CN' ? 'cn' : 'en',
            captchaLogoImg: '/mion/svg/zjuph.svg',
        });
        return () => {
            document.getElementById('aliyunCaptcha-mask')?.remove();
            document.getElementById('aliyunCaptcha-window-popup')?.remove();
        };
    }, [onSuccess]);

    return (
        <div className={styles.container}>
            <div id="aliyun-captcha-button"></div>
            <div id="aliyun-captcha-element"></div>
        </div>
    );
});

AliCaptchaPanel.displayName = 'AliCaptchaPanel';
