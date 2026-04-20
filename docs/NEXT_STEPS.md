# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Immediate

1. **Remove the compatibility symlink** once all open shells/editors have had a chance to restart:
   ```bash
   rm /Users/junlee/cognitive-os
   ```
   Created to keep the current Claude Code session's Bash cwd valid while the migration completed. After removal, only `/Users/junlee/episteme` exists.

2. **Verify marketplace install path** — `/plugin marketplace add junjslee/episteme`
   (old `junjslee/cognitive-os` URL still 301-redirects).

3. **Tag the migration** — `git tag v0.8.0 && git push --tags`

---

## Short-term (next cycle)

- Replace ASCII control-plane diagram in `README.md` with an SVG asset (concept already defined)
- Add `last_elicited` timestamp field to operator profile schema (Gap B in KERNEL_LIMITS.md)
- Implement calibration telemetry stub — `decisions/*.md` append-only log (Gap A)

---

## Medium-term (roadmap)

- Multi-operator mode design (Gap C)
- `tacit-call` decision marker in Reasoning Surface schema (Gap D)
- Cynefin domain classification field in `reasoning-surface.json` schema (companion to KERNEL_LIMITS.md addition)
