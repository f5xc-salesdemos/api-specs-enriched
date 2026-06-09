---
title: فهرس امتدادات الإثراء
description: المرجع الأساسي لكل امتداد x-* في مواصفات OpenAPI المُثرَاة
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# فهرس امتدادات الإثراء

المرجع الأساسي لكل امتداد `x-*` يظهر في
`docs/specifications/api/*.json`. يتم فرض التطابق مع
`scripts/utils/extension_constants.py` بواسطة
`tests/test_extension_catalog.py`.

تم توثيق ثلاث فئات من الامتدادات هنا:

- **مُحقَنة هنا** — امتدادات تضيفها أدوات الإثراء الخاصة بنا (`x-f5xc-*` و
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / متغيرات
  الاكتشاف). هذه هي التي يجب أن تستهلكها الأدوات اللاحقة.
- **تمرير من المصدر الأصلي** — امتدادات تصدرها F5 في المواصفات المصدرية
  ونحافظ عليها دون تغيير (`x-ves-proto-*`، `x-displayname`، إلخ.).
  موثقة من أجل الشفافية لكن لا يتحكم بها هذا المستودع.
- **محقونة مستقبلاً** — لم تُصدَر بعد؛ يتم توثيقها هنا في اللحظة التي
  تبدأ فيها أداة إثراء بإنتاجها (لا ينطبق عند التعبئة الأولية).

## مخطط الإدخال

كل إدخال أدناه له هذا الشكل بالضبط. يتسامح اختبار التطابق في
`tests/test_extension_catalog.py` مع كون نص القسم مختصراً طالما أن
عنوان `### x-name` موجود وعلامة `Pass-through from upstream:`
حاضرة بقيمة `yes` أو `no`.

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

## محقونة — مستوى المواصفات (قسم info)

### x-f5xc-cli-domain

- **يُطبَّق على:** info
- **الغرض:** يحدد معرّف نطاق CLI (مثل `http_loadbalancer`) لمواصفة مُثرَاة.
- **المستهلكون:** CLI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-cli-metadata

- **يُطبَّق على:** info
- **الغرض:** كتلة بيانات وصفية على مستوى CLI (اسم الأداة، تلميحات الإصدار، تجميع النطاق).
- **المستهلكون:** CLI
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/cli_metadata.yaml
- **مثال:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-upstream-timestamp

- **يُطبَّق على:** info
- **الغرض:** الطابع الزمني لمواصفة المصدر الأصلي التي بُني منها الملف المُثرَى.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "date-time"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-upstream-etag

- **يُطبَّق على:** info
- **الغرض:** علامة ETag لأصل إصدار مواصفة المصدر الأصلي.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-enriched-version

- **يُطبَّق على:** info
- **الغرض:** إصدار دلالي يُختم على المواصفة المُثرَاة بواسطة خط الأنابيب.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-enriched-version": "3.2.1"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-glossary

- **يُطبَّق على:** info
- **الغرض:** كتلة مسرد العلامة التجارية/المصطلحات المطبقة على كل مواصفة نطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/branding.py
- **مُحرَّك بالتهيئة:** config/branding.yaml
- **مثال:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-discovered-at

- **يُطبَّق على:** info
- **الغرض:** الطابع الزمني لتنفيذ جولة اكتشاف واجهة API الحية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "date-time"}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery.yaml
- **مثال:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-api-url

- **يُطبَّق على:** info
- **الغرض:** عنوان URL الأساسي لواجهة API الحية التي تم فحصها أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "uri"}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery.yaml
- **مثال:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-api-reference-url

- **يُطبَّق على:** info
- **الغرض:** عنوان URL لصفحة توثيق مرجع API المستضافة لهذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "format": "uri"}`
- **يُحقن بواسطة:** scripts/utils/external_docs_enricher.py
- **مُحرَّك بالتهيئة:** لا يوجد (مُشتق من اسم النطاق)
- **مثال:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-response-time-ms

- **يُطبَّق على:** info
- **الغرض:** زمن الاستجابة المُلاحَظ (بالمللي ثانية) لواجهة API المفحوصة أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** number
- **مخطط القيمة:** `{"type": "number"}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery.yaml
- **مثال:** `"x-f5xc-response-time-ms": 42`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-best-practices

- **يُطبَّق على:** info
- **الغرض:** إرشادات أفضل الممارسات المنتقاة لنطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُحقن بواسطة:** scripts/utils/best_practices_enricher.py
- **مُحرَّك بالتهيئة:** config/best_practices.yaml
- **مثال:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-guided-workflows

- **يُطبَّق على:** info
- **الغرض:** سير عمل مُسمّاة خطوة بخطوة لإنجاز المهام الشائعة في نطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُحقن بواسطة:** scripts/utils/guided_workflow_enricher.py
- **مُحرَّك بالتهيئة:** config/guided_workflows.yaml
- **مثال:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-acronyms

- **يُطبَّق على:** info
- **الغرض:** جدول توسيع الاختصارات الخاص بكل نطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/acronym_enricher.py
- **مُحرَّك بالتهيئة:** config/acronyms.yaml
- **مثال:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **تمرير من المصدر الأصلي:** لا

## محقونة — مستوى المخطط (مخططات المكونات)

### x-f5xc-minimum-configuration

- **يُطبَّق على:** schema
- **الغرض:** الحد الأدنى من مجموعة الحقول القابلة للتطبيق المطلوبة لنجاح عملية POST/PUT لهذا المورد.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/minimum_configuration_enricher.py
- **مُحرَّك بالتهيئة:** config/minimum_configs.yaml
- **مثال:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-namespace-profile

- **يُطبَّق على:** info
- **الغرض:** يوفر بيانات وصفية لقيود مساحة الأسماء والتوصيات والتصنيف لمورد معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **يُحقن بواسطة:** scripts/utils/namespace_profile_enricher.py
- **مُحرَّك بالتهيئة:** config/namespace_profile.yaml
- **مثال:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-displayorder

- **يُطبَّق على:** schema
- **الغرض:** الترتيب المقترح للخصائص لعرضها في واجهة المستخدم/CLI.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-terraform-resource

- **يُطبَّق على:** schema
- **الغرض:** اسم نوع مورد Terraform الذي يُعيَّن لهذا المخطط.
- **المستهلكون:** Terraform
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-display-name

- **يُطبَّق على:** schema
- **الغرض:** اسم عرض مقروء للبشر لمخطط مورد (يتجاوز التوليد التلقائي).
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **تمرير من المصدر الأصلي:** لا

## محقونة — مستوى الخاصية

### x-f5xc-description

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** وصف مُثرَى للخاصية يُكمِّل `description` من المصدر الأصلي.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_descriptions.yaml
- **مثال:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-validation

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** قواعد تحقق تصريحية مُشتقة من `ves.io.schema.rules` الخاصة بـ protobuf من المصدر الأصلي.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/validation_enricher.py
- **مُحرَّك بالتهيئة:** config/validation_rules.yaml
- **مثال:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-examples

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** قيم أمثلة توضيحية متعددة لخاصية ما.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array"}`
- **يُحقن بواسطة:** scripts/utils/resource_examples_enricher.py
- **مُحرَّك بالتهيئة:** config/resource_examples.yaml
- **مثال:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-example

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** قيمة مثال قياسية واحدة.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُحقن بواسطة:** scripts/utils/field_description_enricher.py
- **مُحرَّك بالتهيئة:** config/field_descriptions.yaml
- **مثال:** `"x-f5xc-example": "example.com"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-completion

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** تلميحات إكمال Shell (قائمة ثابتة أو أمر ديناميكي).
- **المستهلكون:** CLI
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-defaults

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** القيمة/القيم الافتراضية لعرضها في التوثيق المُولَّد وواجهات المستخدم.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-defaults": {"value": "default"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-required-for-operations

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** يسرد عمليات HTTP (POST/PUT/...) التي تتطلب هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-required-for

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** يسرد مجموعات الميزات المُسمّاة التي تتطلب هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/minimum_configuration_enricher.py
- **مُحرَّك بالتهيئة:** config/minimum_configs.yaml
- **مثال:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-conditions

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** متطلبات شرطية (مثل مطلوبة عندما يساوي حقل شقيق القيمة X).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-deprecated

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** إشعار إهمال مع إرشادات البديل.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/field_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/field_metadata.yaml
- **مثال:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-server-default

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** القيمة الافتراضية التي يُعيِّنها الخادم عندما يحذف العميل الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُحقن بواسطة:** scripts/utils/default_value_enricher.py
- **مُحرَّك بالتهيئة:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-recommended-value

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** القيمة الموصى بها للإنتاج لحقل تكون فيه القيمة الافتراضية للخادم غير مثالية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{}`
- **يُحقن بواسطة:** scripts/utils/default_value_enricher.py
- **مُحرَّك بالتهيئة:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-recommended-oneof-variant

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** لكتل `oneOf`، يشير إلى المتغير الموصى به.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/default_value_enricher.py
- **مُحرَّك بالتهيئة:** config/discovered_defaults.yaml
- **مثال:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-conflicts-with

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** يسرد الخصائص الشقيقة التي لا يمكن تعيينها بجانب هذه الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/conflicts_with_enricher.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-requires

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** يوثق تبعيات الحقول المتقاطعة حيث يتطلب حقل ما تعيين حقل آخر.
- **المستهلكون:** compile_catalog.py، xcsh CLI
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **يُحقن بواسطة:** scripts/utils/dependency_enricher.py
- **مُحرَّك بالتهيئة:** config/minimum_configs.yaml (قسم التبعيات)
- **مثال:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-constraints

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** قيود رقمية / نصية مُشتقة من فحص واجهة API الحية أو أنماط ثابتة.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/constraint_enricher.py
- **مُحرَّك بالتهيئة:** config/constraint_patterns.yaml
- **مثال:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-uniqueness

- **يُطبَّق على:** خاصية المخطط
- **الغرض:** يُعلِن ما إذا كان الحقل يجب أن يكون فريداً ضمن نطاقه.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/uniqueness_enricher.py
- **مُحرَّك بالتهيئة:** مُضمَّن في الكود
- **مثال:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **تمرير من المصدر الأصلي:** لا

## محقونة — مستوى العملية

### x-f5xc-required-fields

- **يُطبَّق على:** operation
- **الغرض:** يُسمِّي حقول جسم العملية التي يجب توفيرها لنجاحها.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/operation_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-danger-level

- **يُطبَّق على:** operation
- **الغرض:** يُصنِّف نطاق تأثير العملية (منخفض/متوسط/مرتفع/حرج).
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **يُحقن بواسطة:** scripts/utils/operation_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-danger-level": "high"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-confirmation-required

- **يُطبَّق على:** operation
- **الغرض:** ما إذا كان يجب على CLI/واجهة المستخدم مطالبة المستخدم بالتأكيد قبل التنفيذ.
- **المستهلكون:** متعددون
- **نوع القيمة:** boolean
- **مخطط القيمة:** `{"type": "boolean"}`
- **يُحقن بواسطة:** scripts/utils/operation_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-confirmation-required": true`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-side-effects

- **يُطبَّق على:** operation
- **الغرض:** يسرد الآثار الجانبية الملاحظة للعملية (إعادة تشغيل، إعادة تهيئة، إلخ.).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/utils/operation_metadata_enricher.py
- **مُحرَّك بالتهيئة:** config/operation_metadata.yaml
- **مثال:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-discovered-response-time

- **يُطبَّق على:** operation
- **الغرض:** زمن الاستجابة المقاس تجريبياً لهذه العملية أثناء الاكتشاف.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-discovered-rate-limits

- **يُطبَّق على:** operation
- **الغرض:** ترويسات/سلوك تحديد المعدل الملاحظة من واجهة API الحية.
- **المستهلكون:** متعددون
- **نوع القيمة:** object
- **مخطط القيمة:** `{"type": "object"}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-discovered-error-catalog

- **يُطبَّق على:** operation
- **الغرض:** فهرس استجابات الأخطاء الملاحظة أثناء الاكتشاف الحي، مع حمولات عينة.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "object"}}`
- **يُحقن بواسطة:** scripts/utils/discovery_enricher.py
- **مُحرَّك بالتهيئة:** config/discovery_enrichment.yaml
- **مثال:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **تمرير من المصدر الأصلي:** لا

## محقونة — مستوى الفهرس (بيانات النطاق الوصفية)

### x-f5xc-category

- **يُطبَّق على:** info
- **الغرض:** فئة التجميع العليا لـ CLI / واجهة المستخدم / التوثيق / Terraform لنطاق معين.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-category": "networking"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-primary-resources

- **يُطبَّق على:** info
- **الغرض:** قائمة أنواع الموارد الأساسية التي تُعرِّف النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-critical-resources

- **يُطبَّق على:** info
- **الغرض:** الموارد التي تتطلب عناية مرتفعة (حرجة للإنتاج).
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/critical_resources.yaml
- **مثال:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-description-short

- **يُطبَّق على:** info
- **الغرض:** وصف قصير (~60 حرف) للنطاق. ينطبق أيضاً على مستوى الخاصية للأوصاف الطويلة.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/property_description_short_enricher.py
- **مُحرَّك بالتهيئة:** config/property_description_short.yaml
- **مثال:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-description-medium

- **يُطبَّق على:** info
- **الغرض:** وصف متوسط (~150 حرف) للنطاق. ينطبق أيضاً على مستوى الخاصية.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/property_description_short_enricher.py
- **مُحرَّك بالتهيئة:** config/property_description_short.yaml
- **مثال:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-description-long

- **يُطبَّق على:** info
- **الغرض:** وصف طويل (~500 حرف) للنطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/utils/description_enricher.py
- **مُحرَّك بالتهيئة:** config/domain_descriptions.yaml
- **مثال:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-complexity

- **يُطبَّق على:** info
- **الغرض:** مستوى التعقيد النسبي لتأليف التهيئات في هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-complexity": "medium"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-requires-tier

- **يُطبَّق على:** info
- **الغرض:** الحد الأدنى من مستوى اشتراك F5 XC المطلوب.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-requires-tier": "enterprise"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-is-preview

- **يُطبَّق على:** info
- **الغرض:** يُعلِّم النطاق كميزة معاينة / تجريبية.
- **المستهلكون:** متعددون
- **نوع القيمة:** boolean
- **مخطط القيمة:** `{"type": "boolean"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-is-preview": false`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-use-cases

- **يُطبَّق على:** info
- **الغرض:** حالات الاستخدام المُسمّاة التي يدعمها هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-icon

- **يُطبَّق على:** info
- **الغرض:** معرّف الأيقونة المُستخدم عند عرض هذا النطاق في واجهة المستخدم.
- **المستهلكون:** Web UI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-logo-svg

- **يُطبَّق على:** info
- **الغرض:** SVG مضمّن (أو مسار) لشعار العلامة التجارية الذي يمثل النطاق.
- **المستهلكون:** Web UI
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-related-domains

- **يُطبَّق على:** info
- **الغرض:** روابط متقاطعة لنطاقات أخرى تُستخدم عادةً مع هذا النطاق.
- **المستهلكون:** متعددون
- **نوع القيمة:** array
- **مخطط القيمة:** `{"type": "array", "items": {"type": "string"}}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **تمرير من المصدر الأصلي:** لا

### x-f5xc-doc-section

- **يُطبَّق على:** info
- **الغرض:** معرّف قسم التوثيق / تجميع التنقل للتوثيق المُعرَض.
- **المستهلكون:** متعددون
- **نوع القيمة:** string
- **مخطط القيمة:** `{"type": "string"}`
- **يُحقن بواسطة:** scripts/merge_specs.py
- **مُحرَّك بالتهيئة:** config/domain_patterns.yaml
- **مثال:** `"x-f5xc-doc-section": "load-balancing"`
- **تمرير من المصدر الأصلي:** لا

## التمرير من المصدر الأصلي

### x-ves-proto-package

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **تمرير من المصدر الأصلي:** نعم

### x-ves-proto-file

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **تمرير من المصدر الأصلي:** نعم

### x-ves-proto-message

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **تمرير من المصدر الأصلي:** نعم

### x-ves-proto-service

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **تمرير من المصدر الأصلي:** نعم

### x-ves-proto-rpc

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **تمرير من المصدر الأصلي:** نعم

### x-displayname

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** `"x-displayname": "Namespace"`
- **تمرير من المصدر الأصلي:** نعم

### x-ves-oneof

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** انظر توثيق F5 الأصلي.
- **تمرير من المصدر الأصلي:** نعم

### x-ves-default

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** انظر توثيق F5 الأصلي.
- **تمرير من المصدر الأصلي:** نعم

### x-ves-required

- **يُطبَّق على:** المصدر الأصلي
- **الغرض:** محفوظ دون تغيير من مواصفة F5 الأصلية.
- **المستهلكون:** غير متاح
- **نوع القيمة:** متنوع
- **مخطط القيمة:** غير متاح
- **يُحقن بواسطة:** المصدر الأصلي
- **مُحرَّك بالتهيئة:** المصدر الأصلي
- **مثال:** انظر توثيق F5 الأصلي.
- **تمرير من المصدر الأصلي:** نعم
