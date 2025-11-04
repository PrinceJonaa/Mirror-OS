# Workflow Edge Case Documentation

This document describes the defensive patterns implemented in all workflows to handle extreme edge cases.

## Global Safeguards

### 1. **Disk Space Monitoring**
- Check available disk space before heavy operations
- Warn if < 5GB available
- Abort if < 1GB available

### 2. **Timeout Protection**
- Job-level timeouts: 5-30 minutes (based on operation)
- Step-level timeouts for potentially hanging operations
- `ulimit` resource constraints where applicable

### 3. **Zombie Process Cleanup**
- Check for lingering processes after test runs
- Kill orphaned pytest/node processes
- Memory limit enforcement (4GB virtual memory cap)

### 4. **Network Resilience**
- 3-retry pattern for all network operations
- Exponential backoff (5s, 10s, 20s delays)
- Timeout enforcement (60-120s per request)
- Fallback to --no-cache-dir on failures

### 5. **Cache Corruption Handling**
- Detect and delete zero-byte cache files
- Remove empty cache directories
- Fallback install without cache
- Per-package install as last resort

## Python CI Edge Cases

| Edge Case | Solution |
|-----------|----------|
| Missing requirements.txt | Skip install, continue with tests |
| Corrupted pip cache | Clear zero-byte files, retry without cache |
| PyPI rate limiting | 3 retries with 60s timeout, then per-package install |
| Unicode filenames | Use `find` with proper quoting, not globbing |
| Empty test directory | Create stub coverage.xml, skip pytest |
| Hanging tests | 300s timeout per test, 20min job timeout |
| Memory exhaustion | ulimit to 4GB virtual memory |
| Zombie processes | Check and report lingering processes |

## TypeScript CI Edge Cases

| Edge Case | Solution |
|-----------|----------|
| Missing package.json | Skip entire job for that app |
| Corrupted node_modules | Try `npm ci || npm install || npm install --force` |
| npm registry failure | 3 retries, fallback to `--prefer-offline` |
| Out-of-sync lock file | `npm ci` fails → `npm install` auto-fixes |
| Disk space exhaustion | Monitor before install, clean cache if needed |
| Parallel install conflicts | Removed npm cache from setup-node |
| Missing .next/dist/build | Use `if-no-files-found: warn` on artifact upload |

## Security Workflows

| Edge Case | Solution |
|-----------|----------|
| CodeQL conflicts with default setup | `continue-on-error: true` on analyze step |
| API rate limits (GitHub/npm) | Scheduled jobs spaced 1+ hour apart |
| Large repository scan timeout | 30min job timeout |
| Shallow clone issues | `fetch-depth: 0` for full history when needed |
| Fork security (secrets unavailable) | `if: github.event.pull_request.head.repo.full_name == github.repository` |

## Coherence Gate

| Edge Case | Solution |
|-----------|----------|
| Empty PR (no files changed) | Check changed file count, skip if 0 |
| Binary files in diff | Filter to `.py` and `.md` only |
| Deleted files in git diff | Verify file exists before processing |
| Shallow clone (no base ref) | Fallback to `git ls-files` |
| Unicode filenames | Proper bash quoting, avoid unquoted variables |
| Concurrent runs | Concurrency group cancels previous runs |

## Dependency Update Workflow

| Edge Case | Solution |
|-----------|----------|
| Conflicting simultaneous updates | Separate by ecosystem (Python/Node) and app |
| Branch protection blocking push | `create-pull-request` action handles this |
| PR flood (many outdated deps) | `open-pull-requests-limit` in dependabot.yml |
| Incompatible version updates | `ignore` rules for major versions |
| Lock file corruption | Regenerated during update |

## Artifact Handling

All artifact uploads use:
```yaml
if-no-files-found: warn  # Don't fail if optional
retention-days: 7-90     # Based on importance
compression-level: 6-9   # Balance speed/size
```

## Conditional Execution Patterns

### Check if directory exists AND has files:
```bash
if [ -d "$DIR" ] && [ "$(ls -A $DIR 2>/dev/null)" ]; then
```

### Check if file exists before operations:
```bash
if [ -f "$FILE" ]; then
```

### Handle unicode/special characters:
```bash
find "$DIR" -name "*.py" -print0 | xargs -0 command
```

### Retry with backoff:
```bash
for i in {1..3}; do
  if command; then break
  elif [ $i -lt 3 ]; then
    sleep $((5 * i))
  fi
done
```

## Performance Optimizations

1. **Shallow Clones**: `fetch-depth: 1` for non-git-history operations
2. **Parallel Execution**: `fail-fast: false` with matrix strategies
3. **Conditional Jobs**: `needs:` and `if:` to skip unnecessary work
4. **Cached Dependencies**: pip/npm cache with corruption handling
5. **Compressed Artifacts**: compression-level 6-9 based on size/speed tradeoff

## Fork Safety

All workflows that create commits/PRs check:
```yaml
if: github.event.pull_request.head.repo.full_name == github.repository
```

This prevents failures in forks where secrets/permissions are unavailable.

## Monitoring and Debugging

Each workflow logs:
- Disk space before heavy operations
- Memory usage
- CPU core count
- Cache hit/miss
- Retry attempts
- Timeout warnings
- Resource limit hits

---

**Last Updated**: 2025-11-04
**Maintained By**: Workflow automation team
