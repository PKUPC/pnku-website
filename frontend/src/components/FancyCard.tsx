import { ReactNode } from 'react';

export default function FancyCard({
    title,
    children,
    extra,
    className,
}: {
    title: string | ReactNode;
    children: ReactNode;
    extra?: ReactNode;
    className?: string;
}) {
    const extraClassName = className ? ' ' + className : '';
    return (
        <>
            <div className={'border-base-300 rounded-box border-[1px]' + extraClassName}>
                <div className="bg-base-200 h-9 py-2 px-4 text-[0.875rem] font-bold rounded-t-box">{title}</div>
                <div className="bg-base-200/30 h-full w-full p-3 rounded-b-box">
                    <div>{children}</div>
                    <div>{extra}</div>
                </div>
            </div>
        </>
    );
}
