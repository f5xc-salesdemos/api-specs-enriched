---
title: แคตตาล็อกส่วนขยาย Enrichment
description: >-
  แหล่งข้อมูลหลักสำหรับทุกส่วนขยาย x-* ใน OpenAPI specifications
  ที่ผ่านการเสริมข้อมูล
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# แคตตาล็อกส่วนขยาย Enrichment

แหล่งข้อมูลหลักสำหรับทุกส่วนขยาย `x-*` ที่ปรากฏใน
`docs/specifications/api/*.json` ความสอดคล้องกับ
`scripts/utils/extension_constants.py` ถูกบังคับโดย
`tests/test_extension_catalog.py`

ส่วนขยายสามประเภทที่ถูกบันทึกไว้ที่นี่:

- **เพิ่มเข้ามาที่นี่** — ส่วนขยายที่ enrichers ของเราเพิ่มเข้ามา (`x-f5xc-*` และ
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / ตัวแปร
  discovery) เหล่านี้คือส่วนที่เครื่องมือปลายทางควรใช้งาน
- **ส่งผ่านจากต้นทาง** — ส่วนขยายที่ F5 ส่งมาในสเปกต้นทาง
  และเราคงไว้โดยไม่เปลี่ยนแปลง (`x-ves-proto-*`, `x-displayname` เป็นต้น)
  บันทึกเพื่อความโปร่งใสแต่ไม่ได้ควบคุมโดยรีโพนี้
- **จะเพิ่มในอนาคต** — ยังไม่ได้ส่งออก; บันทึกไว้ที่นี่ทันทีที่
  enricher เริ่มผลิตออกมา (ไม่เกี่ยวข้องในการเริ่มต้นครั้งแรก)

## โครงสร้างรายการ

ทุกรายการด้านล่างมีรูปแบบที่แน่นอนดังนี้ การทดสอบความสอดคล้องใน
`tests/test_extension_catalog.py` ยอมรับเนื้อหาส่วนที่สั้นได้ ตราบใดที่
ส่วนหัว `### x-name` มีอยู่และแฟล็ก
`Pass-through from upstream:` มีอยู่พร้อมค่า `yes` หรือ `no`

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

## เพิ่มเข้ามา — ระดับสเปก (ส่วน info)

### x-f5xc-cli-domain

- **ใช้ที่:** info
- **วัตถุประสงค์:** ระบุ CLI domain slug (เช่น `http_loadbalancer`) สำหรับสเปกที่ผ่านการเสริมข้อมูล
- **ผู้ใช้งาน:** CLI
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-cli-metadata

- **ใช้ที่:** info
- **วัตถุประสงค์:** บล็อกข้อมูลเมตาระดับ CLI (ชื่อเครื่องมือ, คำใบ้เวอร์ชัน, การจัดกลุ่มโดเมน)
- **ผู้ใช้งาน:** CLI
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/cli_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-upstream-timestamp

- **ใช้ที่:** info
- **วัตถุประสงค์:** ประทับเวลาของสเปกต้นทางที่ไฟล์เสริมข้อมูลถูกสร้างขึ้นมา
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "format": "date-time"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-upstream-etag

- **ใช้ที่:** info
- **วัตถุประสงค์:** ETag ของ release asset ของสเปกต้นทาง
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-enriched-version

- **ใช้ที่:** info
- **วัตถุประสงค์:** เวอร์ชันเชิงความหมายที่ประทับบนสเปกที่เสริมข้อมูลโดยไปป์ไลน์
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-enriched-version": "3.2.1"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-glossary

- **ใช้ที่:** info
- **วัตถุประสงค์:** บล็อกคำศัพท์แบรนด์/คำศัพท์เฉพาะทางที่ใช้กับสเปกแต่ละโดเมน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/branding.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/branding.yaml
- **ตัวอย่าง:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-discovered-at

- **ใช้ที่:** info
- **วัตถุประสงค์:** ประทับเวลาเมื่อดำเนินการค้นหา live-API discovery
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "format": "date-time"}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery.yaml
- **ตัวอย่าง:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-api-url

- **ใช้ที่:** info
- **วัตถุประสงค์:** URL ฐานของ live API ที่ถูกตรวจสอบระหว่างการค้นหา
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "format": "uri"}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery.yaml
- **ตัวอย่าง:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-api-reference-url

- **ใช้ที่:** info
- **วัตถุประสงค์:** URL ไปยังหน้าเอกสารอ้างอิง API ที่โฮสต์สำหรับโดเมนนี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "format": "uri"}`
- **เพิ่มโดย:** scripts/utils/external_docs_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** none (อนุมานจากชื่อโดเมน)
- **ตัวอย่าง:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-response-time-ms

- **ใช้ที่:** info
- **วัตถุประสงค์:** เวลาตอบสนองที่สังเกตได้ (มิลลิวินาที) สำหรับ API ที่ตรวจสอบระหว่างการค้นหา
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** number
- **สคีมาค่า:** `{"type": "number"}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery.yaml
- **ตัวอย่าง:** `"x-f5xc-response-time-ms": 42`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-best-practices

- **ใช้ที่:** info
- **วัตถุประสงค์:** คำแนะนำแนวปฏิบัติที่ดีที่สุดที่คัดสรรสำหรับโดเมน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "object"}}`
- **เพิ่มโดย:** scripts/utils/best_practices_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/best_practices.yaml
- **ตัวอย่าง:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-guided-workflows

- **ใช้ที่:** info
- **วัตถุประสงค์:** เวิร์กโฟลว์ทีละขั้นตอนที่มีชื่อเพื่อทำงานทั่วไปในโดเมนให้สำเร็จ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "object"}}`
- **เพิ่มโดย:** scripts/utils/guided_workflow_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/guided_workflows.yaml
- **ตัวอย่าง:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-acronyms

- **ใช้ที่:** info
- **วัตถุประสงค์:** ตารางขยายคำย่อเฉพาะโดเมน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/acronym_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/acronyms.yaml
- **ตัวอย่าง:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **ส่งผ่านจากต้นทาง:** no

## เพิ่มเข้ามา — ระดับสคีมา (component schemas)

### x-f5xc-minimum-configuration

- **ใช้ที่:** schema
- **วัตถุประสงค์:** ชุดฟิลด์ขั้นต่ำที่จำเป็นเพื่อ POST/PUT ทรัพยากรนี้สำเร็จ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/minimum_configuration_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/minimum_configs.yaml
- **ตัวอย่าง:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-namespace-profile

- **ใช้ที่:** info
- **วัตถุประสงค์:** ให้ข้อมูลเมตาเกี่ยวกับข้อจำกัด namespace, คำแนะนำ และการจำแนกประเภทสำหรับทรัพยากร
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **เพิ่มโดย:** scripts/utils/namespace_profile_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/namespace_profile.yaml
- **ตัวอย่าง:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-displayorder

- **ใช้ที่:** schema
- **วัตถุประสงค์:** ลำดับที่แนะนำของคุณสมบัติสำหรับการนำเสนอใน UI/CLI
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-terraform-resource

- **ใช้ที่:** schema
- **วัตถุประสงค์:** ชื่อประเภททรัพยากร Terraform ที่แมปกับสคีมานี้
- **ผู้ใช้งาน:** Terraform
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-display-name

- **ใช้ที่:** schema
- **วัตถุประสงค์:** ชื่อแสดงผลที่มนุษย์อ่านได้สำหรับสคีมาทรัพยากร (แทนที่การสร้างอัตโนมัติ)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **ส่งผ่านจากต้นทาง:** no

## เพิ่มเข้ามา — ระดับคุณสมบัติ

### x-f5xc-description

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** คำอธิบายคุณสมบัติที่เสริมข้อมูลเพื่อเสริม `description` จากต้นทาง
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_descriptions.yaml
- **ตัวอย่าง:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-validation

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** กฎการตรวจสอบความถูกต้องแบบประกาศที่ได้มาจาก `ves.io.schema.rules` ของ protobuf ต้นทาง
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/validation_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/validation_rules.yaml
- **ตัวอย่าง:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-examples

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ค่าตัวอย่างหลายค่าเพื่อแสดงประกอบสำหรับคุณสมบัติ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array"}`
- **เพิ่มโดย:** scripts/utils/resource_examples_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/resource_examples.yaml
- **ตัวอย่าง:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-example

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ค่าตัวอย่างมาตรฐานเดียว
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{}`
- **เพิ่มโดย:** scripts/utils/field_description_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_descriptions.yaml
- **ตัวอย่าง:** `"x-f5xc-example": "example.com"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-completion

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** คำใบ้การเติมคำอัตโนมัติสำหรับเชลล์ (enum คงที่หรือคำสั่งแบบไดนามิก)
- **ผู้ใช้งาน:** CLI
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-defaults

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ค่าเริ่มต้นที่จะแสดงในเอกสารที่สร้างขึ้นและ UIs
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-defaults": {"value": "default"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-required-for-operations

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** แสดงรายการการดำเนินการ HTTP (POST/PUT/...) ที่ต้องการคุณสมบัตินี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-required-for

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** แสดงรายการชุดฟีเจอร์ที่มีชื่อซึ่งต้องการคุณสมบัตินี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/minimum_configuration_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/minimum_configs.yaml
- **ตัวอย่าง:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-conditions

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ข้อกำหนดแบบมีเงื่อนไข (เช่น จำเป็นเมื่อฟิลด์ข้างเคียงมีค่าเท่ากับ X)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "object"}}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-deprecated

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ประกาศการเลิกใช้งานพร้อมคำแนะนำการแทนที่
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/field_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/field_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-server-default

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ค่าเริ่มต้นที่เซิร์ฟเวอร์กำหนดเมื่อไคลเอ็นต์ไม่ส่งคุณสมบัตินี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{}`
- **เพิ่มโดย:** scripts/utils/default_value_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovered_defaults.yaml
- **ตัวอย่าง:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-recommended-value

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ค่าที่แนะนำสำหรับการใช้งานจริงสำหรับฟิลด์ที่ค่าเริ่มต้นของเซิร์ฟเวอร์ไม่เหมาะสม
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{}`
- **เพิ่มโดย:** scripts/utils/default_value_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovered_defaults.yaml
- **ตัวอย่าง:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-recommended-oneof-variant

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** สำหรับบล็อก `oneOf` ระบุว่าตัวเลือกใดที่แนะนำ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/default_value_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovered_defaults.yaml
- **ตัวอย่าง:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-conflicts-with

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** แสดงรายการคุณสมบัติข้างเคียงที่ไม่สามารถตั้งค่าพร้อมกันได้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/conflicts_with_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-requires

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** บันทึกการพึ่งพาข้ามฟิลด์ที่ฟิลด์หนึ่งต้องการให้ฟิลด์อื่นถูกตั้งค่า
- **ผู้ใช้งาน:** compile_catalog.py, xcsh CLI
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **เพิ่มโดย:** scripts/utils/dependency_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/minimum_configs.yaml (ส่วน dependencies)
- **ตัวอย่าง:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-constraints

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ข้อจำกัดตัวเลข / สตริงที่ได้มาจากการตรวจสอบ live-API หรือรูปแบบคงที่
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/constraint_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/constraint_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-uniqueness

- **ใช้ที่:** schema property
- **วัตถุประสงค์:** ประกาศว่าฟิลด์ต้องไม่ซ้ำกันภายในขอบเขตของมัน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/uniqueness_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** hardcoded
- **ตัวอย่าง:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **ส่งผ่านจากต้นทาง:** no

## เพิ่มเข้ามา — ระดับการดำเนินการ

### x-f5xc-required-fields

- **ใช้ที่:** operation
- **วัตถุประสงค์:** ระบุชื่อฟิลด์ในเนื้อหาของการดำเนินการที่ต้องให้มาเพื่อให้สำเร็จ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/operation_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/operation_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-danger-level

- **ใช้ที่:** operation
- **วัตถุประสงค์:** จำแนกระดับผลกระทบของการดำเนินการ (low/medium/high/critical)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **เพิ่มโดย:** scripts/utils/operation_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/operation_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-danger-level": "high"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-confirmation-required

- **ใช้ที่:** operation
- **วัตถุประสงค์:** ระบุว่า CLI/UI ควรแจ้งให้ผู้ใช้ยืนยันก่อนดำเนินการหรือไม่
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** boolean
- **สคีมาค่า:** `{"type": "boolean"}`
- **เพิ่มโดย:** scripts/utils/operation_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/operation_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-confirmation-required": true`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-side-effects

- **ใช้ที่:** operation
- **วัตถุประสงค์:** แสดงรายการผลข้างเคียงที่สังเกตได้ของการดำเนินการ (restart, reconfigure เป็นต้น)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/utils/operation_metadata_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/operation_metadata.yaml
- **ตัวอย่าง:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-discovered-response-time

- **ใช้ที่:** operation
- **วัตถุประสงค์:** เวลาตอบสนองที่วัดได้จริงสำหรับการดำเนินการนี้ระหว่างการค้นหา
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery_enrichment.yaml
- **ตัวอย่าง:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-discovered-rate-limits

- **ใช้ที่:** operation
- **วัตถุประสงค์:** ส่วนหัว rate-limit / พฤติกรรมที่สังเกตได้จาก live API
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** object
- **สคีมาค่า:** `{"type": "object"}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery_enrichment.yaml
- **ตัวอย่าง:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-discovered-error-catalog

- **ใช้ที่:** operation
- **วัตถุประสงค์:** แคตตาล็อกของการตอบสนองข้อผิดพลาดที่สังเกตได้ระหว่างการค้นหาแบบสด พร้อม payload ตัวอย่าง
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "object"}}`
- **เพิ่มโดย:** scripts/utils/discovery_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/discovery_enrichment.yaml
- **ตัวอย่าง:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **ส่งผ่านจากต้นทาง:** no

## เพิ่มเข้ามา — ระดับดัชนี (ข้อมูลเมตาโดเมน)

### x-f5xc-category

- **ใช้ที่:** info
- **วัตถุประสงค์:** หมวดหมู่การจัดกลุ่มระดับบนสุดสำหรับ CLI / UI / เอกสาร / Terraform ของโดเมน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-category": "networking"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-primary-resources

- **ใช้ที่:** info
- **วัตถุประสงค์:** รายการประเภททรัพยากรหลักที่กำหนดโดเมน
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-critical-resources

- **ใช้ที่:** info
- **วัตถุประสงค์:** ทรัพยากรที่ต้องการการดูแลเป็นพิเศษ (สำคัญต่อการผลิต)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/critical_resources.yaml
- **ตัวอย่าง:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-description-short

- **ใช้ที่:** info
- **วัตถุประสงค์:** คำอธิบายโดเมนแบบสั้น (~60 ตัวอักษร) ใช้ได้ที่ระดับคุณสมบัติสำหรับคำอธิบายยาวด้วย
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/property_description_short_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/property_description_short.yaml
- **ตัวอย่าง:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-description-medium

- **ใช้ที่:** info
- **วัตถุประสงค์:** คำอธิบายโดเมนแบบกลาง (~150 ตัวอักษร) ใช้ได้ที่ระดับคุณสมบัติด้วย
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/property_description_short_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/property_description_short.yaml
- **ตัวอย่าง:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-description-long

- **ใช้ที่:** info
- **วัตถุประสงค์:** คำอธิบายโดเมนแบบยาว (~500 ตัวอักษร)
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/utils/description_enricher.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_descriptions.yaml
- **ตัวอย่าง:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-complexity

- **ใช้ที่:** info
- **วัตถุประสงค์:** ระดับความซับซ้อนสัมพัทธ์สำหรับการเขียนการกำหนดค่าในโดเมนนี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-complexity": "medium"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-requires-tier

- **ใช้ที่:** info
- **วัตถุประสงค์:** ระดับการสมัครสมาชิก F5 XC ขั้นต่ำที่ต้องการ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-requires-tier": "enterprise"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-is-preview

- **ใช้ที่:** info
- **วัตถุประสงค์:** ทำเครื่องหมายโดเมนว่าเป็นฟีเจอร์ตัวอย่าง / เบต้า
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** boolean
- **สคีมาค่า:** `{"type": "boolean"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-is-preview": false`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-use-cases

- **ใช้ที่:** info
- **วัตถุประสงค์:** กรณีการใช้งานที่มีชื่อซึ่งโดเมนนี้รองรับ
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-icon

- **ใช้ที่:** info
- **วัตถุประสงค์:** ตัวระบุไอคอนที่จะใช้เมื่อแสดงผลโดเมนนี้ใน UI
- **ผู้ใช้งาน:** Web UI
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-logo-svg

- **ใช้ที่:** info
- **วัตถุประสงค์:** SVG แบบอินไลน์ (หรือเส้นทาง) สำหรับโลโก้แบรนด์ที่เป็นตัวแทนของโดเมน
- **ผู้ใช้งาน:** Web UI
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-related-domains

- **ใช้ที่:** info
- **วัตถุประสงค์:** ลิงก์ข้ามไปยังโดเมนอื่นที่มักใช้ร่วมกันกับโดเมนนี้
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** array
- **สคีมาค่า:** `{"type": "array", "items": {"type": "string"}}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **ส่งผ่านจากต้นทาง:** no

### x-f5xc-doc-section

- **ใช้ที่:** info
- **วัตถุประสงค์:** ส่วนเอกสาร / slug การจัดกลุ่มเมนูนำทางสำหรับเอกสารที่แสดงผล
- **ผู้ใช้งาน:** multiple
- **ประเภทค่า:** string
- **สคีมาค่า:** `{"type": "string"}`
- **เพิ่มโดย:** scripts/merge_specs.py
- **ขับเคลื่อนโดยการกำหนดค่า:** config/domain_patterns.yaml
- **ตัวอย่าง:** `"x-f5xc-doc-section": "load-balancing"`
- **ส่งผ่านจากต้นทาง:** no

## ส่งผ่านจากต้นทาง

### x-ves-proto-package

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-proto-file

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-proto-message

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-proto-service

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-proto-rpc

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **ส่งผ่านจากต้นทาง:** yes

### x-displayname

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** `"x-displayname": "Namespace"`
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-oneof

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** ดูเอกสารต้นทางของ F5
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-default

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** ดูเอกสารต้นทางของ F5
- **ส่งผ่านจากต้นทาง:** yes

### x-ves-required

- **ใช้ที่:** upstream
- **วัตถุประสงค์:** คงไว้โดยไม่เปลี่ยนแปลงจากสเปกต้นทางของ F5
- **ผู้ใช้งาน:** N/A
- **ประเภทค่า:** varies
- **สคีมาค่า:** N/A
- **เพิ่มโดย:** upstream
- **ขับเคลื่อนโดยการกำหนดค่า:** upstream
- **ตัวอย่าง:** ดูเอกสารต้นทางของ F5
- **ส่งผ่านจากต้นทาง:** yes
