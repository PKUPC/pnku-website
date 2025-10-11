import react from '@vitejs/plugin-react';
import Md5 from 'crypto-js/md5';
import { resolve } from 'path';
import obfuscator from 'rollup-plugin-obfuscator';
import { defineConfig, loadEnv } from 'vite';
import { analyzer } from 'vite-bundle-analyzer';
import { compression, defineAlgorithm } from 'vite-plugin-compression2';
import { createHtmlPlugin } from 'vite-plugin-html';
import svgr from 'vite-plugin-svgr';
import zlib from 'zlib';

function getCurrentTimeFormatted() {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-based in JS
    const year = String(now.getFullYear()).slice(-2);
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    return `${year}${month}${day}${hour}${minute}`;
}

process.env.VITE_APP_BUILD_INFO = getCurrentTimeFormatted();

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const DEV_BACKEND_URL = env.DEV_BACKEND_URL || 'http://127.0.0.1:8080';
    const DEV_FRONTEND_PORT = Number(env.DEV_FRONTEND_PORT) || 3333;
    const DEV_FRONTEND_HOST = env.DEV_FRONTEND_HOST || 'localhost';

    return {
        root: '.',
        publicDir: 'public',
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
        build: {
            target: ['es2022', 'firefox128', 'chrome111', 'safari16.4'],
            outDir: 'build',
            assetsInlineLimit: 8192,
            sourcemap: false,
            chunkSizeWarningLimit: 1500,
            reportCompressedSize: true,
            rollupOptions: {
                output: {
                    compact: true,
                    manualChunks: {
                        vendor: [
                            'react',
                            'react-dom',
                            'react-router',
                            'react-timeago',
                            'react-copy-to-clipboard',
                            'react-google-recaptcha',
                            'react-use-error-boundary',
                            'html-react-parser',
                            'crypto-js',
                            'seedrandom',
                            'swr',
                            'colorjs.io',
                        ],
                        antd: [
                            'antd/es/form',
                            'antd/es/input',
                            'antd/es/upload',
                            'antd/es/modal',
                            'antd/es/notification',
                            'antd/es/theme',
                            'antd/es/button',
                            'antd/es/progress',
                            'antd/es/style',
                            'antd/es/badge',
                            'antd/es/float-button',
                            'antd/es/config-provider',
                            'antd/es/message',
                            'antd/es/input-number',
                            'antd/es/image',
                            'antd/es/drawer',
                            'antd/es/timeline',
                            'antd/es/alert',
                            'antd/es/tag',
                            'antd/es/tooltip',
                            'antd/es/empty',
                            'antd/es/grid',
                            'antd/es/carousel',
                            'antd/es/collapse',
                            'antd/es/switch',
                            'antd/es/locale',
                            'antd/es/result',
                        ],
                    },
                },
            },
            minify: 'terser',
            terserOptions: {
                compress: {
                    drop_console: true,
                },
            },
        },
        esbuild: {
            legalComments: 'none',
        },
        resolve: {
            alias: [
                { find: '@', replacement: resolve(__dirname, 'src') },
                {
                    find: /^(\.\/(?:noFound|serverError|unauthorized))$/,
                    replacement: '$1',
                    customResolver: (_source, importer, _options) => {
                        if (importer && /\/node_modules\/antd\/es\/result\/index\.js$/.test(importer)) {
                            return resolve(__dirname, 'src/empty.ts');
                        }
                        return null;
                    },
                },
                {
                    find: /^(\.\.\/skeleton)$/,
                    replacement: '$1',
                    customResolver: (_source, importer, _options) => {
                        if (importer && /\/node_modules\/antd\/es\/.*?$/.test(importer)) {
                            return resolve(__dirname, 'src/empty.ts');
                        }
                        return null;
                    },
                },
            ],
        },
        plugins: [
            react(),
            svgr(),
            obfuscator({
                include: 'src/setup.ts',
                options: {
                    controlFlowFlattening: true,
                    deadCodeInjection: true,
                    splitStrings: true,
                    splitStringsChunkLength: 5,
                    stringArrayEncoding: ['base64'],
                    unicodeEscapeSequence: true,
                },
            }),
            createHtmlPlugin({ minify: true }),
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
        server: {
            open: true,
            host: DEV_FRONTEND_HOST,
            port: DEV_FRONTEND_PORT,
            proxy: {
                '/service/': {
                    target: DEV_BACKEND_URL,
                    changeOrigin: true,
                    ws: true,
                },
                '/media/': {
                    target: DEV_BACKEND_URL,
                    changeOrigin: true,
                },
                '/m/': {
                    target: DEV_BACKEND_URL,
                    changeOrigin: true,
                },
                '/t/': {
                    target: DEV_BACKEND_URL,
                    changeOrigin: true,
                },
            },
        },
    };
});
