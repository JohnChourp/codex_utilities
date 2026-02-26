// eslint-disable-next-line eslint-comments/disable-enable-pair
/* eslint-disable import/no-unresolved */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import angularEslint from "@angular-eslint/eslint-plugin";
import { fixupConfigRules, fixupPluginRules } from "@eslint/compat";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import typescriptEslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import _import from "eslint-plugin-import";
import preferArrow from "eslint-plugin-prefer-arrow";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ESLINT_FLAT_CONFIG_FILENAMES = ["eslint.config.js", "eslint.config.mjs", "eslint.config.cjs"];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  {
    ignores: ["**/node_modules/", "**/.angular/", "**/www/", "**/dist/", "**/*.html", "**/*.spec.ts"],
  },
  ...fixupConfigRules(
    compat.extends(
      "eslint:recommended",
      "plugin:@typescript-eslint/recommended",
      "plugin:@angular-eslint/recommended",
      "plugin:@angular-eslint/template/process-inline-templates",
      "plugin:import/recommended",
      "plugin:import/typescript",
      "plugin:eslint-comments/recommended",
      "plugin:security/recommended-legacy",
      "plugin:unicorn/recommended"
    )
  ),
  {
    plugins: {
      "@typescript-eslint": fixupPluginRules(typescriptEslint),
      "@angular-eslint": fixupPluginRules(angularEslint),
      import: fixupPluginRules(_import),
      "prefer-arrow": preferArrow,
    },

    languageOptions: {
      globals: {
        ...globals.browser,
      },

      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: "module",
    },

    rules: {
      "no-debugger": "error",

      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": [
        "off",
      ],
      
      "no-undef": "error",
      semi: ["error", "always"],
      quotes: ["error", "double"],
      "prefer-const": "error",
      "object-curly-spacing": ["error", "always"],
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@angular-eslint/no-empty-lifecycle-method": "warn",
      "@angular-eslint/no-input-rename": "warn",
      "prefer-arrow-callback": "error",
      "no-magic-numbers": "off",
      "unicorn/no-null": "off",
      "unicorn/prefer-structured-clone": "off",
      "no-mixed-spaces-and-tabs": "off",
      "unicorn/empty-brace-spaces": "off",
      "unicorn/prefer-add-event-listener": "off",
      "security/detect-object-injection": "off",
      "unicorn/numeric-separators-style": "off",
      "@angular-eslint/prefer-standalone": "off",
      "unicorn/no-nested-ternary": "off",
      "unicorn/prefer-top-level-await":"off",
      "unicorn/consistent-function-scoping": "off",

      "unicorn/prevent-abbreviations": [
        "error",
        {
          allowList: {
            res: true,
          },
        },
      ],

      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "app",
          style: "camelCase",
        },
      ],

      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "app",
          style: "kebab-case",
        },
      ],

      "@typescript-eslint/member-ordering": [
        "error",
        {
          default: [
            "public-static-field",
            "protected-static-field",
            "private-static-field",
            "public-instance-field",
            "protected-instance-field",
            "private-instance-field",
            "constructor",
            "public-method",
            "protected-method",
            "private-method",
          ],
        },
      ],

      "@angular-eslint/component-class-suffix": [
        "error",
        {
          suffixes: ["Component", "Page", "View"],
        },
      ],
    },
  },
];
