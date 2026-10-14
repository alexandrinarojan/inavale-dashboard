"""Builds the dashboard into a single file: index.html (in the project root).

The page is assembled from:
  page.html        page structure, with four placeholders
  styles.css       all styles             -> <!-- STYLES -->
  fonts/*.woff2    the two fonts, embedded -> <!-- FONTS -->
  vendor/chart.umd.js  Chart.js            -> <!-- CHART_JS -->
  data.json, i18n_en.json, chat_answers.json and the JS files -> <!-- SCRIPTS -->

Run: python3 src/build.py
"""

import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The JavaScript files share one global scope and are loaded in this order.
JS_FILES = [
    "1_base.js",
    "2_screens_layers12.js",
    "3_screens_layers34.js",
    "4_screens_segments.js",
    "5_screen_data.js",
    "6_ui_chat.js",
]


# Fonts embedded in the page (no request to Google Fonts): (family, file prefix, weights).
# Each weight has a "latin" and a "latin-ext" file (ș, ț, ă and the other letters of Romanian).
FONTS = [
    ("IBM Plex Sans", "ibm-plex-sans", [400, 500, 600]),
    ("Source Serif 4", "source-serif-4", [400, 600]),
]
RANGES = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
    "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,"
    "U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,"
    "U+2C60-2C7F,U+A720-A7FF",
}


def fonts_css():
    out = []
    for family, prefix, weights in FONTS:
        for w in weights:
            for subset in ("latin-ext", "latin"):
                with open(
                    os.path.join(HERE, "fonts", f"{prefix}-{subset}-{w}-normal.woff2"),
                    "rb",
                ) as f:
                    b64 = base64.b64encode(f.read()).decode()
                out.append(
                    f'@font-face{{font-family:"{family}";font-style:normal;font-weight:{w};'
                    f'font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2");'
                    f"unicode-range:{RANGES[subset]}}}"
                )
    return "<style>" + "".join(out) + "</style>"


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as f:
        return f.read()


def build():
    styles = "<style>\n" + read("styles.css") + "</style>"
    chart_js = "<script>" + read("vendor/chart.umd.js") + "</script>"
    data = (
        "<script>window.__DATA__=\n"
        + read("data.json")
        + "\n;window.__EN__=\n"
        + read("i18n_en.json")
        + "\n;window.__PREP__=\n"
        + read("chat_answers.json")
        + "\n;</script>"
    )
    app = "<script>\n" + "\n".join(read(p) for p in JS_FILES) + "\n</script>"

    html = read("page.html")
    for placeholder, content in [
        ("<!-- FONTS -->", fonts_css()),
        ("<!-- STYLES -->", styles),
        ("<!-- CHART_JS -->", chart_js),
        ("<!-- SCRIPTS -->", data + app),
    ]:
        assert html.count(placeholder) == 1, f"placeholder missing: {placeholder}"
        html = html.replace(placeholder, content)

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html built:", round(len(html.encode()) / 1024), "KB")


if __name__ == "__main__":
    build()
