---
title: แคตตาล็อกส่วนขยายการเพิ่มประสิทธิภาพ
description: >-
  แหล่งข้อมูลหลักสำหรับส่วนขยาย x-* ทุกรายการในข้อกำหนด OpenAPI
  ที่เพิ่มประสิทธิภาพแล้ว
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# แคตตาล็อกส่วนขยายการเพิ่มประสิทธิภาพ

แหล่งข้อมูลหลักสำหรับส่วนขยาย `x-*` ทุกรายการที่ปรากฏใน
`docs/specifications/api/*.json` ความสอดคล้องกับ
`scripts/utils/extension_constants.py` ถูกบังคับใช้โดย
`tests/test_extension_catalog.py`

ส่วนขยายสามประเภทได้รับการจัดทำเอกสารไว้ที่นี่:

- **ฉีดเข้าที่นี่** — ส่วนขยายที่ตัวเพิ่มประสิทธิภาพของเราเพิ่มเข้าไป (`x-f5xc-*` และ
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / ตัวแปรการค้นพบ)
  เหล่านี้คือส่วนขยายที่เครื่องมือปลายทางควรนำไปใช้
- **ส่งผ่านจากต้นทาง** — ส่วนขยายที่ F5 ส่งออกในข้อกำหนดต้นทางและเราเก็บรักษาไว้โดยไม่เปลี่ยนแปลง (`x-ves-proto-*`, `x-displayname` ฯลฯ)
  จัดทำเอกสารไว้เพื่อความโปร่งใสแต่ไม่ได้ควบคุมโดย repo นี้
- **จะฉีดในอนาคต** — ยังไม่ได้ส่งออก จะจัดทำเอกสารทันทีที่
  ตัวเพิ่มประสิทธิภาพเริ่มสร้าง (ไม่มีผลในการเติมข้อมูลครั้งแรก)

## รูปแบบรายการ

ทุกรายการด้านล่างมีรูปแบบดังนี้ การทดสอบความสอดคล้องใน
`tests/test_extension_catalog.py` ยอมรับให้เนื้อหาส่วนนี้สั้นได้
ตราบใดที่หัวข้อ `### x-name` มีอยู่และ
แฟล็ก `Pass-through from upstream:` ระบุค่าเป็น `yes` หรือ `no`

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

## ฉีดเข้า — ระดับสเปค (ส่วน info)

### x-f5xc-cli-domain

- **Applied at:** info
- **Purpose:** ระบุสลัก CLI domain (เช่น `http_loadbalancer`) สำหรับสเปคที่เพิ่มประสิทธิภาพแล้ว
- **Consumers:** CLI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-cli-metadata

- **Applied at:** info
- **Purpose:** บล็อกข้อมูลเมตาสำหรับ CLI ทั้งระบบ (ชื่อเครื่องมือ, คำแนะนำเวอร์ชัน, การจัดกลุ่ม domain)
- **Consumers:** CLI
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/cli_metadata.yaml
- **Example:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Pass-through from upstream:** no

### x-f5xc-upstream-timestamp

- **Applied at:** info
- **Purpose:** การประทับเวลาของสเปคต้นทางที่ใช้สร้างไฟล์ที่เพิ่มประสิทธิภาพแล้ว
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "date-time"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-upstream-etag

- **Applied at:** info
- **Purpose:** ETag ของ asset รีลีสสเปคต้นทาง
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Pass-through from upstream:** no

### x-f5xc-enriched-version

- **Applied at:** info
- **Purpose:** เวอร์ชัน Semantic ที่ประทับไว้บนสเปคที่เพิ่มประสิทธิภาพแล้วโดย pipeline
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-enriched-version": "3.2.1"`
- **Pass-through from upstream:** no

### x-f5xc-glossary

- **Applied at:** info
- **Purpose:** บล็อกคำศัพท์การสร้างแบรนด์/คำศัพท์เทคนิคที่ใช้กับแต่ละสเปค domain
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/branding.py
- **Driven by config:** config/branding.yaml
- **Example:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-at

- **Applied at:** info
- **Purpose:** การประทับเวลาเมื่อรันการค้นพบ live-API
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "date-time"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-api-url

- **Applied at:** info
- **Purpose:** URL พื้นฐานของ live API ที่ถูกตรวจสอบระหว่างการค้นพบ
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "uri"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Pass-through from upstream:** no

### x-f5xc-api-reference-url

- **Applied at:** info
- **Purpose:** URL ไปยังหน้าเอกสารอ้างอิง API ที่โฮสต์ไว้สำหรับ domain นี้
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "uri"}`
- **Injected by:** scripts/utils/external_docs_enricher.py
- **Driven by config:** none (derived from domain name)
- **Example:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Pass-through from upstream:** no

### x-f5xc-response-time-ms

- **Applied at:** info
- **Purpose:** เวลาตอบสนองที่สังเกตได้ (มิลลิวินาที) สำหรับ API ที่ถูกตรวจสอบระหว่างการค้นพบ
- **Consumers:** multiple
- **Value type:** number
- **Value schema:** `{"type": "number"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-response-time-ms": 42`
- **Pass-through from upstream:** no

### x-f5xc-best-practices

- **Applied at:** info
- **Purpose:** คำแนะนำแนวปฏิบัติที่ดีที่สุดสำหรับ domain
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/best_practices_enricher.py
- **Driven by config:** config/best_practices.yaml
- **Example:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Pass-through from upstream:** no

### x-f5xc-guided-workflows

- **Applied at:** info
- **Purpose:** เวิร์กโฟลว์แบบขั้นตอนที่มีชื่อสำหรับการดำเนินงานทั่วไปใน domain
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/guided_workflow_enricher.py
- **Driven by config:** config/guided_workflows.yaml
- **Example:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Pass-through from upstream:** no

### x-f5xc-acronyms

- **Applied at:** info
- **Purpose:** ตารางขยายคำย่อเฉพาะ domain
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Injected by:** scripts/utils/acronym_enricher.py
- **Driven by config:** config/acronyms.yaml
- **Example:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Pass-through from upstream:** no

## ฉีดเข้า — ระดับ schema (component schemas)

### x-f5xc-minimum-configuration

- **Applied at:** schema
- **Purpose:** ชุดฟิลด์ขั้นต่ำที่จำเป็นสำหรับการ POST/PUT ทรัพยากรนี้ให้สำเร็จ
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/minimum_configuration_enricher.py
- **Driven by config:** config/minimum_configs.yaml
- **Example:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Pass-through from upstream:** no

### x-f5xc-namespace-profile

- **Applied at:** info
- **Purpose:** ให้ข้อมูลเมตาเกี่ยวกับข้อจำกัด, คำแนะนำ และการจำแนกประเภท namespace สำหรับทรัพยากร
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Injected by:** scripts/utils/namespace_profile_enricher.py
- **Driven by config:** config/namespace_profile.yaml
- **Example:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Pass-through from upstream:** no

### x-f5xc-displayorder

- **Applied at:** schema
- **Purpose:** ลำดับที่แนะนำของ properties สำหรับการแสดงผลใน UI/CLI
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Pass-through from upstream:** no

### x-f5xc-terraform-resource

- **Applied at:** schema
- **Purpose:** ชื่อประเภท Terraform resource ที่แมปกับ schema นี้
- **Consumers:** Terraform
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-display-name

- **Applied at:** schema
- **Purpose:** ชื่อที่แสดงอ่านได้สำหรับมนุษย์สำหรับ resource schema (แทนที่การสร้างอัตโนมัติ)
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Pass-through from upstream:** no

## ฉีดเข้า — ระดับ property

### x-f5xc-description

- **Applied at:** schema property
- **Purpose:** คำอธิบาย property ที่เพิ่มประสิทธิภาพซึ่งเสริม `description` จากต้นทาง
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_descriptions.yaml
- **Example:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Pass-through from upstream:** no

### x-f5xc-validation

- **Applied at:** schema property
- **Purpose:** กฎการตรวจสอบแบบ Declarative ที่ได้จาก `ves.io.schema.rules` ของ protobuf ต้นทาง
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/validation_enricher.py
- **Driven by config:** config/validation_rules.yaml
- **Example:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Pass-through from upstream:** no

### x-f5xc-examples

- **Applied at:** schema property
- **Purpose:** ค่าตัวอย่างหลายรายการสำหรับ property
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array"}`
- **Injected by:** scripts/utils/resource_examples_enricher.py
- **Driven by config:** config/resource_examples.yaml
- **Example:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Pass-through from upstream:** no

### x-f5xc-example

- **Applied at:** schema property
- **Purpose:** ค่าตัวอย่างมาตรฐานเดียว
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/field_description_enricher.py
- **Driven by config:** config/field_descriptions.yaml
- **Example:** `"x-f5xc-example": "example.com"`
- **Pass-through from upstream:** no

### x-f5xc-completion

- **Applied at:** schema property
- **Purpose:** คำแนะนำสำหรับการเติมข้อความ shell (enum แบบ static หรือคำสั่งแบบ dynamic)
- **Consumers:** CLI
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Pass-through from upstream:** no

### x-f5xc-defaults

- **Applied at:** schema property
- **Purpose:** ค่าเริ่มต้นที่แสดงในเอกสารที่สร้างขึ้นและ UI
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-defaults": {"value": "default"}`
- **Pass-through from upstream:** no

### x-f5xc-required-for-operations

- **Applied at:** schema property
- **Purpose:** แสดงรายการ HTTP operations (POST/PUT/...) ที่ต้องการ property นี้
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Pass-through from upstream:** no

### x-f5xc-required-for

- **Applied at:** schema property
- **Purpose:** แสดงรายการชุดฟีเจอร์ที่มีชื่อซึ่งต้องการ property นี้
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/minimum_configuration_enricher.py
- **Driven by config:** config/minimum_configs.yaml
- **Example:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Pass-through from upstream:** no

### x-f5xc-conditions

- **Applied at:** schema property
- **Purpose:** ข้อกำหนดแบบมีเงื่อนไข (เช่น จำเป็นเมื่อฟิลด์ข้างเคียงมีค่าเท่ากับ X)
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Pass-through from upstream:** no

### x-f5xc-deprecated

- **Applied at:** schema property
- **Purpose:** ประกาศการเลิกใช้พร้อมคำแนะนำทางเลือกแทน
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Pass-through from upstream:** no

### x-f5xc-server-default

- **Applied at:** schema property
- **Purpose:** ค่าเริ่มต้นที่เซิร์ฟเวอร์กำหนดเมื่อ client ละเว้น property
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-value

- **Applied at:** schema property
- **Purpose:** ค่าที่แนะนำสำหรับการใช้งานจริงสำหรับฟิลด์ที่ค่าเริ่มต้นของเซิร์ฟเวอร์ไม่เหมาะสม
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-oneof-variant

- **Applied at:** schema property
- **Purpose:** สำหรับบล็อก `oneOf` ระบุว่าตัวแปรใดที่แนะนำ
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Pass-through from upstream:** no

### x-f5xc-conflicts-with

- **Applied at:** schema property
- **Purpose:** แสดงรายการ properties ข้างเคียงที่ไม่สามารถตั้งค่าพร้อมกับ property นี้ได้
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/conflicts_with_enricher.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Pass-through from upstream:** no

### x-f5xc-requires

- **Applied at:** schema property
- **Purpose:** จัดทำเอกสารการพึ่งพาข้ามฟิลด์ซึ่งฟิลด์หนึ่งต้องการให้อีกฟิลด์หนึ่งถูกตั้งค่า
- **Consumers:** compile_catalog.py, xcsh CLI
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Injected by:** scripts/utils/dependency_enricher.py
- **Driven by config:** config/minimum_configs.yaml (dependencies section)
- **Example:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Pass-through from upstream:** no

### x-f5xc-constraints

- **Applied at:** schema property
- **Purpose:** ข้อจำกัดตัวเลข / สตริงที่ได้จากการตรวจสอบ live-API หรือรูปแบบ static
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/constraint_enricher.py
- **Driven by config:** config/constraint_patterns.yaml
- **Example:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Pass-through from upstream:** no

### x-f5xc-uniqueness

- **Applied at:** schema property
- **Purpose:** ประกาศว่าฟิลด์ต้องมีค่าเฉพาะภายในขอบเขตของตัวหรือไม่
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/uniqueness_enricher.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Pass-through from upstream:** no

## ฉีดเข้า — ระดับ operation

### x-f5xc-required-fields

- **Applied at:** operation
- **Purpose:** ระบุชื่อฟิลด์ใน operation body ที่ต้องระบุเพื่อให้สำเร็จ
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Pass-through from upstream:** no

### x-f5xc-danger-level

- **Applied at:** operation
- **Purpose:** จำแนกระดับผลกระทบของ operation (low/medium/high/critical)
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-danger-level": "high"`
- **Pass-through from upstream:** no

### x-f5xc-confirmation-required

- **Applied at:** operation
- **Purpose:** ระบุว่า CLI/UI ควรแจ้งให้ผู้ใช้ยืนยันก่อนดำเนินการหรือไม่
- **Consumers:** multiple
- **Value type:** boolean
- **Value schema:** `{"type": "boolean"}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-confirmation-required": true`
- **Pass-through from upstream:** no

### x-f5xc-side-effects

- **Applied at:** operation
- **Purpose:** แสดงรายการผลข้างเคียงที่สังเกตได้จาก operation (restart, reconfigure ฯลฯ)
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Pass-through from upstream:** no

### x-f5xc-discovered-response-time

- **Applied at:** operation
- **Purpose:** เวลาตอบสนองที่วัดได้จากการทดลองจริงสำหรับ operation นี้ระหว่างการค้นพบ
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-rate-limits

- **Applied at:** operation
- **Purpose:** headers / พฤติกรรม rate-limit ที่สังเกตได้จาก live API
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-error-catalog

- **Applied at:** operation
- **Purpose:** แคตตาล็อกของการตอบสนองข้อผิดพลาดที่สังเกตได้ระหว่างการค้นพบสด พร้อม payload ตัวอย่าง
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Pass-through from upstream:** no

## ฉีดเข้า — ระดับ index (ข้อมูลเมตา domain)

### x-f5xc-category

- **Applied at:** info
- **Purpose:** หมวดหมู่การจัดกลุ่มระดับสูงสุดสำหรับ CLI / UI / เอกสาร / Terraform ของ domain
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-category": "networking"`
- **Pass-through from upstream:** no

### x-f5xc-primary-resources

- **Applied at:** info
- **Purpose:** รายการประเภททรัพยากรหลักที่กำหนด domain
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Pass-through from upstream:** no

### x-f5xc-critical-resources

- **Applied at:** info
- **Purpose:** ทรัพยากรที่ต้องการความระมัดระวังสูง (สำคัญต่อการใช้งานจริง)
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/critical_resources.yaml
- **Example:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-description-short

- **Applied at:** info
- **Purpose:** คำอธิบาย domain สั้น (~60 ตัวอักษร) ใช้ได้ที่ระดับ property สำหรับคำอธิบายยาวด้วย
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/property_description_short_enricher.py
- **Driven by config:** config/property_description_short.yaml
- **Example:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Pass-through from upstream:** no

### x-f5xc-description-medium

- **Applied at:** info
- **Purpose:** คำอธิบาย domain ระดับกลาง (~150 ตัวอักษร) ใช้ได้ที่ระดับ property ด้วย
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/property_description_short_enricher.py
- **Driven by config:** config/property_description_short.yaml
- **Example:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Pass-through from upstream:** no

### x-f5xc-description-long

- **Applied at:** info
- **Purpose:** คำอธิบาย domain แบบยาว (~500 ตัวอักษร)
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/description_enricher.py
- **Driven by config:** config/domain_descriptions.yaml
- **Example:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Pass-through from upstream:** no

### x-f5xc-complexity

- **Applied at:** info
- **Purpose:** ระดับความซับซ้อนสัมพัทธ์สำหรับการเขียนการกำหนดค่าใน domain นี้
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-complexity": "medium"`
- **Pass-through from upstream:** no

### x-f5xc-requires-tier

- **Applied at:** info
- **Purpose:** ระดับการสมัครใช้งาน F5 XC ขั้นต่ำที่ต้องการ
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-requires-tier": "enterprise"`
- **Pass-through from upstream:** no

### x-f5xc-is-preview

- **Applied at:** info
- **Purpose:** ทำเครื่องหมาย domain ว่าเป็นฟีเจอร์ preview / beta
- **Consumers:** multiple
- **Value type:** boolean
- **Value schema:** `{"type": "boolean"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-is-preview": false`
- **Pass-through from upstream:** no

### x-f5xc-use-cases

- **Applied at:** info
- **Purpose:** กรณีการใช้งานที่มีชื่อซึ่ง domain นี้รองรับ
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Pass-through from upstream:** no

### x-f5xc-icon

- **Applied at:** info
- **Purpose:** ตัวระบุไอคอนที่ใช้เมื่อแสดง domain นี้ใน UI
- **Consumers:** Web UI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Pass-through from upstream:** no

### x-f5xc-logo-svg

- **Applied at:** info
- **Purpose:** SVG แบบ inline (หรือ path) สำหรับโลโก้แบรนด์ที่แสดงถึง domain
- **Consumers:** Web UI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Pass-through from upstream:** no

### x-f5xc-related-domains

- **Applied at:** info
- **Purpose:** ลิงก์ข้ามไปยัง domain อื่นที่มักใช้ร่วมกับ domain นี้
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-doc-section

- **Applied at:** info
- **Purpose:** สลักส่วนเอกสาร / การจัดกลุ่มนำทางสำหรับเอกสารที่แสดงผล
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-doc-section": "load-balancing"`
- **Pass-through from upstream:** no

## ส่งผ่านจากต้นทาง

### x-ves-proto-package

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Pass-through from upstream:** yes

### x-ves-proto-file

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Pass-through from upstream:** yes

### x-ves-proto-message

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Pass-through from upstream:** yes

### x-ves-proto-service

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Pass-through from upstream:** yes

### x-ves-proto-rpc

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Pass-through from upstream:** yes

### x-displayname

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-displayname": "Namespace"`
- **Pass-through from upstream:** yes

### x-ves-oneof

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** ดูเอกสารต้นทาง F5
- **Pass-through from upstream:** yes

### x-ves-default

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** ดูเอกสารต้นทาง F5
- **Pass-through from upstream:** yes

### x-ves-required

- **Applied at:** upstream
- **Purpose:** เก็บรักษาไว้โดยไม่เปลี่ยนแปลงจากสเปคต้นทาง F5
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** ดูเอกสารต้นทาง F5
- **Pass-through from upstream:** yes
