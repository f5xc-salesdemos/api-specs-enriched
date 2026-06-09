---
title: Catalogo delle estensioni di arricchimento
description: Fonte di verità per ogni estensione x-* nelle specifiche OpenAPI arricchite
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# Catalogo delle estensioni di arricchimento

Fonte di verità per ogni estensione `x-*` che appare in
`docs/specifications/api/*.json`. La parità con
`scripts/utils/extension_constants.py` è verificata da
`tests/test_extension_catalog.py`.

Qui sono documentate tre classi di estensioni:

- **Iniettate qui** — estensioni aggiunte dai nostri enricher (`x-f5xc-*` e
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / varianti
  discovery). Queste sono quelle che gli strumenti a valle dovrebbero consumare.
- **Pass-through upstream** — estensioni emesse da F5 nelle specifiche sorgente
  e preservate senza modifiche (`x-ves-proto-*`, `x-displayname`, ecc.).
  Documentate per trasparenza ma non controllate da questo repository.
- **Future-iniettate** — non ancora emesse; documentate qui nel momento in cui
  un enricher inizia a produrle (non applicabile al popolamento iniziale).

## Schema delle voci

Ogni voce qui sotto ha esattamente questa forma. Il test di parità in
`tests/test_extension_catalog.py` tollera che il corpo della sezione sia
ridotto purché l'intestazione `### x-name` esista e il flag
`Pass-through from upstream:` sia presente con valore `yes` o `no`.

    ### x-<name>
    - **Applicata a:** <schema | parameter | operation | path-item | info | response>
    - **Scopo:** <una frase>
    - **Consumatori:** <CLI | VSCode | Terraform | Web UI | multipli | N/A>
    - **Tipo di valore:** <string | number | boolean | object | array>
    - **Schema del valore:** <frammento JSON Schema, o N/A>
    - **Iniettata da:** <scripts/utils/<enricher>.py, o "upstream">
    - **Guidata da config:** <config/<file>.yaml, o "hardcoded", o "upstream">
    - **Esempio:** <breve frammento>
    - **Pass-through from upstream:** <yes/no>

## Iniettate — livello spec (sezione info)

### x-f5xc-cli-domain

- **Applicata a:** info
- **Scopo:** Identifica lo slug del dominio CLI (es. `http_loadbalancer`) per una specifica arricchita.
- **Consumatori:** CLI
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-cli-metadata

- **Applicata a:** info
- **Scopo:** Blocco di metadati a livello CLI (nome dello strumento, suggerimenti di versione, raggruppamento per dominio).
- **Consumatori:** CLI
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/cli_metadata.yaml
- **Esempio:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Pass-through from upstream:** no

### x-f5xc-upstream-timestamp

- **Applicata a:** info
- **Scopo:** Timestamp della specifica sorgente upstream da cui è stato costruito il file arricchito.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "format": "date-time"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-upstream-etag

- **Applicata a:** info
- **Scopo:** ETag dell'asset di rilascio della specifica sorgente upstream.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Pass-through from upstream:** no

### x-f5xc-enriched-version

- **Applicata a:** info
- **Scopo:** Versione semantica apposta sulla specifica arricchita dalla pipeline.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-enriched-version": "3.2.1"`
- **Pass-through from upstream:** no

### x-f5xc-glossary

- **Applicata a:** info
- **Scopo:** Blocco glossario di branding/terminologia applicato a ciascuna specifica di dominio.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/branding.py
- **Guidata da config:** config/branding.yaml
- **Esempio:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-at

- **Applicata a:** info
- **Scopo:** Timestamp di quando è stata eseguita la fase di discovery dell'API live.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "format": "date-time"}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery.yaml
- **Esempio:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-api-url

- **Applicata a:** info
- **Scopo:** URL base dell'API live che è stata sondata durante la discovery.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "format": "uri"}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery.yaml
- **Esempio:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Pass-through from upstream:** no

### x-f5xc-api-reference-url

- **Applicata a:** info
- **Scopo:** URL alla pagina della documentazione di riferimento API ospitata per questo dominio.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "format": "uri"}`
- **Iniettata da:** scripts/utils/external_docs_enricher.py
- **Guidata da config:** nessuna (derivata dal nome del dominio)
- **Esempio:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Pass-through from upstream:** no

### x-f5xc-response-time-ms

- **Applicata a:** info
- **Scopo:** Tempo di risposta osservato (ms) per l'API sondata durante la discovery.
- **Consumatori:** multipli
- **Tipo di valore:** number
- **Schema del valore:** `{"type": "number"}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery.yaml
- **Esempio:** `"x-f5xc-response-time-ms": 42`
- **Pass-through from upstream:** no

### x-f5xc-best-practices

- **Applicata a:** info
- **Scopo:** Linee guida curate sulle migliori pratiche per un dominio.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "object"}}`
- **Iniettata da:** scripts/utils/best_practices_enricher.py
- **Guidata da config:** config/best_practices.yaml
- **Esempio:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Pass-through from upstream:** no

### x-f5xc-guided-workflows

- **Applicata a:** info
- **Scopo:** Workflow nominati passo-passo per svolgere attività comuni in un dominio.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "object"}}`
- **Iniettata da:** scripts/utils/guided_workflow_enricher.py
- **Guidata da config:** config/guided_workflows.yaml
- **Esempio:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Pass-through from upstream:** no

### x-f5xc-acronyms

- **Applicata a:** info
- **Scopo:** Tabella di espansione degli acronimi per dominio.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Iniettata da:** scripts/utils/acronym_enricher.py
- **Guidata da config:** config/acronyms.yaml
- **Esempio:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Pass-through from upstream:** no

## Iniettate — livello schema (schema dei componenti)

### x-f5xc-minimum-configuration

- **Applicata a:** schema
- **Scopo:** Insieme minimo di campi necessari per eseguire con successo una POST/PUT su questa risorsa.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/minimum_configuration_enricher.py
- **Guidata da config:** config/minimum_configs.yaml
- **Esempio:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Pass-through from upstream:** no

### x-f5xc-namespace-profile

- **Applicata a:** info
- **Scopo:** Fornisce metadati di vincolo, raccomandazione e classificazione del namespace per una risorsa.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Iniettata da:** scripts/utils/namespace_profile_enricher.py
- **Guidata da config:** config/namespace_profile.yaml
- **Esempio:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Pass-through from upstream:** no

### x-f5xc-displayorder

- **Applicata a:** schema
- **Scopo:** Ordinamento suggerito delle proprietà per la presentazione UI/CLI.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Pass-through from upstream:** no

### x-f5xc-terraform-resource

- **Applicata a:** schema
- **Scopo:** Nome del tipo di risorsa Terraform che corrisponde a questo schema.
- **Consumatori:** Terraform
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-display-name

- **Applicata a:** schema
- **Scopo:** Nome visualizzato leggibile per uno schema di risorsa (sovrascrive la generazione automatica).
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Pass-through from upstream:** no

## Iniettate — livello proprietà

### x-f5xc-description

- **Applicata a:** proprietà dello schema
- **Scopo:** Descrizione arricchita della proprietà che integra la `description` upstream.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_descriptions.yaml
- **Esempio:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Pass-through from upstream:** no

### x-f5xc-validation

- **Applicata a:** proprietà dello schema
- **Scopo:** Regole di validazione dichiarative derivate dalle `ves.io.schema.rules` protobuf upstream.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/validation_enricher.py
- **Guidata da config:** config/validation_rules.yaml
- **Esempio:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Pass-through from upstream:** no

### x-f5xc-examples

- **Applicata a:** proprietà dello schema
- **Scopo:** Valori di esempio illustrativi multipli per una proprietà.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array"}`
- **Iniettata da:** scripts/utils/resource_examples_enricher.py
- **Guidata da config:** config/resource_examples.yaml
- **Esempio:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Pass-through from upstream:** no

### x-f5xc-example

- **Applicata a:** proprietà dello schema
- **Scopo:** Un singolo valore di esempio canonico.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{}`
- **Iniettata da:** scripts/utils/field_description_enricher.py
- **Guidata da config:** config/field_descriptions.yaml
- **Esempio:** `"x-f5xc-example": "example.com"`
- **Pass-through from upstream:** no

### x-f5xc-completion

- **Applicata a:** proprietà dello schema
- **Scopo:** Suggerimenti di completamento shell (enum statico o comando dinamico).
- **Consumatori:** CLI
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Pass-through from upstream:** no

### x-f5xc-defaults

- **Applicata a:** proprietà dello schema
- **Scopo:** Valori predefiniti da esporre nella documentazione generata e nelle interfacce utente.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-defaults": {"value": "default"}`
- **Pass-through from upstream:** no

### x-f5xc-required-for-operations

- **Applicata a:** proprietà dello schema
- **Scopo:** Elenca le operazioni HTTP (POST/PUT/...) che richiedono questa proprietà.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Pass-through from upstream:** no

### x-f5xc-required-for

- **Applicata a:** proprietà dello schema
- **Scopo:** Elenca le combinazioni di funzionalità denominate che richiedono questa proprietà.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/minimum_configuration_enricher.py
- **Guidata da config:** config/minimum_configs.yaml
- **Esempio:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Pass-through from upstream:** no

### x-f5xc-conditions

- **Applicata a:** proprietà dello schema
- **Scopo:** Requisiti condizionali (es. obbligatorio quando un campo fratello è uguale a X).
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "object"}}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Pass-through from upstream:** no

### x-f5xc-deprecated

- **Applicata a:** proprietà dello schema
- **Scopo:** Avviso di deprecazione con indicazioni sulla sostituzione.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/field_metadata_enricher.py
- **Guidata da config:** config/field_metadata.yaml
- **Esempio:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Pass-through from upstream:** no

### x-f5xc-server-default

- **Applicata a:** proprietà dello schema
- **Scopo:** Valore predefinito che il server assegna quando il client omette la proprietà.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{}`
- **Iniettata da:** scripts/utils/default_value_enricher.py
- **Guidata da config:** config/discovered_defaults.yaml
- **Esempio:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-value

- **Applicata a:** proprietà dello schema
- **Scopo:** Valore raccomandato per la produzione per un campo dove il valore predefinito del server è subottimale.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{}`
- **Iniettata da:** scripts/utils/default_value_enricher.py
- **Guidata da config:** config/discovered_defaults.yaml
- **Esempio:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-oneof-variant

- **Applicata a:** proprietà dello schema
- **Scopo:** Per i blocchi `oneOf`, indica quale variante è raccomandata.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/default_value_enricher.py
- **Guidata da config:** config/discovered_defaults.yaml
- **Esempio:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Pass-through from upstream:** no

### x-f5xc-conflicts-with

- **Applicata a:** proprietà dello schema
- **Scopo:** Elenca le proprietà sorelle che non possono essere impostate insieme a questa.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/conflicts_with_enricher.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Pass-through from upstream:** no

### x-f5xc-requires

- **Applicata a:** proprietà dello schema
- **Scopo:** Documenta le dipendenze tra campi dove un campo richiede che un altro sia impostato.
- **Consumatori:** compile_catalog.py, xcsh CLI
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Iniettata da:** scripts/utils/dependency_enricher.py
- **Guidata da config:** config/minimum_configs.yaml (sezione dependencies)
- **Esempio:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Pass-through from upstream:** no

### x-f5xc-constraints

- **Applicata a:** proprietà dello schema
- **Scopo:** Vincoli numerici / di stringa derivati dal sondaggio dell'API live o da pattern statici.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/constraint_enricher.py
- **Guidata da config:** config/constraint_patterns.yaml
- **Esempio:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Pass-through from upstream:** no

### x-f5xc-uniqueness

- **Applicata a:** proprietà dello schema
- **Scopo:** Dichiara se un campo deve essere univoco all'interno del suo ambito.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/uniqueness_enricher.py
- **Guidata da config:** hardcoded
- **Esempio:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Pass-through from upstream:** no

## Iniettate — livello operazione

### x-f5xc-required-fields

- **Applicata a:** operation
- **Scopo:** Elenca i campi del corpo dell'operazione che devono essere forniti per il successo.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/operation_metadata_enricher.py
- **Guidata da config:** config/operation_metadata.yaml
- **Esempio:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Pass-through from upstream:** no

### x-f5xc-danger-level

- **Applicata a:** operation
- **Scopo:** Classifica il raggio d'impatto di un'operazione (low/medium/high/critical).
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Iniettata da:** scripts/utils/operation_metadata_enricher.py
- **Guidata da config:** config/operation_metadata.yaml
- **Esempio:** `"x-f5xc-danger-level": "high"`
- **Pass-through from upstream:** no

### x-f5xc-confirmation-required

- **Applicata a:** operation
- **Scopo:** Indica se CLI/UI dovrebbe richiedere conferma all'utente prima dell'esecuzione.
- **Consumatori:** multipli
- **Tipo di valore:** boolean
- **Schema del valore:** `{"type": "boolean"}`
- **Iniettata da:** scripts/utils/operation_metadata_enricher.py
- **Guidata da config:** config/operation_metadata.yaml
- **Esempio:** `"x-f5xc-confirmation-required": true`
- **Pass-through from upstream:** no

### x-f5xc-side-effects

- **Applicata a:** operation
- **Scopo:** Elenca gli effetti collaterali osservabili dell'operazione (riavvio, riconfigurazione, ecc.).
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/utils/operation_metadata_enricher.py
- **Guidata da config:** config/operation_metadata.yaml
- **Esempio:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Pass-through from upstream:** no

### x-f5xc-discovered-response-time

- **Applicata a:** operation
- **Scopo:** Tempo di risposta misurato empiricamente per questa operazione durante la discovery.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery_enrichment.yaml
- **Esempio:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-rate-limits

- **Applicata a:** operation
- **Scopo:** Header e comportamento di rate-limit osservati dall'API live.
- **Consumatori:** multipli
- **Tipo di valore:** object
- **Schema del valore:** `{"type": "object"}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery_enrichment.yaml
- **Esempio:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-error-catalog

- **Applicata a:** operation
- **Scopo:** Catalogo delle risposte di errore osservate durante la discovery live, con payload di esempio.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "object"}}`
- **Iniettata da:** scripts/utils/discovery_enricher.py
- **Guidata da config:** config/discovery_enrichment.yaml
- **Esempio:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Pass-through from upstream:** no

## Iniettate — livello indice (metadati del dominio)

### x-f5xc-category

- **Applicata a:** info
- **Scopo:** Categoria di raggruppamento di primo livello per CLI / UI / documentazione / Terraform per un dominio.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-category": "networking"`
- **Pass-through from upstream:** no

### x-f5xc-primary-resources

- **Applicata a:** info
- **Scopo:** Elenco dei tipi di risorsa primari che definiscono il dominio.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Pass-through from upstream:** no

### x-f5xc-critical-resources

- **Applicata a:** info
- **Scopo:** Risorse che richiedono attenzione elevata (critiche per la produzione).
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/critical_resources.yaml
- **Esempio:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-description-short

- **Applicata a:** info
- **Scopo:** Descrizione breve del dominio (~60 caratteri). Si applica anche a livello di proprietà per descrizioni lunghe.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/property_description_short_enricher.py
- **Guidata da config:** config/property_description_short.yaml
- **Esempio:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Pass-through from upstream:** no

### x-f5xc-description-medium

- **Applicata a:** info
- **Scopo:** Descrizione media del dominio (~150 caratteri). Si applica anche a livello di proprietà.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/property_description_short_enricher.py
- **Guidata da config:** config/property_description_short.yaml
- **Esempio:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Pass-through from upstream:** no

### x-f5xc-description-long

- **Applicata a:** info
- **Scopo:** Descrizione lunga del dominio (~500 caratteri).
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/utils/description_enricher.py
- **Guidata da config:** config/domain_descriptions.yaml
- **Esempio:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Pass-through from upstream:** no

### x-f5xc-complexity

- **Applicata a:** info
- **Scopo:** Livello di complessità relativa per la creazione di configurazioni in questo dominio.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-complexity": "medium"`
- **Pass-through from upstream:** no

### x-f5xc-requires-tier

- **Applicata a:** info
- **Scopo:** Livello minimo di sottoscrizione F5 XC richiesto.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-requires-tier": "enterprise"`
- **Pass-through from upstream:** no

### x-f5xc-is-preview

- **Applicata a:** info
- **Scopo:** Contrassegna un dominio come funzionalità in anteprima / beta.
- **Consumatori:** multipli
- **Tipo di valore:** boolean
- **Schema del valore:** `{"type": "boolean"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-is-preview": false`
- **Pass-through from upstream:** no

### x-f5xc-use-cases

- **Applicata a:** info
- **Scopo:** Casi d'uso denominati supportati da questo dominio.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Pass-through from upstream:** no

### x-f5xc-icon

- **Applicata a:** info
- **Scopo:** Identificatore dell'icona da utilizzare nel rendering di questo dominio in una UI.
- **Consumatori:** Web UI
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Pass-through from upstream:** no

### x-f5xc-logo-svg

- **Applicata a:** info
- **Scopo:** SVG inline (o percorso) per un logo del brand che rappresenta il dominio.
- **Consumatori:** Web UI
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Pass-through from upstream:** no

### x-f5xc-related-domains

- **Applicata a:** info
- **Scopo:** Riferimenti incrociati ad altri domini comunemente utilizzati insieme a questo.
- **Consumatori:** multipli
- **Tipo di valore:** array
- **Schema del valore:** `{"type": "array", "items": {"type": "string"}}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-doc-section

- **Applicata a:** info
- **Scopo:** Sezione della documentazione / slug di raggruppamento nella navigazione per la documentazione renderizzata.
- **Consumatori:** multipli
- **Tipo di valore:** string
- **Schema del valore:** `{"type": "string"}`
- **Iniettata da:** scripts/merge_specs.py
- **Guidata da config:** config/domain_patterns.yaml
- **Esempio:** `"x-f5xc-doc-section": "load-balancing"`
- **Pass-through from upstream:** no

## Pass-through upstream

### x-ves-proto-package

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Pass-through from upstream:** yes

### x-ves-proto-file

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Pass-through from upstream:** yes

### x-ves-proto-message

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Pass-through from upstream:** yes

### x-ves-proto-service

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Pass-through from upstream:** yes

### x-ves-proto-rpc

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Pass-through from upstream:** yes

### x-displayname

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** `"x-displayname": "Namespace"`
- **Pass-through from upstream:** yes

### x-ves-oneof

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** Consultare la documentazione upstream F5.
- **Pass-through from upstream:** yes

### x-ves-default

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** Consultare la documentazione upstream F5.
- **Pass-through from upstream:** yes

### x-ves-required

- **Applicata a:** upstream
- **Scopo:** Preservata senza modifiche dalla specifica upstream F5.
- **Consumatori:** N/A
- **Tipo di valore:** varia
- **Schema del valore:** N/A
- **Iniettata da:** upstream
- **Guidata da config:** upstream
- **Esempio:** Consultare la documentazione upstream F5.
- **Pass-through from upstream:** yes
