# Swift Importer Plan (CLI-First, Test-Driven)

## Goal

Bring the Swift CLI importer to functional parity with the existing implementation by driving all compatibility tests to green, while keeping a durable architecture that can continue toward full feature parity.

## Scope and Constraints

- Keep the Swift port in this repo under `/Users/paulo/Developer/sketch-hq/fig2sketch/swift/`.
- Keep CLI contract compatible: `fig2sketch <input.fig> <output.sketch>` and existing flags.
- Treat the existing implementation and test suite as behavioral oracle.
- Prioritize architecture that supports iterative expansion; avoid one-off slice code.

## Current Baseline (2026-03-12, oracle and stability pass)

Command:

- `swift test --disable-sandbox`

Result:

- 187 tests executed
- 0 failures
- 0 unexpected failures
- parity hardening delta: maintained `0` failures while changing mapper/frame semantics
- CLI parity delta: executable now uses shared `CLIParser` contract (no `ArgumentParser`-derived `fig2-sketch-command` help surface)
- version parity delta: runtime version source now resolves repo-local Python package metadata when running from this checkout, so local Swift builds match the Python CLI's reported version
- CLI UX delta: help text, parse-error wording, and parse-failure exit code now align with the Python `fig2sketch` entrypoint shape
- font-resolution delta: cache miss now follows the Python Google Fonts fetch/download path and emits Python-style warning messages
- mapper organization delta: `FigTreeToDocumentMapper` is now split into concern-focused extensions (`LayerNodes`, `Layout`, `Styles`, `CroppedImages`) with behavior preserved under full test coverage
- vector organization delta: vector-network and shape-path mapping now live in `/Users/paulo/Developer/sketch-hq/fig2sketch/swift/Sources/Fig2SketchCore/Import/FigTreeToDocumentMapper+Vector.swift`
- archive organization delta: `SketchBundleBuilder` is split into assembly, layer/style JSON, page support, and asset preparation files
- orchestration naming delta: CLI/tests now call `CLIConversionRunner` directly; the `StubConverter` pass-through shim has been removed
- oracle regression delta: Python-vs-Swift semantic oracle tests now run against `tests/data/structure.fig`, `tests/data/vector.fig`, and `tests/data/broken_images.fig`
- stability delta: version resolution now has bounded ancestor traversal, and version tests run against an in-memory filesystem rather than host filesystem state
- validation note: raw `.sketch` archive bytes are not stable under the default CLI path because object IDs are salted with a fresh UUID; even with a fixed salt, ZIP entry headers still carry current modification times, so regression checks should compare unpacked entry contents, not only top-level archive hashes
- refactor verification note: fixed-salt unpacked outputs for `tests/data/vector.fig`, `tests/data/structure.fig`, and `tests/data/broken_images.fig` matched the pre-refactor baseline exactly

Python-vs-Swift semantic spot-check fixtures:

- `tests/data/broken_images.fig`: coordinate-space mismatch fixed (child layers now parent-local).
- `tests/data/structure.fig`: detached instance class/frame parity fixed (`Component 3` now `group` at local coordinates).
- `tests/data/vector.fig`: vector region/loop hierarchy and shape-path geometry parity fixed (points/handles/closed flags align semantically with oracle).

Compatibility baseline status:

- `ConverterTest_frameTests`: 0 failures
- `ConverterTest_groupTests`: 0 failures
- `ConverterTest_layoutTests`: 0 failures
- `ConverterTest_instanceTests`: 0 failures
- `ConverterTest_symbolTests`: 0 failures
- `ConverterTest_textTests`: 0 failures
- `ConverterTest_prototypeTests`: 0 failures
- `ConverterTest_shape_pathTests`: 0 failures
- `ConverterTest_styleTests`: 0 failures
- `ConverterTest_userTests`: 0 failures
- `IntegrationTest_structureTests`: 0 failures
- `ConverterTest_baseTests`: 0 failures
- `ConverterTest_positioningTests`: 0 failures

## Priority-Ordered Workstreams

### 1) Core Importer Kernel and Cross-Cutting Semantics (Completed)

Why first:

- Most remaining suites are blocked by missing generic node-conversion infrastructure, not isolated feature bugs.

Primary concerns:

- Introduce a node conversion pipeline (type dispatch + shared conversion context).
- Centralize deterministic IDs, warnings, inherited style resolution, and child ordering.
- Match positioning edge-case behavior (NaN/zero-size handling).

Expected impact:

- Unblocks coherent implementation of frame/group/layout/symbol/text/prototype without duplicating logic.

### 2) Container Nodes and Layout Semantics (Completed)

Why second:

- Largest failure cluster (frame/group/layout = 89 failures) and foundational for page structure.

Primary concerns:

- Frame and group conversion behavior.
- Background treatment, clipping behavior, resize constraints.
- Layout grids and auto-layout serialization.
- Proper layer ordering and nested coordinate mapping.

Expected impact:

- Restores structural correctness for most document-level conversion and reduces integration drift.

### 3) Components, Symbols, and Instances (Completed)

Why third:

- Depends on stable container and inheritance behavior.

Primary concerns:

- Symbol master/page generation.
- Instance conversion in `detach` and `ignore` modes.
- Override propagation (fill/border/text/property overrides).

Expected impact:

- Closes high-value gaps in real design-system documents.

### 4) Text Engine Parity (Completed)

Why fourth:

- High failure count, but should be implemented on top of stable container/context and override plumbing.

Primary concerns:

- Attributed string run segmentation.
- Multi-color, emoji, and multi-code-point handling.
- Kerning rules and feature flags.
- Font references and serialization hooks required by package integration tests.

Expected impact:

- Resolves most content-level visual mismatches.

### 5) Prototype/Interaction Mapping (Completed)

Why fifth:

- Mostly independent once symbols/instances and page/layer IDs are stable.

Primary concerns:

- Flow actions, overlay actions, manual placement, discard/warning behavior.

Expected impact:

- Brings interactive document behavior into compatibility range.

### 6) Vector/Shape-Path Completeness (Completed)

Why sixth:

- Smaller failure count and isolated geometry behaviors.

Primary concerns:

- Winding-rule behavior, arrow overrides, complex/empty vector path handling.

Expected impact:

- Closes remaining shape-path-specific conversion mismatches.

### 7) Package Assembly and Integration Fidelity (Completed)

Why last:

- Final assembly depends on prior conversion correctness.

Primary concerns:

- `document.json`, `meta.json`, `user.json` parity details.
- Multi-page output (including symbols page).
- Fonts/assets inclusion and file hashes.
- Final archive file list/entry parity.

Expected impact:

- Clears end-to-end integration tests and validates converter output as a complete Sketch archive.

### 8) Semantic Parity Hardening (Completed)

Why now:

- Compatibility tests are green, but oracle comparison still shows semantic deltas that affect correctness confidence on real files.

Primary concerns:

- Keep decoded layer coordinates in node-local space (no synthetic parent-offset accumulation).
- Align detached-instance container class semantics with oracle behavior.
- Build vector layer hierarchy from decoded vector network topology (regions/loops/segments), not a flattened placeholder shape group.

Done in this pass:

- Local-coordinate frame model applied across importer mapping.
- Detached unsupported instance overrides now emit `group` container semantics.
- Vector conversion now decodes and maps region/loop hierarchy from vector network data (including blob-backed networks).
- Shape-path geometry model and serialization now emit `points`, handle vectors, and `isClosed` for vector loops.

Outcome:

- Semantic oracle checks now cover the existing real fixtures and pass against the repo-local Python implementation.
- Remaining differences observed on checked fixtures are limited to metadata-only formatting (not render-critical semantics).

### 9) Semantic Oracle Regression Harness (Completed)

Why next:

- Compatibility suites were green, but they still needed a committed Python-vs-Swift regression layer over the real `.fig` fixtures already in the repo.

Primary concerns:

- Discover and run the repo-local Python oracle deterministically.
- Compare unpacked archive entry contents, not raw `.sketch` ZIP bytes.
- Compare JSON semantically while ignoring non-render-critical formatting noise.
- Keep `user.json` validation in integration tests rather than duplicating that contract in the oracle.

Done in this pass:

- Added repo-local oracle discovery (`.venv/bin/fig2sketch` first, then `.venv/bin/python src/fig2sketch.py`).
- Added semantic archive comparison for `document.json`, `meta.json`, page JSON, and binary asset entries.
- Normalized numeric and point-string formatting differences during semantic comparison.
- Added one oracle test per real fixture: `structure.fig`, `vector.fig`, and `broken_images.fig`.
- Kept the full Swift suite green after adding oracle coverage.
- Hardened version-resolution tests by replacing host-filesystem fixtures with an in-memory fake filesystem and bounding ancestor traversal in production code.

Outcome:

- Oracle tests pass when the repo-local Python converter is available.
- Oracle tests skip cleanly when the repo-local Python converter is unavailable.
- Fixture failures report archive entry and normalized JSON path.

## Next Phase Priorities

1. Expand fixture coverage when more real `.fig` files are available.
2. Deepen oracle normalization only if it reveals additional render-critical mismatches.
3. Treat deterministic ZIP metadata or point-string normalization as diff-hygiene work, not a v1 blocker.

## Completed Foundations

- Real `.fig` decode path and CLI conversion path to `.sketch`.
- Rectangle conversion with fill, stroke, and opacity.
- Gradient, effect, and image style foundations plus serialization.
- Cropped-image rewrite foundation and image warning codes.
- Full compatibility test port into the Swift test target.
- Symbol masters, symbols page assembly, and instance override modes (`detach` / `ignore`).
- Text attributed runs, emoji segmentation, kerning conversion, and OpenType feature mapping.

## CLI Parity Status

What now matches the Python venv entrypoint closely:

- executable name and flag surface (`fig2sketch`)
- argparse-style `--help` text layout
- argparse-style parse errors for unknown options, missing values, invalid choices, and missing required positionals
- parse-failure exit code (`2`)
- font warning wording on Google Fonts lookup/download failures

What remains context-dependent:

- if the CLI is run outside a repo checkout and without `FIG2SKETCH_VERSION` or bundle metadata, `--version` still falls back to `unknown version`

## Architecture Rules for Implementation

- Keep module boundaries explicit:
  - Decode (`FigFormat`)
  - Mapping (`Fig2SketchCore/Import`)
  - Output assembly (`Fig2SketchCore/SketchArchive`)
- Introduce extension points instead of adding more logic directly into `FigTreeToDocumentMapper`.
- Keep mapper concerns split by domain (`LayerNodes`, `Layout`, `Styles`, `CroppedImages`, and later `Vector`) instead of re-growing a single monolithic importer file.
- Keep archive serialization split by concern (`SketchBundleBuilder`, `+LayerJSON`, `+StyleJSON`, `+PageSupport`, `+Assets`) instead of re-growing `SketchBundleBuilder.swift`.
- Prefer small, typed value models over ad hoc dictionary mutation.
- Each new behavior should land with focused compatibility tests and local unit tests.

## Execution Strategy

For each workstream:

1. Port one concern end-to-end (decode -> map -> bundle output).
2. Run targeted compatibility tests for that concern.
3. Run full test suite, capture delta in failure counts.
4. Update `/Users/paulo/Developer/sketch-hq/fig2sketch/swift/PLAN.md`.

Definition of completion:

- All compatibility suites green under `swift test`.
- Existing core/unit tests stay green.
- CLI conversion remains functional for real fixtures (including `/Users/paulo/Downloads/rectangle.fig`).
