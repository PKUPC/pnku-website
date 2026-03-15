/**
 * 将外部库的 import 替换为从 window 中获取，例如
 * import React from 'react';
 * 替换为
 * const React = window.React;
 *
 * import { useState, useEffect } from 'react';
 * 替换为
 * const { useState, useEffect } = window.React;
 *
 * 主要用于 esm 形式打包的 Remote Component 使用，只能处理简单的内容，复杂的第三方库不行。
 */
import MagicString from 'magic-string';
import type { Plugin } from 'vite';

export interface ExternalLibrary {
    /** 包名，例如 'react' */
    packageName: string;
    /** 全局变量名，例如 'window.React' */
    globalName: string;
    /** 排除的路径模式，例如 'node_modules/react/' */
    excludePattern?: string | RegExp;
    /** 是否支持 default import，默认为 true */
    supportsDefaultImport?: boolean;
    /** 允许的 named imports 列表，如果未指定则允许所有 */
    allowedNamedImports?: string[];
    /** 遇到不支持的导入时的处理方式：'error' 抛出错误，'warn' 警告但继续，'ignore' 忽略，默认为 'warn' */
    onUnsupportedImport?: 'error' | 'warn' | 'ignore';
}

interface ImportMatch {
    start: number;
    end: number;
    defaultImport?: string;
    namedImports?: string;
    rawMatch: string;
}

/**
 * 解析 named imports 字符串，提取导入项名称
 * 例如: "{ useState, useEffect as useE, lazy }" -> ["useState", "useEffect", "lazy"]
 */
function parseNamedImports(namedImportsStr: string): string[] {
    if (!namedImportsStr) {
        return [];
    }

    // 移除花括号和空格
    const cleaned = namedImportsStr.replace(/[{}]/g, '').trim();
    if (!cleaned) {
        return [];
    }

    // 分割并提取导入项名称（处理 as 别名）
    return cleaned.split(',').map((item) => {
        const trimmed = item.trim();
        // 处理 "useState as useS" 这种情况，取前面的名称
        const asIndex = trimmed.indexOf(' as ');
        return asIndex >= 0 ? trimmed.substring(0, asIndex).trim() : trimmed;
    });
}

/**
 * 验证导入是否被支持
 * @param defaultImport default import 名称
 * @param namedImports named imports 字符串
 * @param library 库配置
 * @returns 验证结果和错误信息
 */
function validateImports(
    defaultImport: string | undefined,
    namedImports: string | undefined,
    library: ExternalLibrary,
): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const { supportsDefaultImport = true, allowedNamedImports, onUnsupportedImport = 'warn' } = library;

    // 检查 default import
    if (defaultImport) {
        if (!supportsDefaultImport) {
            errors.push(
                `库 "${library.packageName}" 不支持 default import，但代码中使用了 "import ${defaultImport} from '${library.packageName}'"`,
            );
        }
    }

    // 检查 named imports
    if (namedImports && allowedNamedImports) {
        const parsedImports = parseNamedImports(namedImports);
        const unsupported = parsedImports.filter((imp) => !allowedNamedImports.includes(imp));

        if (unsupported.length > 0) {
            errors.push(
                `库 "${library.packageName}" 不支持以下 named imports: ${unsupported.join(', ')}。允许的 imports: ${allowedNamedImports.join(', ')}`,
            );
        }
    }

    return {
        valid: errors.length === 0 || onUnsupportedImport === 'ignore',
        errors,
    };
}

/**
 * 处理单个库的导入替换
 * @param code 源代码
 * @param library 库配置
 * @param id 文件路径（用于错误报告）
 * @param debug 是否开启调试模式
 * @returns 替换后的代码和 source map，如果没有匹配则返回 null
 */
function replaceImportsForLibrary(
    code: string,
    library: ExternalLibrary,
    id: string,
    debug: boolean = false,
): { code: string; map: any } | null {
    const { packageName, globalName, onUnsupportedImport = 'warn' } = library;

    // 构建匹配该库导入的正则表达式
    const escapedPackageName = packageName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const importRegex = new RegExp(
        `import\\s+(?:([^,\\s]+)\\s*,?\\s*)?(?:\\{([^}]+)\\})?\\s+from\\s+['"]${escapedPackageName}['"]\\s*;?`,
        'g',
    );

    const matches: ImportMatch[] = [];
    let match;

    while ((match = importRegex.exec(code)) !== null) {
        matches.push({
            start: match.index,
            end: match.index + match[0].length,
            defaultImport: match[1]?.trim(),
            namedImports: match[2]?.trim(),
            rawMatch: match[0],
        });
    }

    if (matches.length === 0) {
        return null;
    }

    // 验证所有导入
    for (const matchItem of matches) {
        const validation = validateImports(matchItem.defaultImport, matchItem.namedImports, library);
        if (!validation.valid) {
            if (onUnsupportedImport === 'error') {
                throw new Error(
                    `[vite-plugin-remote-component] 在文件 ${id} 中发现不支持的导入:\n${validation.errors.join('\n')}`,
                );
            } else if (onUnsupportedImport === 'warn') {
                console.warn(
                    `[vite-plugin-remote-component] 在文件 ${id} 中发现不支持的导入:\n${validation.errors.join('\n')}\n原始导入: ${matchItem.rawMatch}`,
                );
            }
        }
    }

    const s = new MagicString(code);

    // 从后往前替换，避免位置偏移
    for (let i = matches.length - 1; i >= 0; i--) {
        const { start, end, defaultImport, namedImports, rawMatch } = matches[i];

        let replacement = '';

        if (defaultImport && namedImports) {
            // import React, { useState, lazy } from 'react';
            replacement = `const ${defaultImport} = ${globalName};\nconst { ${namedImports} } = ${defaultImport};`;
        } else if (defaultImport) {
            // import React from 'react';
            replacement = `const ${defaultImport} = ${globalName};`;
        } else if (namedImports) {
            // import { useState, lazy } from 'react';
            replacement = `const { ${namedImports} } = ${globalName};`;
        }

        if (debug) {
            console.log(
                `[vite-plugin-remote-component] 文件: ${id}\n  库: ${packageName}\n  原始: ${rawMatch.trim()}\n  替换为: ${replacement.trim()}\n`,
            );
        }

        s.overwrite(start, end, replacement);
    }

    return {
        code: s.toString(),
        map: s.generateMap({ hires: true }),
    };
}

/**
 * 检查文件路径是否应该被排除
 */
function shouldExcludeFile(id: string, library: ExternalLibrary): boolean {
    if (!library.excludePattern) {
        return false;
    }

    if (typeof library.excludePattern === 'string') {
        return id.includes(library.excludePattern);
    }

    return library.excludePattern.test(id);
}

export interface RemoteComponentPluginOptions {
    /** 需要外部化的库列表，默认为 [{ packageName: 'react', globalName: 'window.React' }] */
    libraries?: ExternalLibrary[];
    /** 是否开启调试模式，开启后会输出每个文件的替换信息，默认为 false */
    debug?: boolean;
}

export function remoteComponentPlugin(options?: RemoteComponentPluginOptions): Plugin {
    // 默认配置：支持 react
    const libraries: ExternalLibrary[] = options?.libraries ?? [];

    const debug = options?.debug ?? false;

    return {
        name: 'vite-plugin-remote-component',
        apply: 'build', // 只在打包时应用

        transform(code, id) {
            // 只处理 js/ts/jsx/tsx 文件
            if (!/\.(j|t)sx?$/.test(id)) {
                return null;
            }

            let result: { code: string; map: any } | null = null;
            let modifiedCode = code;

            // 依次处理每个库
            for (const library of libraries) {
                // 检查是否应该排除该文件
                if (shouldExcludeFile(id, library)) {
                    if (debug) {
                        console.log(
                            `[vite-plugin-remote-component] 文件: ${id}\n  库: ${library.packageName}\n  状态: 已排除（匹配排除模式）\n`,
                        );
                    }
                    continue;
                }

                // 处理该库的导入替换
                const libraryResult = replaceImportsForLibrary(modifiedCode, library, id, debug);
                if (libraryResult) {
                    modifiedCode = libraryResult.code;
                    result = libraryResult;
                }
            }

            return result;
        },
    };
}
