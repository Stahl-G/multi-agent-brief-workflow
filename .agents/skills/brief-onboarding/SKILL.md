---
name: brief-onboarding
description: Use when the user wants to initialize, start, configure, or set up a multi-agent-brief workspace. Interview the user in plain language and convert answers into onboarding.json.
---

# Brief Onboarding

You are onboarding a non-programmer user.

Keep the conversation in plain business language. Developer-facing details such as YAML, JSON, schemas, CLI flags, source_profile, selector_max_items, retrieval_provider, and output_formats belong in internal setup work unless the user asks for them.

Ask at most 14 questions:

0. What should this brief be called?
   Required field. Examples: "Canadian Solar Photovoltaic Weekly", "阿特斯光伏行业周报", "Global Macro Strategy Monthly".
   Suggested default: "{Company} {Industry} Weekly" after user confirmation.

1. What is your company or organization name?
   Required field.

2. What is your role or department?
   Examples: Strategy, Research, Marketing, Investor Relations, Policy, Management.
   Suggested default: Strategy.

3. What should this brief monitor?
   Suggested default: company + industry + policy + competitors + risk events.

4. Should competitor monitoring be enabled?
   If yes, ask which specific competitors to track.
   Examples: "Yes — track Acme Corp and Globex Inc" or "No, not now".

5. Who will read it?
   Suggested default: management / leadership team / marketing / investment team / research.

6. How broad should sources be?
   Suggested default: reliable public sources + industry media.

7. What language and cadence?
   Suggested default: Chinese, weekly.

8. What specific focus areas are most important?
   Suggested default: based on industry.

9. Should live web search be enabled?
   Options: yes with available backends, or local files only.
   Suggested default: configure later.

10. How many items should each brief contain?
    Suggested default: 20 items.

11. What is the maximum age for source materials, in days?
    Suggested default: 14 days.

12. How strict should the audit be?
    Options: standard, strict, lenient.
    Suggested default: standard.

13. Are there any sources or topics to exclude?
    Suggested default: none.

Accept natural-language answers. Confirm required fields and defaults before creating the workspace.

Then create `onboarding.json` with:
- target
- brief_title
- company_or_org
- industry_or_theme
- role_plain
- audience_plain
- source_style_plain
- output_style_plain
- language_plain
- cadence_plain
- must_watch
- focus_areas_plain
- search_backend_plain
- max_items_per_brief
- source_age_days
- audit_strictness
- forbidden_sources
- competitor_preferences (object with `enabled: true/false` and `names: [list of competitor names]`)

Then run:

```bash
multi-agent-brief init --from-onboarding onboarding.json
```

Finally summarize:

* brief title
* workspace created
* brief audience
* monitor scope
* competitor monitoring status
* source style
* search backend
* max items per brief
* source age limit
* audit strictness
* output style
* next command
