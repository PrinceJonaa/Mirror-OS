# run_agents.py
"""
Run orchestrated AI agents inside the Truth Lattice framework.
Each agent corresponds to a lens (R, S, L, E, P) with Inner Devotion binding them.
"""

from truth_lattice import TruthLattice
from relational import RelationalLens
from symbolic import SymbolicLens
from logical import LogicalLens
from empirical import EmpiricalLens
from paradox import ParadoxField

class AgentRunner:
    def __init__(self):
        self.lattice = TruthLattice()
        self.agents = {
            "R": RelationalLens(self.lattice),
            "S": SymbolicLens(self.lattice),
            "L": LogicalLens(self.lattice),
            "E": EmpiricalLens(self.lattice),
            "P": ParadoxField(self.lattice),
        }

    def run_cycle(self, task):
        """Run one O-P-W-T-R cycle (Orient, Plan, Write, Test, Reflect)."""
        print(f"\n--- Running Task: {task} ---")
        
        # 1. Orient (R + S)
        rel_output = self.agents["R"].analyze(task)
        sym_output = self.agents["S"].compress(task)
        
        # 2. Plan (L)
        plan = self.agents["L"].structure(task, rel_output, sym_output)
        
        # 3. Write (implementation stub, could expand later)
        draft = f"Drafting based on plan: {plan}"
        
        # 4. Test (E)
        test_result = self.agents["E"].verify(draft)
        
        # 5. Reflect (P)
        reflection = self.agents["P"].hold_and_resolve([rel_output, sym_output, plan, test_result])
        
        # Log into lattice
        self.lattice.log_trace(task, {
            "R": rel_output,
            "S": sym_output,
            "L": plan,
            "E": test_result,
            "P": reflection,
        })
        
        return reflection

if __name__ == "__main__":
    runner = AgentRunner()
    
    # Example tasks
    tasks = [
        "Design a micro-service offering for Intervised LLC",
        "Formulate devotion as a logical axiom",
        "Integrate paradox into a repeatable algorithm",
    ]
    
    for t in tasks:
        result = runner.run_cycle(t)
        print("Reflection:", result)