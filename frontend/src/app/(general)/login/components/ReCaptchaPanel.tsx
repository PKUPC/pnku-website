import { forwardRef, useImperativeHandle, useRef, useState } from 'react';
import ReCAPTCHA from 'react-google-recaptcha';

import { Loading } from '@/components/Loading';

import { CaptchaPanelRef } from '../EmailLogin';

export const ReCaptchaPanel = forwardRef<CaptchaPanelRef, { setCaptchaData: (value: Record<string, string>) => void }>(
    ({ setCaptchaData }, ref) => {
        const recaptchaRef = useRef<ReCAPTCHA>(null);
        const [recaptchaLoaded, setRecaptchaLoaded] = useState(false);

        useImperativeHandle(ref, () => ({
            reset: () => {
                recaptchaRef.current?.reset();
                setCaptchaData({});
            },
        }));

        const onFinishCaptcha = (value: string | null) => {
            setCaptchaData({
                response: value ?? '',
            });
        };

        return (
            <div className="flex justify-center mb-6">
                <ReCAPTCHA
                    ref={recaptchaRef}
                    sitekey={import.meta.env.VITE_RECAPTCHA_KEY ?? ''}
                    onChange={onFinishCaptcha}
                    hl={navigator.language === 'zh-CN' ? 'zh-CN' : 'en'}
                    size={'normal'}
                    asyncScriptOnLoad={() => {
                        console.log('recaptcha loaded!!');
                        setRecaptchaLoaded(true);
                    }}
                />
                {!recaptchaLoaded && <Loading text="人机验证加载中" style={{ height: 100 }} />}
            </div>
        );
    },
);

ReCaptchaPanel.displayName = 'ReCaptchaPanel';
