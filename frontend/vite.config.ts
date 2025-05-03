import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import obfuscator from 'rollup-plugin-obfuscator';
import { defineConfig, loadEnv } from 'vite';
import { compression } from 'vite-plugin-compression2';
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
    return {
        root: '.',
        publicDir: 'public',
        build: {
            target: ['es2015', 'firefox78', 'chrome79', 'safari13'],
            outDir: 'build',
            assetsInlineLimit: 8192,
            sourcemap: process.env.GENERATE_SOURCEMAP === 'true',
            chunkSizeWarningLimit: 1500,
            reportCompressedSize: true,
            rollupOptions: {
                output: {
                    compact: true,
                    manualChunks: {
                        vendor: [
                            'react',
                            'react-dom',
                            'react-router-dom',
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
            compression({
                include: /\.*$/,
                exclude: /\.(png|jpg|jpeg|webp|mp3|ogg|webm)$/i,
                algorithm: 'brotliCompress',
                compressionOptions: {
                    params: {
                        [zlib.constants.BROTLI_PARAM_MODE]: zlib.constants.BROTLI_MODE_TEXT,
                        [zlib.constants.BROTLI_PARAM_QUALITY]: zlib.constants.BROTLI_MAX_QUALITY,
                    },
                },
            }),
            compression({
                include: /\.*$/,
                exclude: /\.(png|jpg|jpeg|webp|mp3|ogg|webm)$/i,
                algorithm: 'gzip',
                compressionOptions: {
                    level: zlib.constants.Z_BEST_COMPRESSION,
                },
            }),
        ],
        server: {
            open: true,
            port: 3333,
            proxy: {
                '/service/': {
                    target: env.DEV_BACKEND_URL,
                    changeOrigin: true,
                    ws: true,
                },
                '/media/': {
                    target: env.DEV_BACKEND_URL,
                    changeOrigin: true,
                },
                '/m/': {
                    target: env.DEV_BACKEND_URL,
                    changeOrigin: true,
                },
                '/t/': {
                    target: env.DEV_BACKEND_URL,
                    changeOrigin: true,
                },
            },
        },
    };
});
