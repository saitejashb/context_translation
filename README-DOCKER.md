# Docker Deployment Guide

## Security Notes ⚠️

**IMPORTANT**: This Docker setup is designed to keep sensitive files secure:
- `.env` files are **NOT** included in the Docker image
- JSON credential files are **NOT** included in the Docker image
- Sensitive files are mounted as read-only volumes at runtime

## Prerequisites

1. Docker and Docker Compose installed
2. `.env` file in the project root (not committed to git)
3. Google service account JSON file in the project root

## Quick Start

### Using Docker Compose (Recommended)

1. **Build the image:**
   ```bash
   docker-compose build
   ```

2. **Run the container:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t context-translation:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name context-translation-app \
     -p 5000:5000 \
     -v "$(pwd)/.env:/app/.env:ro" \
     -v "$(pwd)/concise-memory-477512-u4-d4e9392c74c4 (1).json:/app/service-account.json:ro" \
     -e GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account.json \
     -e FLASK_ENV=production \
     context-translation:latest
   ```

## Verify Security

After building, verify sensitive files are NOT in the image:

```bash
# Check if .env is in the image (should return nothing or error)
docker run --rm context-translation:latest ls -la /app/.env 2>&1

# Check if JSON files are in the image (should return nothing)
docker run --rm context-translation:latest find /app -name "*.json" 2>&1
```

## Environment Variables

The following environment variables can be set:

- `FLASK_SECRET_KEY` - Flask secret key (from .env)
- `FLASK_DEBUG` - Set to "true" for debug mode (default: "false")
- `FLASK_ENV` - Flask environment (default: "production")
- `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to service account JSON (default: `/app/service-account.json`)
- All other variables from your `.env` file

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs`
- Verify `.env` file exists and is readable
- Verify JSON service account file path is correct in `docker-compose.yml`

### Permission errors
- The container runs as user 1000:1000 by default
- Adjust the `user` field in `docker-compose.yml` if needed

### Port already in use
- Change the port mapping in `docker-compose.yml`: `"8080:5000"` (host:container)

