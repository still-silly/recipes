# The recipe box

Personal recipes in [Cooklang](https://cooklang.org/docs/), with readable views for GitHub and a small, printable website.

**[Browse the recipe website](https://still-silly.github.io/recipes/)**

## Recipes

| Recipe | Read on GitHub | Cooklang source |
| --- | --- | --- |
| Spicy Beef and Bean Chili | [Rendered recipe](rendered/spicy-beef-and-bean-chili.md) | [`.cook` file](recipes/Spicy%20Beef%20and%20Bean%20Chili.cook) |

The chili is based on **1.5 lb beef**, **1–2 whole onions**, **1 whole garlic bulb**, and **4 limes**. Peppers, tomatoes, and spice quantities remain as supplied. Beans are optional and go in with the beef. Kidney beans may be replaced with pinto beans; habaneros may be replaced with serranos. Lime juice is added at the end.

## Preview the website

No install or build is needed to read the included pages: open `docs/index.html` in a browser. To serve them locally:

```sh
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

Open <http://localhost:8000>. The recipe page includes an ingredient checklist, quantities in each step, a print layout, and a downloadable Cooklang source.

## Edit and rebuild

Edit the `.cook` source in `recipes/`, then regenerate the views. Python 3.10+ and **CookCLI 0.41.1** are required. The official CLI parses and validates the Cooklang; the Python script only formats its structured output. Generated files in `docs/` and `rendered/` should be committed with recipe changes.

Linux x86_64:

```sh
bash scripts/install-cook.sh
python3 scripts/build.py
```

The installer downloads the pinned official release and verifies its SHA-256 before extracting. Other platforms can download the matching binary from [CookCLI v0.41.1](https://github.com/cooklang/cookcli/releases/tag/v0.41.1), then use:

```sh
COOK_BIN=/absolute/path/to/cook python3 scripts/build.py
```

Add more `.cook` files under `recipes/` and rebuild to add them to the website automatically. The build fails for unsupported structured items rather than silently omitting them. Add new entries to the table above as needed.

## Publishing

The repository is public. GitHub Actions validates recipes, rebuilds the rendered views, and checks that generated files match the sources. Successful pushes to `main` deploy `docs/` to [GitHub Pages](https://still-silly.github.io/recipes/). Pull requests run validation without deploying. You can also run the workflow manually on `main` to redeploy. The repository's Pages publishing source is **GitHub Actions**.

## Format conventions

- `.cook` files, YAML front matter, paragraph steps, ingredient quantities, preparation notes, and `~{15%minutes}` follow the [Cooklang specification](https://cooklang.org/docs/spec/).
- Optional beans use `@?kidney beans{1%can}(or pinto beans)`. Alternatives are preparation notes so shopping lists do not require both varieties.
- `source`, `title`, `description`, and `tags` follow the [metadata conventions](https://cooklang.org/docs/conventions/).
- No serving count is invented. This recipe describes one batch with 1.5 lb of meat; existing ingredient quantities were not halved.
