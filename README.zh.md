# Hermes Desktop Light Builder

**语言：** [English](README.md) · 简体中文 · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md)

本仓库为 Apple Silicon Mac 构建 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 桌面应用的 **Hermes Light** 变体。Light 只作为远程客户端，不捆绑 Hermes Python 后端或 `agent-payload`。仓库维护独立的说明和 GitHub Actions 工作流，每次构建都检出上游 `main` 的一个精确提交；产物是源码快照构建，并非上游官方发布版。

## 下载并连接

1. 从本仓库的 [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases) 下载 Apple Silicon DMG。标签以 `-unsigned.1` 结尾的是未签名预览版，需要**手动安装**。
2. 将 **Hermes Light.app** 拖入 `/Applications` 并启动。
3. 首次启动选择 **Connect to existing Hermes**，填写你自己的 HTTPS 服务器地址，点 **Test connection**，然后在应用内登录并应用连接。仓库和应用包都不包含你的服务器密码或私人地址。

构建不会运行上游 `install.sh`，也不会修改服务器。macOS Gatekeeper 可能拦截未签名预览版；确认下载来源后，可在“系统设置 → 隐私与安全性”中允许打开，或对该应用执行 `xattr -cr`。

## 构建与更新

[构建工作流](.github/workflows/build-light.yml) 每天 **03:17 UTC**（北京时间 11:17）运行，也可在 Actions 中手动启动。它检出上游的精确提交，在 Apple Silicon runner 上构建 Light，验证应用身份、Light 标记、更新配置及发布文件，然后发布到本仓库的 Releases。上游改动若使构建或验证失败，工作流会停止发布。

创建本仓库时，上游最新稳定标签还没有 Light 打包配置，因此工作流跟踪 `main`。版本号取自上游提交的 UTC 时间；Release 说明会列出精确提交。CI 临时使用 Python 构建工具，最终应用不带本地 Python 运行时。

应用包内的 `app-update.yml` 指向 `royzheng/hermes-desktop-light-builder`，ZIP 和 `stable-mac.yml` 用于 `stable` 更新通道。但**未签名预览版不能可靠地在 macOS 应用内自动更新**，而且预发布版不会成为 GitHub 的最新正式 Release。首个签名并公证的正式版本需要手动覆盖安装；之后还需用下一次签名发布验证应用内更新。签名所需的 GitHub Actions Secrets 和更多实现细节见 [英文 README](README.md#enable-signed-releases)。

## 来源

Desktop 源码、产品名称和 Light 变体来自采用 [MIT 许可证](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 的 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。本仓库是独立构建自动化，**不代表 Nous Research 官方发布**。
