# Hermes Desktop Light Builder

**Sprachen:** [English](README.md) · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · Deutsch · [Español](README.es.md)

Dieses Repository erstellt **Hermes Light**, die reine Remote-Variante der Desktop-App von [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), für Macs mit Apple Silicon. Es enthält eine eigene Dokumentation und einen GitHub-Actions-Workflow. Jeder Build verwendet einen bestimmten Commit aus dem Upstream-Branch `main`. Die Ergebnisse sind Builds aus Quellcode-Snapshots und keine offiziellen Upstream-Releases.

## Herunterladen und verbinden

1. Lade die Apple-Silicon-DMG von den [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases) dieses Repositories herunter. Versionen mit dem Tag-Suffix `-unsigned.1` sind unsignierte Vorabversionen zur **manuellen Installation**.
2. Ziehe **Hermes Light.app** nach `/Applications` und öffne die App.
3. Wähle beim ersten Start **Connect to existing Hermes**, gib die HTTPS-Adresse deines Servers ein und klicke auf **Test connection**. Melde dich anschließend in der App an und übernimm die Verbindung. Weder das Repository noch das App-Paket enthalten dein Serverpasswort oder deine private Serveradresse.

Hermes Light enthält weder das Python-Backend von Hermes noch `agent-payload`. Beim Build wird das Upstream-Skript `install.sh` nicht ausgeführt und dein Server nicht verändert. macOS Gatekeeper kann eine unsignierte Vorabversion blockieren. Prüfe zuerst die Downloadquelle und erlaube dann das Öffnen unter „Systemeinstellungen → Datenschutz & Sicherheit“ oder führe `xattr -cr` für diese App aus.

## Builds und Updates

Der [Build-Workflow](.github/workflows/build-light.yml) läuft täglich um **03:17 UTC** und kann in Actions manuell gestartet werden. Er erstellt Light aus einem bestimmten Upstream-Commit, prüft App-Identität, Paketinhalt, Update-Konfiguration und Release-Dateien und veröffentlicht die Artefakte in den Releases dieses Repositories. Wenn eine Upstream-Änderung den Build oder die Prüfungen fehlschlagen lässt, wird nichts veröffentlicht.

Als dieses Repository erstellt wurde, enthielt das neueste stabile Upstream-Tag noch keine Paketkonfiguration für Light. Daher verfolgt der Workflow `main`. Die Versionsnummer wird aus der UTC-Zeit des Upstream-Commits abgeleitet; die Release-Notizen nennen den genauen Commit. Python wird in CI nur vorübergehend als Build-Werkzeug verwendet. Die fertige App enthält keine lokale Python-Laufzeitumgebung.

Die integrierte Datei `app-update.yml` verweist auf `royzheng/hermes-desktop-light-builder`. **Automatische macOS-Updates sind mit unsignierten Vorabversionen jedoch nicht zuverlässig möglich**; Vorabversionen gelten bei GitHub außerdem nicht als neuestes reguläres Release. Installiere das erste signierte und notarisierte Produktions-Release manuell über die Vorabversion. Teste die integrierte Updatefunktion anschließend mit einem weiteren signierten Release. Die benötigten GitHub-Actions-Secrets und technische Details stehen in der [englischen README](README.md#enable-signed-releases).

## Herkunft

Desktop-Quellcode, Produktname und Light-Variante stammen aus [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) unter der [MIT-Lizenz](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE). Dieses Repository automatisiert Builds unabhängig und ist **kein offizielles Release von Nous Research**.
