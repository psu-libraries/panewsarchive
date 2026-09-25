# PSU Custom Overrides

This directory contains PSU-specific customizations layered on top of Open ONI.

## Solr Reindexing

If Solr search results are missing, stale, or inconsistent after loading data,
run the following commands from the app directory (`open-oni/`):

```bash
./manage.py setup_index
./manage.py index
```

### What These Commands Do

- `setup_index`: Ensures Solr schema/config required by Open ONI is present.
- `index`: Rebuilds Solr title and page search documents (including OCR-backed
  page search).

### Optional Recovery Steps

If batch loading used async tasks and indexing still looks incomplete:

```bash
./manage.py psu_rerun_failed
./manage.py setup_index
./manage.py index
```

If Solr is badly out of sync, last-resort full reset:

```bash
./manage.py zap_index
./manage.py setup_index
./manage.py index
```

Use `zap_index` with care: it deletes all Solr documents before rebuilding.
