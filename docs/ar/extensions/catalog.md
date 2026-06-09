---
title: فهرس إضافات الإثراء
description: المرجع الموثوق لكل إضافة x-* في مواصفات OpenAPI المُثراة
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# فهرس إضافات الإثراء

المرجع الموثوق لكل إضافة `x-*` تظهر في
`docs/specifications/api/*.json`. يتم فرض التطابق مع
`scripts/utils/extension_constants.py` بواسطة
`tests/test_extension_catalog.py`.

ثلاث فئات من الإضافات موثقة هنا:

- **مُضافة هنا** — إضافات يضيفها المُثريون لدينا (`x-f5xc-*` و
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / متغيرات
  الاكتشاف). هذه هي التي يجب أن تستهلكها الأدوات النهائية.
- **تمرير من المنبع** — إضافات تصدرها F5 في المواصفات المصدرية
  ونحتفظ بها دون تغيير (`x-ves-proto-*`، `x-displayname`، إلخ.).
  موثقة من أجل الشفافية لكن لا يتحكم بها هذا المستودع.
- **مُضافة مستقبلاً** — لم تُصدر بعد؛ توثق هنا في اللحظة التي
  يبدأ فيها مُثرٍ بإنتاجها (لا ينطبق عند التعبئة الأولية).

## مخطط الإدخال

كل إدخال أدناه له هذا الشكل بالضبط. يتسامح اختبار التطابق في
`tests/test_extension_catalog.py` مع كون نص القسم مختصراً طالما أن
عنوان `### x-name` موجود وعلامة `Pass-through from upstream:` حاضرة
بقيمة `yes` أو `no`.

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

## مُضافة — على مستوى المواصفة (قسم info)

### x-f5xc-cli-domain

- **يُطبق على:** info
- **الغرض:** يحدد معرف نطاق CLI (مثل `http_loadbalancer`) لمواصفة مُثراة.
- **المستهلكون:** CLI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **تمرير من المنبع:** لا

### x-f5xc-cli-metadata

- **يُطبق على:** info
- **الغرض:** كتلة بيانات وصفية على مستوى CLI (اسم الأداة، تلميحات الإصدار، تجميع النطاق).
- **المستهلكون:** CLI
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/cli_metadata.yaml
- **مثال:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **تمرير من المنبع:** لا

### x-f5xc-upstream-timestamp

- **يُطبق على:** info
- **الغرض:** الطابع الزمني لمواصفة المنبع المصدرية التي بُني منها الملف المُثرى.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "date-time"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **تمرير من المنبع:** لا

### x-f5xc-upstream-etag

- **يُطبق على:** info
- **الغرض:** علامة ETag لأصل إصدار مواصفة المنبع المصدرية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **تمرير من المنبع:** لا

### x-f5xc-enriched-version

- **يُطبق على:** info
- **الغرض:** الإصدار الدلالي المختوم على المواصفة المُثراة بواسطة خط الأنابيب.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-enriched-version": "3.2.1"`
- **تمرير من المنبع:** لا

### x-f5xc-glossary

- **يُطبق على:** info
- **الغرض:** كتلة مسرد العلامة التجارية/المصطلحات المُطبقة على كل مواصفة نطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/branding.py
- **يُحدد بالإعداد:** config/branding.yaml
- **مثال:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **تمرير من المنبع:** لا

### x-f5xc-discovered-at

- **يُطبق على:** info
- **الغرض:** الطابع الزمني لوقت تنفيذ عملية اكتشاف API الحية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "date-time"}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery.yaml
- **مثال:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **تمرير من المنبع:** لا

### x-f5xc-api-url

- **يُطبق على:** info
- **الغرض:** عنوان URL الأساسي لواجهة API الحية التي تم فحصها أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "uri"}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery.yaml
- **مثال:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **تمرير من المنبع:** لا

### x-f5xc-api-reference-url

- **يُطبق على:** info
- **الغرض:** عنوان URL لصفحة وثائق مرجع API المستضافة لهذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "uri"}`
- **يُضاف بواسطة:** scripts/utils/external_docs_enricher.py
- **يُحدد بالإعداد:** لا شيء (مُشتق من اسم النطاق)
- **مثال:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **تمرير من المنبع:** لا

### x-f5xc-response-time-ms

- **يُطبق على:** info
- **الغرض:** زمن الاستجابة المُلاحظ (بالمللي ثانية) لواجهة API المفحوصة أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** number
- **مخطط القيمة:** `{"type": "number"}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery.yaml
- **مثال:** `"x-f5xc-response-time-ms": 42`
- **تمرير من المنبع:** لا

### x-f5xc-best-practices

- **يُطبق على:** info
- **الغرض:** إرشادات أفضل الممارسات المنتقاة لنطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُضاف بواسطة:** scripts/utils/best_practices_enricher.py
- **يُحدد بالإعداد:** config/best_practices.yaml
- **مثال:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **تمرير من المنبع:** لا

### x-f5xc-guided-workflows

- **يُطبق على:** info
- **الغرض:** سلاسل عمل مُسماة خطوة بخطوة لإنجاز المهام الشائعة في نطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُضاف بواسطة:** scripts/utils/guided_workflow_enricher.py
- **يُحدد بالإعداد:** config/guided_workflows.yaml
- **مثال:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **تمرير من المنبع:** لا

### x-f5xc-acronyms

- **يُطبق على:** info
- **الغرض:** جدول توسيع الاختصارات الخاص بكل نطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/acronym_enricher.py
- **يُحدد بالإعداد:** config/acronyms.yaml
- **مثال:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **تمرير من المنبع:** لا

## مُضافة — على مستوى المخطط (مخططات المكونات)

### x-f5xc-minimum-configuration

- **يُطبق على:** schema
- **الغرض:** الحد الأدنى من مجموعة الحقول المطلوبة لنجاح عملية POST/PUT لهذا المورد.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/minimum_configuration_enricher.py
- **يُحدد بالإعداد:** config/minimum_configs.yaml
- **مثال:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **تمرير من المنبع:** لا

### x-f5xc-namespace-profile

- **يُطبق على:** info
- **الغرض:** يوفر بيانات وصفية لقيود فضاء الأسماء والتوصيات والتصنيف لمورد ما.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **يُضاف بواسطة:** scripts/utils/namespace_profile_enricher.py
- **يُحدد بالإعداد:** config/namespace_profile.yaml
- **مثال:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **تمرير من المنبع:** لا

### x-f5xc-displayorder

- **يُطبق على:** schema
- **الغرض:** ترتيب مقترح للخصائص لعرضها في واجهة المستخدم/CLI.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **تمرير من المنبع:** لا

### x-f5xc-terraform-resource

- **يُطبق على:** schema
- **الغرض:** اسم نوع مورد Terraform الذي يُعين إلى هذا المخطط.
- **المستهلكون:** Terraform
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **تمرير من المنبع:** لا

### x-f5xc-display-name

- **يُطبق على:** schema
- **الغرض:** اسم عرض مقروء للبشر لمخطط مورد (يتجاوز التوليد التلقائي).
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **تمرير من المنبع:** لا

## مُضافة — على مستوى الخاصية

### x-f5xc-description

- **يُطبق على:** خاصية المخطط
- **الغرض:** وصف مُثرى للخاصية يُكمّل `description` القادم من المنبع.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_descriptions.yaml
- **مثال:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **تمرير من المنبع:** لا

### x-f5xc-validation

- **يُطبق على:** خاصية المخطط
- **الغرض:** قواعد تحقق تصريحية مُشتقة من `ves.io.schema.rules` في protobuf المنبع.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/validation_enricher.py
- **يُحدد بالإعداد:** config/validation_rules.yaml
- **مثال:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **تمرير من المنبع:** لا

### x-f5xc-examples

- **يُطبق على:** خاصية المخطط
- **الغرض:** قيم أمثلة توضيحية متعددة لخاصية ما.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array"}`
- **يُضاف بواسطة:** scripts/utils/resource_examples_enricher.py
- **يُحدد بالإعداد:** config/resource_examples.yaml
- **مثال:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **تمرير من المنبع:** لا

### x-f5xc-example

- **يُطبق على:** خاصية المخطط
- **الغرض:** قيمة مثال قانونية واحدة.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُضاف بواسطة:** scripts/utils/field_description_enricher.py
- **يُحدد بالإعداد:** config/field_descriptions.yaml
- **مثال:** `"x-f5xc-example": "example.com"`
- **تمرير من المنبع:** لا

### x-f5xc-completion

- **يُطبق على:** خاصية المخطط
- **الغرض:** تلميحات إكمال الأوامر في الصدفة (تعداد ثابت أو أمر ديناميكي).
- **المستهلكون:** CLI
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **تمرير من المنبع:** لا

### x-f5xc-defaults

- **يُطبق على:** خاصية المخطط
- **الغرض:** القيم الافتراضية لعرضها في الوثائق المُولدة وواجهات المستخدم.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-defaults": {"value": "default"}`
- **تمرير من المنبع:** لا

### x-f5xc-required-for-operations

- **يُطبق على:** خاصية المخطط
- **الغرض:** يسرد عمليات HTTP (POST/PUT/...) التي تتطلب هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **تمرير من المنبع:** لا

### x-f5xc-required-for

- **يُطبق على:** خاصية المخطط
- **الغرض:** يسرد تركيبات الميزات المُسماة التي تتطلب هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/minimum_configuration_enricher.py
- **يُحدد بالإعداد:** config/minimum_configs.yaml
- **مثال:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **تمرير من المنبع:** لا

### x-f5xc-conditions

- **يُطبق على:** خاصية المخطط
- **الغرض:** متطلبات شرطية (مثل: مطلوب عندما يساوي حقل شقيق القيمة X).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **تمرير من المنبع:** لا

### x-f5xc-deprecated

- **يُطبق على:** خاصية المخطط
- **الغرض:** إشعار إيقاف الاستخدام مع إرشادات البديل.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/field_metadata_enricher.py
- **يُحدد بالإعداد:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **تمرير من المنبع:** لا

### x-f5xc-server-default

- **يُطبق على:** خاصية المخطط
- **الغرض:** القيمة الافتراضية التي يعينها الخادم عندما يحذف العميل الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُضاف بواسطة:** scripts/utils/default_value_enricher.py
- **يُحدد بالإعداد:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **تمرير من المنبع:** لا

### x-f5xc-recommended-value

- **يُطبق على:** خاصية المخطط
- **الغرض:** القيمة الموصى بها للإنتاج لحقل تكون فيه القيمة الافتراضية للخادم غير مثالية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُضاف بواسطة:** scripts/utils/default_value_enricher.py
- **يُحدد بالإعداد:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **تمرير من المنبع:** لا

### x-f5xc-recommended-oneof-variant

- **يُطبق على:** خاصية المخطط
- **الغرض:** لكتل `oneOf`، يشير إلى المتغير الموصى به.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/default_value_enricher.py
- **يُحدد بالإعداد:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **تمرير من المنبع:** لا

### x-f5xc-conflicts-with

- **يُطبق على:** خاصية المخطط
- **الغرض:** يسرد الخصائص الشقيقة التي لا يمكن تعيينها بالتزامن مع هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/conflicts_with_enricher.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **تمرير من المنبع:** لا

### x-f5xc-requires

- **يُطبق على:** خاصية المخطط
- **الغرض:** يوثق التبعيات بين الحقول حيث يتطلب حقل ما تعيين حقل آخر.
- **المستهلكون:** compile_catalog.py، xcsh CLI
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **يُضاف بواسطة:** scripts/utils/dependency_enricher.py
- **يُحدد بالإعداد:** config/minimum_configs.yaml (قسم التبعيات)
- **مثال:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **تمرير من المنبع:** لا

### x-f5xc-constraints

- **يُطبق على:** خاصية المخطط
- **الغرض:** قيود رقمية / نصية مُشتقة من فحص API الحي أو أنماط ثابتة.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/constraint_enricher.py
- **يُحدد بالإعداد:** config/constraint_patterns.yaml
- **مثال:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **تمرير من المنبع:** لا

### x-f5xc-uniqueness

- **يُطبق على:** خاصية المخطط
- **الغرض:** يُصرح ما إذا كان يجب أن يكون الحقل فريداً ضمن نطاقه.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/uniqueness_enricher.py
- **يُحدد بالإعداد:** hardcoded
- **مثال:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **تمرير من المنبع:** لا

## مُضافة — على مستوى العملية

### x-f5xc-required-fields

- **يُطبق على:** operation
- **الغرض:** يُسمي حقول نص العملية التي يجب توفيرها للنجاح.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/operation_metadata_enricher.py
- **يُحدد بالإعداد:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **تمرير من المنبع:** لا

### x-f5xc-danger-level

- **يُطبق على:** operation
- **الغرض:** يصنف نطاق تأثير العملية (منخفض/متوسط/عالٍ/حرج).
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **يُضاف بواسطة:** scripts/utils/operation_metadata_enricher.py
- **يُحدد بالإعداد:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-danger-level": "high"`
- **تمرير من المنبع:** لا

### x-f5xc-confirmation-required

- **يُطبق على:** operation
- **الغرض:** ما إذا كان يجب على CLI/واجهة المستخدم مطالبة المستخدم بالتأكيد قبل التنفيذ.
- **المستهلكون:** متعددون
- **نوع القيمة:** boolean
- **مخطط القيمة:** `{"type": "boolean"}`
- **يُضاف بواسطة:** scripts/utils/operation_metadata_enricher.py
- **يُحدد بالإعداد:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-confirmation-required": true`
- **تمرير من المنبع:** لا

### x-f5xc-side-effects

- **يُطبق على:** operation
- **الغرض:** يسرد الآثار الجانبية الملاحظة للعملية (إعادة التشغيل، إعادة التكوين، إلخ.).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/utils/operation_metadata_enricher.py
- **يُحدد بالإعداد:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **تمرير من المنبع:** لا

### x-f5xc-discovered-response-time

- **يُطبق على:** operation
- **الغرض:** زمن الاستجابة المقاس تجريبياً لهذه العملية أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **تمرير من المنبع:** لا

### x-f5xc-discovered-rate-limits

- **يُطبق على:** operation
- **الغرض:** رؤوس/سلوك حدود المعدل المُلاحظة من واجهة API الحية.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **تمرير من المنبع:** لا

### x-f5xc-discovered-error-catalog

- **يُطبق على:** operation
- **الغرض:** فهرس استجابات الأخطاء المُلاحظة أثناء الاكتشاف الحي، مع حمولات نموذجية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُضاف بواسطة:** scripts/utils/discovery_enricher.py
- **يُحدد بالإعداد:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **تمرير من المنبع:** لا

## مُضافة — على مستوى الفهرس (بيانات النطاق الوصفية)

### x-f5xc-category

- **يُطبق على:** info
- **الغرض:** فئة التجميع العليا لـ CLI / واجهة المستخدم / الوثائق / Terraform لنطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-category": "networking"`
- **تمرير من المنبع:** لا

### x-f5xc-primary-resources

- **يُطبق على:** info
- **الغرض:** قائمة أنواع الموارد الأساسية التي تُعرّف النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **تمرير من المنبع:** لا

### x-f5xc-critical-resources

- **يُطبق على:** info
- **الغرض:** الموارد التي تتطلب عناية مرتفعة (حرجة للإنتاج).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/critical_resources.yaml
- **مثال:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **تمرير من المنبع:** لا

### x-f5xc-description-short

- **يُطبق على:** info
- **الغرض:** وصف قصير للنطاق (~60 حرفاً). يُطبق أيضاً على مستوى الخاصية للأوصاف الطويلة.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/property_description_short_enricher.py
- **يُحدد بالإعداد:** config/property_description_short.yaml
- **مثال:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **تمرير من المنبع:** لا

### x-f5xc-description-medium

- **يُطبق على:** info
- **الغرض:** وصف متوسط للنطاق (~150 حرفاً). يُطبق أيضاً على مستوى الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/property_description_short_enricher.py
- **يُحدد بالإعداد:** config/property_description_short.yaml
- **مثال:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **تمرير من المنبع:** لا

### x-f5xc-description-long

- **يُطبق على:** info
- **الغرض:** وصف طويل للنطاق (~500 حرف).
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/utils/description_enricher.py
- **يُحدد بالإعداد:** config/domain_descriptions.yaml
- **مثال:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **تمرير من المنبع:** لا

### x-f5xc-complexity

- **يُطبق على:** info
- **الغرض:** مستوى التعقيد النسبي لتأليف التكوينات في هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-complexity": "medium"`
- **تمرير من المنبع:** لا

### x-f5xc-requires-tier

- **يُطبق على:** info
- **الغرض:** الحد الأدنى لمستوى اشتراك F5 XC المطلوب.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-requires-tier": "enterprise"`
- **تمرير من المنبع:** لا

### x-f5xc-is-preview

- **يُطبق على:** info
- **الغرض:** يُعلّم نطاقاً كميزة معاينة / تجريبية.
- **المستهلكون:** متعددون
- **نوع القيمة:** boolean
- **مخطط القيمة:** `{"type": "boolean"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-is-preview": false`
- **تمرير من المنبع:** لا

### x-f5xc-use-cases

- **يُطبق على:** info
- **الغرض:** حالات الاستخدام المُسماة التي يدعمها هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **تمرير من المنبع:** لا

### x-f5xc-icon

- **يُطبق على:** info
- **الغرض:** معرف الأيقونة المستخدمة عند عرض هذا النطاق في واجهة المستخدم.
- **المستهلكون:** Web UI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **تمرير من المنبع:** لا

### x-f5xc-logo-svg

- **يُطبق على:** info
- **الغرض:** SVG مُضمن (أو مسار) لشعار العلامة التجارية الذي يمثل النطاق.
- **المستهلكون:** Web UI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **تمرير من المنبع:** لا

### x-f5xc-related-domains

- **يُطبق على:** info
- **الغرض:** روابط متقاطعة لنطاقات أخرى تُستخدم عادةً مع هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **تمرير من المنبع:** لا

### x-f5xc-doc-section

- **يُطبق على:** info
- **الغرض:** معرف قسم التوثيق / تجميع التنقل للوثائق المعروضة.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُضاف بواسطة:** scripts/merge_specs.py
- **يُحدد بالإعداد:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-doc-section": "load-balancing"`
- **تمرير من المنبع:** لا

## تمرير من المنبع

### x-ves-proto-package

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **تمرير من المنبع:** نعم

### x-ves-proto-file

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **تمرير من المنبع:** نعم

### x-ves-proto-message

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **تمرير من المنبع:** نعم

### x-ves-proto-service

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **تمرير من المنبع:** نعم

### x-ves-proto-rpc

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **تمرير من المنبع:** نعم

### x-displayname

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** `"x-displayname": "Namespace"`
- **تمرير من المنبع:** نعم

### x-ves-oneof

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** انظر وثائق F5 المنبع.
- **تمرير من المنبع:** نعم

### x-ves-default

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** انظر وثائق F5 المنبع.
- **تمرير من المنبع:** نعم

### x-ves-required

- **يُطبق على:** المنبع
- **الغرض:** محفوظ بدون تغيير من مواصفة F5 المنبع.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متغير
- **مخطط القيمة:** غير متاح
- **يُضاف بواسطة:** المنبع
- **يُحدد بالإعداد:** المنبع
- **مثال:** انظر وثائق F5 المنبع.
- **تمرير من المنبع:** نعم
