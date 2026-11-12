# snakemake-deploy-oauth

Tiny Vercel functions that perform the GitHub OAuth code exchange for the
[Snakemake deploy webapp](https://github.com/Hocnonsense/snakemake-deploy-webapp).
The client secret stays on Vercel; the functions do not store anything.

## Endpoints

- `GET /api/start?state=<nonce>&origin=<app-origin>` — validates the origin and
  redirects to GitHub.
- `GET /api/callback?code=...&state=...` — exchanges the code for a token and
  returns a small HTML page that `postMessage`s it to the opener.

## Environment variables

```text
GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET
GITHUB_CALLBACK_URL=https://<project>.vercel.app/api/callback
APP_ORIGINS=https://<user>.github.io,http://localhost:8000
GITHUB_OAUTH_SCOPE=read:user public_repo
```

Use `read:user repo` instead of `public_repo` if users should deploy into
private repositories.

## Deploy

```bash
npm install -g vercel   # or use npx vercel
vercel login
vercel                   # first run: create/link the project
vercel --prod
```

Create a GitHub OAuth App with:

```text
Homepage URL:     https://<user>.github.io/snakemake-deploy-webapp/
Callback URL:     https://<project>.vercel.app/api/callback
```

Set the environment variables in the Vercel project, redeploy, and update the
`OAUTH_ORIGIN` constant in the webapp's `index.html`.

## Local test

```bash
pixi run test
```

The tests only cover the pure helpers; the endpoints are exercised against
GitHub in a deployed preview.
