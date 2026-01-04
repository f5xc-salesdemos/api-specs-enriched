# Migration Guide: x-f5xc-* Extension Namespace

**Version**: 2.0.0
**Issue**: #292
**Date**: 2026-01-04

## Summary

This release migrates all OpenAPI extension fields from mixed namespaces (`x-ves-*`, non-prefixed) to a unified `x-f5xc-*` namespace. This is a **breaking change** for downstream consumers.

## Why This Change

| Problem | Solution |
|---------|----------|
| Non-prefixed fields (e.g., `domain_category`) violated OpenAPI extension conventions | All fields now use `x-f5xc-*` prefix |
| `x-ves-*` fields conflicted with F5 native extensions | Clear ownership with `x-f5xc-*` namespace |
| No clear distinction between upstream F5 fields and our enrichment | `x-f5xc-*` = our enrichment, `x-ves-proto-*` = F5 native |

## Field Migration Table

### Index.json Fields

| Old Field | New Field |
|-----------|-----------|
| `domain_category` | `x-f5xc-domain-category` |
| `ui_category` | `x-f5xc-ui-category` |
| `primary_resources` | `x-f5xc-primary-resources` |
| `description_short` | `x-f5xc-description-short` |
| `description_medium` | `x-f5xc-description-medium` |
| `complexity` | `x-f5xc-complexity` |
| `requires_tier` | `x-f5xc-requires-tier` |
| `is_preview` | `x-f5xc-is-preview` |
| `aliases` | `x-f5xc-aliases` |
| `use_cases` | `x-f5xc-use-cases` |
| `icon` | `x-f5xc-icon` |
| `logo_svg` | `x-f5xc-logo-svg` |
| `related_domains` | `x-f5xc-related-domains` |

### Spec-Level Fields (info section)

| Old Field | New Field |
|-----------|-----------|
| `x-ves-cli-domain` | `x-f5xc-cli-domain` |
| `x-upstream-timestamp` | `x-f5xc-upstream-timestamp` |
| `x-upstream-etag` | `x-f5xc-upstream-etag` |
| `x-enriched-version` | `x-f5xc-enriched-version` |

### Schema-Level Fields

| Old Field | New Field |
|-----------|-----------|
| `x-ves-cli-domain` | `x-f5xc-cli-domain` |
| `x-ves-cli-aliases` | `x-f5xc-cli-aliases` |
| `x-ves-minimum-configuration` | `x-f5xc-minimum-configuration` |
| `x-ves-namespace-scope` | `x-f5xc-namespace-scope` |
| `x-ves-displayorder` | `x-f5xc-displayorder` |

### Property-Level Fields

| Old Field | New Field |
|-----------|-----------|
| `x-ves-description` | `x-f5xc-description` |
| `x-ves-validation` | `x-f5xc-validation` |
| `x-ves-examples` | `x-f5xc-examples` |
| `x-ves-example` | `x-f5xc-example` |
| `x-ves-completion` | `x-f5xc-completion` |
| `x-ves-defaults` | `x-f5xc-defaults` |
| `x-ves-required-for-operations` | `x-f5xc-required-for-operations` |
| `x-ves-required-for` | `x-f5xc-required-for` |
| `x-ves-conditions` | `x-f5xc-conditions` |
| `x-ves-deprecated` | `x-f5xc-deprecated` |

### Operation-Level Fields

| Old Field | New Field |
|-----------|-----------|
| `x-ves-required-fields` | `x-f5xc-required-fields` |
| `x-ves-danger-level` | `x-f5xc-danger-level` |
| `x-ves-confirmation-required` | `x-f5xc-confirmation-required` |
| `x-ves-side-effects` | `x-f5xc-side-effects` |

## New Fields Added

| Field | Purpose | Level |
|-------|---------|-------|
| `x-f5xc-terraform-resource` | Terraform resource name | Schema |
| `x-f5xc-doc-section` | Documentation navigation | Spec |
| `x-f5xc-display-name` | Human-friendly name | Schema |

## Migration Steps for Downstream Consumers

### 1. Find All Affected Code

```bash
# Search for old field names
grep -r "x-ves-" --include="*.ts" --include="*.py" --include="*.go" --include="*.json" .
grep -r "domain_category\|ui_category\|primary_resources" --include="*.ts" --include="*.py" .
```

### 2. Update Field References

Replace all occurrences using the migration table above. For example:

**TypeScript/JavaScript:**

```typescript
// Before
const domain = spec.info["x-ves-cli-domain"];
const minConfig = schema["x-ves-minimum-configuration"];

// After
const domain = spec.info["x-f5xc-cli-domain"];
const minConfig = schema["x-f5xc-minimum-configuration"];
```

**Python:**

```python
# Before
domain = spec["info"].get("x-ves-cli-domain")
min_config = schema.get("x-ves-minimum-configuration")

# After
domain = spec["info"].get("x-f5xc-cli-domain")
min_config = schema.get("x-f5xc-minimum-configuration")
```

**Go:**

```go
// Before
domain := spec.Info.Extensions["x-ves-cli-domain"]

// After
domain := spec.Info.Extensions["x-f5xc-cli-domain"]
```

### 3. Update Type Definitions

If you have type definitions for the enriched specs, update them:

```typescript
// Before
interface EnrichedInfo {
  "x-ves-cli-domain"?: string;
  "x-ves-namespace-scope"?: string;
}

// After
interface EnrichedInfo {
  "x-f5xc-cli-domain"?: string;
  "x-f5xc-namespace-scope"?: string;
}
```

### 4. Verify with Tests

Run your test suite to catch any remaining references to old field names.

## Extension Registry

All `x-f5xc-*` extensions are documented in `config/extension_registry.yaml`. This file serves as the single source of truth for:

- Extension names and their purposes
- Expected data types
- Which consumers use each extension
- Valid values (for enums)

## F5 Native Fields (Unchanged)

The following F5 native fields are **preserved unchanged**:

- `x-ves-proto-*` fields (protobuf mappings)
- `x-displayname` (F5 display names)
- Any other `x-ves-*` fields from upstream F5 specs

These are not enrichment fields - they come from F5's original specifications.

## Centralized Constants

For Python code in this repository, use the centralized constants:

```python
from scripts.utils.extension_constants import (
    X_F5XC_CLI_DOMAIN,
    X_F5XC_NAMESPACE_SCOPE,
    X_F5XC_MINIMUM_CONFIGURATION,
    # ... etc
)
```

This ensures consistency and makes future migrations easier.

## Backward Compatibility

**This is a breaking change.** There is no backward compatibility layer because:

1. This project is pre-1.0 and still in active development
2. A clean break is simpler than maintaining both namespaces
3. All downstream consumers are internal and can be updated together

## Timeline

- **v2.0.0 Released**: 2026-01-04
- **Migration Deadline**: Immediate (no deprecation period)

## Support

If you encounter issues during migration:

1. Check the field migration tables above
2. Review `config/extension_registry.yaml` for field documentation
3. Open an issue on GitHub if you find unmigrated fields

---

*This migration guide was generated as part of Issue #292.*
