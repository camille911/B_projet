# Tester boundary rule

Inspect contracts and dependency coordinates first. Integration tests must call
the real B1 implementation, the delivered B3 package, and the published signing
asset. Do not edit production code to hide a test failure. Keep unit and
integration results distinct. Refresh the B index only after a reviewed commit
and explicit confirmation.

