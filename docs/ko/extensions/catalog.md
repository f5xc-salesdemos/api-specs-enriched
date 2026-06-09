---
title: 보강 확장 카탈로그
description: 보강된 OpenAPI 명세에 포함된 모든 x-* 확장의 공식 참조 문서
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# 보강 확장 카탈로그

`docs/specifications/api/*.json`에 등장하는 모든 `x-*` 확장의 공식 참조 문서입니다.
`scripts/utils/extension_constants.py`와의 일관성은
`tests/test_extension_catalog.py`에 의해 강제됩니다.

여기에는 세 가지 종류의 확장이 문서화되어 있습니다:

- **여기서 주입됨** — 보강기(enricher)가 추가하는 확장입니다 (`x-f5xc-*` 및
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / 디스커버리
  변형). 이것들은 다운스트림 도구가 사용해야 하는 확장입니다.
- **업스트림 패스스루** — F5가 소스 명세에서 생성하고
  우리가 변경 없이 보존하는 확장입니다 (`x-ves-proto-*`, `x-displayname` 등).
  투명성을 위해 문서화되었지만 이 저장소에서 관리하지 않습니다.
- **향후 주입 예정** — 아직 생성되지 않으며, 보강기가 생성을 시작하는 시점에
  여기에 문서화됩니다 (초기 작성 시점에는 해당 없음).

## 항목 스키마

아래의 모든 항목은 정확히 이 형태를 따릅니다. `tests/test_extension_catalog.py`의
일관성 테스트는 `### x-name` 헤더가 존재하고
`Pass-through from upstream:` 플래그가 `yes` 또는 `no` 값으로 존재하는 한
섹션 본문이 간략해도 허용합니다.

    ### x-<name>
    - **적용 위치:** <schema | parameter | operation | path-item | info | response>
    - **목적:** <한 문장>
    - **소비자:** <CLI | VSCode | Terraform | Web UI | multiple | N/A>
    - **값 타입:** <string | number | boolean | object | array>
    - **값 스키마:** <JSON Schema 스니펫, 또는 N/A>
    - **주입 주체:** <scripts/utils/<enricher>.py, 또는 "upstream">
    - **설정 기반:** <config/<file>.yaml, 또는 "hardcoded", 또는 "upstream">
    - **예시:** <짧은 스니펫>
    - **업스트림 패스스루 여부:** <yes/no>

## 주입됨 — 명세 수준 (info 섹션)

### x-f5xc-cli-domain

- **적용 위치:** info
- **목적:** 보강된 명세의 CLI 도메인 슬러그(예: `http_loadbalancer`)를 식별합니다.
- **소비자:** CLI
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **업스트림 패스스루 여부:** no

### x-f5xc-cli-metadata

- **적용 위치:** info
- **목적:** CLI 전체 메타데이터 블록 (도구 이름, 버전 힌트, 도메인 그룹화).
- **소비자:** CLI
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/cli_metadata.yaml
- **예시:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-upstream-timestamp

- **적용 위치:** info
- **목적:** 보강 파일이 빌드된 업스트림 소스 명세의 타임스탬프.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "format": "date-time"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **업스트림 패스스루 여부:** no

### x-f5xc-upstream-etag

- **적용 위치:** info
- **목적:** 업스트림 소스 명세 릴리스 에셋의 ETag.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **업스트림 패스스루 여부:** no

### x-f5xc-enriched-version

- **적용 위치:** info
- **목적:** 파이프라인에 의해 보강된 명세에 부여된 시맨틱 버전.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-enriched-version": "3.2.1"`
- **업스트림 패스스루 여부:** no

### x-f5xc-glossary

- **적용 위치:** info
- **목적:** 각 도메인 명세에 적용되는 브랜딩/용어 용어집 블록.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/branding.py
- **설정 기반:** config/branding.yaml
- **예시:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-discovered-at

- **적용 위치:** info
- **목적:** 라이브 API 디스커버리 패스가 실행된 타임스탬프.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "format": "date-time"}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery.yaml
- **예시:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **업스트림 패스스루 여부:** no

### x-f5xc-api-url

- **적용 위치:** info
- **목적:** 디스커버리 중 프로빙된 라이브 API의 기본 URL.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "format": "uri"}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery.yaml
- **예시:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **업스트림 패스스루 여부:** no

### x-f5xc-api-reference-url

- **적용 위치:** info
- **목적:** 이 도메인의 호스팅된 API 참조 문서 페이지 URL.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "format": "uri"}`
- **주입 주체:** scripts/utils/external_docs_enricher.py
- **설정 기반:** none (도메인 이름에서 파생)
- **예시:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **업스트림 패스스루 여부:** no

### x-f5xc-response-time-ms

- **적용 위치:** info
- **목적:** 디스커버리 중 프로빙된 API의 관측된 응답 시간(ms).
- **소비자:** multiple
- **값 타입:** number
- **값 스키마:** `{"type": "number"}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery.yaml
- **예시:** `"x-f5xc-response-time-ms": 42`
- **업스트림 패스스루 여부:** no

### x-f5xc-best-practices

- **적용 위치:** info
- **목적:** 도메인에 대한 선별된 모범 사례 안내.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "object"}}`
- **주입 주체:** scripts/utils/best_practices_enricher.py
- **설정 기반:** config/best_practices.yaml
- **예시:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **업스트림 패스스루 여부:** no

### x-f5xc-guided-workflows

- **적용 위치:** info
- **목적:** 도메인에서 일반적인 작업을 수행하기 위한 명명된 단계별 워크플로.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "object"}}`
- **주입 주체:** scripts/utils/guided_workflow_enricher.py
- **설정 기반:** config/guided_workflows.yaml
- **예시:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **업스트림 패스스루 여부:** no

### x-f5xc-acronyms

- **적용 위치:** info
- **목적:** 도메인별 약어 확장 테이블.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **주입 주체:** scripts/utils/acronym_enricher.py
- **설정 기반:** config/acronyms.yaml
- **예시:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **업스트림 패스스루 여부:** no

## 주입됨 — 스키마 수준 (컴포넌트 스키마)

### x-f5xc-minimum-configuration

- **적용 위치:** schema
- **목적:** 이 리소스를 성공적으로 POST/PUT하는 데 필요한 최소 필드 세트.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/minimum_configuration_enricher.py
- **설정 기반:** config/minimum_configs.yaml
- **예시:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **업스트림 패스스루 여부:** no

### x-f5xc-namespace-profile

- **적용 위치:** info
- **목적:** 리소스에 대한 네임스페이스 제약, 권장 사항 및 분류 메타데이터를 제공합니다.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **주입 주체:** scripts/utils/namespace_profile_enricher.py
- **설정 기반:** config/namespace_profile.yaml
- **예시:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **업스트림 패스스루 여부:** no

### x-f5xc-displayorder

- **적용 위치:** schema
- **목적:** UI/CLI 표시를 위한 속성의 권장 정렬 순서.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-terraform-resource

- **적용 위치:** schema
- **목적:** 이 스키마에 매핑되는 Terraform 리소스 타입 이름.
- **소비자:** Terraform
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **업스트림 패스스루 여부:** no

### x-f5xc-display-name

- **적용 위치:** schema
- **목적:** 리소스 스키마의 사람이 읽을 수 있는 표시 이름 (자동 생성을 대체).
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **업스트림 패스스루 여부:** no

## 주입됨 — 속성 수준

### x-f5xc-description

- **적용 위치:** schema property
- **목적:** 업스트림 `description`을 보완하는 보강된 속성 설명.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_descriptions.yaml
- **예시:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **업스트림 패스스루 여부:** no

### x-f5xc-validation

- **적용 위치:** schema property
- **목적:** 업스트림 protobuf `ves.io.schema.rules`에서 파생된 선언적 유효성 검증 규칙.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/validation_enricher.py
- **설정 기반:** config/validation_rules.yaml
- **예시:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **업스트림 패스스루 여부:** no

### x-f5xc-examples

- **적용 위치:** schema property
- **목적:** 속성에 대한 여러 설명용 예시 값.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array"}`
- **주입 주체:** scripts/utils/resource_examples_enricher.py
- **설정 기반:** config/resource_examples.yaml
- **예시:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-example

- **적용 위치:** schema property
- **목적:** 단일 표준 예시 값.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{}`
- **주입 주체:** scripts/utils/field_description_enricher.py
- **설정 기반:** config/field_descriptions.yaml
- **예시:** `"x-f5xc-example": "example.com"`
- **업스트림 패스스루 여부:** no

### x-f5xc-completion

- **적용 위치:** schema property
- **목적:** 셸 자동 완성 힌트 (정적 enum 또는 동적 명령).
- **소비자:** CLI
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-defaults

- **적용 위치:** schema property
- **목적:** 생성된 문서 및 UI에 표시할 기본값.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-defaults": {"value": "default"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-required-for-operations

- **적용 위치:** schema property
- **목적:** 이 속성이 필요한 HTTP 작업(POST/PUT/...)을 나열합니다.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-required-for

- **적용 위치:** schema property
- **목적:** 이 속성이 필요한 명명된 기능 조합을 나열합니다.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/minimum_configuration_enricher.py
- **설정 기반:** config/minimum_configs.yaml
- **예시:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-conditions

- **적용 위치:** schema property
- **목적:** 조건부 요구 사항 (예: 형제 필드가 X와 같을 때 필수).
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "object"}}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **업스트림 패스스루 여부:** no

### x-f5xc-deprecated

- **적용 위치:** schema property
- **목적:** 대체 안내가 포함된 사용 중단 알림.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/field_metadata_enricher.py
- **설정 기반:** config/field_metadata.yaml
- **예시:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-server-default

- **적용 위치:** schema property
- **목적:** 클라이언트가 속성을 생략할 때 서버가 할당하는 기본값.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{}`
- **주입 주체:** scripts/utils/default_value_enricher.py
- **설정 기반:** config/discovered_defaults.yaml
- **예시:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **업스트림 패스스루 여부:** no

### x-f5xc-recommended-value

- **적용 위치:** schema property
- **목적:** 서버 기본값이 최적이 아닌 경우 필드에 대한 프로덕션 권장 값.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{}`
- **주입 주체:** scripts/utils/default_value_enricher.py
- **설정 기반:** config/discovered_defaults.yaml
- **예시:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **업스트림 패스스루 여부:** no

### x-f5xc-recommended-oneof-variant

- **적용 위치:** schema property
- **목적:** `oneOf` 블록에서 권장되는 변형을 나타냅니다.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/default_value_enricher.py
- **설정 기반:** config/discovered_defaults.yaml
- **예시:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **업스트림 패스스루 여부:** no

### x-f5xc-conflicts-with

- **적용 위치:** schema property
- **목적:** 이 속성과 함께 설정할 수 없는 형제 속성을 나열합니다.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/conflicts_with_enricher.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-requires

- **적용 위치:** schema property
- **목적:** 한 필드가 다른 필드의 설정을 필요로 하는 교차 필드 의존성을 문서화합니다.
- **소비자:** compile_catalog.py, xcsh CLI
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **주입 주체:** scripts/utils/dependency_enricher.py
- **설정 기반:** config/minimum_configs.yaml (dependencies 섹션)
- **예시:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **업스트림 패스스루 여부:** no

### x-f5xc-constraints

- **적용 위치:** schema property
- **목적:** 라이브 API 프로빙 또는 정적 패턴에서 파생된 숫자/문자열 제약 조건.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/constraint_enricher.py
- **설정 기반:** config/constraint_patterns.yaml
- **예시:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **업스트림 패스스루 여부:** no

### x-f5xc-uniqueness

- **적용 위치:** schema property
- **목적:** 필드가 해당 범위 내에서 고유해야 하는지 선언합니다.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/uniqueness_enricher.py
- **설정 기반:** hardcoded
- **예시:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **업스트림 패스스루 여부:** no

## 주입됨 — 오퍼레이션 수준

### x-f5xc-required-fields

- **적용 위치:** operation
- **목적:** 성공적인 실행을 위해 제공해야 하는 오퍼레이션 본문 필드를 명시합니다.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/operation_metadata_enricher.py
- **설정 기반:** config/operation_metadata.yaml
- **예시:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-danger-level

- **적용 위치:** operation
- **목적:** 오퍼레이션의 영향 범위를 분류합니다 (low/medium/high/critical).
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **주입 주체:** scripts/utils/operation_metadata_enricher.py
- **설정 기반:** config/operation_metadata.yaml
- **예시:** `"x-f5xc-danger-level": "high"`
- **업스트림 패스스루 여부:** no

### x-f5xc-confirmation-required

- **적용 위치:** operation
- **목적:** CLI/UI가 실행 전에 사용자에게 확인을 요청해야 하는지 여부.
- **소비자:** multiple
- **값 타입:** boolean
- **값 스키마:** `{"type": "boolean"}`
- **주입 주체:** scripts/utils/operation_metadata_enricher.py
- **설정 기반:** config/operation_metadata.yaml
- **예시:** `"x-f5xc-confirmation-required": true`
- **업스트림 패스스루 여부:** no

### x-f5xc-side-effects

- **적용 위치:** operation
- **목적:** 오퍼레이션의 관찰 가능한 부작용을 나열합니다 (재시작, 재구성 등).
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/utils/operation_metadata_enricher.py
- **설정 기반:** config/operation_metadata.yaml
- **예시:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-discovered-response-time

- **적용 위치:** operation
- **목적:** 디스커버리 중 이 오퍼레이션에 대해 실험적으로 측정된 응답 시간.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery_enrichment.yaml
- **예시:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **업스트림 패스스루 여부:** no

### x-f5xc-discovered-rate-limits

- **적용 위치:** operation
- **목적:** 라이브 API에서 확인된 속도 제한 헤더/동작.
- **소비자:** multiple
- **값 타입:** object
- **값 스키마:** `{"type": "object"}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery_enrichment.yaml
- **예시:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **업스트림 패스스루 여부:** no

### x-f5xc-discovered-error-catalog

- **적용 위치:** operation
- **목적:** 라이브 디스커버리 중 관찰된 오류 응답 카탈로그 (샘플 페이로드 포함).
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "object"}}`
- **주입 주체:** scripts/utils/discovery_enricher.py
- **설정 기반:** config/discovery_enrichment.yaml
- **예시:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **업스트림 패스스루 여부:** no

## 주입됨 — 인덱스 수준 (도메인 메타데이터)

### x-f5xc-category

- **적용 위치:** info
- **목적:** 도메인의 최상위 CLI / UI / 문서 / Terraform 그룹화 카테고리.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-category": "networking"`
- **업스트림 패스스루 여부:** no

### x-f5xc-primary-resources

- **적용 위치:** info
- **목적:** 도메인을 정의하는 기본 리소스 타입 목록.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-critical-resources

- **적용 위치:** info
- **목적:** 높은 수준의 주의가 필요한 리소스 (프로덕션 중요).
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/critical_resources.yaml
- **예시:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-description-short

- **적용 위치:** info
- **목적:** 짧은 (~60자) 도메인 설명. 긴 설명이 있는 속성 수준에도 적용됩니다.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/property_description_short_enricher.py
- **설정 기반:** config/property_description_short.yaml
- **예시:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **업스트림 패스스루 여부:** no

### x-f5xc-description-medium

- **적용 위치:** info
- **목적:** 중간 길이 (~150자) 도메인 설명. 속성 수준에도 적용됩니다.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/property_description_short_enricher.py
- **설정 기반:** config/property_description_short.yaml
- **예시:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **업스트림 패스스루 여부:** no

### x-f5xc-description-long

- **적용 위치:** info
- **목적:** 긴 (~500자) 도메인 설명.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/utils/description_enricher.py
- **설정 기반:** config/domain_descriptions.yaml
- **예시:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **업스트림 패스스루 여부:** no

### x-f5xc-complexity

- **적용 위치:** info
- **목적:** 이 도메인에서 구성을 작성하기 위한 상대적 복잡도 등급.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-complexity": "medium"`
- **업스트림 패스스루 여부:** no

### x-f5xc-requires-tier

- **적용 위치:** info
- **목적:** 필요한 최소 F5 XC 구독 등급.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-requires-tier": "enterprise"`
- **업스트림 패스스루 여부:** no

### x-f5xc-is-preview

- **적용 위치:** info
- **목적:** 도메인을 프리뷰 / 베타 기능으로 표시합니다.
- **소비자:** multiple
- **값 타입:** boolean
- **값 스키마:** `{"type": "boolean"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-is-preview": false`
- **업스트림 패스스루 여부:** no

### x-f5xc-use-cases

- **적용 위치:** info
- **목적:** 이 도메인이 지원하는 명명된 사용 사례.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-icon

- **적용 위치:** info
- **목적:** UI에서 이 도메인을 렌더링할 때 사용할 아이콘 식별자.
- **소비자:** Web UI
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **업스트림 패스스루 여부:** no

### x-f5xc-logo-svg

- **적용 위치:** info
- **목적:** 도메인을 나타내는 브랜드 로고의 인라인 SVG (또는 경로).
- **소비자:** Web UI
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **업스트림 패스스루 여부:** no

### x-f5xc-related-domains

- **적용 위치:** info
- **목적:** 이 도메인과 함께 자주 사용되는 다른 도메인에 대한 교차 링크.
- **소비자:** multiple
- **값 타입:** array
- **값 스키마:** `{"type": "array", "items": {"type": "string"}}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **업스트림 패스스루 여부:** no

### x-f5xc-doc-section

- **적용 위치:** info
- **목적:** 렌더링된 문서의 문서 섹션 / 네비게이션 그룹화 슬러그.
- **소비자:** multiple
- **값 타입:** string
- **값 스키마:** `{"type": "string"}`
- **주입 주체:** scripts/merge_specs.py
- **설정 기반:** config/domain_patterns.yaml
- **예시:** `"x-f5xc-doc-section": "load-balancing"`
- **업스트림 패스스루 여부:** no

## 업스트림 패스스루

### x-ves-proto-package

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **업스트림 패스스루 여부:** yes

### x-ves-proto-file

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **업스트림 패스스루 여부:** yes

### x-ves-proto-message

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **업스트림 패스스루 여부:** yes

### x-ves-proto-service

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **업스트림 패스스루 여부:** yes

### x-ves-proto-rpc

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **업스트림 패스스루 여부:** yes

### x-displayname

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** `"x-displayname": "Namespace"`
- **업스트림 패스스루 여부:** yes

### x-ves-oneof

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** F5 업스트림 문서를 참조하세요.
- **업스트림 패스스루 여부:** yes

### x-ves-default

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** F5 업스트림 문서를 참조하세요.
- **업스트림 패스스루 여부:** yes

### x-ves-required

- **적용 위치:** upstream
- **목적:** F5 업스트림 명세에서 변경 없이 보존됨.
- **소비자:** N/A
- **값 타입:** varies
- **값 스키마:** N/A
- **주입 주체:** upstream
- **설정 기반:** upstream
- **예시:** F5 업스트림 문서를 참조하세요.
- **업스트림 패스스루 여부:** yes
