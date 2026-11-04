# Guide: a new language

How to translate Beer Crawler into one more language. The script has English and Hungarian; the example adds German (`de`). Part of [Guides](../guides/README.md).

> Related: [Command Line, GUI & Docker](../command-line-gui-and-docker.md) (the `--language` argument and the GUI dropdown)

---

## What a language is here

A language is **one JSON file** in `lang/`. The file name (`de.json`) is the language code. Nothing in the code lists the languages: `get_languages()` reads the file names of the folder, and the GUI dropdown shows each language by the value of its own code key (`"de": "German"` is read from the **currently loaded** file).

---

## Steps

### 1. Copy the file

Copy `lang/en.json` to `lang/de.json` and translate the values. Keep every key. The file has about 35 keys: the Excel column names (`NAME`, `BREWERY`, ...), the log lines (`BROWSE_*`, `NO_NEW_BEER`, `DELETE_FILE`, `REPORT_CREATED`), the GUI labels (`RUN`, `LANG`, `ROTATE`, `CLEAN`, `SHOPS`, `BEER_COUNT`).

### 2. Name the language in every file

Each file has one key per language holding that language's name in the file's own language:

```
en.json:  "en": "English",  "hu": "Hungarian",  "de": "German"
hu.json:  "en": "Angol",    "hu": "Magyar",     "de": "Német"
de.json:  "en": "Englisch", "hu": "Ungarisch",  "de": "Deutsch"
```

The GUI turns a name back into a code with `get_lang_code()`, so **the names inside one file must be different** from each other.

### 3. Try it

```
python main.py --language de --shops beerselection --beercount 3
python main.py --gui
```

Missing keys show "Text not found" (the `NO_TEXT` value of the file), a missing file falls back to English.

### 4. Docs

Add the language to the list in the README and `docs/docker/README.md`, and to the help text of `--language` in `common.py`.

---

## Checklist

* [ ] `lang/de.json` has every key of `en.json`
* [ ] A `"de"` key in every language file, names in the right language, no two equal inside one file
* [ ] The script starts with `--language de` and the GUI lists German
* [ ] README, help text and wiki pages updated
