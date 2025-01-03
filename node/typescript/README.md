# Typescript Lambda

Do deploy, run included build script, and/or:

1. Install prerequisites

  ```bash
  $ npm install @types/aws-lambda
  $ npm install --save-exact --save-dev esbuild

  # or just
  $ npm install
  ```

2. Compile to javascript

  ```bash
  $ ./node_modules/.bin/esbuild handler.ts --bundle --minify --sourcemap \
      --platform=node --target=es2020 --outfile=handler.js
  ```

3. Deploy as normal

  ```bash
  $ aweserv sls deploy
  ```
