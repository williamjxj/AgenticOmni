# Frontend Environment Configuration

Create a `.env.local` file in the `frontend/` directory with the following variables:

**⚠️ IMPORTANT**: The `NEXT_PUBLIC_API_URL` **MUST** include the `/api/v1` path!

```bash
# Backend API URL (MUST include /api/v1 path)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Optional: Enable debug mode
# NEXT_PUBLIC_DEBUG=true
```

## Development

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Production

```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com/api/v1
```

## Usage

The API client in `lib/api/client.ts` automatically uses the `NEXT_PUBLIC_API_URL` environment variable.
If not set, it defaults to `http://localhost:8000/api/v1`.
