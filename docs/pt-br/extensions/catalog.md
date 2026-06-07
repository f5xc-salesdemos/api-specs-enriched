---
title: Catálogo de Extensões de Enriquecimento
description: >-
  Fonte de verdade para cada extensão x-* nas especificações OpenAPI
  enriquecidas
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# Catálogo de Extensões de Enriquecimento

Fonte de verdade para cada extensão `x-*` que aparece em
`docs/specifications/api/*.json`. A paridade com
`scripts/utils/extension_constants.py` é aplicada por
`tests/test_extension_catalog.py`.

Três classes de extensões são documentadas aqui:

- **Injetadas aqui** — extensões que nossos enriquecedores adicionam (`x-f5xc-*` e
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / variantes de
  descoberta). Estas são as que ferramentas downstream devem consumir.
- **Passagem do upstream** — extensões que a F5 emite nas specs de origem
  e que preservamos sem alteração (`x-ves-proto-*`, `x-displayname`, etc.).
  Documentadas para transparência, mas não controladas por este repositório.
- **Injeção futura** — ainda não emitidas; documentadas aqui no momento
  em que um enriquecedor começar a produzi-las (não aplicável na
  população inicial).

## Esquema de entrada

Cada entrada abaixo possui exatamente este formato. O teste de paridade em
`tests/test_extension_catalog.py` tolera que o corpo da seção seja
resumido, desde que o cabeçalho `### x-name` exista e o
flag `Pass-through from upstream:` esteja presente com o valor `yes` ou `no`.

    ### x-<name>
    - **Applied at:** <schema | parameter | operation | path-item | info | response>
    - **Purpose:** <one sentence>
    - **Consumers:** <CLI | VSCode | Terraform | Web UI | multiple | N/A>
    - **Value type:** <string | number | boolean | object | array>
    - **Value schema:** <JSON Schema snippet, or N/A>
    - **Injected by:** <scripts/utils/<enricher>.py, or "upstream">
    - **Driven by config:** <config/<file>.yaml, or "hardcoded", or "upstream">
    - **Example:** <short snippet>
    - **Pass-through from upstream:** <yes/no>

## Injetadas — nível de spec (seção info)

### x-f5xc-cli-domain

- **Aplicado em:** info
- **Propósito:** Identifica o slug do domínio CLI (ex.: `http_loadbalancer`) para uma spec enriquecida.
- **Consumidores:** CLI
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-cli-metadata

- **Aplicado em:** info
- **Propósito:** Bloco de metadados globais do CLI (nome da ferramenta, dicas de versão, agrupamento de domínio).
- **Consumidores:** CLI
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/cli_metadata.yaml
- **Exemplo:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Pass-through from upstream:** no

### x-f5xc-upstream-timestamp

- **Aplicado em:** info
- **Propósito:** Timestamp da spec de origem upstream a partir da qual o arquivo enriquecido foi construído.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "format": "date-time"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-upstream-etag

- **Aplicado em:** info
- **Propósito:** ETag do asset de release da spec de origem upstream.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Pass-through from upstream:** no

### x-f5xc-enriched-version

- **Aplicado em:** info
- **Propósito:** Versão semântica carimbada na spec enriquecida pelo pipeline.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-enriched-version": "3.2.1"`
- **Pass-through from upstream:** no

### x-f5xc-glossary

- **Aplicado em:** info
- **Propósito:** Bloco de glossário de marca/terminologia aplicado a cada spec de domínio.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/branding.py
- **Dirigido pela configuração:** config/branding.yaml
- **Exemplo:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-at

- **Aplicado em:** info
- **Propósito:** Timestamp de quando a passagem de descoberta da API ao vivo foi executada.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "format": "date-time"}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery.yaml
- **Exemplo:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-api-url

- **Aplicado em:** info
- **Propósito:** URL base da API ao vivo que foi sondada durante a descoberta.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "format": "uri"}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery.yaml
- **Exemplo:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Pass-through from upstream:** no

### x-f5xc-api-reference-url

- **Aplicado em:** info
- **Propósito:** URL para a página hospedada de documentação de referência da API deste domínio.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "format": "uri"}`
- **Injetado por:** scripts/utils/external_docs_enricher.py
- **Dirigido pela configuração:** none (derivado do nome do domínio)
- **Exemplo:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Pass-through from upstream:** no

### x-f5xc-response-time-ms

- **Aplicado em:** info
- **Propósito:** Tempo de resposta observado (ms) para a API sondada durante a descoberta.
- **Consumidores:** multiple
- **Tipo de valor:** number
- **Esquema do valor:** `{"type": "number"}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery.yaml
- **Exemplo:** `"x-f5xc-response-time-ms": 42`
- **Pass-through from upstream:** no

### x-f5xc-best-practices

- **Aplicado em:** info
- **Propósito:** Orientações de boas práticas curadas para um domínio.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "object"}}`
- **Injetado por:** scripts/utils/best_practices_enricher.py
- **Dirigido pela configuração:** config/best_practices.yaml
- **Exemplo:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Pass-through from upstream:** no

### x-f5xc-guided-workflows

- **Aplicado em:** info
- **Propósito:** Fluxos de trabalho passo a passo nomeados para realizar tarefas comuns em um domínio.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "object"}}`
- **Injetado por:** scripts/utils/guided_workflow_enricher.py
- **Dirigido pela configuração:** config/guided_workflows.yaml
- **Exemplo:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Pass-through from upstream:** no

### x-f5xc-acronyms

- **Aplicado em:** info
- **Propósito:** Tabela de expansão de acrônimos por domínio.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Injetado por:** scripts/utils/acronym_enricher.py
- **Dirigido pela configuração:** config/acronyms.yaml
- **Exemplo:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Pass-through from upstream:** no

## Injetadas — nível de schema (component schemas)

### x-f5xc-minimum-configuration

- **Aplicado em:** schema
- **Propósito:** Conjunto mínimo viável de campos necessários para realizar POST/PUT deste recurso com sucesso.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/minimum_configuration_enricher.py
- **Dirigido pela configuração:** config/minimum_configs.yaml
- **Exemplo:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Pass-through from upstream:** no

### x-f5xc-namespace-profile

- **Aplicado em:** info
- **Propósito:** Fornece metadados de restrição, recomendação e classificação de namespace para um recurso.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Injetado por:** scripts/utils/namespace_profile_enricher.py
- **Dirigido pela configuração:** config/namespace_profile.yaml
- **Exemplo:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Pass-through from upstream:** no

### x-f5xc-displayorder

- **Aplicado em:** schema
- **Propósito:** Ordenação sugerida de propriedades para apresentação em UI/CLI.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Pass-through from upstream:** no

### x-f5xc-terraform-resource

- **Aplicado em:** schema
- **Propósito:** Nome do tipo de recurso Terraform que mapeia para este schema.
- **Consumidores:** Terraform
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-display-name

- **Aplicado em:** schema
- **Propósito:** Nome de exibição legível por humanos para um schema de recurso (substitui a geração automática).
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Pass-through from upstream:** no

## Injetadas — nível de propriedade

### x-f5xc-description

- **Aplicado em:** schema property
- **Propósito:** Descrição enriquecida da propriedade que complementa a `description` do upstream.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_descriptions.yaml
- **Exemplo:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Pass-through from upstream:** no

### x-f5xc-validation

- **Aplicado em:** schema property
- **Propósito:** Regras de validação declarativas derivadas das `ves.io.schema.rules` do protobuf upstream.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/validation_enricher.py
- **Dirigido pela configuração:** config/validation_rules.yaml
- **Exemplo:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Pass-through from upstream:** no

### x-f5xc-examples

- **Aplicado em:** schema property
- **Propósito:** Múltiplos valores de exemplo ilustrativos para uma propriedade.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array"}`
- **Injetado por:** scripts/utils/resource_examples_enricher.py
- **Dirigido pela configuração:** config/resource_examples.yaml
- **Exemplo:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Pass-through from upstream:** no

### x-f5xc-example

- **Aplicado em:** schema property
- **Propósito:** Um único valor de exemplo canônico.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{}`
- **Injetado por:** scripts/utils/field_description_enricher.py
- **Dirigido pela configuração:** config/field_descriptions.yaml
- **Exemplo:** `"x-f5xc-example": "example.com"`
- **Pass-through from upstream:** no

### x-f5xc-completion

- **Aplicado em:** schema property
- **Propósito:** Dicas de autocompletar do shell (enum estático ou comando dinâmico).
- **Consumidores:** CLI
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Pass-through from upstream:** no

### x-f5xc-defaults

- **Aplicado em:** schema property
- **Propósito:** Valor(es) padrão para exibir em documentações e UIs geradas.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-defaults": {"value": "default"}`
- **Pass-through from upstream:** no

### x-f5xc-required-for-operations

- **Aplicado em:** schema property
- **Propósito:** Lista as operações HTTP (POST/PUT/...) que requerem esta propriedade.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Pass-through from upstream:** no

### x-f5xc-required-for

- **Aplicado em:** schema property
- **Propósito:** Lista combinações de funcionalidades nomeadas que requerem esta propriedade.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/minimum_configuration_enricher.py
- **Dirigido pela configuração:** config/minimum_configs.yaml
- **Exemplo:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Pass-through from upstream:** no

### x-f5xc-conditions

- **Aplicado em:** schema property
- **Propósito:** Requisitos condicionais (ex.: obrigatório quando um campo irmão é igual a X).
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "object"}}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Pass-through from upstream:** no

### x-f5xc-deprecated

- **Aplicado em:** schema property
- **Propósito:** Aviso de depreciação com orientação de substituição.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/field_metadata_enricher.py
- **Dirigido pela configuração:** config/field_metadata.yaml
- **Exemplo:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Pass-through from upstream:** no

### x-f5xc-server-default

- **Aplicado em:** schema property
- **Propósito:** Valor padrão que o servidor atribui quando o cliente omite a propriedade.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{}`
- **Injetado por:** scripts/utils/default_value_enricher.py
- **Dirigido pela configuração:** config/discovered_defaults.yaml
- **Exemplo:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-value

- **Aplicado em:** schema property
- **Propósito:** Valor recomendado para produção de um campo onde o padrão do servidor é subótimo.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{}`
- **Injetado por:** scripts/utils/default_value_enricher.py
- **Dirigido pela configuração:** config/discovered_defaults.yaml
- **Exemplo:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-oneof-variant

- **Aplicado em:** schema property
- **Propósito:** Para blocos `oneOf`, indica qual variante é recomendada.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/default_value_enricher.py
- **Dirigido pela configuração:** config/discovered_defaults.yaml
- **Exemplo:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Pass-through from upstream:** no

### x-f5xc-conflicts-with

- **Aplicado em:** schema property
- **Propósito:** Lista propriedades irmãs que não podem ser definidas junto com esta.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/conflicts_with_enricher.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Pass-through from upstream:** no

### x-f5xc-requires

- **Aplicado em:** schema property
- **Propósito:** Documenta dependências entre campos onde um campo requer que outro esteja definido.
- **Consumidores:** compile_catalog.py, xcsh CLI
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Injetado por:** scripts/utils/dependency_enricher.py
- **Dirigido pela configuração:** config/minimum_configs.yaml (seção de dependências)
- **Exemplo:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Pass-through from upstream:** no

### x-f5xc-constraints

- **Aplicado em:** schema property
- **Propósito:** Restrições numéricas / de string derivadas da sondagem da API ao vivo ou padrões estáticos.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/constraint_enricher.py
- **Dirigido pela configuração:** config/constraint_patterns.yaml
- **Exemplo:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Pass-through from upstream:** no

### x-f5xc-uniqueness

- **Aplicado em:** schema property
- **Propósito:** Declara se um campo deve ser único dentro do seu escopo.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/uniqueness_enricher.py
- **Dirigido pela configuração:** hardcoded
- **Exemplo:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Pass-through from upstream:** no

## Injetadas — nível de operação

### x-f5xc-required-fields

- **Aplicado em:** operation
- **Propósito:** Nomeia os campos do corpo da operação que devem ser fornecidos para sucesso.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/operation_metadata_enricher.py
- **Dirigido pela configuração:** config/operation_metadata.yaml
- **Exemplo:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Pass-through from upstream:** no

### x-f5xc-danger-level

- **Aplicado em:** operation
- **Propósito:** Classifica o raio de impacto de uma operação (low/medium/high/critical).
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Injetado por:** scripts/utils/operation_metadata_enricher.py
- **Dirigido pela configuração:** config/operation_metadata.yaml
- **Exemplo:** `"x-f5xc-danger-level": "high"`
- **Pass-through from upstream:** no

### x-f5xc-confirmation-required

- **Aplicado em:** operation
- **Propósito:** Indica se o CLI/UI deve solicitar confirmação do usuário antes de executar.
- **Consumidores:** multiple
- **Tipo de valor:** boolean
- **Esquema do valor:** `{"type": "boolean"}`
- **Injetado por:** scripts/utils/operation_metadata_enricher.py
- **Dirigido pela configuração:** config/operation_metadata.yaml
- **Exemplo:** `"x-f5xc-confirmation-required": true`
- **Pass-through from upstream:** no

### x-f5xc-side-effects

- **Aplicado em:** operation
- **Propósito:** Lista efeitos colaterais observáveis da operação (reinicialização, reconfiguração, etc.).
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/utils/operation_metadata_enricher.py
- **Dirigido pela configuração:** config/operation_metadata.yaml
- **Exemplo:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Pass-through from upstream:** no

### x-f5xc-discovered-response-time

- **Aplicado em:** operation
- **Propósito:** Tempo de resposta medido empiricamente para esta operação durante a descoberta.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery_enrichment.yaml
- **Exemplo:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-rate-limits

- **Aplicado em:** operation
- **Propósito:** Cabeçalhos/comportamento de limite de taxa observados a partir da API ao vivo.
- **Consumidores:** multiple
- **Tipo de valor:** object
- **Esquema do valor:** `{"type": "object"}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery_enrichment.yaml
- **Exemplo:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-error-catalog

- **Aplicado em:** operation
- **Propósito:** Catálogo de respostas de erro observadas durante a descoberta ao vivo, com payloads de exemplo.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "object"}}`
- **Injetado por:** scripts/utils/discovery_enricher.py
- **Dirigido pela configuração:** config/discovery_enrichment.yaml
- **Exemplo:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Pass-through from upstream:** no

## Injetadas — nível de índice (metadados de domínio)

### x-f5xc-category

- **Aplicado em:** info
- **Propósito:** Categoria de agrupamento de nível superior para CLI / UI / documentação / Terraform de um domínio.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-category": "networking"`
- **Pass-through from upstream:** no

### x-f5xc-primary-resources

- **Aplicado em:** info
- **Propósito:** Lista de tipos de recursos primários que definem o domínio.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Pass-through from upstream:** no

### x-f5xc-critical-resources

- **Aplicado em:** info
- **Propósito:** Recursos que requerem cuidado elevado (críticos para produção).
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/critical_resources.yaml
- **Exemplo:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-description-short

- **Aplicado em:** info
- **Propósito:** Descrição curta (~60 caracteres) do domínio. Também se aplica no nível de propriedade para descrições longas.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/property_description_short_enricher.py
- **Dirigido pela configuração:** config/property_description_short.yaml
- **Exemplo:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Pass-through from upstream:** no

### x-f5xc-description-medium

- **Aplicado em:** info
- **Propósito:** Descrição média (~150 caracteres) do domínio. Também se aplica no nível de propriedade.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/property_description_short_enricher.py
- **Dirigido pela configuração:** config/property_description_short.yaml
- **Exemplo:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Pass-through from upstream:** no

### x-f5xc-description-long

- **Aplicado em:** info
- **Propósito:** Descrição longa (~500 caracteres) do domínio.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/utils/description_enricher.py
- **Dirigido pela configuração:** config/domain_descriptions.yaml
- **Exemplo:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Pass-through from upstream:** no

### x-f5xc-complexity

- **Aplicado em:** info
- **Propósito:** Nível de complexidade relativa para criar configurações neste domínio.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-complexity": "medium"`
- **Pass-through from upstream:** no

### x-f5xc-requires-tier

- **Aplicado em:** info
- **Propósito:** Nível mínimo de assinatura F5 XC necessário.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-requires-tier": "enterprise"`
- **Pass-through from upstream:** no

### x-f5xc-is-preview

- **Aplicado em:** info
- **Propósito:** Indica que um domínio é uma funcionalidade em preview / beta.
- **Consumidores:** multiple
- **Tipo de valor:** boolean
- **Esquema do valor:** `{"type": "boolean"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-is-preview": false`
- **Pass-through from upstream:** no

### x-f5xc-use-cases

- **Aplicado em:** info
- **Propósito:** Casos de uso nomeados que este domínio suporta.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Pass-through from upstream:** no

### x-f5xc-icon

- **Aplicado em:** info
- **Propósito:** Identificador de ícone para usar ao renderizar este domínio em uma UI.
- **Consumidores:** Web UI
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Pass-through from upstream:** no

### x-f5xc-logo-svg

- **Aplicado em:** info
- **Propósito:** SVG inline (ou caminho) para um logotipo de marca representando o domínio.
- **Consumidores:** Web UI
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Pass-through from upstream:** no

### x-f5xc-related-domains

- **Aplicado em:** info
- **Propósito:** Links cruzados para outros domínios comumente usados em conjunto com este.
- **Consumidores:** multiple
- **Tipo de valor:** array
- **Esquema do valor:** `{"type": "array", "items": {"type": "string"}}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-doc-section

- **Aplicado em:** info
- **Propósito:** Slug de seção/agrupamento de navegação da documentação para documentação renderizada.
- **Consumidores:** multiple
- **Tipo de valor:** string
- **Esquema do valor:** `{"type": "string"}`
- **Injetado por:** scripts/merge_specs.py
- **Dirigido pela configuração:** config/domain_patterns.yaml
- **Exemplo:** `"x-f5xc-doc-section": "load-balancing"`
- **Pass-through from upstream:** no

## Passagem do upstream

### x-ves-proto-package

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Pass-through from upstream:** yes

### x-ves-proto-file

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Pass-through from upstream:** yes

### x-ves-proto-message

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Pass-through from upstream:** yes

### x-ves-proto-service

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Pass-through from upstream:** yes

### x-ves-proto-rpc

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Pass-through from upstream:** yes

### x-displayname

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** `"x-displayname": "Namespace"`
- **Pass-through from upstream:** yes

### x-ves-oneof

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** Consulte a documentação upstream da F5.
- **Pass-through from upstream:** yes

### x-ves-default

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** Consulte a documentação upstream da F5.
- **Pass-through from upstream:** yes

### x-ves-required

- **Aplicado em:** upstream
- **Propósito:** Preservado sem alteração da spec upstream da F5.
- **Consumidores:** N/A
- **Tipo de valor:** varies
- **Esquema do valor:** N/A
- **Injetado por:** upstream
- **Dirigido pela configuração:** upstream
- **Exemplo:** Consulte a documentação upstream da F5.
- **Pass-through from upstream:** yes
