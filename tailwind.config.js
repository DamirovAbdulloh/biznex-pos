/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.html',
        './*/templates/**/*.html',
        './static/spa/**/*.js',
    ],
    theme: {
        extend: {},
    },
    plugins: [],
};
