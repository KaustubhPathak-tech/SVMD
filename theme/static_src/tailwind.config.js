module.exports = {
  content: [
    "../templates/**/*.html",
    "../../templates/**/*.html",
    "../../**/*.html",
    "../../**/*.js",
    "../../**/*.py",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("daisyui")
  ],
}
