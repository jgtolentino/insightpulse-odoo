# Docker Runbook

## Disk Pressure

**Severity**: P0
**Symptoms**: Container start failures, image pull failures, build errors

### Detect
- Alert `DockerDiskPressure` fired
- Docker commands failing with "no space left on device"
- Build failures

### Check
```bash
# 1. Check disk usage
df -h

# 2. Check Docker disk usage
docker system df

# 3. Check detailed breakdown
docker system df -v

# 4. Find large containers
docker ps -a --size | sort -k7 -h -r | head -10

# 5. Find large images
docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | sort -k2 -h -r | head -10

# 6. Check logs size
sudo du -sh /var/lib/docker/containers/*/*.log | sort -h -r | head -10

# 7. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}/node_filesystem_size_bytes' | jq .
```

### Heal
```bash
# Run auto-heal handlers
./auto-healing/handlers/prune_docker.sh
./auto-healing/handlers/prune_logs.sh

# Or manually prune
docker system prune -af --volumes
docker image prune -af
docker volume prune -f

# Truncate large log files
sudo find /var/lib/docker/containers -name '*-json.log' -size +200M -exec truncate -s 0 {} \;
```

### Verify
```bash
# Check disk usage improved
df -h
docker system df

# Should show >20% free space

# Test container operations
docker run --rm alpine echo "test"
# Should succeed
```

### Prevent
- Regular prune schedule (daily/weekly cron)
- Configure log rotation in `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```
- Use volume lifecycle policies
- Monitor disk usage trends
- Set up disk usage alerts
- Remove unused volumes regularly

---

## OOM Kill

**Severity**: P1
**Symptoms**: Container restarts, OOMKilled status, application crashes

### Detect
- Alert `DockerOOMKill` fired
- Container shows "OOMKilled" in status
- Application logs cut off abruptly

### Check
```bash
# 1. Check container status
docker ps -a | grep -i oomkilled

# 2. Check detailed container info
docker inspect <container_id> | jq '.[0].State'

# 3. Check memory usage
docker stats --no-stream

# 4. Check memory limits
docker inspect <container_id> | jq '.[0].HostConfig.Memory'

# 5. Check dmesg for OOM killer messages
sudo dmesg | grep -i "out of memory\|oom"

# 6. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=rate(container_oom_kill_total[10m])' | jq .
curl -s 'http://localhost:9090/api/v1/query?query=container_memory_usage_bytes/container_spec_memory_limit_bytes' | jq .
```

### Heal
```bash
# Run auto-heal handlers
./auto-healing/handlers/restart_container.sh <container_name>
./auto-healing/handlers/increase_memory_limit.sh <container_name>

# Or manually restart
docker compose restart <service>

# Or increase memory limit
# Edit docker-compose.yml:
# services:
#   <service>:
#     mem_limit: 2g  # Increase as needed
docker compose up -d <service>
```

### Verify
```bash
# 1. Check container running
docker ps | grep <container_name>

# 2. Monitor memory usage
watch -n 10 'docker stats --no-stream | grep <container_name>'

# Should stabilize below 85% of limit

# 3. Check logs for normal operation
docker compose logs <service> --tail 50
```

### Prevent
- Set appropriate memory limits based on workload
- Monitor memory usage trends
- Implement backpressure mechanisms
- Optimize application memory usage
- Use memory profiling tools
- Configure swap (if appropriate)
- Scale horizontally instead of vertically

---

## Network Isolation

**Severity**: P2
**Symptoms**: Containers can't communicate, DNS resolution failures, connection timeouts

### Detect
- Alert `DockerNetworkIsolation` fired
- Application logs showing connection errors
- Inter-service communication failing

### Check
```bash
# 1. Check networks
docker network ls

# 2. Inspect network
docker network inspect <network_name>

# 3. Check container network settings
docker inspect <container_id> | jq '.[0].NetworkSettings'

# 4. Test DNS resolution from container
docker exec <container> nslookup <other_container>
docker exec <container> ping -c 3 <other_container>

# 5. Check firewall rules
sudo iptables -L -n | grep DOCKER

# 6. Check network connectivity
docker exec <container_a> curl -v http://<container_b>:8000

# 7. Check for network errors
curl -s 'http://localhost:9090/api/v1/query?query=rate(container_network_receive_errors_total[5m])' | jq .
```

### Heal
```bash
# Run auto-heal handler
./auto-healing/handlers/restart_docker_network.sh

# Or manually recreate network
docker network rm <network_name>
docker compose up -d

# Or restart Docker daemon
sudo systemctl restart docker
docker compose up -d
```

### Verify
```bash
# 1. Test inter-container connectivity
docker exec <container_a> ping -c 3 <container_b>
# Should succeed

# 2. Test DNS resolution
docker exec <container_a> nslookup <container_b>
# Should return IP address

# 3. Test application connectivity
docker exec <container_a> curl http://<container_b>:8000/health
# Should return 200 OK
```

### Prevent
- Use explicit Docker networks (not default bridge)
- Test inter-container connectivity in CI
- Document network architecture
- Use Docker Compose networking
- Set proper DNS configuration
- Monitor network errors
- Use service discovery when appropriate

---

## Image Pull Rate Limit

**Severity**: P2
**Symptoms**: Pull failures with 429 errors, cannot start new containers, deploy blocked

### Detect
- Alert `DockerImagePullRateLimit` fired
- Docker pull shows "rate limit exceeded"
- CI/CD deployments failing

### Check
```bash
# 1. Check recent pull errors
docker events --since 1h --filter 'type=image' --filter 'event=pull'

# 2. Check Docker Hub rate limit status
TOKEN=$(curl "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)
curl --head -H "Authorization: Bearer $TOKEN" https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest 2>&1 | grep -i ratelimit

# 3. Check if authenticated
docker info | grep -i username

# 4. Check Prometheus
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(image_pull_errors_total{error=~".*rate limit.*"}[5m]))' | jq .
```

### Heal
```bash
# No auto-heal - requires authentication or strategy change

# 1. Authenticate to Docker Hub
docker login -u <username>

# 2. Or use image from other registry
# Edit docker-compose.yml or Dockerfile to use:
# - ghcr.io (GitHub Container Registry)
# - quay.io
# - Private registry

# 3. Or pull less frequently
# Use local image cache
```

### Verify
```bash
# 1. Test image pull
docker pull alpine:latest
# Should succeed

# 2. Check rate limit status
TOKEN=$(curl "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)
curl --head -H "Authorization: Bearer $TOKEN" https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest 2>&1 | grep -i ratelimit
# Should show increased limit (200/6h for authenticated vs 100/6h anonymous)
```

### Prevent
- Authenticate Docker pulls (use Docker Hub account)
- Use image cache or mirror
- Reduce pull frequency (cache images locally)
- Use alternative registries (GitHub Container Registry, etc.)
- Implement image pull-through cache
- Monitor pull counts
- Use registry authentication in CI/CD

---

## Additional Resources

- Error Catalog: [ops/error-catalog/docker.yaml](../../ops/error-catalog/docker.yaml)
- Prometheus Alerts: [monitoring/prometheus/alerts_docker.yml](../../monitoring/prometheus/alerts_docker.yml)
- Auto-heal Handlers: [auto-healing/handlers/](../../auto-healing/handlers/)
- Docker Docs: https://docs.docker.com/
