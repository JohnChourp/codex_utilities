import pluginJs from "@eslint/js";
import globals from "globals";

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    ignores: ["**/node_modules/"],
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      sourceType: "commonjs",
      globals: {
        ...globals.browser,
        process: "readonly", // Add 'process' as a global variable
      },
    },
  },
  pluginJs.configs.recommended,
];
