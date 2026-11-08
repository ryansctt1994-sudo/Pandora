# Quantum state semantics: one authoritative state for gates and measurement

**Status:** Proposed. Design review only. No implementation is included or authorized by this document.

**Tracking:** Task #14 in the working session. GitHub Issues are disabled on this repository by owner decision, so this document and its draft pull request are the review record.

**Scope excluded:** Changes to executable code, tests, dependencies, CI, repository settings, the committed `ouroboros_sync.so` binary, and `security/quantum_mirror_firewall.py`.

**Labels used below:**
- **[Established]** verified from the repository at `55a4c61`, or from a test run described where it occurs.
- **[Proposed]** a change or contract this document recommends. Not implemented.
- **[Open]** a question for review.

---

## 1. Summary

[Established] The quantum processors contain two state models that do not interact:

1. A **classical register** (`QuantumVirtualProcessor.state`, a Python list of 0/1 values). Gates act on it.
2. A **profile state vector** (`quantum_profiles/base_profile.py`, a complex NumPy array of dimension `2**n`, initialized to `|0…0⟩`). `measure()` samples from it.

[Established] No code path applies a gate to the profile state vector. Gates therefore cannot change the outcome distribution that `measure()` samples.

[Proposed] Replace both with one authoritative complex state vector per processor, on which gates and measurement both operate, under the contract in section 5.

---

## 2. Root cause

[Established] `QuantumVirtualProcessor.apply_gate(gate, reg)` in `quantum_virtual_processor.py` modifies `self.state`:

- `H` sets the target bit to `random.randint(0, 1)`.
- `X` and `Y` flip the bit. `Y` is treated as a bit flip; its phase is dropped.
- `Z` and `T` are no-ops.
- Unknown gate names raise `ValueError`.

[Established] `QuantumVirtualProcessor.measure()` with no argument samples `np.random.choice` over `|profile_state|²`, where `profile_state` comes from `self.profile_manager.get_state()`.

[Established] `measure(i)` reads `self.state[i]`, the classical register. The two arguments of one method therefore answer from different models.

[Established] Verification run, Python 3.12, on the merged code: after `apply_gate("X", 0)`, `apply_gate("H", 0)`, `apply_gate("Y", 0)` on a 3-qubit `alternative` profile, `np.array_equal(profile_state_before, profile_state_after)` returned `True`. Gates did not touch the profile state.

---

## 3. Affected components

[Established] Each row was checked against the source at `55a4c61`.

| Component | Current behavior | Consequence |
|---|---|---|
| Base `QuantumVirtualProcessor` | Gates act on the classical register; `measure()` samples the profile state; `measure(i)` reads the register | Two models in one class |
| `HiveQuantumVirtualProcessor` | `apply_gate` runs ML hooks, then the base register gate; `measure()` samples the profile state | ML hooks see gates that never reach measurement |
| `CastleQuantumVirtualProcessor` | Same as Hive | Same |
| `EmpireQuantumVirtualProcessor` | Delegates `apply_gate` and `measure()` to its `control_lattice`, a base processor | Inherits the split |
| `AlternativeQuantumVirtualProcessor` | Its own `QuantumQubitBuffer`: 0/1 values plus superposition flags. No profile state. `measure()` picks 0 or 1 at random for flagged qubits | A third model with no amplitudes |
| `entangle(q1, q2)` | Copies the value of `q1` into `q2` in the register | Not entanglement. No amplitude changes |
| `quantum_random_number(bits)` | Applies `H` and reads `measure(i)` from the register | Independent of the profile state |
| `QuantumRandomizer.quantum_port()` in `security/quantum_mirror_firewall.py` | Calls `apply_gate("H", 0)`, then `measure()` with no argument | The `H` has no effect on the value returned |
| `demo.py` | Prints `get_state_vector()` (register) and `quantum_random_number()` | Demonstrated output reflects the register only |
| ML addon (`quantum_profiles/ml_quantum_addon.py`) | Logs gate and measurement events | Its training data inherits the split |
| `expand_qubits` / `expand_control_lattice` | Increase the qubit count | [Open] Whether the profile state is resized is not verified |
| Randomness reproducibility | `np.random` global generator, unseeded | Measurement outcomes cannot be asserted exactly in tests |

---

## 4. Established facts versus proposals

| Statement | Status |
|---|---|
| Gates act on the classical register only | Established |
| `measure()` samples the profile state, which gates never change | Established |
| The profile state is a complex vector of dimension `2**n` initialized to `|0…0⟩` | Established |
| `measure(i)` reads the register | Established |
| The firewall's `quantum_port()` returns a value unaffected by its `H` gate | Established (follows from the two facts above) |
| `av_engine.py` is missing from the repository | Established. `scan_with_all` and `any_infected` are not defined anywhere in the repository or in `PANDORA25.zip` |
| One authoritative state vector should replace both models | Proposed |
| The contract in section 5 | Proposed |
| `entangle` should become a real two-qubit gate or be removed | Proposed |
| `expand_qubits` should extend the state with `|0⟩` ancillas | Proposed, with [Open] status |
| `Alternative` should share the common state | [Open] |

---

## 5. Proposed state-vector contract

[Proposed] Each processor owns one complex state vector `ψ` of dimension `2**n`.

1. **Normalization.** `ψ` is normalized: `|‖ψ‖ − 1| < 1e-12` after every gate, evolution, measurement and expansion.
2. **Gates.** Each gate is a unitary matrix on its target qubit(s). Gates are applied in call order. `H`, `X`, `Y`, `Z`, `T` use their textbook matrices. Any two-qubit gate is added explicitly.
3. **Measurement.** `measure()` samples a basis index with probability `|ψ_k|²` (Born rule), then collapses `ψ` onto that basis state and renormalizes.
4. **Single-qubit measurement.** `measure(i)` returns the marginal outcome of qubit `i` from the same `ψ`, then collapses `ψ` accordingly.
5. **Entanglement.** `entangle` is either removed or defined as a real two-qubit operation. It is not kept as a copy.
6. **Random numbers.** `quantum_random_number(bits)` draws from `ψ` and is documented as simulated (section 7).
7. **Seeding.** Processors accept an explicit `numpy.random.Generator`. A fixed seed gives identical outcomes across runs and platforms.

---

## 6. Compatibility risks

[Established] Public surfaces and callers that depend on current behavior:

- `measure()` returns an index sampled from the profile state. Once gates affect that state, its outcome distribution changes for any circuit with gates.
- `measure(i)` returns a register value. Callers may depend on values that the new contract would replace with marginal outcomes.
- `get_state_vector()` returns `{'qubits', 'state', 'measurements'}`, where `state` is currently a list of bits. The keys should stay; the type of `state` changes.
- `quantum_random_number(bits)` returns an integer. Signature should stay.
- `QuantumRandomizer.quantum_port()` in the firewall, which is non-functional regardless (section 8).
- `demo.py` and `examples_quantum_profiles.py`, which call `apply_gate` and `measure` on each profile.
- Tests: `test_quantum_hamiltonian.py` (26 tests), `test_empire_quantum_processor.py` (12), `test_quantum_profiles.py` (7). Their measurement expectations will need review, not only relaxation.
- Processor-specific buffers in `Alternative`, and the ML addon's event log.

[Open] Whether to keep a deprecated classical-register view, or remove it.

---

## 7. Security limitations

This section is separate from section 5. Correct quantum semantics do not establish security, and the reverse is also true.

- **Simulated measurement is not physical quantum entropy.** A simulator samples from a classical probability distribution computed by software. Its output is pseudorandom.
- **It is not a cryptographically secure random source.** `numpy.random` is a Mersenne Twister generator and is not suitable for keys, tokens, nonces, or security decisions, even when the simulation is correct.
- **Wording must match.** The `quantum_random_number` docstring currently says "truly random". It must not say that after any change. Documentation must not describe simulated output as quantum-generated or as a security randomness source.
- **Security randomness source.** Anything security-sensitive must use the operating system CSPRNG, through `secrets` or `os.urandom`.
- **Firewall.** `quantum_port()` must not be presented as a quantum or security randomness source.

---

## 8. Firewall status

[Established] `security/quantum_mirror_firewall.py` imports `from security.av_engine import scan_with_all, any_infected`. Neither `security/av_engine.py` nor any definition of those functions exists in the repository at `55a4c61`, or in `PANDORA25.zip`.

[Established] The module compiles. It cannot be imported, because the import fails at load time.

**The firewall is non-functional.** This PR does not supply `av_engine.py`, stub it, or change the firewall. This document does not claim it provides malware protection.

[Open] Owner decision: recover the module from its author, or mark the firewall explicitly non-functional.

---

## 9. Acceptance criteria

For any future implementation PR, not for this one:

1. **Normalization:** `|‖ψ‖ − 1| < 1e-12` after any sequence of gates, evolution, collapse and expansion.
2. **Gate correctness:** each gate matrix is unitary and matches its textbook definition. Tests compare against known outputs, for example `H|0⟩ = (|0⟩ + |1⟩)/√2`.
3. **Composition:** `H·H = I` on one qubit within tolerance. Gate order is respected.
4. **Born rule:** with a fixed seed and `N` shots, empirical frequencies agree with `|ψ_k|²` under a chi-squared test at a stated significance level.
5. **Collapse:** after `measure(i)`, the qubit is in a basis state and `ψ` remains normalized.
6. **Reproducibility:** identical seeds give identical outcomes on Python 3.11, 3.12 and 3.13.
7. **Cross-profile consistency:** every profile that uses the base semantics passes the same test vectors. Any intentional difference is listed and tested.
8. **Compatibility:** each public surface in section 6 has a test. Each behavior change is listed in the changelog.
9. **Security documentation:** docstrings for `quantum_random_number` and `quantum_port` state that outputs are simulated and not for cryptographic use. A test asserts that wording is present.
10. **Separation check:** the PR does not describe the firewall as working unless `av_engine.py` is present and its tests pass.

---

## 10. Verification plan, Python 3.11–3.13

[Proposed] Each verification step runs on Python 3.11, 3.12 and 3.13, in a clean checkout, with run IDs recorded in the implementation PR:

1. Compile every tracked Python file (`git ls-files -z '*.py' | xargs -0 python -m py_compile`).
2. Duplicate-definition check (`.github/scripts/check_duplicate_definitions.py`).
3. Portable-path check (`.github/scripts/check_portable_paths.py`).
4. Build `ouroboros_sync` from source with `build_ouroboros_sync.sh`, using `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` (required for 3.13).
5. Full test suite (`python -m pytest -q -rs`).
6. Acceptance tests from section 9, including seeded Born-rule chi-squared checks.
7. Reproducibility check: run the seeded suite twice and compare outcomes byte for byte.

[Established] Local replays of steps 1–5 on the current `main` pass on 3.11, 3.12 and 3.13 (149 passed, 1 skipped for tkinter). GitHub CI on `55a4c61` passed (run 42532665284).

[Open] Whether seeded chi-squared tests should run on every CI matrix entry, or only on one, to bound runtime.

---

## 11. Open questions

1. Should `Alternative` adopt the common state vector, or remain a separate, explicitly non-quantum model under a different name?
2. Should the classical register survive as a deprecated view, or be removed?
3. How should `expand_qubits` extend the state? Tensor with `|0⟩` ancillas is the candidate.
4. Should `entangle` become a real two-qubit gate, or be removed?
5. Owner decision on the firewall: recover `av_engine.py` from its author, or mark the module non-functional.
6. Does the Hamiltonian evolution (`time_evolution`) preserve normalization? Not yet verified.

---

## 12. Non-goals

- Implementing the state-vector contract.
- Describing the simulator as physical quantum hardware, or as a source of hardware randomness.
- Supplying `av_engine.py`, changing firewall behavior, or claiming malware protection.
- Removing the committed `ouroboros_sync.so`.
- Changing repository settings, including enabling GitHub Issues.

---

## 13. Traceability

- Tracking task: #14 (working session).
- GitHub Issues: disabled on `ryansctt1994-sudo/Pandora` by owner decision. This document replaces the issue as the review record.
- Draft pull request: linked from task #14 when opened.
- Implementation PR: not yet created. It must link back to this document.

Evidence checklist for the eventual implementation PR:

- [ ] Review sign-off on sections 5 and 11
- [ ] Implementation PR links to this document
- [ ] Acceptance tests from section 9 pass on Python 3.11, 3.12 and 3.13 in CI, with run IDs recorded
- [ ] Compatibility list (section 6) reviewed against the implementation diff
- [ ] Security documentation (section 7) reviewed
- [ ] Firewall status (section 8) re-checked
