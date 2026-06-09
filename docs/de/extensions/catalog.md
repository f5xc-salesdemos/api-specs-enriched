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
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / Discovery-Varianten).
  Diese sind diejenigen, die nachgelagerte Tools konsumieren sollten.
- **Upstream-Durchreichung** — Erweiterungen, die F5 in den Quellspezifikationen
  ausgibt und die wir unverändert beibehalten (`x-ves-proto-*`, `x-displayname` usw.).
  Aus Transparenzgründen dokumentiert, aber nicht von diesem Repository kontrolliert.
- **Zukünftig injiziert** — noch nicht ausgegeben; hier dokumentiert, sobald
  ein Enricher beginnt, sie zu erzeugen (zum Zeitpunkt der initialen
  Befüllung nicht zutreffend).

## Eintragsschema

Jeder Eintrag unten hat genau diese Form. Der Paritätstest in
`tests/test_extension_catalog.py` toleriert es, wenn der Abschnittskörper
knapp gehalten ist, solange die `### x-name`-Überschrift existiert und das
Flag `Pass-through from upstream:` mit dem Wert `yes` oder `no` vorhanden ist.

    ### x-<name>
    - **Angewendet auf:** <schema | parameter | operation | path-item | info | response>
    - **Zweck:** <ein Satz>
    - **Konsumenten:** <CLI | VSCode | Terraform | Web UI | mehrere | N/A>
    - **Werttyp:** <string | number | boolean | object | array>
    - **Wertschema:** <JSON-Schema-Ausschnitt oder N/A>
    - **Injiziert durch:** <scripts/utils/<enricher>.py oder "upstream">
    - **Gesteuert durch Konfiguration:** <config/<datei>.yaml oder "hardcodiert" oder "upstream">
    - **Beispiel:** <kurzer Ausschnitt>
    - **Durchreichung von Upstream:** <ja/nein>

## Injiziert — Spezifikationsebene (Info-Abschnitt)

### x-f5xc-cli-domain

- **Angewendet auf:** info
- **Zweck:** Identifiziert den CLI-Domain-Slug (z. B. `http_loadbalancer`) für eine angereicherte Spezifikation.
- **Konsumenten:** CLI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Durchreichung von Upstream:** nein

### x-f5xc-cli-metadata

- **Angewendet auf:** info
- **Zweck:** CLI-weiter Metadatenblock (Toolname, Versionshinweise, Domain-Gruppierung).
- **Konsumenten:** CLI
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/cli_metadata.yaml
- **Beispiel:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-upstream-timestamp

- **Angewendet auf:** info
- **Zweck:** Zeitstempel der Upstream-Quellspezifikation, aus der die angereicherte Datei erstellt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "date-time"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Durchreichung von Upstream:** nein

### x-f5xc-upstream-etag

- **Angewendet auf:** info
- **Zweck:** ETag des Release-Assets der Upstream-Quellspezifikation.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Durchreichung von Upstream:** nein

### x-f5xc-enriched-version

- **Angewendet auf:** info
- **Zweck:** Semantische Version, die von der Pipeline auf die angereicherte Spezifikation gestempelt wird.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-enriched-version": "3.2.1"`
- **Durchreichung von Upstream:** nein

### x-f5xc-glossary

- **Angewendet auf:** info
- **Zweck:** Branding-/Terminologie-Glossarblock, der auf jede Domain-Spezifikation angewendet wird.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/branding.py
- **Gesteuert durch Konfiguration:** config/branding.yaml
- **Beispiel:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-discovered-at

- **Angewendet auf:** info
- **Zweck:** Zeitstempel, wann der Live-API-Discovery-Durchlauf ausgeführt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "date-time"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Durchreichung von Upstream:** nein

### x-f5xc-api-url

- **Angewendet auf:** info
- **Zweck:** Basis-URL der Live-API, die während der Discovery abgefragt wurde.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "uri"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Durchreichung von Upstream:** nein

### x-f5xc-api-reference-url

- **Angewendet auf:** info
- **Zweck:** URL zur gehosteten API-Referenzdokumentationsseite für diese Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "format": "uri"}`
- **Injiziert durch:** scripts/utils/external_docs_enricher.py
- **Gesteuert durch Konfiguration:** keine (abgeleitet vom Domain-Namen)
- **Beispiel:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Durchreichung von Upstream:** nein

### x-f5xc-response-time-ms

- **Angewendet auf:** info
- **Zweck:** Beobachtete Antwortzeit (ms) für die abgefragte API während der Discovery.
- **Konsumenten:** mehrere
- **Werttyp:** number
- **Wertschema:** `{"type": "number"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery.yaml
- **Beispiel:** `"x-f5xc-response-time-ms": 42`
- **Durchreichung von Upstream:** nein

### x-f5xc-best-practices

- **Angewendet auf:** info
- **Zweck:** Kuratierte Best-Practice-Empfehlungen für eine Domain.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/best_practices_enricher.py
- **Gesteuert durch Konfiguration:** config/best_practices.yaml
- **Beispiel:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Durchreichung von Upstream:** nein

### x-f5xc-guided-workflows

- **Angewendet auf:** info
- **Zweck:** Benannte Schritt-für-Schritt-Workflows zur Erledigung gängiger Aufgaben in einer Domain.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/guided_workflow_enricher.py
- **Gesteuert durch Konfiguration:** config/guided_workflows.yaml
- **Beispiel:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Durchreichung von Upstream:** nein

### x-f5xc-acronyms

- **Angewendet auf:** info
- **Zweck:** Pro-Domain-Akronym-Auflösungstabelle.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/acronym_enricher.py
- **Gesteuert durch Konfiguration:** config/acronyms.yaml
- **Beispiel:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Durchreichung von Upstream:** nein

## Injiziert — Schema-Ebene (Komponentenschemata)

### x-f5xc-minimum-configuration

- **Angewendet auf:** schema
- **Zweck:** Minimaler lebensfähiger Feldsatz, der für ein erfolgreiches POST/PUT dieser Ressource erforderlich ist.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/minimum_configuration_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml
- **Beispiel:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Durchreichung von Upstream:** nein

### x-f5xc-namespace-profile

- **Angewendet auf:** info
- **Zweck:** Stellt Namespace-Einschränkungs-, Empfehlungs- und Klassifizierungsmetadaten für eine Ressource bereit.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Injiziert durch:** scripts/utils/namespace_profile_enricher.py
- **Gesteuert durch Konfiguration:** config/namespace_profile.yaml
- **Beispiel:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Durchreichung von Upstream:** nein

### x-f5xc-displayorder

- **Angewendet auf:** schema
- **Zweck:** Vorgeschlagene Reihenfolge der Eigenschaften für die UI-/CLI-Darstellung.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-terraform-resource

- **Angewendet auf:** schema
- **Zweck:** Name des Terraform-Ressourcentyps, der diesem Schema zugeordnet ist.
- **Konsumenten:** Terraform
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Durchreichung von Upstream:** nein

### x-f5xc-display-name

- **Angewendet auf:** schema
- **Zweck:** Menschenlesbarer Anzeigename für ein Ressourcenschema (überschreibt die automatische Generierung).
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Durchreichung von Upstream:** nein

## Injiziert — Eigenschaftsebene

### x-f5xc-description

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Angereicherte Eigenschaftsbeschreibung, die die Upstream-`description` ergänzt.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_descriptions.yaml
- **Beispiel:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Durchreichung von Upstream:** nein

### x-f5xc-validation

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Deklarative Validierungsregeln, abgeleitet aus Upstream-Protobuf `ves.io.schema.rules`.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/validation_enricher.py
- **Gesteuert durch Konfiguration:** config/validation_rules.yaml
- **Beispiel:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Durchreichung von Upstream:** nein

### x-f5xc-examples

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Mehrere veranschaulichende Beispielwerte für eine Eigenschaft.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array"}`
- **Injiziert durch:** scripts/utils/resource_examples_enricher.py
- **Gesteuert durch Konfiguration:** config/resource_examples.yaml
- **Beispiel:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-example

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Ein einzelner kanonischer Beispielwert.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/field_description_enricher.py
- **Gesteuert durch Konfiguration:** config/field_descriptions.yaml
- **Beispiel:** `"x-f5xc-example": "example.com"`
- **Durchreichung von Upstream:** nein

### x-f5xc-completion

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Shell-Vervollständigungshinweise (statische Enumeration oder dynamischer Befehl).
- **Konsumenten:** CLI
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-defaults

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Standardwert(e), die in generierten Dokumentationen und Benutzeroberflächen angezeigt werden.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-defaults": {"value": "default"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-required-for-operations

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Listet HTTP-Operationen (POST/PUT/...) auf, die diese Eigenschaft erfordern.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-required-for

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Listet benannte Feature-Kombinationen auf, die diese Eigenschaft erfordern.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/minimum_configuration_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml
- **Beispiel:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-conditions

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Bedingte Anforderungen (z. B. erforderlich wenn ein Geschwisterfeld den Wert X hat).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Durchreichung von Upstream:** nein

### x-f5xc-deprecated

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Hinweis zur Veraltung mit Ersatzempfehlung.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/field_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/field_metadata.yaml
- **Beispiel:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-server-default

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Standardwert, den der Server zuweist, wenn der Client die Eigenschaft weglässt.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Durchreichung von Upstream:** nein

### x-f5xc-recommended-value

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Empfohlener Produktionswert für ein Feld, bei dem der Serverstandard suboptimal ist.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Durchreichung von Upstream:** nein

### x-f5xc-recommended-oneof-variant

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Gibt bei `oneOf`-Blöcken an, welche Variante empfohlen wird.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/default_value_enricher.py
- **Gesteuert durch Konfiguration:** config/discovered_defaults.yaml
- **Beispiel:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Durchreichung von Upstream:** nein

### x-f5xc-conflicts-with

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Listet Geschwistereigenschaften auf, die nicht gleichzeitig mit dieser gesetzt werden können.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/conflicts_with_enricher.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-requires

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Dokumentiert feldübergreifende Abhängigkeiten, bei denen ein Feld erfordert, dass ein anderes gesetzt ist.
- **Konsumenten:** compile_catalog.py, xcsh CLI
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Injiziert durch:** scripts/utils/dependency_enricher.py
- **Gesteuert durch Konfiguration:** config/minimum_configs.yaml (Abhängigkeitsabschnitt)
- **Beispiel:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Durchreichung von Upstream:** nein

### x-f5xc-constraints

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Numerische / String-Einschränkungen, abgeleitet aus Live-API-Abfragen oder statischen Mustern.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/constraint_enricher.py
- **Gesteuert durch Konfiguration:** config/constraint_patterns.yaml
- **Beispiel:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Durchreichung von Upstream:** nein

### x-f5xc-uniqueness

- **Angewendet auf:** Schema-Eigenschaft
- **Zweck:** Deklariert, ob ein Feld innerhalb seines Gültigkeitsbereichs eindeutig sein muss.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/uniqueness_enricher.py
- **Gesteuert durch Konfiguration:** hardcodiert
- **Beispiel:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Durchreichung von Upstream:** nein

## Injiziert — Operationsebene

### x-f5xc-required-fields

- **Angewendet auf:** operation
- **Zweck:** Benennt die Felder im Operationskörper, die für einen Erfolg bereitgestellt werden müssen.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-danger-level

- **Angewendet auf:** operation
- **Zweck:** Klassifiziert den Wirkungsradius einer Operation (low/medium/high/critical).
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-danger-level": "high"`
- **Durchreichung von Upstream:** nein

### x-f5xc-confirmation-required

- **Angewendet auf:** operation
- **Zweck:** Gibt an, ob CLI/UI den Benutzer vor der Ausführung zur Bestätigung auffordern soll.
- **Konsumenten:** mehrere
- **Werttyp:** boolean
- **Wertschema:** `{"type": "boolean"}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-confirmation-required": true`
- **Durchreichung von Upstream:** nein

### x-f5xc-side-effects

- **Angewendet auf:** operation
- **Zweck:** Listet beobachtbare Nebeneffekte der Operation auf (Neustart, Neukonfiguration usw.).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/utils/operation_metadata_enricher.py
- **Gesteuert durch Konfiguration:** config/operation_metadata.yaml
- **Beispiel:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-discovered-response-time

- **Angewendet auf:** operation
- **Zweck:** Empirisch gemessene Antwortzeit für diese Operation während der Discovery.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Durchreichung von Upstream:** nein

### x-f5xc-discovered-rate-limits

- **Angewendet auf:** operation
- **Zweck:** Beobachtete Rate-Limit-Header / -Verhalten, die aus der Live-API ermittelt wurden.
- **Konsumenten:** mehrere
- **Werttyp:** object
- **Wertschema:** `{"type": "object"}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Durchreichung von Upstream:** nein

### x-f5xc-discovered-error-catalog

- **Angewendet auf:** operation
- **Zweck:** Katalog der während der Live-Discovery beobachteten Fehlerantworten mit Beispiel-Payloads.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "object"}}`
- **Injiziert durch:** scripts/utils/discovery_enricher.py
- **Gesteuert durch Konfiguration:** config/discovery_enrichment.yaml
- **Beispiel:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Durchreichung von Upstream:** nein

## Injiziert — Indexebene (Domain-Metadaten)

### x-f5xc-category

- **Angewendet auf:** info
- **Zweck:** Übergeordnete CLI- / UI- / Doku- / Terraform-Gruppierungskategorie für eine Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-category": "networking"`
- **Durchreichung von Upstream:** nein

### x-f5xc-primary-resources

- **Angewendet auf:** info
- **Zweck:** Liste der primären Ressourcentypen, die die Domain definieren.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-critical-resources

- **Angewendet auf:** info
- **Zweck:** Ressourcen, die erhöhte Sorgfalt erfordern (produktionskritisch).
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/critical_resources.yaml
- **Beispiel:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-description-short

- **Angewendet auf:** info
- **Zweck:** Kurze (~60 Zeichen) Domain-Beschreibung. Wird auch auf Eigenschaftsebene für lange Beschreibungen verwendet.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/property_description_short_enricher.py
- **Gesteuert durch Konfiguration:** config/property_description_short.yaml
- **Beispiel:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Durchreichung von Upstream:** nein

### x-f5xc-description-medium

- **Angewendet auf:** info
- **Zweck:** Mittellange (~150 Zeichen) Domain-Beschreibung. Wird auch auf Eigenschaftsebene verwendet.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/property_description_short_enricher.py
- **Gesteuert durch Konfiguration:** config/property_description_short.yaml
- **Beispiel:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Durchreichung von Upstream:** nein

### x-f5xc-description-long

- **Angewendet auf:** info
- **Zweck:** Lange (~500 Zeichen) Domain-Beschreibung.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/utils/description_enricher.py
- **Gesteuert durch Konfiguration:** config/domain_descriptions.yaml
- **Beispiel:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Durchreichung von Upstream:** nein

### x-f5xc-complexity

- **Angewendet auf:** info
- **Zweck:** Relative Komplexitätsstufe für das Erstellen von Konfigurationen in dieser Domain.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-complexity": "medium"`
- **Durchreichung von Upstream:** nein

### x-f5xc-requires-tier

- **Angewendet auf:** info
- **Zweck:** Mindestens erforderliche F5 XC-Abonnementstufe.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-requires-tier": "enterprise"`
- **Durchreichung von Upstream:** nein

### x-f5xc-is-preview

- **Angewendet auf:** info
- **Zweck:** Markiert eine Domain als Vorschau- / Beta-Feature.
- **Konsumenten:** mehrere
- **Werttyp:** boolean
- **Wertschema:** `{"type": "boolean"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-is-preview": false`
- **Durchreichung von Upstream:** nein

### x-f5xc-use-cases

- **Angewendet auf:** info
- **Zweck:** Benannte Anwendungsfälle, die diese Domain unterstützt.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-icon

- **Angewendet auf:** info
- **Zweck:** Icon-Bezeichner zur Verwendung beim Rendern dieser Domain in einer Benutzeroberfläche.
- **Konsumenten:** Web UI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Durchreichung von Upstream:** nein

### x-f5xc-logo-svg

- **Angewendet auf:** info
- **Zweck:** Inline-SVG (oder Pfad) für ein Markenlogo, das die Domain repräsentiert.
- **Konsumenten:** Web UI
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Durchreichung von Upstream:** nein

### x-f5xc-related-domains

- **Angewendet auf:** info
- **Zweck:** Querverweise auf andere Domains, die häufig zusammen mit dieser verwendet werden.
- **Konsumenten:** mehrere
- **Werttyp:** array
- **Wertschema:** `{"type": "array", "items": {"type": "string"}}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Durchreichung von Upstream:** nein

### x-f5xc-doc-section

- **Angewendet auf:** info
- **Zweck:** Dokumentationsabschnitt / Navigationsgruppierungs-Slug für gerenderte Dokumentation.
- **Konsumenten:** mehrere
- **Werttyp:** string
- **Wertschema:** `{"type": "string"}`
- **Injiziert durch:** scripts/merge_specs.py
- **Gesteuert durch Konfiguration:** config/domain_patterns.yaml
- **Beispiel:** `"x-f5xc-doc-section": "load-balancing"`
- **Durchreichung von Upstream:** nein

## Upstream-Durchreichung

### x-ves-proto-package

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Durchreichung von Upstream:** ja

### x-ves-proto-file

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Durchreichung von Upstream:** ja

### x-ves-proto-message

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Durchreichung von Upstream:** ja

### x-ves-proto-service

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Durchreichung von Upstream:** ja

### x-ves-proto-rpc

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Durchreichung von Upstream:** ja

### x-displayname

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** `"x-displayname": "Namespace"`
- **Durchreichung von Upstream:** ja

### x-ves-oneof

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Durchreichung von Upstream:** ja

### x-ves-default

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Durchreichung von Upstream:** ja

### x-ves-required

- **Angewendet auf:** upstream
- **Zweck:** Unverändert aus der F5-Upstream-Spezifikation beibehalten.
- **Konsumenten:** N/A
- **Werttyp:** variiert
- **Wertschema:** N/A
- **Injiziert durch:** upstream
- **Gesteuert durch Konfiguration:** upstream
- **Beispiel:** Siehe F5-Upstream-Dokumentation.
- **Durchreichung von Upstream:** ja
