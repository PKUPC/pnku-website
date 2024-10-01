/** @type {import("tailwindcss").Config} */
import daisyui from 'daisyui';

export default {
    content: ['./src/**/*.{html,js,jsx,ts,tsx}', 'index.html'],
    theme: {
        screens: {
            sm: '576px',
            w640: '640px',
            md: '768px',
            lg: '992px',
            xl: '1200px',
            xxl: '1600px',
        },
        extend: {},
    },
    daisyui: {
        themes: ['light', 'corporate', 'cupcake', 'dark', 'dracula', 'luxury'],
    },
    plugins: [
        daisyui,
        function ({ addVariant }) {
            addVariant('not-last', '&:not(:last-child)');
        },
    ],
};
