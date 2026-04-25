# Next.js Workflow Trigger UI

This is a minimal Next.js frontend for triggering the Cloud Run SDK service.

## Local setup

```bash
cd labs/dataform-agent-workflow-lab/frontend-nextjs
npm install
cp .env.local.example .env.local
npm run dev
```

Set:

```text
NEXT_PUBLIC_SDK_SERVICE_URL=http://localhost:8080
```

For Cloud Run, set `NEXT_PUBLIC_SDK_SERVICE_URL` to the deployed service URL.

## Flow

```text
Browser form
  -> Next.js page
      -> POST {SDK_SERVICE_URL}/run-workflow
          -> Claude Agent SDK service
```
