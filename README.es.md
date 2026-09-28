# Hermes Desktop Light Builder

**Idiomas:** [English](README.md) · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · [العربية](README.ar.md) · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · Español

Este repositorio compila **Hermes Light**, la variante de la aplicación de escritorio de [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) que solo se conecta a un servidor remoto, para Mac con Apple Silicon. Mantiene su propia documentación y un flujo de GitHub Actions. Cada compilación usa un commit concreto de la rama `main` del proyecto original. Los resultados son compilaciones de instantáneas del código fuente, no versiones oficiales del proyecto original.

## Descargar y conectar

1. Descarga el DMG para Apple Silicon desde [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases). Las versiones cuya etiqueta termina en `-unsigned.1` son versiones preliminares sin firma que requieren **instalación manual**.
2. Arrastra **Hermes Light.app** a `/Applications` y abre la aplicación.
3. En el primer inicio, elige **Connect to existing Hermes**, introduce la URL HTTPS de tu servidor y pulsa **Test connection**. Después inicia sesión en la aplicación y aplica la conexión. Ni el repositorio ni el paquete de la aplicación contienen la contraseña ni la dirección privada de tu servidor.

Hermes Light no incluye el backend de Hermes en Python ni `agent-payload`. La compilación no ejecuta el `install.sh` del proyecto original ni modifica tu servidor. macOS Gatekeeper puede bloquear una versión sin firma. Tras verificar la procedencia de la descarga, permite abrirla en «Configuración del Sistema → Privacidad y seguridad» o ejecuta `xattr -cr` sobre esa aplicación.

## Compilaciones y actualizaciones

El [flujo de compilación](.github/workflows/build-light.yml) se ejecuta todos los días a las **03:17 UTC** y también puede iniciarse manualmente en Actions. Compila Light desde un commit concreto, verifica la identidad de la aplicación, su contenido, la configuración de actualizaciones y los archivos de publicación, y publica los artefactos en Releases de este repositorio. Si un cambio del proyecto original rompe la compilación o las comprobaciones, se detiene la publicación.

Cuando se creó este repositorio, la última etiqueta estable del proyecto original todavía no incluía la configuración de empaquetado de Light; por eso el flujo sigue `main`. La versión se deriva de la fecha UTC del commit original, que aparece en las notas de publicación. CI utiliza Python solo como herramienta temporal de compilación; la aplicación final no incluye un entorno de Python local.

El archivo `app-update.yml` de la aplicación apunta a `royzheng/hermes-desktop-light-builder`. Sin embargo, **las actualizaciones automáticas de macOS no son fiables con versiones preliminares sin firma**, y una versión preliminar no cuenta como el último Release de producción en GitHub. Instala manualmente la primera versión de producción firmada y notarizada sobre la preliminar; después verifica la actualización integrada con otra versión firmada. Los secretos de GitHub Actions necesarios para la firma y los detalles técnicos están en el [README en inglés](README.md#enable-signed-releases).

## Origen

El código de Desktop, el nombre del producto y la variante Light proceden de [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), bajo [licencia MIT](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE). Este repositorio automatiza las compilaciones de forma independiente y **no es una versión oficial de Nous Research**.
