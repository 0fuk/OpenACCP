# Security Policy

OpenACCP is a workflow and artifact kit. It does not run production systems by itself, but it can influence how agents handle source material, credentials, user data, and release decisions.

## Report A Concern

Report security issues through GitHub private vulnerability reporting on this repository: Security -> Report a vulnerability.

Do not publish exploit details before the maintainer has had time to respond.

## Sensitive Material Rules

Do not submit:

- credentials,
- customer or user data,
- private source paths,
- internal logs,
- production deployment details,
- private policy documents,
- proprietary schemas,
- unpublished audit or compliance records.

## Validator Limits

The validator can catch structural gaps and common unsafe claims. It cannot prove that code is secure or that a workflow is legally compliant.

The public-package scan includes lightweight secret markers, but it is not a full secrets scanner. Run a dedicated secret scanning tool before public release.
