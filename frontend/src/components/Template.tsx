import parse from 'html-react-parser';
import { CSSProperties, memo, useCallback, useLayoutEffect, useMemo, useRef } from 'react';
import { Link } from 'react-router';
import useSWR from 'swr';

import NotFound from '@/app/NotFound.tsx';
import { Loading } from '@/components/Loading.tsx';
import { Reloader } from '@/components/Reloader';
import { fetchTemplateFile } from '@/logic/wish';
import { RemoteComponent } from '@/remote/RemoteComponent';

import './Template.css';
import styles from './Template.module.css';
import { TemplateImage } from './template/TemplateImage';
import { TemplateNavigateButton } from './template/TemplateNavigateButton';

export const SimpleTemplateStr = memo(function SimpleTemplateStr({ name, data }: { name: string; data: string }) {
    return <div className={`template-${name} ` + styles.template} dangerouslySetInnerHTML={{ __html: data }} />;
});

export const TemplateStr = memo(function TemplateStr({ name, data }: { name: string; data: string }) {
    const templateRef = useRef<HTMLDivElement>(null);

    const result = useMemo(
        () =>
            parse(data, {
                replace: (domNode, index) => {
                    if (domNode.type === 'tag' && domNode.tagName === 'div' && domNode.attribs?.class) {
                        if (domNode.attribs.class.includes('template-antd-image')) {
                            const src = domNode.attribs['data-src'] as string | undefined;
                            const alt = domNode.attribs['data-alt'] as string | undefined;
                            const aspectRatio = domNode.attribs['data-aspect-ratio'] as string | undefined;
                            const className = domNode.attribs['data-class'] as string | undefined;
                            const preview = domNode.attribs['data-preview'] as string | undefined;
                            let jsonStyle: CSSProperties = {};
                            try {
                                if (domNode.attribs['data-style']) {
                                    jsonStyle = JSON.parse(domNode.attribs['data-style']);
                                }
                            } catch {
                                jsonStyle = {};
                            }
                            console.log(domNode);
                            if (src) {
                                return (
                                    <TemplateImage
                                        src={src}
                                        alt={alt}
                                        aspectRatio={aspectRatio}
                                        className={className}
                                        preview={preview === 'true'}
                                        style={jsonStyle}
                                    />
                                );
                            }
                        } else if (domNode.attribs.class.includes('template-navigate-link')) {
                            const text = domNode.attribs['data-text'];
                            const href = domNode.attribs['data-href'];
                            return <Link to={href}>{text}</Link>;
                        } else if (domNode.attribs.class.includes('template-navigate-button')) {
                            const url = domNode.attribs['data-url'] as string;
                            const text = domNode.attribs['data-text'] as string;
                            const type = domNode.attribs['data-type'] as
                                | 'primary'
                                | 'default'
                                | 'link'
                                | 'text'
                                | 'dashed'
                                | undefined;
                            const className = domNode.attribs['data-class'] as string | undefined;
                            const size = domNode.attribs['data-size'] as 'large' | 'middle' | 'small' | undefined;
                            let jsonStyle: CSSProperties = {};
                            try {
                                if (domNode.attribs['data-style']) {
                                    jsonStyle = JSON.parse(domNode.attribs['data-style']);
                                }
                            } catch {
                                jsonStyle = {};
                            }
                            return (
                                <TemplateNavigateButton
                                    url={url}
                                    text={text}
                                    type={type || 'default'}
                                    className={className}
                                    style={jsonStyle}
                                    size={size}
                                />
                            );
                        } else if (domNode.attribs.class.includes('template-remote-component')) {
                            const name = domNode.attribs['data-name'];
                            const url = domNode.attribs['data-url'];
                            let props = {};
                            try {
                                if (domNode.attribs['data-props']) {
                                    props = JSON.parse(domNode.attribs['data-props']);
                                }
                            } catch {
                                props = {};
                            }
                            return (
                                <RemoteComponent
                                    key={name + url + index}
                                    componentName={name}
                                    componentUrl={url}
                                    {...props}
                                />
                            );
                        }
                    } else if (domNode.type === 'tag' && domNode.tagName === 'span' && domNode.attribs?.class) {
                        if (domNode.attribs.class.includes('template-navigate-link')) {
                            const text = domNode.attribs['data-text'];
                            const href = domNode.attribs['data-href'];
                            return <Link to={href}>{text}</Link>;
                        }
                    }
                },
            }),
        [data],
    );

    const executeScripts = useCallback(() => {
        if (!templateRef.current) return;

        console.log('TemplateStr -> executeScripts: run script');
        const userScripts = Array.from(templateRef.current.getElementsByTagName('script'));

        userScripts.forEach((element, index) => {
            const userScript = element.innerHTML.trim();
            if (!userScript) return;

            const scriptHash = `${name}-${index}-${btoa(encodeURIComponent(userScript)).slice(0, 10)}`;

            try {
                window.eval(userScript);
                console.log(`Script ${scriptHash} executed successfully`);
            } catch (error) {
                console.error(`Script execution error for ${scriptHash}:`, error);
            }
        });
    }, [name]);

    useLayoutEffect(() => {
        const timer = setTimeout(executeScripts, 0);
        return () => clearTimeout(timer);
    }, [data, executeScripts]);

    console.log('template rendered!');
    return (
        <div className={styles.template + ' template-' + name} ref={templateRef}>
            {result}
        </div>
    );
});

export function TemplateFile({ name }: { name: string }) {
    console.log('getting template', name);
    const { data, error, mutate } = useSWR([name], ([key]) => fetchTemplateFile(key));

    if (error) {
        console.log(error.message);
        if (error.message === '错误：HTTP错误 404') return <NotFound />;
        return <Reloader message={error.message} reload={mutate} />;
    }
    if (!data) return <Loading style={{ height: 500 }} />;

    return <TemplateStr name={name} data={data} />;
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

    return <SimpleTemplateStr name={name} data={data} />;
}
