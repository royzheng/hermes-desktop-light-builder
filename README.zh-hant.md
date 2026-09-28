# Hermes Desktop Light Builder

**語言：** [English](README.md) · [简体中文](README.zh.md) · 繁體中文 · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md)

本儲存庫為 Apple Silicon Mac 建置 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 桌面應用程式的 **Hermes Light** 版本。Light 只作為遠端用戶端，不包含 Hermes Python 後端或 `agent-payload`。本儲存庫維護自己的說明及 GitHub Actions 工作流程，每次建置都使用上游 `main` 的特定提交；產物是原始碼快照，並非上游官方發行版。

## 下載與連線

1. 從本儲存庫的 [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases) 下載 Apple Silicon DMG。標籤以 `-unsigned.1` 結尾的是未簽署預覽版，須**手動安裝**。
2. 將 **Hermes Light.app** 拖入 `/Applications` 並啟動。
3. 首次啟動時選擇 **Connect to existing Hermes**，輸入自己的 HTTPS 伺服器網址，按 **Test connection**，再於應用程式內登入並套用連線。儲存庫與應用程式套件都不包含你的伺服器密碼或私人網址。

建置過程不會執行上游 `install.sh`，也不會修改伺服器。macOS Gatekeeper 可能封鎖未簽署預覽版；確認下載來源後，可在「系統設定 → 隱私權與安全性」允許開啟，或對該應用程式執行 `xattr -cr`。

## 建置與更新

[建置工作流程](.github/workflows/build-light.yml) 每天 **03:17 UTC**（北京時間 11:17）執行，也可在 Actions 中手動啟動。它會取用上游的特定提交，在 Apple Silicon runner 上建置 Light，驗證應用程式識別、Light 標記、更新設定及發行檔案，再發佈到本儲存庫的 Releases。若上游變更導致建置或驗證失敗，工作流程會停止發佈。

建立本儲存庫時，上游最新穩定標籤尚未包含 Light 封裝設定，因此工作流程追蹤 `main`。版本號取自上游提交的 UTC 時間；Release 說明會列出確切提交。CI 暫時使用 Python 建置工具，最終應用程式不含本機 Python 執行環境。

應用程式內的 `app-update.yml` 指向 `royzheng/hermes-desktop-light-builder`，ZIP 與 `stable-mac.yml` 用於 `stable` 更新通道。但**未簽署預覽版無法在 macOS 上可靠地自動更新**，而且預覽版不會成為 GitHub 的最新正式 Release。第一個已簽署且公證的正式版須手動覆蓋安裝；之後仍須以另一次簽署發行驗證應用程式內更新。簽署所需的 GitHub Actions Secrets 與更多技術細節請參閱[英文 README](README.md#enable-signed-releases)。

## 來源

Desktop 原始碼、產品名稱與 Light 版本來自採用 [MIT 授權條款](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 的 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。本儲存庫為獨立建置自動化，**並非 Nous Research 官方發行版**。
