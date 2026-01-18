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
  "version": "2.1.0",
  "generated_at": "2026-01-17T12:00:00Z",
  "source": "f5xc-api-enriched",

  "required_fields": { ... },
  "enum_values": { ... },
  "constraints": { ... },
  "patterns": [ ... ],
  "conditional_requirements": { ... },
  "minimum_configurations": { ... },
  "defaults": { ... },
  "extensions": { ... }
}
```

> **v2.1.0 Breaking Change**: The `defaults` section replaces the fragmented `server_defaults`, `oneof_defaults`, `ui_vs_server_defaults`, and `advanced_options_defaults` sections with a unified resource-centric structure.

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

### Defaults (Unified)

All default values organized by resource type. Consolidates server-applied, recommended, advanced options, OneOf choices, and UI vs server discrepancies into a single resource-centric structure.

```json
{
  "defaults": {
    "description": "All default values organized by resource type",
    "resources": {
      "healthcheck": {
        "server_applied": {
          "jitter": 0,
          "jitter_percent": 0
        },
        "recommended": {
          "timeout": 3,
          "interval": 15,
          "unhealthy_threshold": 1,
          "healthy_threshold": 3,
          "jitter_percent": 30
        }
      },
      "origin_pool": {
        "server_applied": {
          "no_tls": {},
          "healthcheck": [],
          "loadbalancer_algorithm": "ROUND_ROBIN",
          "endpoint_selection": "DISTRIBUTED"
        },
        "recommended": {
          "port": 443,
          "connection_timeout": 2000,
          "http_idle_timeout": 300000
        },
        "advanced_options": {
          "connection_timeout": 2000,
          "http_idle_timeout": 300000,
          "same_as_endpoint_port": {},
          "default_circuit_breaker": {},
          "disable_outlier_detection": {}
        },
        "oneof_choices": {
          "port_choice": "port",
          "tls_choice": "no_tls",
          "circuit_breaker_choice": "default_circuit_breaker"
        },
        "ui_vs_server": {
          "loadbalancer_algorithm": {
            "ui_default": "LB_OVERRIDE",
            "server_default": "ROUND_ROBIN",
            "note": "UI pre-selects LB_OVERRIDE but server applies ROUND_ROBIN if omitted"
          }
        }
      },
      "app_firewall": {
        "server_applied": {
          "allow_all_response_codes": {},
          "default_anonymization": {},
          "monitoring": {}
        }
      }
    }
  }
}
```

**Default Categories:**

| Category | Description | Source |
|----------|-------------|--------|
| `server_applied` | Values API applies when fields omitted | Live API testing |
| `recommended` | F5 XC UI pre-populated values | UI analysis |
| `advanced_options` | Nested defaults within advanced_options | API discovery |
| `oneof_choices` | Default OneOf selections | API behavior |
| `ui_vs_server` | Where UI differs from API defaults | Comparative analysis |

**Usage:**

```python
def get_default(resource: str, category: str, field: str = None) -> Any:
    """Get default value from unified structure."""
    spec = load_validation_spec()
    defaults = spec.get("defaults", {}).get("resources", {}).get(resource, {})
    category_data = defaults.get(category, {})
    return category_data.get(field) if field else category_data

# Examples:
timeout = get_default("healthcheck", "recommended", "timeout")  # 3
port = get_default("origin_pool", "recommended", "port")  # 443
tls_choice = get_default("origin_pool", "oneof_choices", "tls_choice")  # "no_tls"
lb_algo = get_default("origin_pool", "server_applied", "loadbalancer_algorithm")  # "ROUND_ROBIN"
```

**Usage in CLI help text:**

```text
$ xcsh origin-pool create --help

DEFAULTS (server-applied):
  --loadbalancer-algorithm  ROUND_ROBIN (if omitted)
  --endpoint-selection      DISTRIBUTED (if omitted)

RECOMMENDED VALUES:
  --port                    443
  --connection-timeout      2000ms

ONEOF DEFAULTS:
  --tls-choice              no_tls (disable TLS to origin)
  --circuit-breaker-choice  default_circuit_breaker
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

    def get_defaults(self, resource_type: str, category: str = None) -> dict:
        """Get defaults for a resource, optionally filtered by category."""
        resource_defaults = self.spec["defaults"]["resources"].get(resource_type, {})
        if category:
            return resource_defaults.get(category, {})
        return resource_defaults

    def get_server_applied(self, resource_type: str) -> dict:
        """Get server-applied defaults for a resource."""
        return self.get_defaults(resource_type, "server_applied")

    def get_recommended(self, resource_type: str) -> dict:
        """Get recommended values for a resource."""
        return self.get_defaults(resource_type, "recommended")

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
    Defaults                 DefaultsSpec                 `json:"defaults"`
    ConditionalRequirements  ConditionalRequirementsSpec  `json:"conditional_requirements"`
    MinimumConfigurations    MinimumConfigSpec            `json:"minimum_configurations"`
}

// DefaultsSpec represents the unified defaults structure
type DefaultsSpec struct {
    Description string                      `json:"description"`
    Resources   map[string]ResourceDefaults `json:"resources"`
}

// ResourceDefaults contains all default categories for a resource
type ResourceDefaults struct {
    ServerApplied   map[string]interface{} `json:"server_applied,omitempty"`
    Recommended     map[string]interface{} `json:"recommended,omitempty"`
    AdvancedOptions map[string]interface{} `json:"advanced_options,omitempty"`
    OneofChoices    map[string]string      `json:"oneof_choices,omitempty"`
    UIVsServer      map[string]UIVsServer  `json:"ui_vs_server,omitempty"`
}

type UIVsServer struct {
    UIDefault     string `json:"ui_default"`
    ServerDefault string `json:"server_default"`
    Note          string `json:"note,omitempty"`
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
version = spec["version"]
major = int(version.split(".")[0])
if major < 2:
    raise ValueError(f"Unsupported validation spec version: {version}. Requires v2.x for unified defaults.")
```

> **Migration Note**: v2.1.0 introduced the unified `defaults` structure. Code using `server_defaults`, `oneof_defaults`, `ui_vs_server_defaults`, or `advanced_options_defaults` must be updated to use `defaults.resources.<resource>.<category>`.

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
