# Reader 2.0 release review

This is the separate Rust application line requested on 8 November 2026. Keep 1.29 reserved. Build artifacts are for review, not publication or installation authorization.

The browser frontend and Rust builds require separate verification. Windows/Mac review packages may be unsigned. Android debug packages and iOS simulator outputs are distinct from signed store/device releases. See NATIVE-2.0.md.

Retain 1.28 and all source identities/stores. Rollback, if ever deployed, uses normal reviewed commits; never force a ref or clear user data. Public promotion, store distribution, signing credentials and access changes require separate confirmation.
