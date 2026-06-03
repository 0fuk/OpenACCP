# Release Checklist

This checklist is for maintainers before tagging a public release. It is not a user setup checklist.

Confirmed release metadata for the first public candidate:

- License: MIT.
- Copyright holder: Vyqo AI.
- GitHub account: `0fuk`.
- Package name: `openacp`.

## Required

- [ ] Confirm the MIT License is the intended release license.
- [ ] Run validator self-tests.
- [ ] Run public-package scan.
- [ ] Check no local paths or private identifiers appear.
- [ ] Check examples are project-neutral.
- [ ] Check README presents Bootstrap and Coordination paths.
- [ ] Check validator docs state that validation is not semantic approval.
- [ ] Check B2/B3 task cards include `authorityCharterRef`.
- [ ] Check strict fixtures are separated from concept examples.
- [ ] Check internal reports and response logs are outside the public package.
- [ ] Run a dedicated secret scan in addition to the OpenACP public-package scan.
- [ ] Check every schema has a documented use.
- [ ] Check skills are concise and generic.

## Owner Decisions

- license changes, if any,
- package manager,
- governance model,
- maintainer contact,
- release cadence,
- final version tag for the first public release.
