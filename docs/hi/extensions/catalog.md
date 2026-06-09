---
title: एनरिचमेंट एक्सटेंशन कैटलॉग
description: एनरिच्ड OpenAPI स्पेसिफिकेशन में प्रत्येक x-* एक्सटेंशन का आधिकारिक स्रोत
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# एनरिचमेंट एक्सटेंशन कैटलॉग

`docs/specifications/api/*.json` में दिखने वाले प्रत्येक `x-*` एक्सटेंशन का आधिकारिक स्रोत।
`scripts/utils/extension_constants.py` के साथ समानता
`tests/test_extension_catalog.py` द्वारा लागू की जाती है।

यहाँ तीन प्रकार के एक्सटेंशन प्रलेखित हैं:

- **यहाँ इंजेक्ट किए गए** — वे एक्सटेंशन जो हमारे एनरिचर्स जोड़ते हैं (`x-f5xc-*` और
  `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / डिस्कवरी
  वेरिएंट)। डाउनस्ट्रीम टूल्स को इन्हीं का उपभोग करना चाहिए।
- **अपस्ट्रीम पास-थ्रू** — वे एक्सटेंशन जो F5 सोर्स स्पेक्स में उत्सर्जित करता है
  और हम बिना बदलाव के संरक्षित रखते हैं (`x-ves-proto-*`, `x-displayname`, आदि)।
  पारदर्शिता के लिए प्रलेखित लेकिन इस रिपॉजिटरी द्वारा नियंत्रित नहीं।
- **भविष्य में इंजेक्ट होने वाले** — अभी तक उत्सर्जित नहीं; जिस क्षण कोई
  एनरिचर इन्हें उत्पन्न करना शुरू करता है, यहाँ प्रलेखित किए जाते हैं (प्रारंभिक
  जनसंख्या के समय लागू नहीं)।

## प्रविष्टि स्कीमा

नीचे प्रत्येक प्रविष्टि का ठीक यही आकार है। `tests/test_extension_catalog.py` में समानता परीक्षण
सेक्शन बॉडी के संक्षिप्त होने को तब तक सहन करता है जब तक `### x-name` हेडर मौजूद हो और
`Pass-through from upstream:` फ्लैग `yes` या `no` मान के साथ उपस्थित हो।

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

## इंजेक्ट किए गए — स्पेक-स्तर (info सेक्शन)

### x-f5xc-cli-domain

- **लागू होता है:** info
- **उद्देश्य:** एक एनरिच्ड स्पेक के लिए CLI डोमेन स्लग (जैसे `http_loadbalancer`) की पहचान करता है।
- **उपभोक्ता:** CLI
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-cli-metadata

- **लागू होता है:** info
- **उद्देश्य:** CLI-व्यापी मेटाडेटा ब्लॉक (टूल नाम, संस्करण संकेत, डोमेन समूहीकरण)।
- **उपभोक्ता:** CLI
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/cli_metadata.yaml
- **उदाहरण:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-upstream-timestamp

- **लागू होता है:** info
- **उद्देश्य:** अपस्ट्रीम सोर्स स्पेक का टाइमस्टैम्प जिससे एनरिच्ड फ़ाइल बनाई गई थी।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "format": "date-time"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-upstream-etag

- **लागू होता है:** info
- **उद्देश्य:** अपस्ट्रीम सोर्स स्पेक रिलीज़ एसेट का ETag।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-enriched-version

- **लागू होता है:** info
- **उद्देश्य:** पाइपलाइन द्वारा एनरिच्ड स्पेक पर अंकित सिमेंटिक संस्करण।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-enriched-version": "3.2.1"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-glossary

- **लागू होता है:** info
- **उद्देश्य:** प्रत्येक डोमेन स्पेक पर लागू ब्रांडिंग/शब्दावली शब्दकोश ब्लॉक।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/branding.py
- **कॉन्फ़िग द्वारा संचालित:** config/branding.yaml
- **उदाहरण:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-discovered-at

- **लागू होता है:** info
- **उद्देश्य:** लाइव-API डिस्कवरी पास कब निष्पादित किया गया था इसका टाइमस्टैम्प।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "format": "date-time"}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery.yaml
- **उदाहरण:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-api-url

- **लागू होता है:** info
- **उद्देश्य:** डिस्कवरी के दौरान जांची गई लाइव API का बेस URL।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "format": "uri"}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery.yaml
- **उदाहरण:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-api-reference-url

- **लागू होता है:** info
- **उद्देश्य:** इस डोमेन के लिए होस्ट किए गए API संदर्भ दस्तावेज़ पृष्ठ का URL।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "format": "uri"}`
- **इंजेक्ट करता है:** scripts/utils/external_docs_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** none (डोमेन नाम से व्युत्पन्न)
- **उदाहरण:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-response-time-ms

- **लागू होता है:** info
- **उद्देश्य:** डिस्कवरी के दौरान जांचे गए API का प्रेक्षित प्रतिक्रिया समय (ms)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** number
- **मान स्कीमा:** `{"type": "number"}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery.yaml
- **उदाहरण:** `"x-f5xc-response-time-ms": 42`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-best-practices

- **लागू होता है:** info
- **उद्देश्य:** किसी डोमेन के लिए क्यूरेटेड सर्वोत्तम अभ्यास मार्गदर्शन।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "object"}}`
- **इंजेक्ट करता है:** scripts/utils/best_practices_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/best_practices.yaml
- **उदाहरण:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-guided-workflows

- **लागू होता है:** info
- **उद्देश्य:** किसी डोमेन में सामान्य कार्यों को पूरा करने के लिए नामित चरण-दर-चरण वर्कफ़्लो।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "object"}}`
- **इंजेक्ट करता है:** scripts/utils/guided_workflow_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/guided_workflows.yaml
- **उदाहरण:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-acronyms

- **लागू होता है:** info
- **उद्देश्य:** प्रति-डोमेन संक्षिप्त नाम विस्तार तालिका।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/acronym_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/acronyms.yaml
- **उदाहरण:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **अपस्ट्रीम से पास-थ्रू:** no

## इंजेक्ट किए गए — स्कीमा-स्तर (कंपोनेंट स्कीमा)

### x-f5xc-minimum-configuration

- **लागू होता है:** schema
- **उद्देश्य:** इस संसाधन को सफलतापूर्वक POST/PUT करने के लिए आवश्यक न्यूनतम व्यवहार्य फ़ील्ड सेट।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/minimum_configuration_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/minimum_configs.yaml
- **उदाहरण:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-namespace-profile

- **लागू होता है:** info
- **उद्देश्य:** किसी संसाधन के लिए नेमस्पेस बाधा, अनुशंसा, और वर्गीकरण मेटाडेटा प्रदान करता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **इंजेक्ट करता है:** scripts/utils/namespace_profile_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/namespace_profile.yaml
- **उदाहरण:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-displayorder

- **लागू होता है:** schema
- **उद्देश्य:** UI/CLI प्रस्तुति के लिए गुणों का सुझाया गया क्रम।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-terraform-resource

- **लागू होता है:** schema
- **उद्देश्य:** इस स्कीमा से मैप होने वाला Terraform संसाधन प्रकार नाम।
- **उपभोक्ता:** Terraform
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-display-name

- **लागू होता है:** schema
- **उद्देश्य:** किसी संसाधन स्कीमा के लिए मानव-पठनीय प्रदर्शन नाम (स्वतः-उत्पादन को ओवरराइड करता है)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **अपस्ट्रीम से पास-थ्रू:** no

## इंजेक्ट किए गए — प्रॉपर्टी-स्तर

### x-f5xc-description

- **लागू होता है:** schema property
- **उद्देश्य:** एनरिच्ड प्रॉपर्टी विवरण जो अपस्ट्रीम `description` को पूरक करता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_descriptions.yaml
- **उदाहरण:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-validation

- **लागू होता है:** schema property
- **उद्देश्य:** अपस्ट्रीम protobuf `ves.io.schema.rules` से प्राप्त घोषणात्मक सत्यापन नियम।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/validation_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/validation_rules.yaml
- **उदाहरण:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-examples

- **लागू होता है:** schema property
- **उद्देश्य:** किसी प्रॉपर्टी के लिए एकाधिक उदाहरणात्मक मान।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array"}`
- **इंजेक्ट करता है:** scripts/utils/resource_examples_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/resource_examples.yaml
- **उदाहरण:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-example

- **लागू होता है:** schema property
- **उद्देश्य:** एक एकल प्रामाणिक उदाहरण मान।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{}`
- **इंजेक्ट करता है:** scripts/utils/field_description_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_descriptions.yaml
- **उदाहरण:** `"x-f5xc-example": "example.com"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-completion

- **लागू होता है:** schema property
- **उद्देश्य:** शेल पूर्णता संकेत (स्थिर enum या गतिशील कमांड)।
- **उपभोक्ता:** CLI
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-defaults

- **लागू होता है:** schema property
- **उद्देश्य:** जनरेटेड डॉक्स और UI में प्रदर्शित करने के लिए डिफ़ॉल्ट मान।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-defaults": {"value": "default"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-required-for-operations

- **लागू होता है:** schema property
- **उद्देश्य:** HTTP ऑपरेशन (POST/PUT/...) सूचीबद्ध करता है जिनके लिए इस प्रॉपर्टी की आवश्यकता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-required-for

- **लागू होता है:** schema property
- **उद्देश्य:** नामित सुविधा संयोजनों को सूचीबद्ध करता है जिनके लिए इस प्रॉपर्टी की आवश्यकता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/minimum_configuration_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/minimum_configs.yaml
- **उदाहरण:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-conditions

- **लागू होता है:** schema property
- **उद्देश्य:** सशर्त आवश्यकताएँ (जैसे, जब सहोदर फ़ील्ड X के बराबर हो तब आवश्यक)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "object"}}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-deprecated

- **लागू होता है:** schema property
- **उद्देश्य:** प्रतिस्थापन मार्गदर्शन के साथ बहिष्करण सूचना।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/field_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/field_metadata.yaml
- **उदाहरण:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-server-default

- **लागू होता है:** schema property
- **उद्देश्य:** वह डिफ़ॉल्ट मान जो क्लाइंट द्वारा प्रॉपर्टी छोड़ने पर सर्वर असाइन करता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{}`
- **इंजेक्ट करता है:** scripts/utils/default_value_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovered_defaults.yaml
- **उदाहरण:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-recommended-value

- **लागू होता है:** schema property
- **उद्देश्य:** किसी फ़ील्ड के लिए अनुशंसित प्रोडक्शन मान जहाँ सर्वर डिफ़ॉल्ट अनुकूलतम नहीं है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{}`
- **इंजेक्ट करता है:** scripts/utils/default_value_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovered_defaults.yaml
- **उदाहरण:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-recommended-oneof-variant

- **लागू होता है:** schema property
- **उद्देश्य:** `oneOf` ब्लॉक के लिए, इंगित करता है कि कौन सा वेरिएंट अनुशंसित है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/default_value_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovered_defaults.yaml
- **उदाहरण:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-conflicts-with

- **लागू होता है:** schema property
- **उद्देश्य:** सहोदर प्रॉपर्टीज़ सूचीबद्ध करता है जिन्हें इसके साथ सेट नहीं किया जा सकता।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/conflicts_with_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-requires

- **लागू होता है:** schema property
- **उद्देश्य:** क्रॉस-फ़ील्ड निर्भरताओं को प्रलेखित करता है जहाँ एक फ़ील्ड के लिए दूसरे को सेट करना आवश्यक है।
- **उपभोक्ता:** compile_catalog.py, xcsh CLI
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **इंजेक्ट करता है:** scripts/utils/dependency_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/minimum_configs.yaml (dependencies सेक्शन)
- **उदाहरण:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-constraints

- **लागू होता है:** schema property
- **उद्देश्य:** लाइव-API प्रोबिंग या स्थिर पैटर्न से प्राप्त संख्यात्मक / स्ट्रिंग बाधाएँ।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/constraint_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/constraint_patterns.yaml
- **उदाहरण:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-uniqueness

- **लागू होता है:** schema property
- **उद्देश्य:** घोषित करता है कि क्या किसी फ़ील्ड को अपने दायरे में अद्वितीय होना चाहिए।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/uniqueness_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** hardcoded
- **उदाहरण:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **अपस्ट्रीम से पास-थ्रू:** no

## इंजेक्ट किए गए — ऑपरेशन-स्तर

### x-f5xc-required-fields

- **लागू होता है:** operation
- **उद्देश्य:** ऑपरेशन-बॉडी फ़ील्ड्स का नाम बताता है जो सफलता के लिए प्रदान किए जाने चाहिए।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/operation_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/operation_metadata.yaml
- **उदाहरण:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-danger-level

- **लागू होता है:** operation
- **उद्देश्य:** किसी ऑपरेशन के प्रभाव क्षेत्र को वर्गीकृत करता है (low/medium/high/critical)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **इंजेक्ट करता है:** scripts/utils/operation_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/operation_metadata.yaml
- **उदाहरण:** `"x-f5xc-danger-level": "high"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-confirmation-required

- **लागू होता है:** operation
- **उद्देश्य:** क्या CLI/UI को निष्पादन से पहले उपयोगकर्ता से पुष्टि के लिए पूछना चाहिए।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** boolean
- **मान स्कीमा:** `{"type": "boolean"}`
- **इंजेक्ट करता है:** scripts/utils/operation_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/operation_metadata.yaml
- **उदाहरण:** `"x-f5xc-confirmation-required": true`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-side-effects

- **लागू होता है:** operation
- **उद्देश्य:** ऑपरेशन के प्रेक्षणीय दुष्प्रभावों को सूचीबद्ध करता है (पुनरारंभ, पुन:कॉन्फ़िगर, आदि)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/utils/operation_metadata_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/operation_metadata.yaml
- **उदाहरण:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-discovered-response-time

- **लागू होता है:** operation
- **उद्देश्य:** डिस्कवरी के दौरान इस ऑपरेशन के लिए अनुभवजन्य रूप से मापा गया प्रतिक्रिया समय।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery_enrichment.yaml
- **उदाहरण:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-discovered-rate-limits

- **लागू होता है:** operation
- **उद्देश्य:** लाइव API से प्रकट प्रेक्षित दर-सीमा हेडर / व्यवहार।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** object
- **मान स्कीमा:** `{"type": "object"}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery_enrichment.yaml
- **उदाहरण:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-discovered-error-catalog

- **लागू होता है:** operation
- **उद्देश्य:** लाइव डिस्कवरी के दौरान प्रेक्षित त्रुटि प्रतिक्रियाओं की सूची, नमूना पेलोड के साथ।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "object"}}`
- **इंजेक्ट करता है:** scripts/utils/discovery_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/discovery_enrichment.yaml
- **उदाहरण:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **अपस्ट्रीम से पास-थ्रू:** no

## इंजेक्ट किए गए — इंडेक्स-स्तर (डोमेन मेटाडेटा)

### x-f5xc-category

- **लागू होता है:** info
- **उद्देश्य:** किसी डोमेन के लिए शीर्ष-स्तरीय CLI / UI / डॉक्स / Terraform समूहीकरण श्रेणी।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-category": "networking"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-primary-resources

- **लागू होता है:** info
- **उद्देश्य:** डोमेन को परिभाषित करने वाले प्राथमिक संसाधन प्रकारों की सूची।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-critical-resources

- **लागू होता है:** info
- **उद्देश्य:** ऐसे संसाधन जिनके लिए उच्च सावधानी आवश्यक है (प्रोडक्शन-महत्वपूर्ण)।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/critical_resources.yaml
- **उदाहरण:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-description-short

- **लागू होता है:** info
- **उद्देश्य:** छोटा (~60 अक्षर) डोमेन विवरण। लंबे विवरणों के लिए प्रॉपर्टी स्तर पर भी लागू होता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/property_description_short_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/property_description_short.yaml
- **उदाहरण:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-description-medium

- **लागू होता है:** info
- **उद्देश्य:** मध्यम (~150 अक्षर) डोमेन विवरण। प्रॉपर्टी स्तर पर भी लागू होता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/property_description_short_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/property_description_short.yaml
- **उदाहरण:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-description-long

- **लागू होता है:** info
- **उद्देश्य:** लंबा (~500 अक्षर) डोमेन विवरण।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/utils/description_enricher.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_descriptions.yaml
- **उदाहरण:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-complexity

- **लागू होता है:** info
- **उद्देश्य:** इस डोमेन में कॉन्फ़िगरेशन बनाने की सापेक्ष जटिलता स्तर।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-complexity": "medium"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-requires-tier

- **लागू होता है:** info
- **उद्देश्य:** आवश्यक न्यूनतम F5 XC सब्सक्रिप्शन टियर।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-requires-tier": "enterprise"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-is-preview

- **लागू होता है:** info
- **उद्देश्य:** किसी डोमेन को प्रीव्यू / बीटा सुविधा के रूप में चिह्नित करता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** boolean
- **मान स्कीमा:** `{"type": "boolean"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-is-preview": false`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-use-cases

- **लागू होता है:** info
- **उद्देश्य:** नामित उपयोग परिदृश्य जिनका यह डोमेन समर्थन करता है।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-icon

- **लागू होता है:** info
- **उद्देश्य:** UI में इस डोमेन को रेंडर करते समय उपयोग करने के लिए आइकन पहचानकर्ता।
- **उपभोक्ता:** Web UI
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-logo-svg

- **लागू होता है:** info
- **उद्देश्य:** डोमेन का प्रतिनिधित्व करने वाले ब्रांड लोगो के लिए इनलाइन SVG (या पथ)।
- **उपभोक्ता:** Web UI
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-related-domains

- **लागू होता है:** info
- **उद्देश्य:** आमतौर पर इसके साथ उपयोग किए जाने वाले अन्य डोमेन के क्रॉस-लिंक।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** array
- **मान स्कीमा:** `{"type": "array", "items": {"type": "string"}}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **अपस्ट्रीम से पास-थ्रू:** no

### x-f5xc-doc-section

- **लागू होता है:** info
- **उद्देश्य:** रेंडर किए गए डॉक्स के लिए दस्तावेज़ सेक्शन / नेविगेशन समूहीकरण स्लग।
- **उपभोक्ता:** multiple
- **मान का प्रकार:** string
- **मान स्कीमा:** `{"type": "string"}`
- **इंजेक्ट करता है:** scripts/merge_specs.py
- **कॉन्फ़िग द्वारा संचालित:** config/domain_patterns.yaml
- **उदाहरण:** `"x-f5xc-doc-section": "load-balancing"`
- **अपस्ट्रीम से पास-थ्रू:** no

## अपस्ट्रीम पास-थ्रू

### x-ves-proto-package

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-proto-file

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-proto-message

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-proto-service

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-proto-rpc

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-displayname

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** `"x-displayname": "Namespace"`
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-oneof

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** F5 अपस्ट्रीम डॉक्स देखें।
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-default

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** F5 अपस्ट्रीम डॉक्स देखें।
- **अपस्ट्रीम से पास-थ्रू:** yes

### x-ves-required

- **लागू होता है:** upstream
- **उद्देश्य:** F5 अपस्ट्रीम स्पेक से बिना बदलाव के संरक्षित।
- **उपभोक्ता:** N/A
- **मान का प्रकार:** varies
- **मान स्कीमा:** N/A
- **इंजेक्ट करता है:** upstream
- **कॉन्फ़िग द्वारा संचालित:** upstream
- **उदाहरण:** F5 अपस्ट्रीम डॉक्स देखें।
- **अपस्ट्रीम से पास-थ्रू:** yes
