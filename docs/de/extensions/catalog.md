---
title: Katalog der Anreicherungs-Erweiterungen
description: >-
  Zentrale Referenz für jede x-*-Erweiterung in den angereicherten
  OpenAPI-Spezifikationen
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# Katalog der Anreicherungs-Erweiterungen

Zentrale Referenz für jede `x-*`-Erweiterung, die in
`docs/specifications/api/*.json` vorkommt. Die Übereinstimmung mit
`scripts/utils/extension_constants.py` wird durch
`tests/test_extension_catalog.py` erzwungen.

Drei Klassen von Erweiterungen werden hier dokumentiert:

- **Hier injiziert** — Erweiterungen, die unsere Enricher hinzufügen (`x-f5xc-*` und
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / Discovery-
  Varianten). Diese sind diejenigen, die nachgelagerte Tools konsumieren sollten.
- **Upstream-Durchreichung** — Erweiterungen, die F5 in den Quellspezifikationen ausgibt
  und die wir unverändert beibehalten (`x-ves-proto-*`, `x-displayname`, etc.).
  Aus Transparenzgründen dokumentiert, aber nicht von diesem Repository kontrolliert.
- **Zukünftig injiziert** — noch nicht ausgegeben; hier dokumentiert, sobald
  ein Enricher beginnt, sie zu erzeugen (beim initialen Befüllen nicht zutreffend).

## Eintragsschema

Jeder Eintrag unten hat genau diese Form. Der Paritätstest in
`tests/test_extension_catalog.py` toleriert einen knappen Abschnittsinhalt,
solange der `### x-name`-Header existiert und das Flag
`Pass-through from upstream:` mit dem Wert `yes` oder `no` vorhanden ist.

    ### x-<name>
    - **Angewandt auf:** <schema | parameter | operation | path-item | info | response>
    - **Zweck:** <ein Satz>
    - **Konsumenten:** <CLI | VSCode | Terraform | Web UI | mehrere | N/A>
    - **Werttyp:** <string | number | boolean | object | array>
    - **Wertschema:** <JSON-Schema-Ausschnitt, oder N/A>
    - **Injiziert durch:** <scripts/utils/<enricher>.py, oder "upstream">
    - **Gesteuert durch Konfiguration:** <config/<file>.yaml, oder "hardcoded", oder "upstream">
    - **Beispiel:** <kurzer Ausschnitt>
    - **Pass-through from upstream:** <yes/no>

## Injiziert — Spezifikationsebene (Info-Abschnitt)

### x-f5xc-cli-domain

- **Angewandt auf:** info
- **Zweck:** Identifiziert den CLI-Domain-Slug (z. B. `http_loadbalancer`) für eine angereicherte Spezifikation.
- **Konsumenten:** CLI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-cli-metadata

- **Angewandt auf:** info
- **Zweck:** CLI-weiter Metadatenblock (Toolname, Versionshinweise, Domain-Gruppierung).
- **Konsumenten:** CLI
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/cli_metadata.yaml
- **Beispiel:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Pass-through from upstream:** no

### x-f5xc-upstream-timestamp

- **Angewandt auf:** info
- **Zweck:** Zeitstempel der Upstream-Quellspezifikation, aus der die angereicherte Datei erstellt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "date-time"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-upstream-etag

- **Angewandt auf:** info
- **Zweck:** ETag des Release-Assets der Upstream-Quellspezifikation.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Pass-through from upstream:** no

### x-f5xc-enriched-version

- **Angewandt auf:** info
- **Zweck:** Semantische Versionsnummer, die der Pipeline auf die angereicherte Spezifikation stempelt.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-enriched-version": "3.2.1"`
- **Pass-through from upstream:** no

### x-f5xc-glossary

- **Angewandt auf:** info
- **Zweck:** Branding-/Terminologie-Glossarblock, der auf jede Domain-Spezifikation angewendet wird.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/branding.py
- **Gesteuert durch Konfiguration:** config/branding.yaml
- **Beispiel:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-at

- **Angewandt auf:** info
- **Zweck:** Zeitstempel, wann der Live-API-Discovery-Durchlauf ausgeführt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "date-time"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-api-url

- **Angewandt auf:** info
- **Zweck:** Basis-URL der Live-API, die während der Discovery abgefragt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "uri"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Pass-through from upstream:** no

### x-f5xc-api-reference-url

- **Angewandt auf:** info
- **Zweck:** URL zur gehosteten API-Referenzdokumentationsseite für diese Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "uri"}`
- **Injiziert durch:** scripts/utils/external_docs_enricher.py
- **Gesteuert durch Konfiguration:** keine (abgeleitet vom Domain-Namen)
- **Beispiel:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Pass-through from upstream:** no

### x-f5xc-response-time-ms

- **Angewandt auf:** info
- **Zweck:** Beobachtete Antwortzeit (ms) für die abgefragte API während der Discovery.
- **Konsumenten:** mehrere
- **Werttyp:** number
- **Wertschema:** `{"type": "number"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-response-time-ms": 42`
- **Pass-through from upstream:** no

### x-f5xc-best-practices

- **Angewandt auf:** info
- **Zweck:** Kuratierte Best-Practice-Empfehlungen für eine Domain.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/best_practices_enricher.py
- **Gesteuert durch Konfiguration:** config/best_practices.yaml
- **Beispiel:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Pass-through from upstream:** no

### x-f5xc-guided-workflows

- **Angewandt auf:** info
- **Zweck:** Benannte Schritt-für-Schritt-Workflows zur Durchführung häufiger Aufgaben in einer Domain.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/guided_workflow_enricher.py
- **Gesteuert durch Konfiguration:** config/guided_workflows.yaml
- **Beispiel:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Pass-through from upstream:** no

### x-f5xc-acronyms

- **Angewandt auf:** info
- **Zweck:** Domainspezifische Akronym-Expansionstabelle.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/acronym_enricher.py
- **Gesteuert durch Konfiguration:** config/acronyms.yaml
- **Beispiel:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Pass-through from upstream:** no

## Injiziert — Schemaebene (Komponentenschemas)

### x-f5xc-minimum-configuration

- **Angewandt auf:** schema
- **Zweck:** Minimaler Feldsatz, der erforderlich ist, um diese Ressource erfolgreich per POST/PUT anzulegen.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/minimum_configuration_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml
- **Beispiel:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Pass-through from upstream:** no

### x-f5xc-namespace-profile

- **Angewandt auf:** info
- **Zweck:** Stellt Namespace-Einschränkungen, Empfehlungen und Klassifizierungsmetadaten für eine Ressource bereit.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Injiziert durch:** scripts/utils/namespace_profile_enricher.py
- **Gesteuert durch Konfiguration:** config/namespace_profile.yaml
- **Beispiel:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Pass-through from upstream:** no

### x-f5xc-displayorder

- **Angewandt auf:** schema
- **Zweck:** Empfohlene Reihenfolge der Eigenschaften für die UI-/CLI-Darstellung.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Pass-through from upstream:** no

### x-f5xc-terraform-resource

- **Angewandt auf:** schema
- **Zweck:** Name des Terraform-Ressourcentyps, der diesem Schema zugeordnet ist.
- **Konsumenten:** Terraform
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-display-name

- **Angewandt auf:** schema
- **Zweck:** Lesbarer Anzeigename für ein Ressourcenschema (überschreibt die automatische Generierung).
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Pass-through from upstream:** no

## Injiziert — Eigenschaftsebene

### x-f5xc-description

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Angereicherte Eigenschaftsbeschreibung, die die Upstream-`description` ergänzt.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_descriptions.yaml
- **Beispiel:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Pass-through from upstream:** no

### x-f5xc-validation

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Deklarative Validierungsregeln, abgeleitet aus den Upstream-Protobuf-`ves.io.schema.rules`.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/validation_enricher.py
- **Gesteuert durch Konfiguration:** config/validation_rules.yaml
- **Beispiel:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Pass-through from upstream:** no

### x-f5xc-examples

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Mehrere veranschaulichende Beispielwerte für eine Eigenschaft.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array"}`
- **Injiziert durch:** scripts/utils/resource_examples_enricher.py
- **Gesteuert durch Konfiguration:** config/resource_examples.yaml
- **Beispiel:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Pass-through from upstream:** no

### x-f5xc-example

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Ein einzelner kanonischer Beispielwert.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/field_description_enricher.py
- **Gesteuert durch Konfiguration:** config/field_descriptions.yaml
- **Beispiel:** `"x-f5xc-example": "example.com"`
- **Pass-through from upstream:** no

### x-f5xc-completion

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Shell-Vervollständigungshinweise (statische Enum oder dynamischer Befehl).
- **Konsumenten:** CLI
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Pass-through from upstream:** no

### x-f5xc-defaults

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Standardwert(e), die in generierten Dokumentationen und UIs angezeigt werden sollen.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-defaults": {"value": "default"}`
- **Pass-through from upstream:** no

### x-f5xc-required-for-operations

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Listet HTTP-Operationen (POST/PUT/...) auf, die diese Eigenschaft erfordern.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Pass-through from upstream:** no

### x-f5xc-required-for

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Listet benannte Feature-Kombinationen auf, die diese Eigenschaft erfordern.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/minimum_configuration_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml
- **Beispiel:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Pass-through from upstream:** no

### x-f5xc-conditions

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Bedingte Anforderungen (z. B. erforderlich, wenn ein Geschwisterfeld den Wert X hat).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Pass-through from upstream:** no

### x-f5xc-deprecated

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Veraltungshinweis mit Empfehlung für einen Ersatz.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Pass-through from upstream:** no

### x-f5xc-server-default

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Standardwert, den der Server zuweist, wenn der Client die Eigenschaft weglässt.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-value

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Empfohlener Produktionswert für ein Feld, bei dem der Serverstandard suboptimal ist.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-oneof-variant

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Gibt bei `oneOf`-Blöcken an, welche Variante empfohlen wird.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Pass-through from upstream:** no

### x-f5xc-conflicts-with

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Listet Geschwistereigenschaften auf, die nicht gleichzeitig mit dieser gesetzt werden können.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/conflicts_with_enricher.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Pass-through from upstream:** no

### x-f5xc-requires

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Dokumentiert feldübergreifende Abhängigkeiten, bei denen ein Feld das Setzen eines anderen erfordert.
- **Konsumenten:** compile_catalog.py, xcsh CLI
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Injiziert durch:** scripts/utils/dependency_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml (Abschnitt dependencies)
- **Beispiel:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Pass-through from upstream:** no

### x-f5xc-constraints

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Numerische / String-Einschränkungen, abgeleitet aus Live-API-Abfragen oder statischen Mustern.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/constraint_enricher.py
- **Gesteuert durch Konfiguration:** config/constraint_patterns.yaml
- **Beispiel:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Pass-through from upstream:** no

### x-f5xc-uniqueness

- **Angewandt auf:** Schema-Eigenschaft
- **Zweck:** Deklariert, ob ein Feld innerhalb seines Geltungsbereichs eindeutig sein muss.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/uniqueness_enricher.py
- **Gesteuert durch Konfiguration:** hardcoded
- **Beispiel:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Pass-through from upstream:** no

## Injiziert — Operationsebene

### x-f5xc-required-fields

- **Angewandt auf:** operation
- **Zweck:** Benennt die Felder im Operationskörper, die für den Erfolg angegeben werden müssen.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Pass-through from upstream:** no

### x-f5xc-danger-level

- **Angewandt auf:** operation
- **Zweck:** Klassifiziert den Auswirkungsradius einer Operation (low/medium/high/critical).
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-danger-level": "high"`
- **Pass-through from upstream:** no

### x-f5xc-confirmation-required

- **Angewandt auf:** operation
- **Zweck:** Ob CLI/UI den Benutzer vor der Ausführung zur Bestätigung auffordern soll.
- **Konsumenten:** mehrere
- **Werttyp:** boolean
- **Wertschema:** `{"type": "boolean"}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-confirmation-required": true`
- **Pass-through from upstream:** no

### x-f5xc-side-effects

- **Angewandt auf:** operation
- **Zweck:** Listet beobachtbare Seiteneffekte der Operation auf (Neustart, Neukonfiguration, etc.).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Pass-through from upstream:** no

### x-f5xc-discovered-response-time

- **Angewandt auf:** operation
- **Zweck:** Empirisch gemessene Antwortzeit für diese Operation während der Discovery.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-rate-limits

- **Angewandt auf:** operation
- **Zweck:** Beobachtete Rate-Limit-Header / -Verhalten, das von der Live-API ermittelt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-error-catalog

- **Angewandt auf:** operation
- **Zweck:** Katalog der während der Live-Discovery beobachteten Fehlerantworten mit Beispiel-Payloads.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Pass-through from upstream:** no

## Injiziert — Indexebene (Domain-Metadaten)

### x-f5xc-category

- **Angewandt auf:** info
- **Zweck:** Übergeordnete CLI-/UI-/Docs-/Terraform-Gruppierungskategorie für eine Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-category": "networking"`
- **Pass-through from upstream:** no

### x-f5xc-primary-resources

- **Angewandt auf:** info
- **Zweck:** Liste der primären Ressourcentypen, die die Domain definieren.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Pass-through from upstream:** no

### x-f5xc-critical-resources

- **Angewandt auf:** info
- **Zweck:** Ressourcen, die erhöhte Sorgfalt erfordern (produktionskritisch).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/critical_resources.yaml
- **Beispiel:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-description-short

- **Angewandt auf:** info
- **Zweck:** Kurze (~60 Zeichen) Domain-Beschreibung. Wird auch auf Eigenschaftsebene für lange Beschreibungen angewendet.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/property_description_short_enricher.py
- **Gesteuert durch Konfiguration:** config/property_description_short.yaml
- **Beispiel:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Pass-through from upstream:** no

### x-f5xc-description-medium

- **Angewandt auf:** info
- **Zweck:** Mittellange (~150 Zeichen) Domain-Beschreibung. Wird auch auf Eigenschaftsebene angewendet.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/property_description_short_enricher.py
- **Gesteuert durch Konfiguration:** config/property_description_short.yaml
- **Beispiel:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Pass-through from upstream:** no

### x-f5xc-description-long

- **Angewandt auf:** info
- **Zweck:** Lange (~500 Zeichen) Domain-Beschreibung.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/description_enricher.py
- **Gesteuert durch Konfiguration:** config/domain_descriptions.yaml
- **Beispiel:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Pass-through from upstream:** no

### x-f5xc-complexity

- **Angewandt auf:** info
- **Zweck:** Relative Komplexitätsstufe für die Erstellung von Konfigurationen in dieser Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-complexity": "medium"`
- **Pass-through from upstream:** no

### x-f5xc-requires-tier

- **Angewandt auf:** info
- **Zweck:** Mindestens erforderliche F5 XC-Abonnementstufe.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-requires-tier": "enterprise"`
- **Pass-through from upstream:** no

### x-f5xc-is-preview

- **Angewandt auf:** info
- **Zweck:** Kennzeichnet eine Domain als Vorschau- / Beta-Funktion.
- **Konsumenten:** mehrere
- **Werttyp:** boolean
- **Wertschema:** `{"type": "boolean"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-is-preview": false`
- **Pass-through from upstream:** no

### x-f5xc-use-cases

- **Angewandt auf:** info
- **Zweck:** Benannte Anwendungsfälle, die diese Domain unterstützt.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Pass-through from upstream:** no

### x-f5xc-icon

- **Angewandt auf:** info
- **Zweck:** Icon-Bezeichner, der beim Rendern dieser Domain in einer UI verwendet wird.
- **Konsumenten:** Web UI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Pass-through from upstream:** no

### x-f5xc-logo-svg

- **Angewandt auf:** info
- **Zweck:** Inline-SVG (oder Pfad) für ein Markenlogo, das die Domain repräsentiert.
- **Konsumenten:** Web UI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Pass-through from upstream:** no

### x-f5xc-related-domains

- **Angewandt auf:** info
- **Zweck:** Querverweise auf andere Domains, die häufig zusammen mit dieser verwendet werden.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-doc-section

- **Angewandt auf:** info
- **Zweck:** Dokumentationsabschnitt / Navigationsgruppierungs-Slug für gerenderte Dokumentation.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-doc-section": "load-balancing"`
- **Pass-through from upstream:** no

## Upstream-Durchreichung

### x-ves-proto-package

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Pass-through from upstream:** yes

### x-ves-proto-file

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Pass-through from upstream:** yes

### x-ves-proto-message

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Pass-through from upstream:** yes

### x-ves-proto-service

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Pass-through from upstream:** yes

### x-ves-proto-rpc

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Pass-through from upstream:** yes

### x-displayname

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-displayname": "Namespace"`
- **Pass-through from upstream:** yes

### x-ves-oneof

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Pass-through from upstream:** yes

### x-ves-default

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Pass-through from upstream:** yes

### x-ves-required

- **Angewandt auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation übernommen.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Pass-through from upstream:** yes
