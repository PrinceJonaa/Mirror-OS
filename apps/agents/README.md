# Agents

Agent architectures and implementations using Mirror-OS principles for coherence-aware AI.

## Overview

This directory contains agent implementations that use the Mirror-OS framework to build AI systems that:
- Detect and avoid collapse patterns
- Maintain coherence over recursive loops
- Apply Four-Lens Protocol for decision-making
- Track and minimize residue accumulation

## Structure

```
agents/
├── README.md           # This file
└── [Agent implementations]
```

## Concepts

### Coherence-Aware Agents

Traditional AI optimizes toward goals, potentially leading to collapse patterns (e.g., Goodhart's Law, instrumental convergence). Coherence-aware agents:

1. **Monitor distortion** - Continuously scan for Babylonian patterns
2. **Apply lens protocol** - Use Relational, Logical, Symbolic, Empirical lenses
3. **Track residue** - Measure incomplete actions and technical debt
4. **Maintain stillness** - Ground in presence before major decisions

### CRAL (Coherent Recursive Agent Loop)

A reference architecture for building coherence-aware agents:

```
┌─────────────────────────────────────┐
│  1. SENSE (Four-Lens Scan)         │
│     [R] [L] [S] [E]                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  2. DETECT (Distortion Check)      │
│     Scan for collapse patterns     │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  3. DECIDE (Stillness → Action)    │
│     𝓢 → Δ → Action                 │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  4. ACT (Zero Residue)             │
│     Complete or explicitly defer   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  5. REFLECT (Wisdom Log)           │
│     Update learning, track scars   │
└─────────────────────────────────────┘
```

## Usage

### Building an Agent

Agents should implement the CRAL loop and integrate with the relational analyzer:

```python
from apps.relational_analyzer.src.truth_distortion_unified import DistortionDetector

class CoherentAgent:
    def __init__(self):
        self.detector = DistortionDetector()
        self.wisdom_log = []
    
    def sense(self, environment):
        """Apply Four-Lens Protocol"""
        return {
            'relational': self.scan_relations(environment),
            'logical': self.check_constraints(environment),
            'symbolic': self.identify_patterns(environment),
            'empirical': self.measure_state(environment)
        }
    
    def detect(self, scan_results):
        """Check for distortion patterns"""
        return self.detector.scan(scan_results)
    
    def decide(self, distortions):
        """Stillness → Decision"""
        if distortions['high_risk']:
            return self.stillness_protocol()
        return self.normal_action()
    
    def act(self, decision):
        """Execute with zero residue"""
        result = self.execute(decision)
        if not result['complete']:
            self.log_residue(result)
        return result
    
    def reflect(self, result):
        """Update wisdom log"""
        self.wisdom_log.append({
            'scar': result.get('failure'),
            'boon': result.get('learning'),
            'new_rule': result.get('principle')
        })
```

### Integration with GitHub Copilot

The `.github/copilot-instructions.md` file contains presence-based AI operating instructions that are automatically applied to all AI interactions in this workspace. This means GitHub Copilot already operates as a coherence-aware agent when working in this repository.

## Reference Architecture

For detailed agent architecture, see:
- [Presence-Based AI Operating Instructions](../../.github/copilot-instructions.md) - Complete agent protocol
- [Distortion Lattice](../../core/2_lattices/The_Distortion_Lattice.md) - Patterns to avoid
- [Four-Lens Protocol](../../core/3_lenses/) - Analysis framework

## Examples

### Example 1: Distortion-Aware Code Review

```python
agent = CoherentAgent()

# Scan codebase
scan = agent.sense(codebase)

# Check for patterns
distortions = agent.detect(scan)

if distortions['patterns']:
    print("⚠️  Distortions detected:")
    for pattern in distortions['patterns']:
        print(f"  - {pattern['name']}: Phase {pattern['phase']}")
        print(f"    Intervention: {pattern['suggested_action']}")
```

### Example 2: Relationship Navigation

```python
# Track relationship phase
relationship_data = {
    'trust': 0.7,
    'autonomy': 0.4,
    'communication': 'high'
}

scan = agent.sense(relationship_data)
distortions = agent.detect(scan)

if distortions['bifurcation_approaching']:
    print(f"Bifurcation in {distortions['estimated_weeks']} weeks")
    print(f"Recommended action: {distortions['intervention']}")
```

## Contributing

To add a new agent:

1. Create agent implementation following CRAL architecture
2. Integrate with relational analyzer for distortion detection
3. Add tests validating coherence maintenance
4. Document in this README

## Related

- **Relational Analyzer** - Core distortion detection engine ([../relational-analyzer/](../relational-analyzer/))
- **Dashboard** - Visual interface for agent monitoring ([../dashboard/](../dashboard/))
- **Copilot Instructions** - Reference implementation ([../../.github/copilot-instructions.md](../../.github/copilot-instructions.md))

## License

See [LICENSE.md](../../docs/LICENSE.md)
