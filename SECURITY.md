# Security Policy

OpenACP is a workflow and artifact kit. It does not run production systems by itself, but it can influence how agents handle source material, credentials, user data, and release decisions.

## Report A Concern

Report security issues through GitHub Security Advisories or the private vulnerability reporting mechanism configured by the repository host. If the hosting platform does not support private reports, use the maintainer contact published on the repository owner profile.

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

## Maintainer Setup

Before public release, enable private vulnerability reporting or GitHub Security Advisories on the repository host. Keep maintainer contact information on the public repository owner profile rather than embedding personal contact details in this package.
