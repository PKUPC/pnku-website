import { ConfigProvider, Image } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import parse from 'html-react-parser';
import { useEffect, useRef } from 'react';
import useSWR from 'swr';

import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { Reloader } from '@/components/Reloader';
import { fetchTemplateFile } from '@/logic/wish';

import './Template.css';
import styles from './Template.module.css';

export function SimpleTemplateStr({ name, children }: { name: string; children: string }) {
    return <div className={`template-${name} ` + styles.template} dangerouslySetInnerHTML={{ __html: children }} />;
}

export function TemplateStr({ name, children }: { name: string; children: string }) {
    const templateRef = useRef<HTMLDivElement>(null);

    const result = parse(children, {
        replace: (domNode) => {
            if (domNode.type === 'tag' && domNode.tagName === 'div' && domNode.attribs?.class) {
                if (domNode.attribs.class.includes('template-antd-image')) {
                    const src = domNode.attribs['data-src'];
                    if (src) {
                        return (
                            <div className={domNode.attribs.class} data-src={src}>
                                <ConfigProvider locale={zhCN}>
                                    <Image src={src} alt={'image'} />
                                </ConfigProvider>
                            </div>
                        );
                    }
                }
            }
        },
    });

    useEffect(() => {
        if (templateRef.current) {
            console.log('TemplateStr -> useEffect: run script');
            console.log(templateRef.current);
            const userScripts = Array.from(templateRef.current.getElementsByTagName('script'));
            userScripts.forEach((element) => {
                const userScript = element.innerHTML;
                window.eval(userScript);
            });
        }
    }, []);

    console.log('template rendered!');
    return (
        <div className={styles.template + ' template-' + name} ref={templateRef}>
            {result}
        </div>
    );
}

export function TemplateFile({ name }: { name: string }) {
    console.log('getting template', name);
    const { data, error, mutate } = useSWR([name], ([key]) => fetchTemplateFile(key));

    if (error) {
        console.log(error.message);
        if (error.message === '错误：HTTP错误 404') return <NotFound />;
        return <Reloader message={error.message} reload={mutate} />;
    }
    if (!data) return <Loading style={{ height: 500 }} />;

    return <TemplateStr name={name}>{data}</TemplateStr>;
}

export function SimpleTemplateFile({ name }: { name: string }) {
    console.log('getting template', name);
    const { data, error, mutate } = useSWR([name], ([key]) => fetchTemplateFile(key));

    if (error) {
        console.log(error.message);
        if (error.message === '错误：HTTP错误 404') return <NotFound />;
        return <Reloader message={error.message} reload={mutate} />;
    }
    if (!data) return <Loading />;

    return <SimpleTemplateStr name={name}>{data}</SimpleTemplateStr>;
}
