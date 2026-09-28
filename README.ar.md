# Hermes Desktop Light Builder

**اللغات:** [English](README.md) · [简体中文](README.zh.md) · [繁體中文](README.zh-hant.md) · [日本語](README.ja.md) · العربية · [Русский](README.ru.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Español](README.es.md)

يبني هذا المستودع نسخة **Hermes Light** المخصّصة للاتصال بخادم بعيد من تطبيق سطح المكتب في [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)، لأجهزة Mac بمعالج Apple Silicon. يحتفظ المستودع بوثائقه وسير عمل GitHub Actions الخاص به، ويستخدم في كل بناء نسخة محددة من فرع `main` في المشروع الأصلي. هذه إصدارات مبنية من لقطات للشيفرة المصدرية، وليست إصدارات رسمية من المشروع الأصلي.

## التنزيل والاتصال

1. نزّل ملف DMG الخاص بـ Apple Silicon من صفحة [Releases](https://github.com/royzheng/hermes-desktop-light-builder/releases). الإصدارات التي تنتهي علامتها بـ `-unsigned.1` تجريبية وغير موقّعة، وتتطلب **تثبيتاً يدوياً**.
2. اسحب **Hermes Light.app** إلى `/Applications` ثم افتحه.
3. عند التشغيل الأول، اختر **Connect to existing Hermes**، وأدخل عنوان HTTPS لخادمك، ثم اضغط **Test connection**. بعد ذلك سجّل الدخول من داخل التطبيق وفعّل الاتصال. لا يحتوي المستودع أو حزمة التطبيق على كلمة مرور خادمك أو عنوانه الخاص.

لا تتضمن نسخة Light خلفية Hermes المكتوبة بلغة Python أو `agent-payload`. ولا ينفّذ البناء ملف `install.sh` الخاص بالمشروع الأصلي أو يغيّر خادمك. قد يمنع macOS Gatekeeper فتح النسخة غير الموقّعة؛ بعد التحقق من مصدر التنزيل، اسمح بفتحها من إعدادات النظام ← الخصوصية والأمان، أو نفّذ `xattr -cr` على التطبيق.

## البناء والتحديثات

يعمل [سير البناء](.github/workflows/build-light.yml) يومياً الساعة **03:17 UTC**، ويمكن تشغيله يدوياً من Actions. يبني نسخة Light من التزام محدد في المشروع الأصلي، ويتحقق من هوية التطبيق ومحتواه وإعدادات التحديث وملفات النشر، ثم يرفعها إلى Releases في هذا المستودع. إذا أدّت تغييرات المشروع الأصلي إلى فشل البناء أو التحقق، يتوقف النشر.

عند إنشاء هذا المستودع، لم تتضمن أحدث علامة مستقرة في المشروع الأصلي إعدادات حزم Light، لذلك يتابع سير العمل فرع `main`. يُشتق رقم النسخة من وقت التزام المشروع الأصلي بتوقيت UTC، وتذكر ملاحظات الإصدار الالتزام الدقيق. تُستخدم Python مؤقتاً في CI كأداة بناء، ولا تتضمن النسخة النهائية بيئة Python محلية.

يشير ملف `app-update.yml` داخل التطبيق إلى `royzheng/hermes-desktop-light-builder`. لكن **التحديث التلقائي داخل تطبيق macOS غير موثوق مع النسخ التجريبية غير الموقّعة**، كما أن النسخة التجريبية لا تُعد أحدث إصدار رسمي على GitHub. ثبّت أول إصدار رسمي موقّع وموثّق يدوياً فوق النسخة التجريبية، ثم اختبر التحديث الداخلي بإصدار موقّع لاحق. راجع [README الإنجليزية](README.md#enable-signed-releases) لمعرفة مفاتيح GitHub Actions المطلوبة للتوقيع والتفاصيل التقنية.

## المصدر

تأتي شيفرة Desktop والاسم ونسخة Light من [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) المرخّص بموجب [MIT](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE). هذا المستودع أتمتة بناء مستقلة، **وليس إصداراً رسمياً من Nous Research**.
