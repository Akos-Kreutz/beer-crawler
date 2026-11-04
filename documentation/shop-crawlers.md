# Shop Crawlers

How the five shop modules work. They are copies of one pattern, so the pattern comes first and the differences after it. Part of [Architecture Overview](architecture-overview.md).

---

## The pattern

Every module (`beerselection.py`, `csakajosor.py`, `onebeer.py`, `drinkstation.py`, `beerbox.py`) has `run()` and `crawl()`:

1. `run()` logs the "Browsing ..." line, builds the listing page URLs and calls `crawl()` for each.
2. The number of listing pages is `ceil(ARGS.beercount / NUMBER_OF_BEERS_PER_PAGE)`, so `--beercount` is the target number of beers per shop (default 20), and the constant is the page size of that shop (20, 36, 36, 200, 21).
3. `crawl()` downloads a listing page, finds the product links, stops when `beercount` beers are collected, and **opens every product page** to read the details.
4. A product page is tried **three times**; after an error the module sleeps 5 seconds. `KeyboardInterrupt` is re-raised.
5. Back in `run()`: if `json/<module>.json` exists, `get_new_entries(old, current)` keeps only the new beers; the current list is then written to that file; the new beers are returned.

All requests use `timeout=(5, 30)` (connect, read).

### The `Beer` object

`common.Beer` has the fields `name, brewery, package, style, country, price, currency, abv, link`. The modules fill an instance and store `beer.__dict__`. Because `__dict__` holds only attributes that were **set on the instance**, a field a module never assigns is missing from the JSON (see [Recommendations](recommendations.md), One Beer).

Helpers for reading HTML, all in `common.py`, all returning `NotAvailable` / `"N/A"` instead of failing: `get_element`, `get_elements`, `get_element_attribute` (reads `.text` and strips), `get_tag_attribute` (reads an HTML attribute such as `content`).

### What "new" means

`get_new_entries()` collects the names **and** links of the old list into one list; a current beer is new when **neither** its name nor its link is in it. A renamed beer whose link did not change is therefore not new, and a beer that was dropped from the first N results and comes back later is new again.

### Name cleanup

`get_formatted_name(name, brewery)` turns the page title into a short name: cuts at the first `|`, removes volumes (`0,5l`, `500ml`), the percentage (`5,2%`) and a trailing bracket (`, (something)`), then removes the brewery name from the title, unless the title contains `&`, the brewery is unknown, or the brewery appears twice.

---

## The five shops

| Module | Shop | Listing URL | Per page | Where the details come from |
|---|---|---|---|---|
| `beerselection.py` | beerselection.hu | newest products (`latest=40`), in stock | 20 | The parameter table of the product page (`featured-alkoholfok`, `-tipus`, `-kiszereles`, `-szaramazas`), the manufacturer row, the price box. Currency is fixed `HUF` |
| `csakajosor.py` | csakajosor.hu | `sort=p.date_available&order=DESC` | 36 | Same table layout as Beerselection (same shop software) plus `-urtartalom` + `-kiszereles` for the package, `-orszag` for the country. Price and currency from the `itemprop` meta tags |
| `onebeer.py` | onebeer.hu | `sorok?infinite_page=N` | 36 | Only **one** listing request: the page number is `ceil(beercount / 36) + 1` of the infinite-scroll URL. Details from `page_artdet_product_param_spec_<id>` blocks (ABV, style, package, brewery). Country is always `N/A` |
| `drinkstation.py` | drinkstation.hu | `kraft-sorok?stockfilter=1&sort=p.date_available` | 200 | Price and currency from the `itemprop` meta tags. Package and ABV are cut out of the page title with a regular expression. Style, country and brewery are always `N/A` |
| `beerbox.py` | beerbox.hu | `product-category/sorok-8?page=N` | 21 | First asks `accept-adult-only` for the `adult_only_accepted` cookie and sends it with every request. Style and ABV are cut out of one `product-content` text; package, brewery, country are the first three cells of a striped table |

Shop modules depend on CSS class names of the shops. When a shop changes its HTML, a field silently becomes `N/A` (the helpers never raise), so a crawl can "succeed" with empty beers.
