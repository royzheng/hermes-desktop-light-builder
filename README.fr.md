# Hermes Desktop Light Builder

**Langues :** [English](README.md) · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · Français · [Deutsch](README.de.md) · [Español](README.es.md)

Ce dépôt construit **Hermes Light**, la variante du logiciel de bureau [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) qui se connecte uniquement à un serveur distant, pour les Mac équipés d’une puce Apple Silicon. Il contient sa propre documentation et son workflow GitHub Actions. Chaque compilation utilise un commit précis de la branche `main` du projet d’origine. Il s’agit de compilations issues d’instantanés du code source, et non de publications officielles du projet d’origine.

## Télécharger et se connecter

1. Téléchargez le DMG pour Apple Silicon depuis les [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases) de ce dépôt. Les versions dont le tag se termine par `-unsigned.1` sont des préversions non signées à **installer manuellement**.
2. Glissez **Hermes Light.app** dans `/Applications`, puis ouvrez l’application.
3. Au premier lancement, choisissez **Connect to existing Hermes**, saisissez l’URL HTTPS de votre serveur, puis cliquez sur **Test connection**. Connectez-vous ensuite dans l’application et appliquez la connexion. Ni le dépôt ni le paquet de l’application ne contiennent votre mot de passe ou l’adresse privée de votre serveur.

Hermes Light n’embarque ni le serveur Hermes en Python ni `agent-payload`. La compilation n’exécute pas le fichier `install.sh` du projet d’origine et ne modifie pas votre serveur. macOS Gatekeeper peut bloquer une préversion non signée : après avoir vérifié la provenance du téléchargement, autorisez son ouverture dans « Réglages Système → Confidentialité et sécurité » ou exécutez `xattr -cr` sur cette application.

## Compilations et mises à jour

Le [workflow de compilation](.github/workflows/build-light.yml) s’exécute chaque jour à **03:17 UTC** et peut aussi être lancé manuellement depuis Actions. Il compile Light depuis un commit précis, vérifie l’identité de l’application, son contenu, sa configuration de mise à jour et ses fichiers de publication, puis publie les résultats dans les Releases de ce dépôt. Si une modification du projet d’origine fait échouer la compilation ou les vérifications, la publication s’arrête.

Lors de la création de ce dépôt, le dernier tag stable du projet d’origine ne contenait pas encore la configuration de paquetage Light ; le workflow suit donc `main`. La version est dérivée de la date UTC du commit, qui figure dans les notes de publication. Python sert uniquement d’outil de compilation temporaire dans la CI ; l’application finale ne contient pas d’environnement Python local.

Le fichier `app-update.yml` intégré à l’application pointe vers `royzheng/hermes-desktop-light-builder`. Toutefois, **les mises à jour automatiques sous macOS ne sont pas fiables avec une préversion non signée**, et une préversion ne devient pas le dernier Release officiel de GitHub. Installez manuellement la première version de production signée et notarisée par-dessus la préversion, puis vérifiez la mise à jour intégrée avec une version signée ultérieure. Les secrets GitHub Actions nécessaires à la signature et les détails techniques figurent dans le [README anglais](README.md#enable-signed-releases).

## Origine

Le code de Desktop, le nom du produit et la variante Light proviennent de [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), sous [licence MIT](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE). Ce dépôt est une automatisation de compilation indépendante, **pas une publication officielle de Nous Research**.
