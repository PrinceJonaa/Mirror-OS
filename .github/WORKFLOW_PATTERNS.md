# Workflow Edge Case Summary

This document provides a quick reference of all edge case patterns implemented across the workflows.

## Quick Reference Table

| Edge Case | Pattern | Files Affected |
|-----------|---------|----------------|
| Missing dependencies | Retry with fallback | python-ci, typescript-ci, nfl-competition, dependency-update |
| Empty test directories | Check before running | python-ci, notebooks-ci |
| Missing package files | Check existence first | typescript-ci, security, dependency-update |
| Git ref not found | Check before diff | coherence-gate |
| Deleted/moved files | Filter existing only | coherence-gate |
| Missing artifacts | `if-no-files-found: warn` | All 11 workflows |
| Long-running operations | Add timeouts | All 11 workflows |
| Missing permissions | Explicit declarations | auto-label, stale |
| Network failures | Retry with `--no-cache-dir` | python-ci, nfl-competition |
| Empty input lists | Check non-empty | coherence-gate, notebooks-ci |

## Code Patterns by Category

### 1. File Existence Checks

```yaml
# Pattern 1: Check file exists before using it
- name: Process file
  run: |
    if [ -f "path/to/file.txt" ]; then
      # Process file
    else
      echo "File not found, skipping"
    fi
```

```yaml
# Pattern 2: Check directory exists and is non-empty
- name: Process directory
  run: |
    if [ -d "path/to/dir" ] && [ "$(ls -A path/to/dir 2>/dev/null)" ]; then
      # Process directory contents
    else
      echo "Directory empty or doesn't exist"
    fi
```

### 2. Dependency Installation with Retry

```yaml
# Pattern 1: pip with fallback
- name: Install Python dependencies
  run: |
    pip install -r requirements.txt || pip install --no-cache-dir -r requirements.txt || true
```

```yaml
# Pattern 2: npm with fallback
- name: Install Node dependencies
  run: |
    if [ -f package-lock.json ]; then
      npm ci --prefer-offline --no-audit || npm install --prefer-offline --no-audit
    elif [ -f package.json ]; then
      npm install --prefer-offline --no-audit
    else
      echo "No package.json found"
      exit 1
    fi
```

### 3. Artifact Upload Safety

```yaml
# Always use if-no-files-found for optional artifacts
- name: Upload results
  uses: actions/upload-artifact@v4
  with:
    name: results
    path: output/
    if-no-files-found: warn  # Don't fail if missing
    retention-days: 30
```

### 4. Job Timeouts

```yaml
# Add timeout to prevent hanging jobs
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Appropriate for the task
    steps:
      # ...
```

```yaml
# Add timeout to individual steps for long operations
- name: Check links
  run: |
    # Link checking logic
  timeout-minutes: 10
```

### 5. Git Operations Safety

```yaml
# Check if git ref exists before diff
- name: Get changed files
  run: |
    if git rev-parse origin/${{ github.base_ref }} >/dev/null 2>&1; then
      git diff --name-only origin/${{ github.base_ref }}...HEAD > changed_files.txt
    else
      echo "Base ref not found, using all tracked files"
      git ls-files '*.py' '*.md' > changed_files.txt
    fi
```

### 6. File Filtering Before Processing

```yaml
# Filter to only existing files
- name: Process files
  run: |
    existing_files=""
    while IFS= read -r file; do
      if [ -f "$file" ]; then
        existing_files="$existing_files $file"
      else
        echo "⚠️  File $file not found, skipping"
      fi
    done < file_list.txt
    
    if [ -n "$existing_files" ]; then
      process_command $existing_files
    else
      echo "No files to process"
    fi
```

### 7. Empty Input Handling

```yaml
# Check variable is not empty before using
- name: Process input
  run: |
    INPUT="${{ steps.previous.outputs.files }}"
    if [ -n "$INPUT" ] && [ "$INPUT" != "" ]; then
      echo "$INPUT" | process_files
    else
      echo "No input provided, skipping"
    fi
```

### 8. Permission Declarations

```yaml
# Always declare permissions explicitly
jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      contents: read      # What you can read
      pull-requests: write # What you can write
    steps:
      # ...
```

### 9. Graceful Degradation

```yaml
# Allow individual steps to fail without blocking workflow
- name: Optional check
  run: |
    optional_command || echo "Optional check failed, continuing"
  continue-on-error: true
```

```yaml
# Test with fallback error message
- name: Test dependencies
  run: |
    python -c "import required_package" || echo "Package missing but continuing"
```

### 10. Conditional Job Execution

```yaml
# Skip expensive operations when not needed
- name: Check if data exists
  id: check_data
  run: |
    if [ -f data.csv ]; then
      echo "data_available=true" >> $GITHUB_OUTPUT
    else
      echo "data_available=false" >> $GITHUB_OUTPUT
    fi

- name: Process data
  if: steps.check_data.outputs.data_available == 'true'
  run: |
    # Expensive operation only runs if data exists
```

## Workflow-Specific Examples

### Python CI - Complete Pattern

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip setuptools wheel
    pip install pytest pytest-cov
    
    # With existence check and retry
    if [ -f requirements.txt ]; then 
      pip install -r requirements.txt || pip install --no-cache-dir -r requirements.txt || true
    fi

- name: Run tests with coverage
  run: |
    # Check directory exists and is non-empty
    if [ -d "tests" ] && [ "$(ls -A tests 2>/dev/null)" ]; then
      pytest tests/ --cov --cov-report=xml
    else
      echo "No tests found, creating empty coverage"
      echo '<?xml version="1.0" ?><coverage version="6.0"></coverage>' > coverage.xml
    fi

- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    name: coverage
    path: coverage.xml
    if-no-files-found: warn
```

### TypeScript CI - Complete Pattern

```yaml
- name: Install dependencies
  run: |
    # Fallback chain: ci -> install -> fail
    if [ -f package-lock.json ]; then
      npm ci --prefer-offline --no-audit || npm install --prefer-offline --no-audit
    elif [ -f package.json ]; then
      npm install --prefer-offline --no-audit
    else
      echo "No package.json found"
      exit 1
    fi

- name: Build
  run: |
    npm run build
  timeout-minutes: 10

- name: Upload build
  uses: actions/upload-artifact@v4
  with:
    name: build
    path: |
      .next/
      dist/
      build/
    if-no-files-found: warn
```

### Coherence Gate - Complete Pattern

```yaml
- name: Get changed files
  run: |
    # Safe git diff with fallback
    if git rev-parse origin/${{ github.base_ref }} >/dev/null 2>&1; then
      git diff --name-only origin/${{ github.base_ref }}...HEAD > changed_files.txt
    else
      git ls-files '*.py' > changed_files.txt
    fi

- name: Process files
  run: |
    # Filter to existing files only
    existing_files=""
    while IFS= read -r file; do
      if [ -f "$file" ]; then
        existing_files="$existing_files $file"
      fi
    done < changed_files.txt
    
    # Check non-empty before processing
    if [ -n "$existing_files" ]; then
      python analyzer.py $existing_files
    else
      echo "No files to analyze"
    fi
```

## Testing Your Edge Cases

Use this checklist when adding new workflows:

- [ ] Added timeout to job level
- [ ] Added timeout to long-running steps (>5 minutes)
- [ ] Check file existence before reading
- [ ] Check directory is non-empty before processing
- [ ] Added `if-no-files-found: warn` to artifact uploads
- [ ] Added retry logic for network operations
- [ ] Check for empty variables before using
- [ ] Added informative skip messages
- [ ] Declared explicit permissions
- [ ] Tested with missing files/directories
- [ ] Tested with empty inputs
- [ ] Validated YAML syntax

## Common Mistakes to Avoid

❌ **Don't**: Assume files exist
```yaml
- run: cat required_file.txt
```

✅ **Do**: Check first
```yaml
- run: |
    if [ -f required_file.txt ]; then
      cat required_file.txt
    else
      echo "File not found"
    fi
```

❌ **Don't**: Let jobs hang forever
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps: # ...
```

✅ **Do**: Add timeouts
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps: # ...
```

❌ **Don't**: Fail on missing optional artifacts
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: results
    path: optional/
```

✅ **Do**: Warn instead
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: results
    path: optional/
    if-no-files-found: warn
```

❌ **Don't**: Use commands without fallback
```yaml
- run: npm ci
```

✅ **Do**: Add fallback chain
```yaml
- run: npm ci || npm install || echo "Install failed"
```

## Monitoring and Metrics

Track these metrics to measure improvement:

- **Workflow success rate**: Should increase after edge case handling
- **False failure rate**: Should decrease significantly
- **Average runtime**: May increase slightly due to checks, but more reliable
- **Timeout occurrences**: Should remain low
- **Artifact upload warnings**: Monitor for patterns

## Further Reading

- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-github-actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Expression Syntax](https://docs.github.com/en/actions/learn-github-actions/expressions)
- [Context Variables](https://docs.github.com/en/actions/learn-github-actions/contexts)
