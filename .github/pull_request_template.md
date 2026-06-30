## Summary

## Validation

## Skill impact

Does this PR change CLI/status/gates/delivery/Product OS/public docs/public
claims, or how agents should operate BriefLoop?

- [ ] No skill impact.
- [ ] Updates runtime workspace operation.
- [ ] Updates experiment 080/090 operation.
- [ ] Updates repair protocol.
- [ ] Updates gates/status/finalize/delivery behavior.
- [ ] Updates public claim boundaries.
- [ ] Updates naming/compatibility.
- [ ] Updates CLI commands or slash commands.
- [ ] Updates ReportPack / PolicyProfile / Product OS surfaces.
- [ ] Updates Quality Panel, release / approval, bundle, Hermes, or Claude command surfaces.

If any box except "No skill impact" is checked, update:

- `.agents/skills/briefloop/...`
- `.claude/skills/briefloop/...` projection if needed
- `integrations/hermes-plugin/mabw/skills/briefloop/...` projection if needed
- skill contract tests
- run `python3 scripts/check_briefloop_skill_freshness.py`
