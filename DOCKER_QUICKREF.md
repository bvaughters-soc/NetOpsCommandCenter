# NetOps Command Center - Docker Quick Reference

## ONE-LINE SETUP

```bash
docker-compose up -d
```

Then open: **http://localhost:5000**

---

## File Structure

```
netops-command-center/
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Service orchestration
├── .dockerignore                # Files to exclude from build
├── network_device_manager.py    # Core device library
├── api_server.py                # Flask API backend
├── requirements.txt             # Python dependencies
└── static/
    └── index.html               # Web interface
```

---

## Essential Commands

| Action | Command |
|--------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **Restart** | `docker-compose restart` |
| **View Logs** | `docker-compose logs -f` |
| **Check Status** | `docker-compose ps` |
| **Rebuild** | `docker-compose up -d --build` |
| **Shell Access** | `docker-compose exec netops bash` |

---

## Docker vs Traditional Setup

### Traditional Setup Problems:
- ❌ "It works on my machine"
- ❌ Dependency conflicts
- ❌ Python version issues
- ❌ Module installation headaches
- ❌ Port conflicts
- ❌ Environment configuration

### Docker Solution:
- ✅ Consistent everywhere
- ✅ All dependencies bundled
- ✅ Isolated environment
- ✅ One command deployment
- ✅ Easy cleanup
- ✅ Production-ready

---

## Architecture

```
┌─────────────────────────────────────┐
│     Docker Host (Your Server)      │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Docker Container (netops)    │ │
│  │                               │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │  Python 3.11            │ │ │
│  │  │  + Flask                │ │ │
│  │  │  + Paramiko             │ │ │
│  │  │  + All Dependencies     │ │ │
│  │  └─────────────────────────┘ │ │
│  │                               │ │
│  │  Port 5000 → Host Port 5000   │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
            ↓
    Network Devices
    (SSH/Telnet)
```

---

## Port Mapping

**Container Internal:** 5000
**Host External:** 5000 (configurable)

Change in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use 8080 on host
```

---

## Environment Variables

Set in `docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=production      # Production mode
  - LOG_LEVEL=INFO           # Logging level
  - API_TIMEOUT=60           # Request timeout
```

---

## Volume Mounts

**Logs (Persistent):**
```yaml
volumes:
  - ./logs:/app/logs
```

**Development (Live Reload):**
```yaml
volumes:
  - ./static:/app/static
  - ./api_server.py:/app/api_server.py
```

---

## Health Check

Docker automatically monitors the container:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' netops-command-center
```

Health endpoint: `GET /api/health`

---

## Resource Limits

Control container resources in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      memory: 512M
```

---

## Networking

**Access from same machine:**
```
http://localhost:5000
```

**Access from another machine:**
```
http://YOUR_SERVER_IP:5000
```

**Custom network (advanced):**
```yaml
networks:
  netops-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Container won't start | `docker-compose logs` |
| Port already in use | Change port in docker-compose.yml |
| Can't connect | Check `docker-compose ps` |
| Code changes not applied | `docker-compose up -d --build` |
| Permission denied | Add user to docker group |
| Out of disk space | `docker system prune -a` |

---

## Production Deployment

### With HTTPS (Recommended):

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - netops
```

---

## Backup & Migration

**Export container:**
```bash
docker commit netops-command-center netops-backup
docker save netops-backup > netops.tar
```

**Restore on another machine:**
```bash
docker load < netops.tar
docker-compose up -d
```

---

## Security Hardening

1. **Run as non-root user:**
```dockerfile
RUN useradd -m -u 1000 netops
USER netops
```

2. **Read-only filesystem:**
```yaml
read_only: true
```

3. **Drop capabilities:**
```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

---

## Performance Tuning

**Multi-worker Flask:**
```bash
# Install gunicorn
pip install gunicorn

# Update CMD in Dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

---

## Monitoring

**View resource usage:**
```bash
docker stats netops-command-center
```

**View real-time logs:**
```bash
docker-compose logs -f --tail=100
```

**Check container uptime:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## CI/CD Integration

### GitHub Actions Example:
```yaml
- name: Build and push Docker image
  run: |
    docker build -t netops:latest .
    docker push your-registry/netops:latest
```

### GitLab CI Example:
```yaml
build:
  script:
    - docker build -t netops:latest .
    - docker push $CI_REGISTRY_IMAGE:latest
```

---

## Multi-Environment Setup

**Development:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Cleanup

**Remove container:**
```bash
docker-compose down
```

**Remove container and volumes:**
```bash
docker-compose down -v
```

**Remove all Docker resources:**
```bash
docker system prune -a --volumes
```

---

## Support

**View full documentation:**
- Docker basics: `DOCKER_README.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- API reference: `README_WEB.md`

**Quick health check:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-29T...",
  "cached_results": 0
}
```

---

## Summary

**To deploy:**
1. Install Docker & Docker Compose
2. Run: `docker-compose up -d`
3. Access: `http://localhost:5000`

**To update:**
1. Pull new code
2. Run: `docker-compose up -d --build`

**To remove:**
1. Run: `docker-compose down`

That's it! 🐳🚀
