import { ReactNode } from 'react';

export function InputWithLabel({
    children,
    label,
    extra,
}: {
    children: ReactNode;
    label: ReactNode;
    extra?: ReactNode;
}) {
    return (
        <div className="flex flex-col sm:flex-row sm:items-start gap-0 sm:gap-2">
            <div className="text-[0.875rem] flex justify-start sm:justify-end items-center h-8 mb-0 sm:mb-2 w-full sm:w-[33.33%] ">
                {label}
            </div>
            <div className="flex-1 sm:w-[66.67%]">
                {children}
                {extra && <div className="text-[0.875rem] text-left text-base-content/70 mt-1">{extra}</div>}
            </div>
        </div>
    );
}
