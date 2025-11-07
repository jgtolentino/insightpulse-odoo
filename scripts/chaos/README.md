# Chaos Testing Scripts

Chaos engineering scripts to validate system resilience and monitoring.

## Overview

These scripts intentionally introduce failures to:
- Verify monitoring and alerting works correctly
- Test auto-healing mechanisms
- Validate system recovery procedures
- Find weaknesses before production incidents

## ⚠️ Safety

**Only run these in staging/test environments!**

- Never run in production without approval
- Understand the impact before running
- Monitor systems during chaos tests
- Have rollback procedures ready

## Scripts

### CPU Stress

Simulates high CPU load:

```bash
./scripts/chaos/cpu_stress.sh

# Custom duration and CPU count
DURATION=120 CPUS=4 ./scripts/chaos/cpu_stress.sh
```

**Expected Results:**
- CPU usage alerts fire
- Performance degradation visible
- Auto-scaling may trigger
- System remains functional

### Kill Worker

Kills a container to test crash recovery:

```bash
./scripts/chaos/kill_worker.sh odoo

# Kill different services
./scripts/chaos/kill_worker.sh superset
./scripts/chaos/kill_worker.sh postgres
```

**Expected Results:**
- Service down alert fires
- Container auto-restarts
- Brief service interruption
- No data loss

### Network Flakiness

Simulates network latency and packet loss:

```bash
./scripts/chaos/net_flaky.sh odoo

# Custom settings
DURATION=120 LATENCY=200ms LOSS=10 ./scripts/chaos/net_flaky.sh odoo
```

**Expected Results:**
- Increased response times
- Timeout warnings
- Retry logic exercised
- System recovers when network normalizes

## Running Chaos Tests

### 1. Pre-Test Checklist

- [ ] Running in non-production environment
- [ ] Monitoring dashboards open
- [ ] Alert channels configured
- [ ] Team notified of chaos test
- [ ] Rollback procedures documented

### 2. Run Test

```bash
# Make scripts executable
chmod +x scripts/chaos/*.sh

# Run a single test
./scripts/chaos/cpu_stress.sh

# Or run via Makefile
make chaos-cpu
make chaos-kill
make chaos-network
```

### 3. Observe and Record

Monitor:
- Alert firing (Prometheus, Alertmanager)
- Auto-healing activation
- Service metrics (CPU, memory, latency)
- Error rates
- Recovery time

### 4. Validate Results

- [ ] Alerts fired as expected
- [ ] Auto-healing worked
- [ ] System recovered
- [ ] No data loss
- [ ] Runbooks accurate

## Advanced Chaos Testing

### Scheduled Chaos

Run chaos tests on a schedule (staging only):

```yaml
# .github/workflows/chaos-test.yml
name: Weekly Chaos Test
on:
  schedule:
    - cron: '0 10 * * 5'  # Friday 10 AM
  workflow_dispatch:

jobs:
  chaos:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run chaos tests
        run: |
          ./scripts/chaos/cpu_stress.sh
          sleep 60
          ./scripts/chaos/kill_worker.sh odoo
```

### Chaos Scenarios

Combine multiple failures:

```bash
# Scenario: Database overload
./scripts/chaos/cpu_stress.sh &
sleep 10
./scripts/chaos/net_flaky.sh postgres

# Scenario: Cascading failure
./scripts/chaos/kill_worker.sh odoo
sleep 5
./scripts/chaos/kill_worker.sh superset
```

## Integration with Monitoring

Chaos tests should trigger these alerts:

| Test | Expected Alert | Expected Recovery |
|------|----------------|-------------------|
| CPU Stress | `OdooCPUHigh` | Load balancing, scaling |
| Kill Worker | `OdooDown` | Auto-restart |
| Network Flaky | `HighLatency` | Retry logic, timeout handling |

## Learning from Chaos

After each chaos test:

1. **Review Alerts** - Did they fire at the right time?
2. **Check Auto-Healing** - Did it work? How long did it take?
3. **Update Runbooks** - Were procedures accurate?
4. **Improve Resilience** - What can be hardened?
5. **Document Findings** - Update this file with learnings

## Resources

- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Chaos Toolkit](https://chaostoolkit.org/)
- [Litmus Chaos](https://litmuschaos.io/)
- [AWS Fault Injection Simulator](https://aws.amazon.com/fis/)
