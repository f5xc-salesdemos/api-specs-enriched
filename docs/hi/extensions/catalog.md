---
title: संवर्धन एक्सटेंशन कैटालॉग
description: संवर्धित OpenAPI विनिर्देशों में प्रत्येक x-* एक्सटेंशन के लिए सत्य का स्रोत
i18n:
  sourceHash: 70e0912cf4b0
  translator: machine
---

# संवर्धन एक्सटेंशन कैटालॉग

`docs/specifications/api/*.json` में दिखाई देने वाले प्रत्येक `x-*` एक्सटेंशन के लिए सत्य का स्रोत। `scripts/utils/extension_constants.py` के साथ समानता `tests/test_extension_catalog.py` द्वारा लागू की जाती है।

यहाँ तीन प्रकार के एक्सटेंशन दस्तावेज़ीकृत हैं:

- **यहाँ इंजेक्ट किए गए** — वे एक्सटेंशन जो हमारे एनरिचर जोड़ते हैं (`x-f5xc-*` और `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / डिस्कवरी वेरिएंट)। ये वे हैं जिन्हें डाउनस्ट्रीम उपकरण उपभोग करें।
- **अपस्ट्रीम पास-थ्रू** — वे एक्सटेंशन जो F5 स्रोत विनिर्देशों में उत्सर्जित करता है और हम अपरिवर्तित संरक्षित रखते हैं (`x-ves-proto-*`, `x-displayname`, आदि)। पारदर्शिता के लिए दस्तावेज़ीकृत लेकिन इस रेपो द्वारा नियंत्रित नहीं।
- **भविष्य में इंजेक्ट किए जाने वाले** — अभी तक उत्सर्जित नहीं; जैसे ही कोई एनरिचर इन्हें उत्पन्न करना शुरू करे, यहाँ दस्तावेज़ीकृत किए जाएंगे (प्रारंभिक पॉपुलेशन पर लागू नहीं)।

## एंट्री स्कीमा

नीचे दी गई प्रत्येक एंट्री का ठीक यही रूप है। `tests/test_extension_catalog.py` में पैरिटी टेस्ट सेक्शन बॉडी के स्टब्बी होने को तब तक सहन करता है जब तक `### x-name` हेडर मौजूद हो और `Pass-through from upstream:` फ्लैग `yes` या `no` मान के साथ उपस्थित हो।

    ### x-<name>
    - **Applied at:** <schema | parameter | operation | path-item | info | response>
    - **Purpose:** <एक वाक्य>
    - **Consumers:** <CLI | VSCode | Terraform | Web UI | multiple | N/A>
    - **Value type:** <string | number | boolean | object | array>
    - **Value schema:** <JSON Schema स्निपेट, या N/A>
    - **Injected by:** <scripts/utils/<enricher>.py, या "upstream">
    - **Driven by config:** <config/<file>.yaml, या "hardcoded", या "upstream">
    - **Example:** <छोटा स्निपेट>
    - **Pass-through from upstream:** <yes/no>

## इंजेक्ट किए गए — स्पेक-स्तर (info सेक्शन)

### x-f5xc-cli-domain

- **Applied at:** info
- **Purpose:** एनरिच्ड स्पेक के लिए CLI डोमेन स्लग (जैसे `http_loadbalancer`) की पहचान करता है।
- **Consumers:** CLI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-cli-metadata

- **Applied at:** info
- **Purpose:** CLI-व्यापी मेटाडेटा ब्लॉक (टूल नाम, संस्करण संकेत, डोमेन ग्रुपिंग)।
- **Consumers:** CLI
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/cli_metadata.yaml
- **Example:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **Pass-through from upstream:** no

### x-f5xc-upstream-timestamp

- **Applied at:** info
- **Purpose:** अपस्ट्रीम स्रोत स्पेक का टाइमस्टैम्प जिससे एनरिच्ड फ़ाइल बनाई गई थी।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "date-time"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-upstream-etag

- **Applied at:** info
- **Purpose:** अपस्ट्रीम स्रोत स्पेक रिलीज़ एसेट का ETag।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **Pass-through from upstream:** no

### x-f5xc-enriched-version

- **Applied at:** info
- **Purpose:** पाइपलाइन द्वारा एनरिच्ड स्पेक पर स्टैम्प किया गया सेमेंटिक संस्करण।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-enriched-version": "3.2.1"`
- **Pass-through from upstream:** no

### x-f5xc-glossary

- **Applied at:** info
- **Purpose:** प्रत्येक डोमेन स्पेक पर लागू ब्रांडिंग/शब्दावली ग्लॉसरी ब्लॉक।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/branding.py
- **Driven by config:** config/branding.yaml
- **Example:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-at

- **Applied at:** info
- **Purpose:** वह टाइमस्टैम्प जब लाइव-API डिस्कवरी पास निष्पादित किया गया था।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "date-time"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **Pass-through from upstream:** no

### x-f5xc-api-url

- **Applied at:** info
- **Purpose:** डिस्कवरी के दौरान जांची गई लाइव API का बेस URL।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "uri"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **Pass-through from upstream:** no

### x-f5xc-api-reference-url

- **Applied at:** info
- **Purpose:** इस डोमेन के लिए होस्टेड API रेफरेंस दस्तावेज़ीकरण पृष्ठ का URL।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "format": "uri"}`
- **Injected by:** scripts/utils/external_docs_enricher.py
- **Driven by config:** none (डोमेन नाम से व्युत्पन्न)
- **Example:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **Pass-through from upstream:** no

### x-f5xc-response-time-ms

- **Applied at:** info
- **Purpose:** डिस्कवरी के दौरान जांची गई API के लिए देखा गया प्रतिक्रिया समय (ms)।
- **Consumers:** multiple
- **Value type:** number
- **Value schema:** `{"type": "number"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery.yaml
- **Example:** `"x-f5xc-response-time-ms": 42`
- **Pass-through from upstream:** no

### x-f5xc-best-practices

- **Applied at:** info
- **Purpose:** किसी डोमेन के लिए क्यूरेटेड सर्वोत्तम-प्रथा मार्गदर्शन।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/best_practices_enricher.py
- **Driven by config:** config/best_practices.yaml
- **Example:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **Pass-through from upstream:** no

### x-f5xc-guided-workflows

- **Applied at:** info
- **Purpose:** किसी डोमेन में सामान्य कार्यों को पूरा करने के लिए नामित चरण-दर-चरण वर्कफ़्लो।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/guided_workflow_enricher.py
- **Driven by config:** config/guided_workflows.yaml
- **Example:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **Pass-through from upstream:** no

### x-f5xc-acronyms

- **Applied at:** info
- **Purpose:** प्रति-डोमेन संक्षिप्त नाम विस्तार तालिका।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **Injected by:** scripts/utils/acronym_enricher.py
- **Driven by config:** config/acronyms.yaml
- **Example:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **Pass-through from upstream:** no

### x-f5xc-console-navigation

- **Applied at:** spec info
- **Purpose:** ग्लोबल कंसोल नेविगेशन ट्री — वर्कस्पेस और मेनू पदानुक्रम।
- **Consumers:** console-catalog, xcsh, browser-automation
- **Value type:** object
- **Value schema:** `{"type": "object", "properties": {"workspaces": "object"}}`
- **Injected by:** scripts/utils/console_ui_enricher.py
- **Driven by config:** config/console_ui.yaml
- **Example:** `"x-f5xc-console-navigation": {"workspaces": {"web-app-and-api-protection": {"label": "Web App & API Protection", "route_prefix": "/web/workspaces/web-app-and-api-protection"}}}`
- **Pass-through from upstream:** no

## इंजेक्ट किए गए — स्कीमा-स्तर (component schemas)

### x-f5xc-minimum-configuration

- **Applied at:** schema
- **Purpose:** इस संसाधन को सफलतापूर्वक POST/PUT करने के लिए आवश्यक न्यूनतम व्यावहारिक फ़ील्ड सेट।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/minimum_configuration_enricher.py
- **Driven by config:** config/minimum_configs.yaml
- **Example:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **Pass-through from upstream:** no

### x-f5xc-namespace-profile

- **Applied at:** info
- **Purpose:** किसी संसाधन के लिए नेमस्पेस बाधा, अनुशंसा और वर्गीकरण मेटाडेटा प्रदान करता है।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **Injected by:** scripts/utils/namespace_profile_enricher.py
- **Driven by config:** config/namespace_profile.yaml
- **Example:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **Pass-through from upstream:** no

### x-f5xc-displayorder

- **Applied at:** schema
- **Purpose:** UI/CLI प्रस्तुति के लिए गुणों का सुझाया गया क्रम।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **Pass-through from upstream:** no

### x-f5xc-terraform-resource

- **Applied at:** schema
- **Purpose:** Terraform संसाधन प्रकार का नाम जो इस स्कीमा से मैप होता है।
- **Consumers:** Terraform
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **Pass-through from upstream:** no

### x-f5xc-display-name

- **Applied at:** schema
- **Purpose:** संसाधन स्कीमा के लिए मानव-पठनीय प्रदर्शन नाम (ऑटो-जनरेशन को ओवरराइड करता है)।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **Pass-through from upstream:** no

### x-f5xc-console

- **Applied at:** schema
- **Purpose:** इस संसाधन के लिए कंसोल UI नेविगेशन, रूटिंग और फ़ॉर्म संरचना।
- **Consumers:** console-catalog, xcsh, vscode-xcsh, browser-automation
- **Value type:** object
- **Value schema:** `{"type": "object", "properties": {"workspace": "string", "menu_path": "array", "route_pattern": "string", "breadcrumbs": "array", "add_action": "object", "form_sections": "array", "metadata": "object"}}`
- **Injected by:** scripts/utils/console_ui_enricher.py
- **Driven by config:** config/console_ui.yaml
- **Example:** `"x-f5xc-console": {"workspace": "web-app-and-api-protection", "menu_path": ["Manage", "Load Balancers", "HTTP Load Balancers"]}`
- **Pass-through from upstream:** no

## इंजेक्ट किए गए — प्रॉपर्टी-स्तर

### x-f5xc-description

- **Applied at:** schema property
- **Purpose:** एनरिच्ड प्रॉपर्टी विवरण जो अपस्ट्रीम `description` को पूरक करता है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_descriptions.yaml
- **Example:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **Pass-through from upstream:** no

### x-f5xc-validation

- **Applied at:** schema property
- **Purpose:** अपस्ट्रीम protobuf `ves.io.schema.rules` से व्युत्पन्न घोषणात्मक सत्यापन नियम।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/validation_enricher.py
- **Driven by config:** config/validation_rules.yaml
- **Example:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **Pass-through from upstream:** no

### x-f5xc-examples

- **Applied at:** schema property
- **Purpose:** किसी प्रॉपर्टी के लिए एकाधिक उदाहरण मान।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array"}`
- **Injected by:** scripts/utils/resource_examples_enricher.py
- **Driven by config:** config/resource_examples.yaml
- **Example:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **Pass-through from upstream:** no

### x-f5xc-example

- **Applied at:** schema property
- **Purpose:** एक एकल विहित उदाहरण मान।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/field_description_enricher.py
- **Driven by config:** config/field_descriptions.yaml
- **Example:** `"x-f5xc-example": "example.com"`
- **Pass-through from upstream:** no

### x-f5xc-completion

- **Applied at:** schema property
- **Purpose:** शेल कम्पलीशन संकेत (स्थिर enum या गतिशील कमांड)।
- **Consumers:** CLI
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **Pass-through from upstream:** no

### x-f5xc-defaults

- **Applied at:** schema property
- **Purpose:** जनरेट किए गए दस्तावेज़ों और UIs में प्रदर्शित करने के लिए डिफ़ॉल्ट मान।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-defaults": {"value": "default"}`
- **Pass-through from upstream:** no

### x-f5xc-required-for-operations

- **Applied at:** schema property
- **Purpose:** HTTP ऑपरेशन (POST/PUT/...) सूचीबद्ध करता है जिनके लिए यह प्रॉपर्टी आवश्यक है।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **Pass-through from upstream:** no

### x-f5xc-required-for

- **Applied at:** schema property
- **Purpose:** नामित फ़ीचर संयोजनों की सूची बनाता है जिनके लिए यह प्रॉपर्टी आवश्यक है।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/minimum_configuration_enricher.py
- **Driven by config:** config/minimum_configs.yaml
- **Example:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **Pass-through from upstream:** no

### x-f5xc-conditions

- **Applied at:** schema property
- **Purpose:** सशर्त आवश्यकताएं (जैसे जब सिब्लिंग फ़ील्ड X के बराबर हो तो आवश्यक)।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **Pass-through from upstream:** no

### x-f5xc-deprecated

- **Applied at:** schema property
- **Purpose:** प्रतिस्थापन मार्गदर्शन के साथ अवमूल्यन सूचना।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/field_metadata_enricher.py
- **Driven by config:** config/field_metadata.yaml
- **Example:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **Pass-through from upstream:** no

### x-f5xc-server-default

- **Applied at:** schema property
- **Purpose:** वह डिफ़ॉल्ट मान जो सर्वर तब असाइन करता है जब क्लाइंट प्रॉपर्टी छोड़ देता है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-value

- **Applied at:** schema property
- **Purpose:** किसी फ़ील्ड के लिए अनुशंसित प्रोडक्शन मान जहाँ सर्वर डिफ़ॉल्ट इष्टतम नहीं है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **Pass-through from upstream:** no

### x-f5xc-recommended-oneof-variant

- **Applied at:** schema property
- **Purpose:** `oneOf` ब्लॉक के लिए, इंगित करता है कि कौन सा वेरिएंट अनुशंसित है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/default_value_enricher.py
- **Driven by config:** config/discovered_defaults.yaml
- **Example:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **Pass-through from upstream:** no

### x-f5xc-conflicts-with

- **Applied at:** schema property
- **Purpose:** उन सिब्लिंग प्रॉपर्टीज़ की सूची बनाता है जो इसके साथ सेट नहीं की जा सकतीं।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/conflicts_with_enricher.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **Pass-through from upstream:** no

### x-f5xc-requires

- **Applied at:** schema property
- **Purpose:** क्रॉस-फ़ील्ड निर्भरताओं को दस्तावेज़ीकृत करता है जहाँ एक फ़ील्ड को दूसरे के सेट होने की आवश्यकता होती है।
- **Consumers:** compile_catalog.py, xcsh CLI
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **Injected by:** scripts/utils/dependency_enricher.py
- **Driven by config:** config/minimum_configs.yaml (dependencies section)
- **Example:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **Pass-through from upstream:** no

### x-f5xc-constraints

- **Applied at:** schema property
- **Purpose:** लाइव-API प्रोबिंग या स्थिर पैटर्न से व्युत्पन्न संख्यात्मक / स्ट्रिंग बाधाएं।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/constraint_enricher.py
- **Driven by config:** config/constraint_patterns.yaml
- **Example:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **Pass-through from upstream:** no

### x-f5xc-uniqueness

- **Applied at:** schema property
- **Purpose:** घोषित करता है कि कोई फ़ील्ड अपने दायरे के भीतर अद्वितीय होनी चाहिए या नहीं।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/uniqueness_enricher.py
- **Driven by config:** hardcoded
- **Example:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **Pass-through from upstream:** no

### x-f5xc-console-field

- **Applied at:** schema property
- **Purpose:** इस API प्रॉपर्टी के लिए कंसोल फ़ॉर्म विजेट मेटाडेटा।
- **Consumers:** console-catalog, xcsh, browser-automation
- **Value type:** object
- **Value schema:** `{"type": "object", "properties": {"widget_type": "string", "label": "string", "default": "any", "selector": "string", "form_section": "string", "show_when": "object", "advanced": "boolean"}}`
- **Injected by:** scripts/utils/console_ui_enricher.py
- **Driven by config:** config/console_field_metadata.yaml
- **Example:** `"x-f5xc-console-field": {"widget_type": "listbox", "default": "HTTPS with Automatic Certificate", "form_section": "domains-and-lb-type"}`
- **Pass-through from upstream:** no

## इंजेक्ट किए गए — ऑपरेशन-स्तर

### x-f5xc-required-fields

- **Applied at:** operation
- **Purpose:** ऑपरेशन-बॉडी फ़ील्ड के नाम बताता है जो सफलता के लिए प्रदान किए जाने चाहिए।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **Pass-through from upstream:** no

### x-f5xc-danger-level

- **Applied at:** operation
- **Purpose:** किसी ऑपरेशन के ब्लास्ट रेडियस को वर्गीकृत करता है (low/medium/high/critical)।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-danger-level": "high"`
- **Pass-through from upstream:** no

### x-f5xc-confirmation-required

- **Applied at:** operation
- **Purpose:** क्या CLI/UI को निष्पादन से पहले उपयोगकर्ता से पुष्टि मांगनी चाहिए।
- **Consumers:** multiple
- **Value type:** boolean
- **Value schema:** `{"type": "boolean"}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-confirmation-required": true`
- **Pass-through from upstream:** no

### x-f5xc-side-effects

- **Applied at:** operation
- **Purpose:** ऑपरेशन के अवलोकन योग्य साइड इफेक्ट्स सूचीबद्ध करता है (restart, reconfigure, आदि)।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/utils/operation_metadata_enricher.py
- **Driven by config:** config/operation_metadata.yaml
- **Example:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **Pass-through from upstream:** no

### x-f5xc-discovered-response-time

- **Applied at:** operation
- **Purpose:** डिस्कवरी के दौरान इस ऑपरेशन के लिए अनुभवजन्य रूप से मापा गया प्रतिक्रिया समय।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-rate-limits

- **Applied at:** operation
- **Purpose:** लाइव API से सर्फेस किए गए देखे गए रेट-लिमिट हेडर / व्यवहार।
- **Consumers:** multiple
- **Value type:** object
- **Value schema:** `{"type": "object"}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **Pass-through from upstream:** no

### x-f5xc-discovered-error-catalog

- **Applied at:** operation
- **Purpose:** लाइव डिस्कवरी के दौरान देखी गई त्रुटि प्रतिक्रियाओं का कैटालॉग, नमूना पेलोड सहित।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "object"}}`
- **Injected by:** scripts/utils/discovery_enricher.py
- **Driven by config:** config/discovery_enrichment.yaml
- **Example:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **Pass-through from upstream:** no

## इंजेक्ट किए गए — इंडेक्स-स्तर (डोमेन मेटाडेटा)

### x-f5xc-category

- **Applied at:** info
- **Purpose:** किसी डोमेन के लिए शीर्ष-स्तरीय CLI / UI / docs / Terraform ग्रुपिंग श्रेणी।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-category": "networking"`
- **Pass-through from upstream:** no

### x-f5xc-primary-resources

- **Applied at:** info
- **Purpose:** प्राथमिक संसाधन प्रकारों की सूची जो डोमेन को परिभाषित करते हैं।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **Pass-through from upstream:** no

### x-f5xc-critical-resources

- **Applied at:** info
- **Purpose:** वे संसाधन जिन्हें उच्च सतर्कता की आवश्यकता है (प्रोडक्शन-क्रिटिकल)।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/critical_resources.yaml
- **Example:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-description-short

- **Applied at:** info
- **Purpose:** संक्षिप्त (~60 char) डोमेन विवरण। लंबे विवरणों के लिए प्रॉपर्टी स्तर पर भी लागू होता है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/property_description_short_enricher.py
- **Driven by config:** config/property_description_short.yaml
- **Example:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **Pass-through from upstream:** no

### x-f5xc-description-medium

- **Applied at:** info
- **Purpose:** मध्यम (~150 char) डोमेन विवरण। प्रॉपर्टी स्तर पर भी लागू होता है।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/property_description_short_enricher.py
- **Driven by config:** config/property_description_short.yaml
- **Example:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **Pass-through from upstream:** no

### x-f5xc-description-long

- **Applied at:** info
- **Purpose:** लंबा (~500 char) डोमेन विवरण।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/utils/description_enricher.py
- **Driven by config:** config/domain_descriptions.yaml
- **Example:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **Pass-through from upstream:** no

### x-f5xc-complexity

- **Applied at:** info
- **Purpose:** इस डोमेन में कॉन्फ़िगरेशन बनाने की सापेक्ष जटिलता स्तर।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-complexity": "medium"`
- **Pass-through from upstream:** no

### x-f5xc-requires-tier

- **Applied at:** info
- **Purpose:** आवश्यक न्यूनतम F5 XC सब्सक्रिप्शन टियर।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-requires-tier": "enterprise"`
- **Pass-through from upstream:** no

### x-f5xc-is-preview

- **Applied at:** info
- **Purpose:** किसी डोमेन को प्रीव्यू / बीटा फ़ीचर के रूप में फ्लैग करता है।
- **Consumers:** multiple
- **Value type:** boolean
- **Value schema:** `{"type": "boolean"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-is-preview": false`
- **Pass-through from upstream:** no

### x-f5xc-use-cases

- **Applied at:** info
- **Purpose:** नामित उपयोग-मामले जो यह डोमेन समर्थित करता है।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **Pass-through from upstream:** no

### x-f5xc-icon

- **Applied at:** info
- **Purpose:** UI में इस डोमेन को रेंडर करते समय उपयोग करने के लिए आइकन पहचानकर्ता।
- **Consumers:** Web UI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **Pass-through from upstream:** no

### x-f5xc-logo-svg

- **Applied at:** info
- **Purpose:** डोमेन का प्रतिनिधित्व करने वाले ब्रांड लोगो के लिए इनलाइन SVG (या पथ)।
- **Consumers:** Web UI
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **Pass-through from upstream:** no

### x-f5xc-related-domains

- **Applied at:** info
- **Purpose:** अन्य डोमेन के क्रॉस-लिंक जो आमतौर पर इसके साथ उपयोग किए जाते हैं।
- **Consumers:** multiple
- **Value type:** array
- **Value schema:** `{"type": "array", "items": {"type": "string"}}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **Pass-through from upstream:** no

### x-f5xc-doc-section

- **Applied at:** info
- **Purpose:** रेंडर किए गए दस्तावेज़ों के लिए दस्तावेज़ीकरण सेक्शन / नेव ग्रुपिंग स्लग।
- **Consumers:** multiple
- **Value type:** string
- **Value schema:** `{"type": "string"}`
- **Injected by:** scripts/merge_specs.py
- **Driven by config:** config/domain_patterns.yaml
- **Example:** `"x-f5xc-doc-section": "load-balancing"`
- **Pass-through from upstream:** no

## अपस्ट्रीम पास-थ्रू

### x-ves-proto-package

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **Pass-through from upstream:** yes

### x-ves-proto-file

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **Pass-through from upstream:** yes

### x-ves-proto-message

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **Pass-through from upstream:** yes

### x-ves-proto-service

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **Pass-through from upstream:** yes

### x-ves-proto-rpc

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **Pass-through from upstream:** yes

### x-displayname

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** `"x-displayname": "Namespace"`
- **Pass-through from upstream:** yes

### x-ves-oneof

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** F5 अपस्ट्रीम दस्तावेज़ देखें।
- **Pass-through from upstream:** yes

### x-ves-default

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** F5 अपस्ट्रीम दस्तावेज़ देखें।
- **Pass-through from upstream:** yes

### x-ves-required

- **Applied at:** upstream
- **Purpose:** F5 अपस्ट्रीम स्पेक से अपरिवर्तित संरक्षित।
- **Consumers:** N/A
- **Value type:** varies
- **Value schema:** N/A
- **Injected by:** upstream
- **Driven by config:** upstream
- **Example:** F5 अपस्ट्रीम दस्तावेज़ देखें।
- **Pass-through from upstream:** yes
