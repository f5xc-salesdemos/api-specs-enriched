# Healthcheck API Specification Enhancements

This document describes the enhancements made to healthcheck-related schemas in the enriched F5 XC API specifications. Downstream projects (CLI tools, Terraform providers, AI assistants) should refactor to leverage these new metadata fields.

## Overview

Healthcheck schemas now include **server-applied default values** that indicate what the F5 XC API will automatically apply when fields are omitted. This enables:

- **CLI tools**: Generate minimal configurations without specifying every field
- **Terraform providers**: Understand which fields have implicit defaults
- **AI assistants**: Create working configurations with fewer required inputs
- **Documentation**: Clearly communicate optional vs required fields

## Enhanced Schemas

### Pattern Matching

All schemas matching `healthcheck.*SpecType` receive these enhancements:

- `healthcheckCreateSpecType`
- `healthcheckReplaceSpecType`
- `healthcheckGetSpecType`

### Top-Level Defaults

| Field | Default Value | Description |
|-------|---------------|-------------|
| `jitter` | `0` | Absolute jitter value for timing randomization |
| `jitter_percent` | `0` | Percentage-based jitter for timing randomization |

### Nested Defaults (http_health_check)

The `http_health_check` property references `healthcheckHttpHealthCheck` schema, which now includes:

| Field | Default Value | Type | Description |
|-------|---------------|------|-------------|
| `use_origin_server_name` | `{}` | object | Use origin server name for Host header |
| `headers` | `{}` | object | Custom headers (empty by default) |
| `request_headers_to_remove` | `[]` | array | Headers to strip from requests |
| `use_http2` | `false` | boolean | HTTP/2 support (disabled by default) |
| `expected_status_codes` | `[]` | array | Status codes to accept (empty = 200-299) |

### Recommended Values

For required fields that have no server default, we provide **recommended values** matching the F5 XC web interface pre-populated values:

| Field | Recommended Value | Description |
|-------|-------------------|-------------|
| `timeout` | `3` | Health check timeout in seconds |
| `interval` | `15` | Interval between health checks in seconds |
| `unhealthy_threshold` | `1` | Consecutive failures before marking unhealthy |
| `healthy_threshold` | `3` | Consecutive successes before marking healthy |
| `jitter_percent` | `30` | Recommended jitter for production use |

## OpenAPI Extensions

### x-f5xc-server-default

When `true`, indicates the field's default value is **server-applied** (not just a documentation suggestion):

```yaml
use_http2:
  type: boolean
  default: false
  x-f5xc-server-default: true
```

**Downstream usage**:

```python
# Check if a field has a server-applied default
if schema.get('x-f5xc-server-default'):
    # Field can be safely omitted - server will apply the default
    pass
```

### x-f5xc-recommended-value

Provides suggested values for required fields:

```yaml
timeout:
  type: integer
  x-f5xc-recommended-value: 3
```

**Downstream usage**:

```python
# Use recommended value as placeholder/suggestion
if 'x-f5xc-recommended-value' in schema:
    suggested = schema['x-f5xc-recommended-value']
```

## Refactoring Guide for Downstream Projects

### CLI Tools

**Before** (requiring all fields):

```bash
f5xc healthcheck create \
  --name my-hc \
  --timeout 3 \
  --interval 15 \
  --unhealthy-threshold 1 \
  --healthy-threshold 3 \
  --jitter 0 \
  --jitter-percent 0
```

**After** (minimal configuration):

```bash
f5xc healthcheck create \
  --name my-hc \
  --timeout 3 \
  --interval 15 \
  --unhealthy-threshold 1 \
  --healthy-threshold 3
# jitter and jitter_percent omitted - server applies defaults
```

### Terraform Providers

**Before** (explicit defaults in schema):

```go
"jitter": {
    Type:     schema.TypeInt,
    Optional: true,
    Default:  0,  // Hardcoded default
},
```

**After** (dynamic from OpenAPI):

```go
"jitter": {
    Type:     schema.TypeInt,
    Optional: true,
    Computed: true,  // Server-applied default
    Description: "Server default: 0",
},
```

### AI Assistants / Code Generation

**Before** (generating verbose configs):

```yaml
spec:
  timeout: 3
  interval: 15
  unhealthy_threshold: 1
  healthy_threshold: 3
  jitter: 0
  jitter_percent: 0
  http_health_check:
    use_origin_server_name: {}
    headers: {}
    request_headers_to_remove: []
    use_http2: false
    expected_status_codes: []
```

**After** (minimal working config):

```yaml
spec:
  timeout: 3
  interval: 15
  unhealthy_threshold: 1
  healthy_threshold: 3
  http_health_check: {}
```

## Validation Logic

Downstream projects should implement validation that accounts for server defaults:

```python
def validate_healthcheck(config, schema):
    """Validate healthcheck config, accounting for server defaults."""
    for field, field_schema in schema['properties'].items():
        if field not in config:
            # Check if server will apply a default
            if field_schema.get('x-f5xc-server-default'):
                continue  # OK - server will handle this
            elif field in schema.get('required', []):
                raise ValidationError(f"Required field '{field}' missing")
```

## Schema Locations

Enhanced schemas are available in:

| File | Schemas |
|------|---------|
| `docs/specifications/api/virtual.json` | `healthcheckHttpHealthCheck`, `healthcheckCreateSpecType`, etc. |
| `docs/specifications/api/openapi.json` | Master spec with all schemas |

## Testing Enhancements

To verify enhancements are present:

```python
import json

with open('docs/specifications/api/virtual.json') as f:
    spec = json.load(f)

schemas = spec['components']['schemas']

# Verify nested defaults in referenced schema
http_hc = schemas['healthcheckHttpHealthCheck']['properties']
assert http_hc['use_http2'].get('default') == False
assert http_hc['use_http2'].get('x-f5xc-server-default') == True

# Verify top-level defaults
create_spec = schemas['healthcheckCreateSpecType']['properties']
assert create_spec['jitter'].get('default') == 0
assert create_spec['jitter'].get('x-f5xc-server-default') == True
```

## Related Resources

- [Server-Applied Defaults Discovery](/docs/case-studies/healthcheck-defaults.md)
- [Origin Pool Enhancements](/docs/ORIGIN_POOL_ENHANCEMENTS.md)
- [Minimum Configuration Guide](/config/minimum_configs.yaml)

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0.30 | 2026-01-16 | Added nested defaults for `$ref` schemas (http_health_check) |
| 2.0.29 | 2026-01-17 | Initial healthcheck defaults discovery |
