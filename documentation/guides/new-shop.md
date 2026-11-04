# Guide: a new shop

How to add a sixth shop. The example is called `examplebeer`. Part of [Guides](../guides/README.md).

> Related: [Shop Crawlers](../shop-crawlers.md) (the pattern every module follows) · [Recommendations](../recommendations.md)

---

## Steps

### 1. Write the module

Copy the shortest module that looks like the new shop (`modules/beerselection.py` for a listing plus product pages) to `modules/examplebeer.py`. A module must have:

* `MODULE_NAME = os.path.basename(__file__).replace(".py", "")`: it names the JSON file (`json/examplebeer.json`).
* `NUMBER_OF_BEERS_PER_PAGE`: the page size of the shop's listing, used to compute how many pages to load for `--beercount`.
* `run()`: logs `get_lang_text("BROWSE_EXAMPLEBEER")`, crawls, then compares with the previous JSON and writes the new one (copy the last lines of any other module), and **returns the new beers**.
* `crawl()`: for each product link, open the product page (3 tries, 5 s sleep) and fill a `Beer`. Set **every** field: `link, name, brewery, package, style, country, price, currency, abv`. A field that is not set is missing from the JSON and breaks the report (`beer['price']`). Use `NotAvailable.text` for what the shop does not give.
* Use `get_formatted_name(title, brewery)` for the name so it matches the other shops.
* Return only strings; the report removes `.`, `Ft` and spaces from the price, so give the price as the shop writes it or as a clean number.

If the shop has an age gate or needs a cookie, read `beerbox.py`: it fetches the cookie once and passes it to every request.

### 2. Register it

In `main.py`:

```python
from modules.examplebeer import run as examplebeer_run
...
case "examplebeer":
    beers["Example Beer"] = examplebeer_run()
```

The key of `beers` is the shop name written into the report's Shop column.

In `modules/common.py`, add the name to the default and the help text of `--shops`. The GUI list is built from that default, so the shop appears there too.

### 3. Texts

Add `BROWSE_EXAMPLEBEER` to **every** file in `lang/` (`en.json`: "Browsing Example Beer", `hu.json`: the Hungarian text). A missing key shows "Text not found".

### 4. Run it

```
python main.py --shops examplebeer --beercount 5 --rotate -1
```

Check `json/examplebeer.json`: every beer has all nine keys. Run it a second time: it must report "No new beer found". Delete `json/examplebeer.json` to see the first-run behaviour.

### 5. Docs

Update the module list in `README.md` and `docs/docker/README.md`, the shop table in [Shop Crawlers](../shop-crawlers.md), and the supported values of `--shops`.

---

## Checklist

* [ ] `modules/examplebeer.py` sets all nine `Beer` fields, returns the new beers, writes `json/examplebeer.json`
* [ ] Imported and added to the `match` in `main.py`
* [ ] Added to the defaults and help of `--shops` in `common.py`
* [ ] `BROWSE_EXAMPLEBEER` in every `lang/*.json`
* [ ] A second run reports nothing new
* [ ] README, Docker README and the wiki pages mention the shop
