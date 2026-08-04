# Order API B

The `demo-start` baseline provides B1 order validation only. Later commits may
integrate independently delivered modules through the public injection port;
they must not copy the company signing implementation.

The complete source-free consumer contract is in `docs/api.md`. Structured
contracts, JSON Schemas, and interoperability vectors are in `docs/`; searchable
asset manifests are in `assets/`.

The developer-facing contract does not authorize access to B source. Module
tests use the read-only contract package and Mock; real B1/B3/signer integration
must be verified in the tester environment.

