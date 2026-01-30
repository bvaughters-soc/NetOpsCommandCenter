# NetOps Command Center - Docker Deployment Guide

Run the NetOps Command Center in Docker with zero configuration headaches! 🐳

## Why Docker?

✅ **No dependency issues** - Everything bundled in the container
✅ **Consistent environment** - Works the same everywhere
✅ **Easy deployment** - One command to start
✅ **Isolated** - Doesn't affect your system
✅ **Portable** - Run on any machine with Docker
✅ **Production-ready** - Includes health checks and restart policies

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

**Check if you have Docker:**
```bash
docker --version
docker-compose --version
```

## Quick Start (Docker Compose - RECOMMENDED)

### Option 1: Using Docker Compose (Easiest)

```bash
# 1. Navigate to the project directory
cd /path/to/netops

# 2. Start the container
docker-compose up -d

# 3. Access the application
# Open browser to http://localhost:5000
```

That's it! The application is now running. 🚀

### Check Status
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Check health
curl http://localhost:5000/api/health
```

### Stop the Container
```bash
docker-compose down
```

## Option 2: Using Docker CLI

```bash
# 1. Build the image
docker build -t netops-command-center .

# 2. Run the container
docker run -d \
  --name netops \
  -p 5000:5000 \
  --restart unless-stopped \
  netops-command-center

# 3. Access the application
# Open browser to http://localhost:5000
```

## Accessing the Application

Once running, open your browser to:
```
http://localhost:5000
```

**From another machine on your network:**
```
http://YOUR_SERVER_IP:5000
```

## Docker Commands Reference

### Container Management
```bash
# Start container
docker-compose up -d

# Stop container
docker-compose down

# Restart container
docker-compose restart

# View logs
docker-compose logs -f netops

# View last 100 lines
docker-compose logs --tail=100 netops

# Execute command in container
docker-compose exec netops bash
```

### Monitoring
```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats netops-command-center

# Check health
docker inspect --format='{{.State.Health.Status}}' netops-command-center
```

### Rebuilding
```bash
# Rebuild after code changes
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

## Configuration

### Changing the Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 8080 to your desired port
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Environment Variables

Edit `docker-compose.yml` to add environment variables:
```yaml
environment:
  - FLASK_ENV=production
  - LOG_LEVEL=INFO
  - API_TIMEOUT=60
```

### Persistent Logs

Logs are automatically saved to `./logs` directory on your host machine.

```bash
# View log files
ls -l logs/

# Tail log file
tail -f logs/app.log
```

## Network Access Configuration

### Allow Access from Other Machines

By default, the container listens on all interfaces (0.0.0.0:5000).

**Firewall Configuration (if needed):**

**Linux:**
```bash
# Allow port 5000
sudo ufw allow 5000/tcp
```

**Windows:**
```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="NetOps" dir=in action=allow protocol=TCP localport=5000
```

## Production Deployment

### Using Nginx Reverse Proxy

Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Add to `docker-compose.yml`:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - netops
```

### HTTPS with Let's Encrypt

Add Certbot service to `docker-compose.yml`:
```yaml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs netops
```

**Common issues:**
- Port 5000 already in use: Change port in docker-compose.yml
- Permission denied: Run with `sudo` or add user to docker group

### Can't Access from Browser

**Check if container is running:**
```bash
docker-compose ps
```

**Check from inside container:**
```bash
docker-compose exec netops curl http://localhost:5000/api/health
```

**Check from host:**
```bash
curl http://localhost:5000/api/health
```

### Health Check Failing

**View health status:**
```bash
docker inspect --format='{{json .State.Health}}' netops-command-center | python -m json.tool
```

**Common causes:**
- Application not starting: Check logs
- Port not exposed: Check Dockerfile and docker-compose.yml
- Firewall blocking: Check firewall rules

### Permission Issues with Volumes

```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/
```

## Development Mode

For development with live code reloading:

Edit `docker-compose.yml`:
```yaml
volumes:
  - ./network_device_manager.py:/app/network_device_manager.py
  - ./api_server.py:/app/api_server.py
  - ./static:/app/static
environment:
  - FLASK_ENV=development
```

Restart:
```bash
docker-compose up -d --build
```

## Backup and Restore

### Backup Container State
```bash
# Export container
docker export netops-command-center > netops-backup.tar

# Save image
docker save netops-command-center:latest > netops-image.tar
```

### Restore
```bash
# Load image
docker load < netops-image.tar

# Start from backed up image
docker-compose up -d
```

## Resource Limits

Add resource limits to `docker-compose.yml`:
```yaml
services:
  netops:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

## Multi-Stage Build (Advanced)

For smaller images, edit `Dockerfile`:
```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["python", "api_server.py"]
```

## Security Best Practices

1. **Don't run as root** (add to Dockerfile):
```dockerfile
RUN useradd -m -u 1000 netops
USER netops
```

2. **Use secrets for credentials:**
```bash
# Create secret
echo "my_secret_password" | docker secret create db_password -

# Use in compose
secrets:
  - db_password
```

3. **Scan for vulnerabilities:**
```bash
docker scan netops-command-center
```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify it's running
docker-compose ps
curl http://localhost:5000/api/health
```

## Complete Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] All files in project directory
- [ ] Port 5000 available (or changed in docker-compose.yml)
- [ ] Run `docker-compose build`
- [ ] Run `docker-compose up -d`
- [ ] Check `docker-compose ps` shows "Up"
- [ ] Access `http://localhost:5000` in browser
- [ ] Configure firewall if accessing remotely
- [ ] Set up HTTPS for production (optional)
- [ ] Configure backups (optional)

## Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify container is running: `docker-compose ps`
3. Test API: `curl http://localhost:5000/api/health`
4. Check inside container: `docker-compose exec netops bash`
5. Rebuild: `docker-compose up -d --build --force-recreate`

## Summary

**To start:** `docker-compose up -d`
**To stop:** `docker-compose down`
**To view logs:** `docker-compose logs -f`
**To access:** `http://localhost:5000`

That's all you need! 🎉
