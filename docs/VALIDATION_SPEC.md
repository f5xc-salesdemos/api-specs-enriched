# F5 XC API Validation Specification

Centralized validation specification for downstream projects consuming the F5 XC API.

## Overview

The f5xc-api-enriched project serves as the **single source of truth** for API validation constraints. Downstream projects (CLI tools, Terraform providers, AI assistants) should consume this centralized validation metadata rather than maintaining their own validation logic.

### Why Centralized?

| Factor | Centralized | Per-Project |
|--------|-------------|-------------|
| Consistency | All consumers validate the same way | Drift between implementations |
| Maintenance | Update once, propagate everywhere | N implementations to update |
| Discovery | Already have infrastructure | Each project rediscovers constraints |
| Accuracy | Derived from actual API behavior | May diverge from real API |
| Cost | One validation test suite | N test suites |

## Validation Specification Format

The validation specification is published as `docs/specifications/api/validation.json` and contains:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "version": "1.0.0",
  "generated_at": "2026-01-17T12:00:00Z",
  "source": "f5xc-api-enriched",

  "required_fields": { ... },
  "enum_values": { ... },
  "constraints": { ... },
  "patterns": [ ... ],
  "server_defaults": { ... },
  "conditional_requirements": { ... },
  "minimum_configurations": { ... },
  "oneof_defaults": { ... },
  "ui_vs_server_defaults": { ... },
  "advanced_options_defaults": { ... },
  "extensions": { ... }
}
```

## Sections

### Required Fields

Specifies which fields are required for each operation (create, update, minimum_config).

```json
{
  "required_fields": {
    "common": {
      "all_operations": ["metadata.name", "metadata.namespace"]
    },
    "resources": {
      "origin_pool": {
        "create": ["metadata.name", "metadata.namespace", "spec.origin_servers", "spec.port"],
        "update": ["metadata.name", "metadata.namespace"],
        "minimum_config": ["metadata.name", "metadata.namespace", "spec.origin_servers", "spec.port"]
      }
    }
  }
}
```

**Usage in downstream projects:**

```python
# Python example
def validate_create(resource_type: str, data: dict) -> list[str]:
    spec = load_validation_spec()
    required = spec["required_fields"]["resources"].get(resource_type, {}).get("create", [])
    errors = []
    for field in required:
        if not get_nested(data, field):
            errors.append(f"Required field missing: {field}")
    return errors
```

```go
// Go example
func ValidateCreate(resourceType string, data map[string]interface{}) []string {
    spec := LoadValidationSpec()
    required := spec.RequiredFields.Resources[resourceType].Create
    var errors []string
    for _, field := range required {
        if !HasNestedField(data, field) {
            errors = append(errors, fmt.Sprintf("Required field missing: %s", field))
        }
    }
    return errors
}
```

### Enum Values

Defines allowed values for constrained fields.

```json
{
  "enum_values": {
    "loadbalancer_algorithm": {
      "description": "Load balancing algorithm for distributing traffic across origin servers",
      "values": [
        {"value": "ROUND_ROBIN", "description": "Each healthy endpoint selected in round robin order"},
        {"value": "LEAST_REQUEST", "description": "Endpoint with fewest active requests selected"},
        {"value": "RING_HASH", "description": "Consistent hashing using ring hash of endpoint names"},
        {"value": "RANDOM", "description": "Random healthy endpoint selection"},
        {"value": "LB_OVERRIDE", "description": "Hash policy inherited from parent load balancer"}
      ],
      "default": "ROUND_ROBIN"
    }
  }
}
```

**Usage:**

```python
def validate_enum(field_name: str, value: str, enum_type: str) -> bool:
    spec = load_validation_spec()
    enum_def = spec["enum_values"].get(enum_type)
    if not enum_def:
        return True  # No constraint
    allowed = [v["value"] for v in enum_def["values"]]
    return value in allowed
```

### Constraints

Type-level validation defaults and pattern-based rules.

```json
{
  "constraints": {
    "type_defaults": {
      "string": {"minLength": 0, "maxLength": 1024},
      "integer": {"minimum": 0, "maximum": 2147483647}
    }
  }
}
```

### Patterns

Field name pattern-based validation rules with confidence scores.

```json
{
  "patterns": [
    {
      "pattern": "\\bport$",
      "constraints": {"minimum": 1, "maximum": 65535},
      "confidence": 0.99,
      "description": "Valid TCP/UDP port range"
    },
    {
      "pattern": "\\bname$",
      "constraints": {
        "minLength": 1,
        "maxLength": 63,
        "pattern": "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"
      },
      "confidence": 0.90,
      "description": "Kubernetes-style naming convention"
    }
  ]
}
```

**Usage:**

```python
import re

def get_field_constraints(field_name: str) -> dict:
    spec = load_validation_spec()
    constraints = {}
    for pattern_def in spec["patterns"]:
        if re.search(pattern_def["pattern"], field_name):
            constraints.update(pattern_def["constraints"])
    return constraints
```

### Server Defaults

Values automatically applied by the F5 XC API when fields are omitted.

```json
{
  "server_defaults": {
    "description": "Values automatically applied by the F5 XC API when fields are omitted",
    "resources": {
      "origin_pool": {
        "spec": {
          "no_tls": {},
          "healthcheck": [],
          "loadbalancer_algorithm": "ROUND_ROBIN",
          "endpoint_selection": "DISTRIBUTED"
        }
      }
    }
  }
}
```

**Usage in CLI help text:**

```text
$ xcsh origin-pool create --help

DEFAULTS (server-applied):
  --loadbalancer-algorithm  ROUND_ROBIN (if omitted)
  --endpoint-selection      DISTRIBUTED (if omitted)
```

### Conditional Requirements

Mutually exclusive fields and conditional dependencies.

```json
{
  "conditional_requirements": {
    "resources": {
      "healthcheck": {
        "mutually_exclusive": [
          {
            "fields": ["spec.http_health_check", "spec.tcp_health_check", "spec.udp_icmp_health_check"],
            "reason": "Choose exactly one health check type"
          }
        ],
        "conditional": []
      }
    }
  }
}
```

**Usage:**

```python
def validate_mutually_exclusive(resource_type: str, data: dict) -> list[str]:
    spec = load_validation_spec()
    requirements = spec["conditional_requirements"]["resources"].get(resource_type, {})
    errors = []

    for exclusion in requirements.get("mutually_exclusive", []):
        present = [f for f in exclusion["fields"] if get_nested(data, f)]
        if len(present) > 1:
            errors.append(f"Mutually exclusive fields: {', '.join(present)}. {exclusion['reason']}")

    return errors
```

### Minimum Configurations

Minimum viable configurations with working examples.

```json
{
  "minimum_configurations": {
    "resources": {
      "origin_pool": {
        "description": "Backend origin servers for load balancing",
        "example": {
          "metadata": {"name": "backend-pool", "namespace": "default"},
          "spec": {
            "origin_servers": [{"public_name": {"dns_name": "backend1.example.com"}}],
            "port": 8080
          }
        }
      }
    }
  }
}
```

### OneOf Defaults

For fields with mutually exclusive choices (OneOf patterns), these specify which option is selected by default when none is explicitly provided.

```json
{
  "oneof_defaults": {
    "origin_pool": {
      "port_choice": "port",
      "tls_choice": "no_tls",
      "circuit_breaker_choice": "default_circuit_breaker",
      "outlier_detection_choice": "disable_outlier_detection",
      "panic_threshold_type": "no_panic_threshold",
      "subset_choice": "disable_subsets",
      "http_protocol_type": "auto_http_config",
      "proxy_protocol_choice": "disable_proxy_protocol",
      "lb_source_ip_persistence_choice": "disable_lb_source_ip_persistance"
    }
  }
}
```

**Usage:**

```python
def get_oneof_default(resource_type: str, oneof_group: str) -> str:
    spec = load_validation_spec()
    return spec["oneof_defaults"].get(resource_type, {}).get(oneof_group)

# Example: Get default TLS choice for origin_pool
default_tls = get_oneof_default("origin_pool", "tls_choice")  # Returns "no_tls"
```

### UI vs Server Defaults

⚠️ **Important**: UI pre-selected values may differ from server-applied defaults!

This section documents cases where the F5 XC web console pre-selects different values than what the API applies when fields are omitted.

```json
{
  "ui_vs_server_defaults": {
    "origin_pool": {
      "loadbalancer_algorithm": {
        "ui_default": "LB_OVERRIDE",
        "server_default": "ROUND_ROBIN",
        "note": "UI pre-selects LB_OVERRIDE but server applies ROUND_ROBIN if omitted"
      }
    }
  }
}
```

**Usage:**

```python
def warn_ui_server_mismatch(resource_type: str) -> list[str]:
    """Generate warnings for fields where UI and server defaults differ."""
    spec = load_validation_spec()
    warnings = []

    mismatches = spec.get("ui_vs_server_defaults", {}).get(resource_type, {})
    for field, info in mismatches.items():
        if info["ui_default"] != info["server_default"]:
            warnings.append(
                f"Field '{field}': UI shows '{info['ui_default']}' but "
                f"server applies '{info['server_default']}' if omitted"
            )
    return warnings
```

### Advanced Options Defaults

Default values for the `advanced_options` object when not explicitly specified.

```json
{
  "advanced_options_defaults": {
    "origin_pool": {
      "connection_timeout": 2000,
      "http_idle_timeout": 300000,
      "same_as_endpoint_port": {},
      "default_circuit_breaker": {},
      "disable_outlier_detection": {},
      "no_panic_threshold": {},
      "disable_subsets": {},
      "auto_http_config": {},
      "disable_proxy_protocol": {},
      "disable_lb_source_ip_persistance": {}
    }
  }
}
```

## OpenAPI Extension Mapping

The enriched OpenAPI specs use these extensions to embed validation metadata:

| Extension | Purpose | Location |
|-----------|---------|----------|
| `x-f5xc-required-for` | Context-specific required fields | Schema properties |
| `x-f5xc-server-default` | Marks server-applied defaults | Schema properties |
| `x-f5xc-recommended-value` | Recommended default value | Schema properties |
| `x-f5xc-conditions` | Conditional requirements | Schema properties |
| `x-f5xc-minimum-configuration` | Minimum config examples | Schema definitions |
| `x-f5xc-validation` | Discovery-derived constraints | Schema properties |

## Integration Examples

### CLI Tool (Python)

```python
import json
from pathlib import Path

class F5XCValidator:
    def __init__(self, spec_path: str = "validation.json"):
        with open(spec_path) as f:
            self.spec = json.load(f)

    def validate_resource(self, resource_type: str, operation: str, data: dict) -> list[str]:
        errors = []

        # Check required fields
        required = self.spec["required_fields"]["resources"].get(resource_type, {}).get(operation, [])
        for field in required:
            if not self._get_nested(data, field):
                errors.append(f"Missing required field: {field}")

        # Check enum values
        errors.extend(self._validate_enums(resource_type, data))

        # Check mutually exclusive fields
        errors.extend(self._validate_mutual_exclusions(resource_type, data))

        return errors

    def get_server_defaults(self, resource_type: str) -> dict:
        return self.spec["server_defaults"]["resources"].get(resource_type, {})

    def get_minimum_config(self, resource_type: str) -> dict:
        return self.spec["minimum_configurations"]["resources"].get(resource_type, {}).get("example", {})
```

### Terraform Provider (Go)

```go
package validation

import (
    "encoding/json"
    "regexp"
)

type ValidationSpec struct {
    RequiredFields           RequiredFieldsSpec           `json:"required_fields"`
    EnumValues               map[string]EnumSpec          `json:"enum_values"`
    Patterns                 []PatternSpec                `json:"patterns"`
    ServerDefaults           ServerDefaultsSpec           `json:"server_defaults"`
    ConditionalRequirements  ConditionalRequirementsSpec  `json:"conditional_requirements"`
    MinimumConfigurations    MinimumConfigSpec            `json:"minimum_configurations"`
}

func (v *ValidationSpec) ValidateCreate(resourceType string, data map[string]interface{}) []error {
    var errors []error

    if fields, ok := v.RequiredFields.Resources[resourceType]; ok {
        for _, field := range fields.Create {
            if !hasNestedField(data, field) {
                errors = append(errors, fmt.Errorf("required field missing: %s", field))
            }
        }
    }

    return errors
}

func (v *ValidationSpec) GetFieldConstraints(fieldName string) map[string]interface{} {
    constraints := make(map[string]interface{})

    for _, pattern := range v.Patterns {
        if matched, _ := regexp.MatchString(pattern.Pattern, fieldName); matched {
            for k, v := range pattern.Constraints {
                constraints[k] = v
            }
        }
    }

    return constraints
}
```

### AI Assistant (MCP Server)

```python
class F5XCValidationTool:
    """MCP tool for AI assistants to validate F5 XC configurations."""

    def __init__(self):
        self.spec = self._load_validation_spec()

    def get_required_fields(self, resource_type: str, operation: str = "create") -> list[str]:
        """Get required fields for a resource operation."""
        return self.spec["required_fields"]["resources"].get(resource_type, {}).get(operation, [])

    def get_allowed_values(self, enum_type: str) -> list[str]:
        """Get allowed values for an enum field."""
        enum_def = self.spec["enum_values"].get(enum_type, {})
        return [v["value"] for v in enum_def.get("values", [])]

    def get_minimum_example(self, resource_type: str) -> dict:
        """Get minimum working configuration example."""
        return self.spec["minimum_configurations"]["resources"].get(resource_type, {}).get("example", {})

    def suggest_fix(self, resource_type: str, error_message: str) -> str:
        """Suggest a fix based on validation error."""
        # AI can use this to provide helpful suggestions
        pass
```

## Fetching the Validation Spec

The validation specification is published alongside the OpenAPI specs:

```bash
# Via GitHub Pages
curl -O https://robinmordasiewicz.github.io/f5xc-api-enriched/specifications/api/validation.json

# Via raw GitHub
curl -O https://raw.githubusercontent.com/robinmordasiewicz/f5xc-api-enriched/main/docs/specifications/api/validation.json
```

## Versioning

The validation spec follows semantic versioning:

- **Major**: Breaking changes to structure or field names
- **Minor**: New validation rules or resources added
- **Patch**: Bug fixes or description updates

Check the `version` field in the spec to ensure compatibility:

```python
spec = load_validation_spec()
if not spec["version"].startswith("1."):
    raise ValueError(f"Unsupported validation spec version: {spec['version']}")
```

## Reconciliation Strategy

When multiple sources provide constraints, the reconciliation priority is:

1. **Existing** - Constraints in original OpenAPI spec (highest priority)
2. **Discovery** - Constraints from live API discovery
3. **Inferred** - Constraints from pattern matching (lowest priority)

This ensures manually curated constraints take precedence while still benefiting from automated discovery.

## What Downstream Projects Should Own

While validation rules are centralized, downstream projects still own:

| Project | Project-Specific Concerns |
|---------|---------------------------|
| **CLI Tools** | Flag parsing, shell completion, interactive prompts, help text formatting |
| **Terraform** | State management, plan/apply logic, provider-specific schema types |
| **AI Assistants** | Context window management, prompt optimization, response formatting |
| **All** | Network timeouts, retry logic, authentication, error display |

## Contributing

To add or update validation rules:

1. Edit `config/validation_schema.yaml`
2. Run the pipeline to regenerate `validation.json`
3. Submit a PR with justification for the change

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - AI assistant instructions
- [DEVELOPMENT.md](DEVELOPMENT.md) - Developer guide
- [config/validation_schema.yaml](../config/validation_schema.yaml) - Source configuration
