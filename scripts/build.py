#!/usr/bin/env python3
"""Render official CookCLI parse output; never parse Cooklang ourselves."""
import html
import json
import os
from pathlib import Path
import re
import shutil
import string
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COOK = os.environ.get("COOK_BIN", str(ROOT / ".tools/cook"))
OUT = ROOT / "docs"


def esc(value):
    return html.escape(str(value), quote=True)


def run(*args):
    return subprocess.check_output([COOK, *map(str, args)], text=True, cwd=ROOT)


def quantity(q):
    if not q:
        return ""
    v = q["value"]
    if v["type"] == "text":
        value = v["value"]
    elif v["type"] == "number" and v["value"]["type"] == "regular":
        value = f'{v["value"]["value"]:g}'
    else:
        raise ValueError(f"Unsupported quantity format: {v}; extend renderer before adding this recipe")
    return " ".join(filter(None, [str(value), q.get("unit")]))


def component(item, include_note=False):
    name = item.get("alias") or item.get("name") or ""
    text = " ".join(filter(None, [quantity(item.get("quantity")), name]))
    if include_note and item.get("note"):
        text += f' ({item["note"]})'
    return esc(text)


def main():
    subprocess.run([COOK, "doctor", "validate", "-b", "recipes", "--strict"], cwd=ROOT, check=True)
    OUT.mkdir(exist_ok=True)
    # Remove stale generated files after a source recipe is renamed or deleted.
    for directory in [OUT / "recipes", ROOT / "rendered"]:
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir()
    (OUT / ".nojekyll").touch()
    shutil.copyfile(ROOT / "site/style.css", OUT / "style.css")
    template = string.Template((ROOT / "site/template.html").read_text())
    cards = []
    for source in sorted((ROOT / "recipes").rglob("*.cook")):
        recipe = json.loads(run("recipe", source, "--format", "json"))
        meta = recipe["metadata"]["map"]
        title = meta.get("title", source.stem)
        slug = re.sub(r"[^a-z0-9]+", "-", str(source.relative_to(ROOT / "recipes").with_suffix("")).lower()).strip("-")
        # Copies allow downloading .cook directly from the published site.
        (OUT / "recipes" / f"{slug}.cook").write_bytes(source.read_bytes())
        markdown = run("recipe", source, "--format", "markdown")
        (ROOT / "rendered" / f"{slug}.md").write_text(markdown.rstrip() + "\n")
        ingredients = []
        for index, item in enumerate(recipe["ingredients"]):
            optional = ' <span class="optional">Optional</span>' if "OPT" in item["modifiers"].split() else ""
            ingredients.append(f'<li><label><input type="checkbox"> <span>{component(item, True)}{optional}</span></label></li>')
        steps, notes = [], []
        for section in recipe["sections"]:
            if section.get("name"):
                steps.append(f'<li class="section-title">{esc(section["name"])}</li>')
            for entry in section["content"]:
                if entry["type"] == "text":
                    notes.append(f'<p>{esc(entry["value"])}</p>')
                    continue
                if entry["type"] != "step":
                    raise ValueError(f"Unsupported content: {entry}")
                parts = []
                for item in entry["value"]["items"]:
                    kind = item["type"]
                    if kind == "text":
                        parts.append(esc(item["value"]))
                    elif kind in ("ingredient", "cookware", "timer"):
                        collection = {"ingredient": "ingredients", "cookware": "cookware", "timer": "timers"}[kind]
                        parts.append(f'<strong>{component(recipe[collection][item["index"]], True)}</strong>')
                    else:
                        raise ValueError(f"Unsupported step item: {item}")
                steps.append('<li>' + ''.join(parts) + '</li>')
        tags = ''.join(f'<span class="tag">{esc(tag)}</span>' for tag in meta.get("tags", []))
        page = template.substitute(title=esc(title), description=esc(meta.get("description", "")), tags=tags,
            ingredients='\n'.join(ingredients), steps='\n'.join(steps), notes=''.join(notes),
            source_href=f"{slug}.cook", index_href="../index.html", style_href="../style.css")
        (OUT / "recipes" / f"{slug}.html").write_text(page)
        cards.append(f'<a class="recipe-card" href="recipes/{slug}.html"><span class="eyebrow">RECIPE</span><h2>{esc(title)}</h2><p>{esc(meta.get("description", ""))}</p><span class="card-link">Cook this recipe &rarr;</span></a>')
    (OUT / "index.html").write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recipes · The recipe box</title><link rel="stylesheet" href="style.css"></head>
<body><main class="collection"><header><p class="eyebrow">THE RECIPE BOX</p><h1>Good food.<br>Written down.</h1>
<p class="intro">A personal collection of recipes to make, share, and make again.</p></header>
<div class="recipe-grid">''' + ''.join(cards) + '''</div><footer>Made with <a href="https://cooklang.org/docs/">Cooklang</a>. Kept in plain text.</footer></main></body></html>''')
    print(f"Rendered {len(cards)} recipe(s) to docs/ and rendered/.")


if __name__ == "__main__":
    main()
