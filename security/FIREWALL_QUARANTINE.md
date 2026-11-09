# QuantumMirrorFirewall — quarantine status

**Status: DISABLED_UNVERIFIED.** This module is a research prototype, not an
antivirus, firewall, security entropy source, or supported deployment target.

## Why it is quarantined

- The referenced `security.av_engine` scanner does not exist in this checkout.
- Earlier `quantum_firewall_cycle()` called `ufw reset`, changed the default
  policy, and opened pseudo-random ports without preserving existing rules.
  Running this on a user's host could disrupt legitimate access.
- The source of its simulated quantum outcomes is not physical entropy and is
  not a CSPRNG. In the current processor, gates and the state-vector measurement
  are disconnected, so the proposed randomness cannot defend port selection.
- The earlier recursion/monitoring claims have not been shown to provide malware
  detection or reliable self-repair.

## Enforced boundary

The following entrypoints now fail with `RuntimeError` before any host firewall
mutation, thread start, or simulated security-port generation:

- `QuantumMirrorFirewallObserver.start()`
- `QuantumMirrorFirewallObserver.quantum_firewall_cycle()`
- `QuantumRandomizer.quantum_port()`

The missing scanner import is caught only to allow inspection and testing of
the quarantine. **No fallback scanner or security function is supplied.**

## Evidence

`tests/test_firewall_quarantine.py` replaces attempted host command and thread
startup with failing test sentinels. CI runs those tests with the existing
Python matrix, without enabling any host security service.

## Requirements for a separate reviewed implementation

1. Define threat model, supported host platforms and an explicit administrator
   consent/authorization model before touching networking.
2. Recover or replace the missing scanner with its own tested provenance and
   operational evidence; no silent mock scanner.
3. Use OS CSPRNG where unpredictability is actually required; prefer
   deterministic, audited firewall policies over rotating random ports.
4. Never reset existing host rules as a generic start step. Propose/diff
   desired rules, support dry runs, rollback and remote access preservation.
5. Run isolated integration tests in disposable network namespaces/VMs, not
   on a developer's host. Include adversarial tests for partial failure,
   unexpected exits, missing tools and loss of administrator privileges.
6. Keep deployment disabled until independent review approves an implementation.

The open quantum-state semantics design work is a separate issue. Fixing
simulation mathematics alone does not validate this firewall.
