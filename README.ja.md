# Hermes Desktop Light Builder

**言語：** [English](README.md) · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · 日本語 · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md)

このリポジトリは、[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) のデスクトップアプリのリモート専用版 **Hermes Light** を Apple Silicon Mac 向けにビルドします。独自のドキュメントと GitHub Actions ワークフローを管理し、毎回 upstream の `main` から特定のコミットをチェックアウトします。成果物はソースのスナップショットであり、upstream の公式リリースではありません。

## ダウンロードと接続

1. このリポジトリの [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases) から Apple Silicon 用 DMG をダウンロードします。タグが `-unsigned.1` で終わるものは未署名のプレビュー版で、**手動インストール**が必要です。
2. **Hermes Light.app** を `/Applications` にドラッグして起動します。
3. 初回起動時に **Connect to existing Hermes** を選び、自分の HTTPS サーバー URL を入力します。**Test connection** を実行してから、アプリ内でログインし、接続を適用します。サーバーのパスワードや個人用 URL はリポジトリにもアプリにも含まれません。

Light には Hermes の Python バックエンドや `agent-payload` は同梱されません。ビルド時に upstream の `install.sh` は実行されず、サーバーも変更されません。macOS Gatekeeper が未署名版をブロックした場合は、入手元を確認したうえで「システム設定 → プライバシーとセキュリティ」から許可するか、そのアプリに `xattr -cr` を実行してください。

## ビルドと更新

[ワークフロー](.github/workflows/build-light.yml) は毎日 **03:17 UTC** に実行され、Actions から手動実行もできます。upstream の特定コミットで Light をビルドし、アプリの識別情報、Light の構成、更新設定、配布ファイルを検証して、このリポジトリの Releases に公開します。upstream の変更でビルドや検証が失敗した場合は公開を停止します。

このリポジトリの作成時点では upstream の安定版タグに Light 用のパッケージ設定がなかったため、`main` を追跡しています。バージョンは upstream コミットの UTC 時刻から生成され、Release ノートにコミットが記載されます。CI では一時的に Python をビルドツールとして使いますが、完成したアプリにローカル Python ランタイムは含まれません。

アプリ内の `app-update.yml` は `royzheng/hermes-desktop-light-builder` を指します。ただし、**未署名プレビュー版では macOS のアプリ内自動更新は安定して利用できません**。プレビュー版は GitHub の最新正式 Release にもなりません。最初の署名・公証済み正式版は手動で上書きインストールし、その次の署名済みリリースでアプリ内更新を検証してください。署名に必要な Secrets と技術詳細は[英語版 README](README.md#enable-signed-releases) を参照してください。

## 出典

Desktop のソース、製品名、Light 版は [MIT ライセンス](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) の [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) に由来します。このリポジトリは独立したビルド自動化であり、**Nous Research の公式リリースではありません**。
