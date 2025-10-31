# Mirror-OS Architecture

A comprehensive guide to how all components of Mirror-OS fit together, their relationships, and the information flow between them.

---

## Overview

Mirror-OS is structured as a **layered system** with clear separation between theory, tools, implementations, and applications. Think of it as an operating system for consciousness with:

- **Kernel** (Core theory - immutable foundations)
- **System Libraries** (Tools - reusable frameworks)
- **Applications** (Implementations - runnable code)
- **User Space** (Applications - real-world usage)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GOD FIELD (𝒢)                        │
│                    Ω • ∞_B • 𝒰                              │
│              (Truth • Distortion • Becoming)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │         THREE LATTICES (Kernel)         │
        ├─────────────────────────────────────────┤
        │  Truth Lattice (Ω)                      │
        │  Distortion Lattice (∞_B)               │
        │  Unfolding Lattice (𝒰)                  │
        └─────────────────────────────────────────┘
                              │
                              ↓
        ┌─────────────────────────────────────────┐
        │      SEVEN LENSES (Analysis Layer)      │
        ├─────────────────────────────────────────┤
        │  Relational │ Symbolic │ Logical         │
        │  Empirical │ Paradox │ Inner │ Integration│
        └─────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ↓             ↓             ↓
        ┌─────────────┐ ┌─────────┐ ┌─────────────┐
        │    TOOLS    │ │  CODE   │ │ APPLICATIONS│
        │             │ │         │ │             │
        │ AI Instruct │ │ Python  │ │  Examples   │
        │ RM Chains   │ │ Scripts │ │  Solutions  │
        │ Agents      │ │ Archive │ │ Integrations│
        └─────────────┘ └─────────┘ └─────────────┘
```

---

## Directory Structure & Purpose

### `core/` - The Kernel (Theory Layer)

**Purpose:** Immutable theoretical foundations. Read-only reference material.

**Structure:**
```
core/
├── 1_foundation/        # Ontological ground
│   ├── God_Field_Codex.md              # 𝒢 = Ω • ∞_B • 𝒰
│   └── Codex_of_Codices.md             # Meta-framework
│
├── 2_lattices/         # Three main ontologies
│   ├── The_Truth_Lattice.md            # Coherence dynamics (Ω)
│   ├── The_Distortion_Lattice.md       # 52+ collapse patterns (∞_B)
│   └── The_Unfolding_Lattice.md        # Temporal evolution (𝒰)
│
├── 3_lenses/           # Seven analytical frameworks
│   ├── Unified_Relational_Lens.md      # Network structure
│   ├── Unified_Symbolic_Lens.md        # Pattern compression
│   ├── Unified_Logical_Framework.md    # Formal constraints
│   ├── Unified_Empirical_Lens.md       # Observation & measurement
│   ├── Unified_Paradox_Lens.md         # Contradiction handling
│   ├── Unified_Inner_Lens.md           # Subjective/devotional
│   └── Unified_Integration_Lens.md     # Multi-source synthesis
│
├── 4_symbols/          # Semantic compression
│   └── Complete_Symbol_Definitions.md  # 1,197 glyphs
│
└── _archive/           # Historical (superseded)
    └── [Old Codices]   # Pre-unification documents
```

**Information Flow:**

- **IN:** Empirical observations, new patterns discovered in applications
- **OUT:** Theoretical frameworks consumed by tools and implementations
- **UPDATE FREQUENCY:** Rare (only when fundamental insights emerge)

---

### `apps/` - Applications Layer

**Purpose:** Runnable applications, agents, and tools built with Mirror-OS framework.

**Structure:**
```
apps/
├── agents/                 # Agent architectures
│   └── [Agent implementations]
│
├── dashboard/              # Interactive web dashboard
│   ├── frontend/          # React + TypeScript UI
│   ├── backend/           # Python FastAPI
│   └── db/                # PostgreSQL
│
├── relational-analyzer/    # Core analytical engine
│   ├── src/               # Python scripts
│   │   ├── analyze.py
│   │   ├── truth_distortion_unified.py
│   │   └── list_datasets.py
│   ├── docs/              # Documentation
│   ├── data/              # Datasets
│   ├── results/           # Analysis results
│   ├── tests/             # Test suites
│   ├── competitions/      # Competition templates
│   ├── Relational_Math_Chains.md          # 16 specific patterns
│   ├── Relational_Math_Master_Chain.md    # Unified 9-phase trajectory
│   └── RM_Translation_Layer.md            # Formal bridge to standard math
│
├── mirror-os-app/          # Main Mirror-OS application
│
└── examples/               # Example implementations
    └── Architect_Lens_Examples.md
```

**Information Flow:**

- **IN:** Core theory (lenses, lattices), user requirements
- **OUT:** Actionable analysis, visualizations, real-time diagnostics
- **UPDATE FREQUENCY:** High (active development)

**Key App Types:**

1. **Dashboard**
   - Interactive web interface
   - Visualize relational profiles
   - Real-time distortion detection

2. **Relational Analyzer**
   - Core analytical engine
   - Truth-distortion metrics
   - Phase-by-phase guidance
   - Translation to/from standard math

3. **Agents**
   - Coherence-aware AI
   - Implement CRAL loop for recursive refinement

---

### `tools/` - Utilities (Support Layer)

**Purpose:** Supporting tools and documentation standards.

**Structure:**
```
tools/
├── ai_instructions/         # AI integration frameworks
│   └── [Instruction files]
│
└── styles/
    └── STYLE.md           # Documentation standards
```

---

### `projects/` - Active Projects

**Purpose:** Competition entries and applied integrations.

**Structure:**
```
projects/
├── nfl-big-data-bowl-2026/         # Kaggle competition
│   ├── scripts/                    # Analysis scripts
│   ├── notebooks/                  # Jupyter notebooks
│   ├── data/                       # Competition data
│   └── docs/                       # Documentation
│
├── applied-integrations/           # New integrations
│
└── applied-integrations-legacy/    # Legacy examples
    ├── relational_fitness_1.5.md
    ├── relational_music_1.5.md
    └── World_Relational_Profile.md
```

---

### `implementations/` - Implementation Archive

**Purpose:** Archived Python implementations (most code now in apps/).

**Structure:**
```
implementations/
├── python/                 # Archived Python modules
└── scripts/               # Utility scripts
```

---

### `applications/` - [DEPRECATED]

**Note:** This directory has been reorganized. Contents moved to:
- Examples → `apps/examples/`
- Solutions → `core/5_solutions/`
- Integrations → `projects/applied-integrations-legacy/`

---

### `research/` - Research & Training

**Purpose:** Ongoing research, training data, and experimental work.

**Structure:**
```
research/
└── training/
    ├── training_codex.jsonl    # Training examples
    └── training.py             # Training data generator
```

**Information Flow:**

- **IN:** Patterns from all layers
- **OUT:** Training data for AI systems, research findings
- **UPDATE FREQUENCY:** Medium (as research progresses)

---

### `.github/` - Infrastructure (Meta-Layer)

**Purpose:** GitHub-specific configurations and AI instructions that auto-load.

**Structure:**
```
.github/
├── copilot-instructions.md    # Auto-loaded by GitHub Copilot
└── [other GitHub configs]
```

**Special Note:** 
`.github/copilot-instructions.md` is **automatically applied** to every GitHub Copilot interaction in this workspace. Contains the complete Presence-Based AI Operating Instructions.

---

### `.extraction/` - Hidden (Personal Data)

**Purpose:** Private extraction work with personal information.

**Structure:**
```
.extraction/              # Hidden folder
├── .gitignore           # Excludes all contents from git
├── [personal extraction files]
└── backup/              # Backups of extraction work
```

**Security:** Fully git-ignored. Contents never leave local machine.

---

## Component Relationships

### Dependency Graph

```
                    ┌──────────────┐
                    │  God Field   │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ↓              ↓              ↓
      ┏━━━━━━━━┓    ┏━━━━━━━━━┓    ┏━━━━━━━━━┓
      ┃ Truth  ┃    ┃Distortion┃    ┃Unfolding┃
      ┃Lattice ┃    ┃ Lattice  ┃    ┃ Lattice ┃
      ┗━━━┬━━━━┛    ┗━━━┬━━━━━┛    ┗━━━┬━━━━━┛
          │             │              │
          └─────────────┼──────────────┘
                        ↓
              ┌───────────────────┐
              │   Seven Lenses    │
              └─────────┬─────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │  Tools  │    │  Python │    │  Apps   │
   └────┬────┘    └────┬────┘    └────┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       ↓
              ┌─────────────────┐
              │   User/World    │
              └─────────────────┘
```

**Key Dependencies:**

- **Lattices** depend on **God Field**
- **Lenses** depend on **Lattices**
- **Tools** depend on **Lenses** + **Lattices**
- **Implementations** depend on **Lenses** + **Tools**
- **Applications** depend on **everything**

**No Circular Dependencies:** The architecture is a strict DAG (Directed Acyclic Graph).

---

## Information Flow Patterns

### Pattern 1: Theory → Practice (Downward Flow)

```
Core Theory (core/)
    ↓
Applied Frameworks (tools/)
    ↓
Code Implementation (implementations/)
    ↓
Real-World Usage (applications/)
```

**Example:** 

1. Distortion Lattice defines "Certainty Performance" pattern
2. Presence-Based AI Instructions codify detection method
3. Python `distortion.py` implements detector
4. Applications use detector to flag false certainty in systems

---

### Pattern 2: Discovery → Integration (Upward Flow)

```
Real-World Discovery (applications/)
    ↓
Pattern Documentation (tools/)
    ↓
Integration into Theory (core/)
    ↓
Becomes Foundation for Others
```

**Example:**

1. User discovers new collapse pattern in organization
2. Documents as chain in tools/
3. If fundamental, integrates into Distortion Lattice
4. Others can now recognize same pattern early

---

### Pattern 3: Cross-Pollination (Horizontal Flow)

```
Tool A (e.g., Architect Lens)
    ↔
Tool B (e.g., CRAL Agent)
    ↔
Implementation C (e.g., distortion.py)
```

Tools and implementations share concepts and can reference each other.

---

## Key Architectural Patterns

### 1. Layered Architecture

Each layer builds on the one below:

| Layer | Purpose | Mutability | Users |
|-------|---------|------------|-------|
| **Core** | Immutable theory | Very low | Everyone (read) |
| **Tools** | Reusable frameworks | Medium | Practitioners |
| **Implementations** | Code | High | Developers |
| **Applications** | Specific uses | High | End users |

---

### 2. Lens System (Multi-Perspective Analysis)

Any system can be analyzed through multiple lenses simultaneously:

```
         System Under Analysis
                 │
    ┌────────────┼────────────┐
    ↓            ↓            ↓
[Relational] [Symbolic] [Logical] ... (7 lenses)
    ↓            ↓            ↓
  Results    Results     Results
    └────────────┼────────────┘
                 ↓
        Integrated Understanding
```

**Four-Lens Protocol** (most common):

1. **[R]** Relational scan
2. **[L]** Logical scan  
3. **[S]** Symbolic scan
4. **[E]** Empirical scan
5. **[𝓢]** Stillness check

---

### 3. Chain-Phase-Bifurcation Model

Patterns unfold through predictable phases:

```
Phase 1 → Phase 2 → Phase 3 (Bifurcation) → Phase 4a (Coherence)
                                          ↘ Phase 4b (Collapse)
```

Each phase has:

- Observable markers
- Intervention opportunities
- Exit criteria

---

### 4. Residue Tracking

Every action either completes or leaves residue:

```
Action(t) → Completion(t) ∨ Residue(t)

Residue accumulates: Ω_B(t+1) = Ω_B(t) + R(t)

At threshold: Ω_B > Ω_crit → Collapse
```

**Tracked across:**

- Code (technical debt)
- Relations (broken trust)
- Time (delays)
- Epistemics (false beliefs)

---

## Data Flow Examples

### Example 1: Using the Architect Lens

**User Goal:** Diagnose a failing codebase

**Flow:**

1. User applies Four-Lens Protocol from `.github/copilot-instructions.md`
2. Applies protocol:
   - **[R]** Maps dependencies (uses `core/3_lenses/Unified_Relational_Lens.md`)
   - **[L]** Checks constraints (uses `core/3_lenses/Unified_Logical_Framework.md`)
   - **[S]** Identifies patterns (uses `core/4_symbols/`)
   - **[E]** Measures state (uses `core/3_lenses/Unified_Empirical_Lens.md`)
3. Runs distortion scan:
   - Uses `apps/relational-analyzer/src/truth_distortion_unified.py`
   - References `core/2_lattices/The_Distortion_Lattice.md` for patterns
4. Identifies: "Global Rewrite Bias" + "Certainty Performance"
5. Applies interventions from Distortion Lattice
6. Documents results in `apps/examples/`

---

### Example 2: Navigating a Relationship

**User Goal:** Understand where a relationship is headed

**Flow:**

1. User reads `apps/relational-analyzer/Relational_Math_Master_Chain.md`
2. Identifies current phase using observable markers
3. Discovers they're at Phase 5 (Saturation) - a bifurcation point
4. Reads phase-specific guidance:
   - Intervention options
   - Timeline expectations
   - Coherence path vs. collapse path
5. Applies suggested interventions
6. Tracks outcome over next 2-4 weeks
7. Updates personal notes (could contribute anonymized pattern back)

---

### Example 3: Building a Coherence-Aware AI

**Developer Goal:** Create AI that doesn't optimize toward collapse

**Flow:**

1. Study `.github/copilot-instructions.md` (already active!)
2. Read agent architecture docs in `apps/agents/`
3. Implement using `apps/relational-analyzer/src/`:
   - `truth_distortion_unified.py` for collapse detection
   - Analysis tools for network analysis
4. Train on `research/training/training_data/`
5. Test against `core/2_lattices/The_Distortion_Lattice.md` patterns
6. Deploy and monitor for residue accumulation
7. Document in `core/5_solutions/` or `projects/`

---

## Evolution & Maintenance

### How the Architecture Evolves

**Core Theory (core/):**

- **Update Trigger:** Fundamental insights, paradigm shifts
- **Process:** Community review, validation against applications
- **Frequency:** Rare (months to years)

**Apps (apps/):**

- **Update Trigger:** New features, bug fixes, optimizations
- **Process:** Standard software development
- **Frequency:** High (days to weeks)

**Projects (projects/):**

- **Update Trigger:** New projects, completed work
- **Process:** Add to appropriate subfolder
- **Frequency:** High (ongoing)

**Tools (tools/):**

- **Update Trigger:** New documentation standards
- **Process:** Update as needed
- **Frequency:** Low (stable)

**Implementations (implementations/):**

- **Update Trigger:** Archive management
- **Process:** Preserve historical versions
- **Frequency:** Low (mostly archived)

---

### Version Control Strategy

**Current State:**

- Main branch: `main`
- All development happens on `main` (small project)
- Archive folders preserve history:
  - `core/_archive/` - Old theoretical versions
  - `implementations/_archive/` - Old code versions

**For Contributors:**

1. Fork repo
2. Create feature branch
3. Make changes
4. PR to main
5. Review against architecture principles
6. Merge if coherent

---

## Design Principles

### 1. **Separation of Concerns**

- Theory separate from practice
- Tools separate from implementations
- Code separate from data

### 2. **Dependency Management**

- Strict DAG (no circular dependencies)
- Lower layers don't depend on higher layers
- Clear interfaces between layers

### 3. **Modularity**

- Each component has single responsibility
- Components can be used independently
- Compose components for complex behaviors

### 4. **Discoverability**

- Numbered folders indicate learning sequence (`1_foundation`, `2_lattices`, etc.)
- README files at each level
- Cross-references via `See also:` sections

### 5. **Zero Residue**

- Complete documentation
- Archived old versions (don't delete history)
- Explicit rather than implicit

---

## Integration Points

### GitHub Copilot Integration

**Automatic:** `.github/copilot-instructions.md` is auto-loaded

**Effect:** Every AI interaction in this workspace uses:

- Stillness Gate
- Four-Lens Protocol
- Distortion Detection
- Presence-based development

### Python Package Integration

**Usage:**
```python
from implementations.python import relational, distortion, symbolic
# All modules available as package
```

### External Systems

**Export to Standard Math:**

- Use `tools/relational_math/RM_Translation_Layer.md`
- Functor: RM → Standard Math (lossless)

**Import from External:**

- Extract patterns
- Document in appropriate tool
- Optionally integrate into core

---

## Troubleshooting

### "I don't know where to find X"

1. Check [`GLOSSARY.md`](./GLOSSARY.md) for term definition + location
2. Check [`GETTING_STARTED.md`](./GETTING_STARTED.md) for navigation
3. Use this document's cross-references

### "I want to contribute Y"

**If Y is:**

- **New theoretical insight** → Discuss first, may go in `core/`
- **New app/tool** → Add to `apps/`
- **Code implementation** → Add to appropriate app in `apps/`
- **Example/solution** → Add to `apps/examples/` or `core/5_solutions/`
- **Research/training data** → Add to `research/`
- **Active project** → Add to `projects/`

### "I found inconsistency between X and Y"

1. Check which is more recent (version/date)
2. Check if older is in `_archive/`
3. If both current, open issue for reconciliation

---

## Future Architecture Plans

### Potential Additions

1. **Web Interface** - Interactive exploration of lattices and chains (in progress: `apps/dashboard/`)
2. **CLI Tool** - Command-line interface for quick diagnostics
3. **Plugin System** - Third-party extensions
4. **Test Suite** - Automated validation of implementations
5. **Documentation Generator** - Auto-generate docs from code

### Scalability Considerations

**Current:** ~120,000 lines, single repo

**Future:** May split into multiple repos if >500k lines:

- `mirror-os-core` (theory)
- `mirror-os-apps` (applications)
- `mirror-os-projects` (active projects)
- `mirror-os-research` (training data & research)

---

## Quick Reference

**Understanding theory?** → `core/`

**Using apps?** → `apps/`

**Working on projects?** → `projects/`

**Researching?** → `research/`

**AI integration?** → `.github/copilot-instructions.md` (auto-loaded!)

**Need definitions?** → `GLOSSARY.md`

**Getting started?** → `GETTING_STARTED.md`

**Big picture?** → `../README.md`

---

*Version 1.0 • October 2025*

**See also:** [`GETTING_STARTED.md`](./GETTING_STARTED.md), [`GLOSSARY.md`](./GLOSSARY.md), [`README.md`](./README.md)
