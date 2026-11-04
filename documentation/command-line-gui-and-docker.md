# Command Line, GUI & Docker

How to run Beer Crawler: the arguments, the GUI, the files it writes, and the Docker image. Part of [Architecture Overview](architecture-overview.md).

---

## Arguments

`common.get_args()` runs when `common.py` is imported, so the arguments are parsed before anything else.

| Argument | Default | Meaning |
|---|---|---|
| `--language`, `-l` | `en` | Language file in `lang/` (`en`, `hu`). An unknown code falls back to English with a printed notice |
| `--shops`, `-s` | all five | Comma separated: `beerselection,csakajosor,onebeer,drinkstation,beerbox`. An unknown name is ignored |
| `--beercount`, `-b` | `20` | Beers to check **per shop** |
| `--rotate`, `-r` | `5` | Newest files to keep in `log/` and `report/`; below zero turns rotation off |
| `--clean`, `-c` | off | Delete everything in `log/`, `report/` and `json/`, then exit |
| `--daily`, `-d` | off | Run only once per day (see below) |
| `--gui`, `-g` | off | Open the tkinter window |
| `--version`, `-v` | off | Print `Beer Crawler v2.11` and exit |

The `VERSION` constant in `common.py` is `2.11`; the `.docker` file says `2.14`. They are not connected.

> The README documents the shop argument as `--shop`; the code defines `--shops` (argparse also accepts the unambiguous prefix `--shop`).

### Rotation and the daily guard

* `rotate_files(n, folder)` sorts the folder by modification time and deletes everything after the newest `n` files. It runs on `log/` and `report/` at every start, never on `json/`.
* `--daily` checks whether today's log (`log/DD-MM-YYYY.log`) contains a `#`. The `#` is written at the end of every finished run, also when nothing new was found. If found, the script logs "The script already ran today" and exits. The guard sits in the `else` branch of the rotation check, so **`--rotate -1` disables the daily guard too**.

---

## The GUI

`--gui` opens a 230x295 window (tkinter) with: a language dropdown (changing it reloads the language file and relabels the widgets), rotate, beer count, a clean checkbox, a multi-select list of shops, a progress bar and a Run button.

* The Run button copies the widgets into `ARGS`, computes the progress step (`round(100 / (shops + 1)) + 1`), disables itself and calls the same `run()` as the command line.
* The window polls the crawl threads every 100 ms (`top.after`) instead of joining them, because tkinter must stay on the main thread. Each finished thread moves the progress bar; at the end `create_template()` writes the report and a message box announces the result.
* tkinter is imported inside a `try`. Without it (Docker) the script still works; with `--gui` it logs the error and exits.

---

## The report

`create_worksheet()` writes one sheet named "Beer Crawler" with the columns Name, Brewery, Country, Style, ABV, Package, Price, Currency, Shop, URL, one row per new beer, grouped by shop. The price text has `.`, `Ft` and spaces removed (`1.290 Ft` becomes `1290`). Nothing is written when no shop found a new beer.

## Logging and crash output

`log_and_print()` prefixes each line with `[HH:MM:SS]`, prints it and appends it to the day's log. `faulthandler` is enabled with a traceback dump every 60 seconds (`dump_traceback_later(60, repeat=True)`) to diagnose hangs and segfaults; the dumps go to stderr.

---

## Docker

```
docker run -v <report>:/report -v <log>:/log -v <json>:/json kreutzakos/beercrawler:latest [ARGS]
```

* The image is `python:3.14.4-slim-trixie`, runs as **root**, copies `main.py`, `lang/`, `modules/` to `/`, and installs the unpinned packages. The entry point is `python /main.py`.
* `SCRIPT_FOLDER` is `/` in the image, so the data folders are `/log`, `/report` and `/json`. Mount all three; `json/` is the memory of the crawler, without it every run reports every beer as new.
* The GUI does not work in the image.
* The image does not run on a schedule; use cron or a systemd timer on the host together with `--daily`.
