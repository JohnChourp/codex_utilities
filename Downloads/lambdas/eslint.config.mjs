import pluginJs from "@eslint/js";
import globals from "globals";

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    ignores: [
      "**/node_modules/",
      "**/codeliver-create-routes/**",
      "**/codeliver-serverless-restart-browser/**",
      "**/codeliver-localserver-x64/**",
      "**/codeliver-create-routes-orchestrator/**",
      "**/codeliver-create-routes-orchestrator",
      "**/codeliver-pos-get-request-image-raster/**",
      "**/codeliver-request-screenshot-lambda/**"
    ]
  },
  pluginJs.configs.recommended,
  {
    files: ["**/*.js"],
    languageOptions: {
      sourceType: "commonjs",
      globals: {
        ...globals.browser,
        process: "readonly", // Add 'process' as a global variable
        Buffer: "readonly", // Node.js built-in global
        __dirname: "readonly" // Node.js CommonJS global
      }
    },
    rules: {
      "no-unused-vars": [
        "error",
        {
          varsIgnorePattern: "^_",
          argsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_"
        }
      ]
    }
  }
];
