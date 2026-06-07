# Source Cache Contract

Daily source cache mode collects public, citable source signals and ends after cache reporting. It does not draft or finalize a brief.

## Path

Write cache files under:

```text
<input workspace>/input/hermes_cache/YYYY-MM-DD.json
```

## Preferred JSON Shape

Use a JSON object with an `items` array, or a JSON array of items. Preserve URL, publication date, source name, and reliability when available.

```json
{
  "items": [
    {
      "source_id": "HERMES_YYYYMMDD_001",
      "source_name": "Source name",
      "source_type": "hermes_daily_cache",
      "title": "Short source title",
      "content": "Concise factual summary with enough context for claim extraction.",
      "url": "https://example.com/source",
      "published_at": "YYYY-MM-DD",
      "reliability": "high",
      "metadata": {
        "collected_by": "hermes",
        "collection_cadence": "daily"
      }
    }
  ]
}
```

## Completion Report

Report saved item count, cache file path, source gaps, and any access limitations.
