import terser from '@rollup/plugin-terser';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import Md5 from 'crypto-js/md5';
import { existsSync } from 'fs';
import { resolve } from 'path';
import { defineConfig, loadEnv } from 'vite';
import { analyzer } from 'vite-bundle-analyzer';
import { compression, defineAlgorithm } from 'vite-plugin-compression2';
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';
import svgr from 'vite-plugin-svgr';
import zlib from 'zlib';

import { remoteComponentPlugin } from './vite-plugin-remote-component';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const DEV_FRONTEND_PORT = Number(env.DEV_FRONTEND_PORT) || 3333;

    const componentName = process.argv.find((arg) => arg.startsWith('--component='))?.split('=')[1] ?? 'HelloWorld';
    console.info(`Trying to build ${componentName}`);

    const componentPath = `./src/remote/${componentName}/index.tsx`;
    if (!existsSync(componentPath)) {
        throw new Error(`Component file does not exist: ${componentPath}`);
    }

    return {
        publicDir: false,
        css: {
            modules: {
                generateScopedName: (name, filename, css) => {
                    // 在name的每个大写字母前加 - 然后把大写转成小写
                    name = name.replace(/([A-Z])/g, '-$1').toLowerCase();
                    const hash = Md5(filename + css)
                        .toString()
                        .substring(0, 8);
                    return `${name}-${hash}`;
                },
            },
        },
        resolve: {
            alias: [{ find: '@', replacement: resolve(__dirname, 'src') }],
        },
        build: {
            lib: {
                entry: { [componentName]: componentPath },
                formats: ['es'],
                fileName: (format, entryName) => `${entryName}.js`,
            },
            target: ['es2022', 'firefox128', 'chrome111', 'safari16.4'],
            outDir: 'build_remote',
            assetsInlineLimit: 8192,
            sourcemap: false,
            chunkSizeWarningLimit: 1500,
            reportCompressedSize: true,
            rollupOptions: {
                output: {
                    compact: true,
                },
                // 参考 https://vite.dev/config/build-options.html#build-minify
                // 在 lib + es module 模式下 vite 默认不会启用 terser，会破坏 tree shaking
                // 但是在我们的场景中并不需要这个 feature，这里直接用 rollup 插件处理
                plugins: [
                    terser({
                        compress: {
                            drop_console: true,
                        },
                    }),
                ],
            },
        },
        esbuild: {
            legalComments: 'none',
        },
        plugins: [
            remoteComponentPlugin({
                libraries: [
                    {
                        packageName: 'react',
                        globalName: 'window.exports.React',
                    },
                ],
                debug: true,
            }),
            react({
                jsxRuntime: 'classic',
            }),
            svgr(),
            tailwindcss(),
            cssInjectedByJsPlugin(),
            ...(process.env.ANALYZE_BUNDLE === 'true'
                ? [
                      analyzer({
                          analyzerMode: 'server',
                          analyzerPort: DEV_FRONTEND_PORT + 1,
                          openAnalyzer: true,
                          defaultSizes: 'brotli',
                          brotliOptions: {
                              params: {
                                  [zlib.constants.BROTLI_PARAM_MODE]: zlib.constants.BROTLI_MODE_TEXT,
                                  [zlib.constants.BROTLI_PARAM_QUALITY]: zlib.constants.BROTLI_MAX_QUALITY,
                              },
                          },
                          gzipOptions: {
                              level: zlib.constants.Z_BEST_COMPRESSION,
                          },
                      }),
                  ]
                : [
                      compression({
                          include: /\.*$/,
                          exclude: /\.(png|jpg|jpeg|webp|mp3|ogg|webm)$/i,
                          algorithms: [
                              defineAlgorithm('brotliCompress', {
                                  params: {
                                      [zlib.constants.BROTLI_PARAM_MODE]: zlib.constants.BROTLI_MODE_TEXT,
                                      [zlib.constants.BROTLI_PARAM_QUALITY]: zlib.constants.BROTLI_MAX_QUALITY,
                                  },
                              }),
                              defineAlgorithm('gzip', {
                                  level: zlib.constants.Z_BEST_COMPRESSION,
                              }),
                          ],
                      }),
                  ]),
        ],
    };
});
