# Hermes Desktop Light Builder

这个仓库独立维护构建说明和 GitHub Actions 工作流。它每天检查
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 的 `main`，
仅在新的 commit 尚未发布时，在 GitHub 的 Apple Silicon macOS runner 上从该精确
commit 构建 **Hermes Light**。这里不复制或长期维护上游 Desktop 源码。

目前上游最新稳定标签 `v2026.9.24` 尚未包含 Light 专用打包配置，因此产物是
**上游 main 的源码快照构建**，并非上游正式发布版。上游更新可能使构建失败；
工作流会在验证不通过时停止发布。

Light 是上游定义的远程客户端变体。构建出的应用不包含 Hermes Python 后端或
`agent-payload`；用户首次启动时可选择 **Connect to existing Hermes**，在应用内输入
远程地址并使用自己的账号登录。构建过程不会运行上游的 `install.sh`，也不会修改远程服务器。

## 下载与使用

1. 在本仓库的 [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases)
   下载适用于 Apple Silicon 的 DMG。`-unsigned.1` 结尾的预发布版本仅供手动安装。
2. 将 **Hermes Light.app** 拖入 `/Applications`，启动后选择 **Connect to existing Hermes**。
3. 在应用表单中填写自己的 HTTPS 地址，点击 **Test connection**，再登录并应用连接。
   服务器地址和密码不会写进这个公开仓库或打包进应用。

无签名预发布包可能被 macOS Gatekeeper 拦截。确认下载来源后，可以在系统设置的
“隐私与安全性”中允许打开，或自行对该应用执行 `xattr -cr`。首次发布正式签名包后，
已有的无签名安装需要手动换成签名版；后续应用内更新才有可靠的签名链。

## 自动构建

工作流 [`.github/workflows/build-light.yml`](.github/workflows/build-light.yml) 每天
03:17 UTC（北京时间 11:17）运行，也可在 Actions 页面手动运行。
它会：

1. 解析上游 `main` 的精确 commit，并检验源码 checkout；
2. 在临时 runner 上安装 Node 和构建工具，运行上游 Desktop 的 `light` 构建；
3. 检查应用身份、Light 构建标记、更新源，以及 DMG、ZIP、更新清单；
4. 把产物发布到本仓库的 GitHub Releases。ZIP 是 macOS 应用内更新所需的包。

上游当前 macOS 配置在没有它的 R2 发布地址时，不会生成 GitHub 更新源。本仓库在临时
checkout 中给打包配置添加一处 [GitHub feed 调整](scripts/patch_mac_feed.py)，使包内
`app-update.yml` 和 Release 的 `stable-mac.yml` 更新清单都指向本仓库；不会改动
上游仓库。这个仓库只发布 Light，所以使用客户端在运行时请求的 `stable` 通道名。

这里使用普通 Desktop 打包路径。应用版本由上游 commit 的 UTC 提交时间生成，
格式为 `年.月.日时分秒` 三段数字；相同 commit 会得到相同版本，新的提交会产生
更高版本。上游 commit 记录在 Release 说明中。CI 所用的 Python 只负责临时
构建工具，应用内不带 Python 运行时。

### 签名与更新

在配置完整签名材料前，工作流发布 `vX.Y.Z-unsigned.1` **预发布版**，供手动下载安装。
配置以下 GitHub Actions Secrets 后，新构建会发布正式 `vX.Y.Z` Release：

| Secret | 内容 |
| --- | --- |
| `MACOS_CERTIFICATE_P12` | Developer ID Application `.p12` 的 base64 内容 |
| `MACOS_CERTIFICATE_PASSWORD` | 该 `.p12` 的密码 |
| `APPLE_API_KEY_P8` | App Store Connect API key 的 `.p8` 内容 |
| `APPLE_API_KEY_ID` | API key ID |
| `APPLE_API_ISSUER` | API issuer ID |

任一项缺失时，不会误发一个标为正式版的未公证包。不要把证书、私钥或远程 Hermes
密码提交到仓库。正式包的内置更新源指向本仓库的 GitHub Releases；发布后还应在
真实 macOS 安装中验证一次更新检查、下载与重启。

## 来源

Desktop 源码、产品名称和 Light 变体均来自
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)，上游项目采用
[MIT License](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE)。
本仓库是独立的构建自动化，不代表 Nous Research 官方发布。
