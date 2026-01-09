# API Specifications

## Master Specification

The master OpenAPI specification combines all domains into a single file:

- [openapi.json](api/openapi.json) - Combined specification (all domains)
- [index.json](api/index.json) - Metadata and domain index

## Domain Specifications

Individual domain specifications are organized by functional area:

| Domain | Description | Endpoints |
|--------|-------------|-----------|
| Virtual | HTTP/HTTPS load balancing and traffic management | [virtual.json](api/virtual.json) |
| WAF | Web Application Firewall policies and rules | [waf.json](api/waf.json) |
| Network | Networking and connectivity services | [network.json](api/network.json) |
| Sites | Infrastructure sites and clusters | [sites.json](api/sites.json) |
| DNS | DNS zone and record management | [dns.json](api/dns.json) |
| Certificates | Certificate management and lifecycle | [certificates.json](api/certificates.json) |

## Download

Download the latest API specifications from the [GitHub Releases](https://github.com/robinmordasiewicz/f5xc-api-enriched/releases/latest) page.

Each release includes:

- ZIP package with all specifications
- Master `openapi.json` (combined spec)
- Master `openapi.yaml` (YAML format)
- Domain-specific JSON files
- Metadata `index.json`
- CHANGELOG.md

## Usage

### Swagger UI

```bash
# Use with Swagger UI
docker run -p 80:8080 \
  -e SWAGGER_JSON=/specs/openapi.json \
  -v $(pwd)/docs/specifications/api:/specs \
  swaggerapi/swagger-ui
```

### OpenAPI Generator

```bash
# Generate client SDK
openapi-generator generate \
  -i docs/specifications/api/openapi.json \
  -g python \
  -o ./client-sdk
```

### Postman

1. Download `openapi.json`
2. Import into Postman: File → Import → OpenAPI 3.0
3. Configure environment variables
4. Start testing endpoints

## Enrichment

All specifications are enriched with:

- Acronym normalization (100+ terms)
- Grammar improvements
- Branding updates (Volterra → F5 Distributed Cloud)
- Fixed orphan `$ref` references
- Type standardization
- Spectral OpenAPI validation

## Version Information

The current version and upstream sync information are available in [index.json](api/index.json):

```json
{
  "version": "2.0.15",
  "x-upstream-timestamp": "2026-01-06",
  "x-enriched-version": "2.0.15",
  "specifications": [...]
}
```
