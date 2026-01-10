# Frontend Environment Configuration

Create a `.env.local` file in the `frontend/` directory with the following variables:

**⚠️ IMPORTANT**: The `NEXT_PUBLIC_API_URL` should be the **base URL only** (WITHOUT `/api/v1`).  
The `api-client.ts` automatically adds `/api/v1` to all requests.

```bash
# Backend API URL (base URL only - /api/v1 is added automatically by api-client.ts)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Enable debug mode
# NEXT_PUBLIC_DEBUG=true
```

## Development

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production

```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

## How It Works

The API client in `lib/api-client.ts` constructs URLs like this:

```typescript
const url = `${API_BASE_URL}/api/${API_VERSION}${endpoint}`;
// Example: http://localhost:8000 + /api/v1 + /health
// Result:  http://localhost:8000/api/v1/health
```

So **DO NOT** include `/api/v1` in the `NEXT_PUBLIC_API_URL` environment variable, or you'll get duplicate paths like `/api/v1/api/v1/health`.

## Correct vs Incorrect

✅ **Correct**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
Result: `http://localhost:8000/api/v1/health` ✓

❌ **Incorrect**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```
Result: `http://localhost:8000/api/v1/api/v1/health` ✗
