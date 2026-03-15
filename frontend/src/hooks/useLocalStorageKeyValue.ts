import { useCallback, useEffect, useState } from 'react';

/**
 * 用于管理 localStorage 中的单个 key-value 对的 hook
 * @param key - localStorage 的 key 名
 * @param defaultValue - 默认值
 * @param validValues - 可选值数组，如果提供，则只接受这些值
 * @returns [value, setValue] - 类似 useState 的返回值
 */
export function useLocalStorageKeyValue(
    key: string,
    defaultValue: string,
    validValues?: readonly string[],
): [string, (value: string) => void] {
    // 从 localStorage 读取初始值，如果不存在或无效则使用默认值
    const getInitialValue = useCallback((): string => {
        const storedValue = localStorage.getItem(key);
        if (storedValue === null) {
            localStorage.setItem(key, defaultValue);
            return defaultValue;
        }
        if (validValues && !validValues.includes(storedValue)) {
            localStorage.setItem(key, defaultValue);
            return defaultValue;
        }
        return storedValue;
    }, [key, defaultValue, validValues]);

    const [value, setValueState] = useState<string>(getInitialValue);

    useEffect(() => {
        const initialValue = getInitialValue();
        setValueState(initialValue);
    }, [key, defaultValue, getInitialValue]);

    const setValue = useCallback(
        (newValue: string) => {
            if (validValues && !validValues.includes(newValue)) {
                return;
            }
            localStorage.setItem(key, newValue);
            setValueState(newValue);
        },
        [key, validValues],
    );

    return [value, setValue];
}
