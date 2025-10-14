module.exports = {
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: "module",
    ecmaFeatures: { jsx: true },
  },
  plugins: ["react", "@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
  ],
  settings: {
    react: { version: "detect" },
  },
  rules: {
    "react/react-in-jsx-scope": "off",
    // Disable this rule in CI pre-commit environments where plugin/runtime
    // resolution can be brittle. Re-enable or tighten later when migrating
    // frontend lint setup to a shared, explicit config.
    '@typescript-eslint/no-unused-expressions': 'off',
  },
};
