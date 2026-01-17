# Origin Pool API Enhancements

Comprehensive documentation of origin_pool validation discoveries for downstream projects (CLI tools, Terraform providers, AI assistants).

## Overview

This document captures all validation constraints, default values, and behavioral patterns discovered through systematic API testing of the F5 XC origin_pool resource. These discoveries enable downstream projects to:

- Generate valid configurations without trial-and-error
- Provide accurate help text and documentation
- Warn users about UI vs Server default discrepancies
- Implement intelligent defaults matching server behavior

---

## Quick Reference

### Required Fields

| Field | Required For | Notes |
|-------|--------------|-------|
| `metadata.name` | All operations | 1-63 chars, lowercase alphanumeric |
| `metadata.namespace` | All operations | Must exist in tenant |
| `spec.origin_servers` | Create | Minimum 1 item required |
| `spec.port` | Create | 1-65535, no default applied |

### Minimum Viable Configuration

```json
{
  "metadata": {
    "name": "my-origin-pool",
    "namespace": "default"
  },
  "spec": {
    "origin_servers": [
      {
        "public_name": {
          "dns_name": "backend.example.com"
        }
      }
    ],
    "port": 443
  }
}
```

---

## All 15 UI Configuration Options

The F5 XC web console presents 15 configuration options for origin pools. Here's how they map to API fields:

| # | UI Label | API Field Path | Type | Default |
|---|----------|----------------|------|---------|
| 1 | Origin Server Port | `spec.[port\|automatic_port\|lb_port]` | OneOf | `port` (explicit) |
| 2 | Connection Pool Reuse | `spec.[enable_conn_pool_reuse\|disable_conn_pool_reuse]` | OneOf | `enable_conn_pool_reuse` |
| 3 | Health Check Port | `spec.advanced_options.[same_as_endpoint_port\|health_check_port]` | OneOf | `same_as_endpoint_port` |
| 4 | LoadBalancer Algorithm | `spec.loadbalancer_algorithm` | Enum | `ROUND_ROBIN` ⚠️ |
| 5 | Endpoint Selection | `spec.endpoint_selection` | Enum | `DISTRIBUTED` |
| 6 | TLS to Origin | `spec.[no_tls\|use_tls]` | OneOf | `no_tls` |
| 7 | Connection Timeout | `spec.advanced_options.connection_timeout` | Integer | 2000 ms |
| 8 | HTTP Idle Timeout | `spec.advanced_options.http_idle_timeout` | Integer | 300000 ms |
| 9 | Circuit Breaker | `spec.advanced_options.[default_circuit_breaker\|disable_circuit_breaker\|circuit_breaker]` | OneOf | `default_circuit_breaker` |
| 10 | Outlier Detection | `spec.advanced_options.[disable_outlier_detection\|outlier_detection]` | OneOf | `disable_outlier_detection` |
| 11 | Panic Threshold | `spec.advanced_options.[no_panic_threshold\|panic_threshold]` | OneOf | `no_panic_threshold` |
| 12 | Subset Load Balancing | `spec.advanced_options.[disable_subsets\|enable_subsets]` | OneOf | `disable_subsets` |
| 13 | HTTP Protocol | `spec.advanced_options.[auto_http_config\|http1_config\|http2_options]` | OneOf | `auto_http_config` |
| 14 | Proxy Protocol | `spec.advanced_options.[disable_proxy_protocol\|proxy_protocol_v1\|proxy_protocol_v2]` | OneOf | `disable_proxy_protocol` |
| 15 | LB Source IP Persistence | `spec.advanced_options.[disable_lb_source_ip_persistance\|enable_lb_source_ip_persistance]` | OneOf | `disable_lb_source_ip_persistance` |

⚠️ **Note**: Option 4 (LoadBalancer Algorithm) has a UI vs Server default discrepancy - see below.

---

## Server-Applied Defaults

When fields are omitted, the F5 XC API automatically applies these values:

### Top-Level Spec Defaults

| Field | Server Default | Description |
|-------|----------------|-------------|
| `no_tls` | `{}` | TLS to origin disabled |
| `healthcheck` | `[]` | No health checks configured |
| `loadbalancer_algorithm` | `ROUND_ROBIN` | Round-robin load balancing |
| `endpoint_selection` | `DISTRIBUTED` | Use all endpoints (local + remote) |

### Advanced Options Defaults

When `advanced_options` is not specified, the server behaves as if these values were set:

| Field | Default Value | Description |
|-------|---------------|-------------|
| `connection_timeout` | 2000 | Connection timeout in milliseconds |
| `http_idle_timeout` | 300000 | HTTP idle timeout in milliseconds (5 min) |
| `same_as_endpoint_port` | `{}` | Health check uses endpoint port |
| `default_circuit_breaker` | `{}` | Default circuit breaker settings |
| `disable_outlier_detection` | `{}` | Outlier detection disabled |
| `no_panic_threshold` | `{}` | No panic threshold |
| `disable_subsets` | `{}` | Subset load balancing disabled |
| `auto_http_config` | `{}` | Automatic HTTP protocol negotiation |
| `disable_proxy_protocol` | `{}` | Proxy protocol disabled |
| `disable_lb_source_ip_persistance` | `{}` | LB source IP persistence disabled |

### Nested Object Defaults

| Path | Default | Description |
|------|---------|-------------|
| `origin_servers[].labels` | `{}` | Empty labels object |
| `origin_servers[].public_name.refresh_interval` | `0` | Use system default DNS refresh |

---

## ⚠️ UI vs Server Default Discrepancy

**Critical Discovery**: The F5 XC web UI pre-selects different values than what the API applies when fields are omitted.

| Field | UI Pre-Selected | Server Applied | Impact |
|-------|-----------------|----------------|--------|
| `loadbalancer_algorithm` | `LB_OVERRIDE` | `ROUND_ROBIN` | Configurations created via UI behave differently than API-created ones with omitted field |

### Implications for Downstream Projects

**CLI Tools**: Display warning when `loadbalancer_algorithm` is omitted:

```text
⚠️  Note: Server will apply 'ROUND_ROBIN' (UI shows 'LB_OVERRIDE' by default)
```

**Terraform Providers**: Consider making this field required or showing drift warnings.

**AI Assistants**: Always explicitly set `loadbalancer_algorithm` to avoid ambiguity.

---

## Enum Values

### loadbalancer_algorithm

| Value | Description | Notes |
|-------|-------------|-------|
| `ROUND_ROBIN` | Each healthy endpoint selected in round-robin order | **Server default** |
| `LEAST_REQUEST` | Endpoint with fewest active requests selected | |
| `RING_HASH` | Consistent hashing using ring hash of endpoint names | |
| `RANDOM` | Random healthy endpoint selection | |
| `LB_OVERRIDE` | Hash policy inherited from parent load balancer | **UI default** |

### endpoint_selection

| Value | Description | Notes |
|-------|-------------|-------|
| `DISTRIBUTED` | Consider both remote and local endpoints | **Default** |
| `LOCAL_ONLY` | Only local endpoints used | |
| `LOCAL_PREFERRED` | Prefer local, fall back to remote if unavailable | |

---

## OneOf Patterns (Mutually Exclusive Fields)

Origin pool uses OneOf patterns extensively. Only ONE field from each group can be specified:

### Port Configuration (Option 1)

```yaml
# Choose exactly one:
spec.port: 443                    # Explicit port number (1-65535)
spec.automatic_port: {}           # Port automatically assigned
spec.lb_port: {}                  # Use load balancer port
```

### TLS to Origin (Option 6)

```yaml
# Choose exactly one:
spec.no_tls: {}                   # Disable TLS (default)
spec.use_tls:                     # Enable TLS with configuration
  sni: "backend.example.com"
  volterra_trusted_ca: {}
```

### Circuit Breaker (Option 9)

```yaml
# Choose exactly one:
spec.advanced_options.default_circuit_breaker: {}     # Use defaults
spec.advanced_options.disable_circuit_breaker: {}     # Disable
spec.advanced_options.circuit_breaker:                # Custom config
  max_connections: 1000
  max_pending_requests: 100
```

### HTTP Protocol (Option 13)

```yaml
# Choose exactly one:
spec.advanced_options.auto_http_config: {}     # Auto-negotiate (default)
spec.advanced_options.http1_config: {}         # HTTP/1.x only
spec.advanced_options.http2_options: {}        # HTTP/2 options
```

### Proxy Protocol (Option 14)

```yaml
# Choose exactly one:
spec.advanced_options.disable_proxy_protocol: {}   # Disabled (default)
spec.advanced_options.proxy_protocol_v1: {}        # Proxy Protocol v1
spec.advanced_options.proxy_protocol_v2: {}        # Proxy Protocol v2
```

---

## Validation Rules

### Mutually Exclusive Field Groups

These field groups are mutually exclusive - specifying more than one causes a validation error:

| Group | Fields | Error Message |
|-------|--------|---------------|
| Port | `port`, `automatic_port`, `lb_port` | Choose exactly one port configuration method |
| TLS | `no_tls`, `use_tls` | Choose exactly one TLS configuration |
| Health Check Port | `same_as_endpoint_port`, `health_check_port` | Choose exactly one health check port method |
| Circuit Breaker | `default_circuit_breaker`, `disable_circuit_breaker`, `circuit_breaker` | Choose exactly one circuit breaker configuration |
| Outlier Detection | `disable_outlier_detection`, `outlier_detection` | Choose exactly one outlier detection configuration |
| Panic Threshold | `no_panic_threshold`, `panic_threshold` | Choose exactly one panic threshold configuration |
| Subset LB | `disable_subsets`, `enable_subsets` | Choose exactly one subset load balancing configuration |
| HTTP Protocol | `auto_http_config`, `http1_config`, `http2_options` | Choose exactly one HTTP protocol configuration |
| Proxy Protocol | `disable_proxy_protocol`, `proxy_protocol_v1`, `proxy_protocol_v2` | Choose exactly one proxy protocol configuration |
| LB Source IP | `disable_lb_source_ip_persistance`, `enable_lb_source_ip_persistance` | Choose exactly one LB source IP persistence configuration |

### Field Constraints

| Field | Type | Constraint |
|-------|------|------------|
| `spec.port` | integer | 1-65535 |
| `spec.advanced_options.connection_timeout` | integer | 0-1,800,000 ms |
| `spec.advanced_options.http_idle_timeout` | integer | 0-600,000 ms |
| `spec.advanced_options.panic_threshold` | integer | 0-100 (percentage) |
| `metadata.name` | string | 1-63 chars, `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$` |

---

## Integration Examples

### Python CLI Tool

```python
from typing import Any

class OriginPoolValidator:
    """Validate origin pool configurations using discovered rules."""

    REQUIRED_FIELDS = ["metadata.name", "metadata.namespace", "spec.origin_servers", "spec.port"]

    SERVER_DEFAULTS = {
        "no_tls": {},
        "healthcheck": [],
        "loadbalancer_algorithm": "ROUND_ROBIN",
        "endpoint_selection": "DISTRIBUTED",
    }

    LB_ALGORITHMS = ["ROUND_ROBIN", "LEAST_REQUEST", "RING_HASH", "RANDOM", "LB_OVERRIDE"]
    ENDPOINT_SELECTIONS = ["DISTRIBUTED", "LOCAL_ONLY", "LOCAL_PREFERRED"]

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if not self._get_nested(config, field):
                errors.append(f"Missing required field: {field}")

        # Validate enum values
        lb_algo = self._get_nested(config, "spec.loadbalancer_algorithm")
        if lb_algo and lb_algo not in self.LB_ALGORITHMS:
            errors.append(f"Invalid loadbalancer_algorithm: {lb_algo}")

        # Check mutually exclusive fields
        port_fields = ["spec.port", "spec.automatic_port", "spec.lb_port"]
        present = [f for f in port_fields if self._get_nested(config, f) is not None]
        if len(present) > 1:
            errors.append(f"Mutually exclusive fields: {', '.join(present)}")

        return errors

    def warn_ui_discrepancies(self, config: dict[str, Any]) -> list[str]:
        warnings = []
        if "loadbalancer_algorithm" not in config.get("spec", {}):
            warnings.append(
                "loadbalancer_algorithm not specified: "
                "Server will apply 'ROUND_ROBIN' (UI shows 'LB_OVERRIDE' by default)"
            )
        return warnings
```

### Go Terraform Provider

```go
func resourceOriginPoolSchema() map[string]*schema.Schema {
    return map[string]*schema.Schema{
        "loadbalancer_algorithm": {
            Type:        schema.TypeString,
            Optional:    true,
            Default:     "ROUND_ROBIN",  // Match server default, not UI default
            Description: "Load balancing algorithm. Server default: ROUND_ROBIN (UI shows LB_OVERRIDE)",
            ValidateFunc: validation.StringInSlice([]string{
                "ROUND_ROBIN", "LEAST_REQUEST", "RING_HASH", "RANDOM", "LB_OVERRIDE",
            }, false),
        },
        "endpoint_selection": {
            Type:        schema.TypeString,
            Optional:    true,
            Default:     "DISTRIBUTED",
            Description: "Endpoint selection policy",
            ValidateFunc: validation.StringInSlice([]string{
                "DISTRIBUTED", "LOCAL_ONLY", "LOCAL_PREFERRED",
            }, false),
        },
        // ... other fields
    }
}
```

### AI Assistant MCP Tool

```python
def get_origin_pool_guidance() -> dict:
    """Provide origin pool configuration guidance for AI assistants."""
    return {
        "minimum_config": {
            "metadata": {"name": "example", "namespace": "default"},
            "spec": {
                "origin_servers": [{"public_name": {"dns_name": "backend.example.com"}}],
                "port": 443
            }
        },
        "important_notes": [
            "spec.port is REQUIRED - no default is applied",
            "spec.origin_servers requires at least 1 item",
            "loadbalancer_algorithm defaults to ROUND_ROBIN (UI shows LB_OVERRIDE)",
            "advanced_options is optional - all options have sensible defaults"
        ],
        "oneof_defaults": {
            "port_choice": "port",
            "tls_choice": "no_tls",
            "circuit_breaker_choice": "default_circuit_breaker"
        }
    }
```

---

## Fetching Validation Data

The validation specification is published at:

```bash
# Via GitHub Pages
curl -O https://robinmordasiewicz.github.io/f5xc-api-enriched/specifications/api/validation.json

# Via raw GitHub
curl -O https://raw.githubusercontent.com/robinmordasiewicz/f5xc-api-enriched/main/docs/specifications/api/validation.json
```

Programmatic access:

```python
import requests

def load_origin_pool_validation():
    url = "https://robinmordasiewicz.github.io/f5xc-api-enriched/specifications/api/validation.json"
    spec = requests.get(url).json()

    return {
        "required": spec["required_fields"]["resources"]["origin_pool"],
        "oneof_defaults": spec["oneof_defaults"]["origin_pool"],
        "ui_vs_server": spec["ui_vs_server_defaults"]["origin_pool"],
        "advanced_defaults": spec["advanced_options_defaults"]["origin_pool"]
    }
```

---

## Discovery Methodology

These discoveries were made through systematic API testing:

1. **Baseline Test**: Create origin pool with minimal config (only required fields)
2. **Read Back**: Retrieve the created resource to see server-applied values
3. **Variation Tests**: Test each UI option with different values
4. **Comparison**: Compare sent vs received payloads to identify defaults

The case study script is available at:
`scripts/case_study_origin_pool_advanced.py`

Run discovery (requires API access):

```bash
export F5XC_API_URL="https://tenant.console.ves.volterra.io"
export F5XC_API_TOKEN="your-token"
python -m scripts.case_study_origin_pool_advanced --verbose
```

---

## Related Documentation

- [VALIDATION_SPEC.md](VALIDATION_SPEC.md) - Full validation specification format
- [config/discovered_defaults.yaml](../config/discovered_defaults.yaml) - Raw discovery data
- [config/validation_schema.yaml](../config/validation_schema.yaml) - Validation schema source

---

*Last Updated: 2026-01-17*
*Version: 2.0.33*
