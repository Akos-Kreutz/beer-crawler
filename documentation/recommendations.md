# Recommendations

Suggested changes found while reading the code. Nothing here is implemented. Part of [Architecture Overview](architecture-overview.md).

---

## Bugs

### One Beer never stores a price

In `modules/onebeer.py` the price is read into a local variable `price` (sale price, else base price) but never assigned to `beer.price`. Because `Beer.price` is only a class attribute, `beer.__dict__` has no `price` key, the JSON file has none, and `create_worksheet()` fails on `beer['price']` with a `KeyError` as soon as One Beer has a new beer. The error stops the whole report (the workbook is never closed, so no `.xlsx` is written for any shop), and because every module has already rewritten its JSON file by then, the new beers of all shops are lost: the next run no longer sees them as new.

*Fix:* `beer.price = price` before `beer.currency = "HUF"`. Defensive: initialise the fields in `Beer.__init__` so `__dict__` always has every key.

### Decimal point stripped from meta prices

The report removes every `.` from the price (meant for `1.290 Ft`). Drink Station and Csak a jó sör read the price from an `itemprop="price"` meta tag, which is a plain number that can contain a decimal point. If it has one, `1290.00` becomes `129000`. *Not verified against the live shops.* Normalise per shop instead of in the report.

### A failed beer is still added

After three failed attempts the loop ends and the half filled `Beer` is appended anyway; its `link` is set, the other fields are missing or `N/A`. It enters the JSON file and the report, and next run it is "known". Skip the beer (and do not write it to the JSON) when all tries failed.

### `--rotate -1` also disables `--daily`

The daily guard sits in the `else` of `if ARGS.rotate < 0`. Move it out of the rotation branch.

### Wrong or stale documentation

* README says `--shop`, the code says `--shops`.
* `VERSION` in `common.py` (2.11) differs from `.docker` (2.14).

---

## Robustness

* **Silent selector failures.** A changed CSS class gives `N/A` without a log line. Count the `N/A` fields per shop and log a warning when most beers have them.
* **First run is a report of everything.** Add an option to only seed the JSON files.
* **JSON is replaced even if the crawl was cut short** (a shop that returned few beers because of a network problem makes the next run report the rest as new). Only replace the file when the crawl reached `beercount` or the last page.
* **Unpinned dependencies and a root container.** The other projects pin hashes (`requirements.in` + `pip-compile`) and run as a non-root user. Do the same here.
* **Duplicate code.** The five `crawl()` functions share the retry loop, the "stop at beercount" check and the `run()` body. A small base function with the selectors as data would remove about 200 lines (see the [new shop guide](guides/new-shop.md) for what a shop has to provide).
* **Crawl politeness.** There is no delay between product page requests, no `User-Agent` and no `robots.txt` check.
* **`SCRIPT_FOLDER` uses `sys.argv[0]`**, so the data folders depend on how the script is started.
