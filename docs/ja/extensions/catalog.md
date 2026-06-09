---
title: エンリッチメント拡張カタログ
description: エンリッチされたOpenAPI仕様におけるすべてのx-*拡張の信頼できる情報源
i18n:
  sourceHash: 7fde0afb4dac
  translator: machine
---

# エンリッチメント拡張カタログ

`docs/specifications/api/*.json` に出現するすべての `x-*` 拡張の信頼できる情報源です。`scripts/utils/extension_constants.py` との整合性は `tests/test_extension_catalog.py` によって強制されます。

ここでは3つのクラスの拡張が文書化されています：

- **ここで注入** — エンリッチャーが追加する拡張（`x-f5xc-*` および `x-ves-cli-*` / `x-ves-field-*` / `x-ves-operation-*` / ディスカバリーバリアント）。これらは下流ツールが消費すべきものです。
- **アップストリームパススルー** — F5がソース仕様で出力し、変更せずに保持する拡張（`x-ves-proto-*`、`x-displayname` など）。透明性のために文書化されていますが、このリポジトリでは管理されません。
- **将来注入** — まだ出力されていません。エンリッチャーが生成を開始した時点でここに文書化されます（初期投入時点では該当なし）。

## エントリスキーマ

以下のすべてのエントリは正確にこの形式を持ちます。`tests/test_extension_catalog.py` の整合性テストは、`### x-name` ヘッダーが存在し、`Pass-through from upstream:` フラグが `yes` または `no` の値で存在する限り、セクション本文が簡略化されていても許容します。

    ### x-<name>
    - **適用先:** <schema | parameter | operation | path-item | info | response>
    - **目的:** <一文>
    - **利用者:** <CLI | VSCode | Terraform | Web UI | multiple | N/A>
    - **値の型:** <string | number | boolean | object | array>
    - **値のスキーマ:** <JSON Schemaスニペット、またはN/A>
    - **注入元:** <scripts/utils/<enricher>.py、または"upstream">
    - **設定による駆動:** <config/<file>.yaml、または"hardcoded"、または"upstream">
    - **例:** <短いスニペット>
    - **アップストリームからのパススルー:** <yes/no>

## 注入 — 仕様レベル（infoセクション）

### x-f5xc-cli-domain

- **適用先:** info
- **目的:** エンリッチされた仕様のCLIドメインスラッグ（例：`http_loadbalancer`）を識別します。
- **利用者:** CLI
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-cli-domain": "http_loadbalancer"`
- **アップストリームからのパススルー:** no

### x-f5xc-cli-metadata

- **適用先:** info
- **目的:** CLI全体のメタデータブロック（ツール名、バージョンヒント、ドメイングループ化）。
- **利用者:** CLI
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/cli_metadata.yaml
- **例:** `"x-f5xc-cli-metadata": {"tool": "xcsh", "domain": "http_loadbalancer"}`
- **アップストリームからのパススルー:** no

### x-f5xc-upstream-timestamp

- **適用先:** info
- **目的:** エンリッチファイルの構築元となったアップストリームソース仕様のタイムスタンプ。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "format": "date-time"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-upstream-timestamp": "2026-04-21T12:00:00Z"`
- **アップストリームからのパススルー:** no

### x-f5xc-upstream-etag

- **適用先:** info
- **目的:** アップストリームソース仕様リリースアセットのETag。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-upstream-etag": "\"abc123\""`
- **アップストリームからのパススルー:** no

### x-f5xc-enriched-version

- **適用先:** info
- **目的:** パイプラインによってエンリッチされた仕様に付与されるセマンティックバージョン。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-enriched-version": "3.2.1"`
- **アップストリームからのパススルー:** no

### x-f5xc-glossary

- **適用先:** info
- **目的:** 各ドメイン仕様に適用されるブランディング/用語の用語集ブロック。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/branding.py
- **設定による駆動:** config/branding.yaml
- **例:** `"x-f5xc-glossary": {"XC": "F5 Distributed Cloud"}`
- **アップストリームからのパススルー:** no

### x-f5xc-discovered-at

- **適用先:** info
- **目的:** ライブAPIディスカバリーパスが実行されたタイムスタンプ。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "format": "date-time"}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery.yaml
- **例:** `"x-f5xc-discovered-at": "2026-04-21T09:15:00Z"`
- **アップストリームからのパススルー:** no

### x-f5xc-api-url

- **適用先:** info
- **目的:** ディスカバリー中にプローブされたライブAPIのベースURL。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "format": "uri"}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery.yaml
- **例:** `"x-f5xc-api-url": "https://f5-amer-ent.console.ves.volterra.io"`
- **アップストリームからのパススルー:** no

### x-f5xc-api-reference-url

- **適用先:** info
- **目的:** このドメインのホスティングされたAPIリファレンスドキュメントページへのURL。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "format": "uri"}`
- **注入元:** scripts/utils/external_docs_enricher.py
- **設定による駆動:** none（ドメイン名から導出）
- **例:** `"x-f5xc-api-reference-url": "https://f5xc-salesdemos.github.io/api-specs-enriched/api-reference/sites/"`
- **アップストリームからのパススルー:** no

### x-f5xc-response-time-ms

- **適用先:** info
- **目的:** ディスカバリー中にプローブされたAPIの観測応答時間（ミリ秒）。
- **利用者:** multiple
- **値の型:** number
- **値のスキーマ:** `{"type": "number"}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery.yaml
- **例:** `"x-f5xc-response-time-ms": 42`
- **アップストリームからのパススルー:** no

### x-f5xc-best-practices

- **適用先:** info
- **目的:** ドメイン向けの厳選されたベストプラクティスガイダンス。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "object"}}`
- **注入元:** scripts/utils/best_practices_enricher.py
- **設定による駆動:** config/best_practices.yaml
- **例:** `"x-f5xc-best-practices": [{"id": "bp-1", "text": "Prefer HTTPS"}]`
- **アップストリームからのパススルー:** no

### x-f5xc-guided-workflows

- **適用先:** info
- **目的:** ドメイン内の一般的なタスクを達成するための名前付きステップバイステップワークフロー。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "object"}}`
- **注入元:** scripts/utils/guided_workflow_enricher.py
- **設定による駆動:** config/guided_workflows.yaml
- **例:** `"x-f5xc-guided-workflows": [{"name": "create-lb", "steps": [...]}]`
- **アップストリームからのパススルー:** no

### x-f5xc-acronyms

- **適用先:** info
- **目的:** ドメインごとの略語展開テーブル。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object", "additionalProperties": {"type": "string"}}`
- **注入元:** scripts/utils/acronym_enricher.py
- **設定による駆動:** config/acronyms.yaml
- **例:** `"x-f5xc-acronyms": {"LB": "Load Balancer"}`
- **アップストリームからのパススルー:** no

## 注入 — スキーマレベル（コンポーネントスキーマ）

### x-f5xc-minimum-configuration

- **適用先:** schema
- **目的:** このリソースのPOST/PUTを正常に実行するために必要な最小限のフィールドセット。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/minimum_configuration_enricher.py
- **設定による駆動:** config/minimum_configs.yaml
- **例:** `"x-f5xc-minimum-configuration": {"required_fields": ["name"]}`
- **アップストリームからのパススルー:** no

### x-f5xc-namespace-profile

- **適用先:** info
- **目的:** リソースのネームスペース制約、推奨、および分類メタデータを提供します。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object", "properties": {"constraint": {"type": "object"}, "recommendation": {"type": "object"}, "classification": {"type": "object"}}}`
- **注入元:** scripts/utils/namespace_profile_enricher.py
- **設定による駆動:** config/namespace_profile.yaml
- **例:** `"x-f5xc-namespace-profile": {"constraint": {"allowed": ["system", "shared", "user"]}, "recommendation": {"default": "shared"}, "classification": {"multi_tenant_pattern": "shared-ref"}}`
- **アップストリームからのパススルー:** no

### x-f5xc-displayorder

- **適用先:** schema
- **目的:** UI/CLI表示用のプロパティの推奨順序。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-displayorder": ["name", "description", "spec"]`
- **アップストリームからのパススルー:** no

### x-f5xc-terraform-resource

- **適用先:** schema
- **目的:** このスキーマにマッピングされるTerraformリソースタイプ名。
- **利用者:** Terraform
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-terraform-resource": "volterra_http_loadbalancer"`
- **アップストリームからのパススルー:** no

### x-f5xc-display-name

- **適用先:** schema
- **目的:** リソーススキーマの人間が読める表示名（自動生成をオーバーライド）。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-display-name": "HTTP Load Balancer"`
- **アップストリームからのパススルー:** no

## 注入 — プロパティレベル

### x-f5xc-description

- **適用先:** schema property
- **目的:** アップストリームの `description` を補完するエンリッチされたプロパティ説明。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_descriptions.yaml
- **例:** `"x-f5xc-description": "Fully-qualified domain name used for TLS SNI."`
- **アップストリームからのパススルー:** no

### x-f5xc-validation

- **適用先:** schema property
- **目的:** アップストリームのprotobuf `ves.io.schema.rules` から派生した宣言的バリデーションルール。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/validation_enricher.py
- **設定による駆動:** config/validation_rules.yaml
- **例:** `"x-f5xc-validation": {"min_len": 1, "max_len": 64}`
- **アップストリームからのパススルー:** no

### x-f5xc-examples

- **適用先:** schema property
- **目的:** プロパティの複数の説明的な例の値。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array"}`
- **注入元:** scripts/utils/resource_examples_enricher.py
- **設定による駆動:** config/resource_examples.yaml
- **例:** `"x-f5xc-examples": ["example.com", "api.example.com"]`
- **アップストリームからのパススルー:** no

### x-f5xc-example

- **適用先:** schema property
- **目的:** 単一の正規の例の値。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{}`
- **注入元:** scripts/utils/field_description_enricher.py
- **設定による駆動:** config/field_descriptions.yaml
- **例:** `"x-f5xc-example": "example.com"`
- **アップストリームからのパススルー:** no

### x-f5xc-completion

- **適用先:** schema property
- **目的:** シェル補完ヒント（静的enumまたは動的コマンド）。
- **利用者:** CLI
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-completion": {"source": "command", "cmd": "xcsh namespace list"}`
- **アップストリームからのパススルー:** no

### x-f5xc-defaults

- **適用先:** schema property
- **目的:** 生成されたドキュメントやUIに表示するデフォルト値。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-defaults": {"value": "default"}`
- **アップストリームからのパススルー:** no

### x-f5xc-required-for-operations

- **適用先:** schema property
- **目的:** このプロパティが必要なHTTPオペレーション（POST/PUT/...）をリストします。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-required-for-operations": ["POST", "PUT"]`
- **アップストリームからのパススルー:** no

### x-f5xc-required-for

- **適用先:** schema property
- **目的:** このプロパティが必要な名前付き機能の組み合わせをリストします。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/minimum_configuration_enricher.py
- **設定による駆動:** config/minimum_configs.yaml
- **例:** `"x-f5xc-required-for": ["tls-origin", "mtls"]`
- **アップストリームからのパススルー:** no

### x-f5xc-conditions

- **適用先:** schema property
- **目的:** 条件付き要件（例：兄弟フィールドがXに等しい場合に必須）。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "object"}}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-conditions": [{"when": "tls.enabled == true", "require": "cert"}]`
- **アップストリームからのパススルー:** no

### x-f5xc-deprecated

- **適用先:** schema property
- **目的:** 置き換えガイダンス付きの非推奨通知。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/field_metadata_enricher.py
- **設定による駆動:** config/field_metadata.yaml
- **例:** `"x-f5xc-deprecated": {"since": "3.0.0", "use": "new_field"}`
- **アップストリームからのパススルー:** no

### x-f5xc-server-default

- **適用先:** schema property
- **目的:** クライアントがプロパティを省略した場合にサーバーが割り当てるデフォルト値。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{}`
- **注入元:** scripts/utils/default_value_enricher.py
- **設定による駆動:** config/discovered_defaults.yaml
- **例:** `"x-f5xc-server-default": "ROUND_ROBIN"`
- **アップストリームからのパススルー:** no

### x-f5xc-recommended-value

- **適用先:** schema property
- **目的:** サーバーデフォルトが最適でない場合のフィールドの推奨プロダクション値。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{}`
- **注入元:** scripts/utils/default_value_enricher.py
- **設定による駆動:** config/discovered_defaults.yaml
- **例:** `"x-f5xc-recommended-value": "LEAST_REQUEST"`
- **アップストリームからのパススルー:** no

### x-f5xc-recommended-oneof-variant

- **適用先:** schema property
- **目的:** `oneOf` ブロックにおいて、どのバリアントが推奨されるかを示します。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/default_value_enricher.py
- **設定による駆動:** config/discovered_defaults.yaml
- **例:** `"x-f5xc-recommended-oneof-variant": "tls_parameters"`
- **アップストリームからのパススルー:** no

### x-f5xc-conflicts-with

- **適用先:** schema property
- **目的:** このプロパティと同時に設定できない兄弟プロパティをリストします。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/conflicts_with_enricher.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-conflicts-with": ["plaintext", "auto_cert"]`
- **アップストリームからのパススルー:** no

### x-f5xc-requires

- **適用先:** schema property
- **目的:** あるフィールドが別のフィールドの設定を要求するクロスフィールド依存関係を文書化します。
- **利用者:** compile_catalog.py, xcsh CLI
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "object", "properties": {"field": {"type": "string"}, "required": {"type": "boolean"}, "reason": {"type": "string"}}}}`
- **注入元:** scripts/utils/dependency_enricher.py
- **設定による駆動:** config/minimum_configs.yaml（dependenciesセクション）
- **例:** `"x-f5xc-requires": [{"field": "tls_config", "required": true, "reason": "use_tls requires tls_config sub-field"}]`
- **アップストリームからのパススルー:** no

### x-f5xc-constraints

- **適用先:** schema property
- **目的:** ライブAPIプローブまたは静的パターンから派生した数値/文字列の制約。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/constraint_enricher.py
- **設定による駆動:** config/constraint_patterns.yaml
- **例:** `"x-f5xc-constraints": {"min": 1, "max": 65535, "source": "live-api"}`
- **アップストリームからのパススルー:** no

### x-f5xc-uniqueness

- **適用先:** schema property
- **目的:** フィールドがそのスコープ内で一意でなければならないかどうかを宣言します。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/uniqueness_enricher.py
- **設定による駆動:** hardcoded
- **例:** `"x-f5xc-uniqueness": {"scope": "namespace"}`
- **アップストリームからのパススルー:** no

## 注入 — オペレーションレベル

### x-f5xc-required-fields

- **適用先:** operation
- **目的:** 成功のためにオペレーションボディで提供する必要があるフィールド名。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/operation_metadata_enricher.py
- **設定による駆動:** config/operation_metadata.yaml
- **例:** `"x-f5xc-required-fields": ["metadata.name", "spec.domains"]`
- **アップストリームからのパススルー:** no

### x-f5xc-danger-level

- **適用先:** operation
- **目的:** オペレーションの影響範囲を分類します（low/medium/high/critical）。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "enum": ["low", "medium", "high", "critical"]}`
- **注入元:** scripts/utils/operation_metadata_enricher.py
- **設定による駆動:** config/operation_metadata.yaml
- **例:** `"x-f5xc-danger-level": "high"`
- **アップストリームからのパススルー:** no

### x-f5xc-confirmation-required

- **適用先:** operation
- **目的:** CLI/UIが実行前にユーザーに確認を求めるべきかどうか。
- **利用者:** multiple
- **値の型:** boolean
- **値のスキーマ:** `{"type": "boolean"}`
- **注入元:** scripts/utils/operation_metadata_enricher.py
- **設定による駆動:** config/operation_metadata.yaml
- **例:** `"x-f5xc-confirmation-required": true`
- **アップストリームからのパススルー:** no

### x-f5xc-side-effects

- **適用先:** operation
- **目的:** オペレーションの観測可能な副作用をリストします（再起動、再構成など）。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/utils/operation_metadata_enricher.py
- **設定による駆動:** config/operation_metadata.yaml
- **例:** `"x-f5xc-side-effects": ["invalidates-cache"]`
- **アップストリームからのパススルー:** no

### x-f5xc-discovered-response-time

- **適用先:** operation
- **目的:** ディスカバリー中にこのオペレーションで経験的に測定された応答時間。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery_enrichment.yaml
- **例:** `"x-f5xc-discovered-response-time": {"p50_ms": 40, "p95_ms": 120}`
- **アップストリームからのパススルー:** no

### x-f5xc-discovered-rate-limits

- **適用先:** operation
- **目的:** ライブAPIから検出されたレート制限ヘッダー/動作。
- **利用者:** multiple
- **値の型:** object
- **値のスキーマ:** `{"type": "object"}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery_enrichment.yaml
- **例:** `"x-f5xc-discovered-rate-limits": {"limit": 100, "window_s": 60}`
- **アップストリームからのパススルー:** no

### x-f5xc-discovered-error-catalog

- **適用先:** operation
- **目的:** ライブディスカバリー中に観測されたエラーレスポンスのカタログ（サンプルペイロード付き）。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "object"}}`
- **注入元:** scripts/utils/discovery_enricher.py
- **設定による駆動:** config/discovery_enrichment.yaml
- **例:** `"x-f5xc-discovered-error-catalog": [{"status": 400, "reason": "bad_request"}]`
- **アップストリームからのパススルー:** no

## 注入 — インデックスレベル（ドメインメタデータ）

### x-f5xc-category

- **適用先:** info
- **目的:** ドメインのトップレベルCLI / UI / ドキュメント / Terraformグループ化カテゴリ。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-category": "networking"`
- **アップストリームからのパススルー:** no

### x-f5xc-primary-resources

- **適用先:** info
- **目的:** ドメインを定義するプライマリリソースタイプのリスト。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-primary-resources": ["http_loadbalancer"]`
- **アップストリームからのパススルー:** no

### x-f5xc-critical-resources

- **適用先:** info
- **目的:** 特別な注意が必要なリソース（本番環境に重要）。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/critical_resources.yaml
- **例:** `"x-f5xc-critical-resources": ["tls_certificate"]`
- **アップストリームからのパススルー:** no

### x-f5xc-description-short

- **適用先:** info
- **目的:** 短い（約60文字）ドメイン説明。長い説明のプロパティレベルにも適用されます。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/property_description_short_enricher.py
- **設定による駆動:** config/property_description_short.yaml
- **例:** `"x-f5xc-description-short": "Layer-7 HTTPS load balancing."`
- **アップストリームからのパススルー:** no

### x-f5xc-description-medium

- **適用先:** info
- **目的:** 中程度（約150文字）のドメイン説明。プロパティレベルにも適用されます。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/property_description_short_enricher.py
- **設定による駆動:** config/property_description_short.yaml
- **例:** `"x-f5xc-description-medium": "HTTP/HTTPS load balancer with advanced routing, WAF, and TLS."`
- **アップストリームからのパススルー:** no

### x-f5xc-description-long

- **適用先:** info
- **目的:** 長い（約500文字）ドメイン説明。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/utils/description_enricher.py
- **設定による駆動:** config/domain_descriptions.yaml
- **例:** `"x-f5xc-description-long": "Full paragraph describing the domain..."`
- **アップストリームからのパススルー:** no

### x-f5xc-complexity

- **適用先:** info
- **目的:** このドメインでの設定作成の相対的な複雑さの階層。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string", "enum": ["low", "medium", "high"]}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-complexity": "medium"`
- **アップストリームからのパススルー:** no

### x-f5xc-requires-tier

- **適用先:** info
- **目的:** 必要な最小F5 XCサブスクリプションティア。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-requires-tier": "enterprise"`
- **アップストリームからのパススルー:** no

### x-f5xc-is-preview

- **適用先:** info
- **目的:** ドメインがプレビュー/ベータ機能であることをフラグ付けします。
- **利用者:** multiple
- **値の型:** boolean
- **値のスキーマ:** `{"type": "boolean"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-is-preview": false`
- **アップストリームからのパススルー:** no

### x-f5xc-use-cases

- **適用先:** info
- **目的:** このドメインがサポートする名前付きユースケース。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-use-cases": ["tls-termination", "waf"]`
- **アップストリームからのパススルー:** no

### x-f5xc-icon

- **適用先:** info
- **目的:** UIでこのドメインをレンダリングする際に使用するアイコン識別子。
- **利用者:** Web UI
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-icon": "f5xc:load-balancer"`
- **アップストリームからのパススルー:** no

### x-f5xc-logo-svg

- **適用先:** info
- **目的:** ドメインを表すブランドロゴのインラインSVG（またはパス）。
- **利用者:** Web UI
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-logo-svg": "<svg>...</svg>"`
- **アップストリームからのパススルー:** no

### x-f5xc-related-domains

- **適用先:** info
- **目的:** このドメインと一般的に併用される他のドメインへのクロスリンク。
- **利用者:** multiple
- **値の型:** array
- **値のスキーマ:** `{"type": "array", "items": {"type": "string"}}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-related-domains": ["origin_pool", "tls_certificate"]`
- **アップストリームからのパススルー:** no

### x-f5xc-doc-section

- **適用先:** info
- **目的:** レンダリングされたドキュメントのドキュメントセクション/ナビゲーショングループ化スラッグ。
- **利用者:** multiple
- **値の型:** string
- **値のスキーマ:** `{"type": "string"}`
- **注入元:** scripts/merge_specs.py
- **設定による駆動:** config/domain_patterns.yaml
- **例:** `"x-f5xc-doc-section": "load-balancing"`
- **アップストリームからのパススルー:** no

## アップストリームパススルー

### x-ves-proto-package

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-ves-proto-package": "ves.io.schema.virtual_host"`
- **アップストリームからのパススルー:** yes

### x-ves-proto-file

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-ves-proto-file": "ves.io/schema/virtual_host/types.proto"`
- **アップストリームからのパススルー:** yes

### x-ves-proto-message

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-ves-proto-message": "ves.io.schema.virtual_host.CreateSpecType"`
- **アップストリームからのパススルー:** yes

### x-ves-proto-service

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-ves-proto-service": "ves.io.schema.virtual_host.API"`
- **アップストリームからのパススルー:** yes

### x-ves-proto-rpc

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-ves-proto-rpc": "ves.io.schema.api_sec.api_crawler.API.Create"`
- **アップストリームからのパススルー:** yes

### x-displayname

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** `"x-displayname": "Namespace"`
- **アップストリームからのパススルー:** yes

### x-ves-oneof

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** F5アップストリームドキュメントを参照してください。
- **アップストリームからのパススルー:** yes

### x-ves-default

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** F5アップストリームドキュメントを参照してください。
- **アップストリームからのパススルー:** yes

### x-ves-required

- **適用先:** upstream
- **目的:** F5アップストリーム仕様からそのまま保持。
- **利用者:** N/A
- **値の型:** varies
- **値のスキーマ:** N/A
- **注入元:** upstream
- **設定による駆動:** upstream
- **例:** F5アップストリームドキュメントを参照してください。
- **アップストリームからのパススルー:** yes
