# Fonts

All three families are published under the SIL Open Font License 1.1, which
allows redistribution together with the licence text (`OFL.txt` in this folder).

| Family | Files | Source |
|---|---|---|
| Assistant | `Assistant-*.ttf`, `AssistantExtraLight-*`, `AssistantLight-*`, `AssistantSemiBold-regular.ttf` | https://github.com/hafontia/Assistant |
| Oswald | `OswaldExtraLight-regular.ttf`, `OswaldLight-regular.ttf` | https://github.com/googlefonts/OswaldFont |
| Work Sans | `WorkSansExtraLight-italic.ttf` | https://github.com/weiweihuanghuang/Work-Sans |

The template degrades gracefully: if a file is missing, the browser falls back
to the generic `sans-serif` in the font stack. Nothing breaks, the page just
looks less like the reference.

To swap the typeface, replace the files and edit the `@font-face` block at the
top of `../cv-template.html`.
