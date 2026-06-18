# Release Checklist

This maintainer checklist is for the final pass before tagging a public release.

Confirmed release metadata for the first public candidate:

- License: MIT.
- Author: Ocean Liu / Liu HanYang.
- Copyright holder: Ocean Liu / Liu HanYang.
- GitHub account: `0fuk`.
- Package name: `openaccp`.

## Required

- [ ] Confirm the MIT License is the intended release license.
- [ ] Run validator self-tests.
- [ ] Run public-package scan.
- [ ] Build wheel and sdist artifacts.
- [ ] Run `twine check` on built artifacts.
- [ ] Install the built wheel in a clean environment and run a validator smoke test.
- [ ] Install the built sdist in a clean environment and run a validator smoke test.
- [ ] Confirm packaged schemas under `openaccp/schemas/` are the only schema source of truth.
- [ ] Check no local paths or private identifiers appear.
- [ ] Check examples are project-neutral.
- [ ] Check README presents Bootstrap and Coordination paths.
- [ ] Check validator docs state that validation is not semantic approval.
- [ ] Check B2/B3 task cards include `authorityCharterRef`.
- [ ] Check strict fixtures are separated from concept examples.
- [ ] Check internal reports and response logs are outside the public package.
- [ ] Run a dedicated secret scan in addition to the OpenACCP public-package scan.
- [ ] Check every schema has a documented use.
- [ ] Check skills are concise and generic.

## Owner Decisions

- license changes, if any,
- package manager,
- governance model,
- maintainer contact,
- release cadence,
- final version tag for the first public release.
