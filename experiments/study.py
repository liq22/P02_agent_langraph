"""Paper-owned conditions using the shared Benchmark study functions."""
from pathlib import Path
from phm_agent_benchmark.research.cli import main
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = {'graph': ['generic', 'graph'], 'graph-components': ['factorial-reactive', 'factorial-state', 'factorial-filter', 'factorial-both'], 'graph-memory': ['graph', 'graph-no-memory'], 'horizon': ['generic', 'graph'], 'all': ['generic', 'graph', 'factorial-reactive', 'factorial-state', 'factorial-filter', 'factorial-both', 'graph-no-memory']}
DESIGNS = [('graph minus generic', [(1, 'graph'), (-1, 'generic')]), ('graph-no-memory minus generic', [(1, 'graph-no-memory'), (-1, 'generic')]), ('factorial-state minus factorial-reactive', [(1, 'factorial-state'), (-1, 'factorial-reactive')]), ('factorial-filter minus factorial-reactive', [(1, 'factorial-filter'), (-1, 'factorial-reactive')]), ('factorial-both minus factorial-reactive', [(1, 'factorial-both'), (-1, 'factorial-reactive')]), ('graph cue-filter interaction', [(1, 'factorial-both'), (-1, 'factorial-state'), (-1, 'factorial-filter'), (1, 'factorial-reactive')])]

def make_policy(condition, client, model, seed, selected_model):
    from phm_graph_agent.agent import GraphDecisionAgent
    from phm_graph_agent.state import GraphPolicyConfig
    from phm_graph_agent.components import make_component_agent
    if condition in {"graph", "graph-no-memory"}:
        profile = "no_persistent_graph_state" if condition == "graph-no-memory" else "full"
        return GraphDecisionAgent(client, model=model, policy_config=GraphPolicyConfig.for_profile(profile))
    return make_component_agent(condition, client, model)

if __name__ == "__main__":
    main(root=ROOT, experiments=EXPERIMENTS, policy_factory=make_policy,
         sources={"graph_entry": (ROOT, ["experiments/study.py", "experiments/run.sh", "src/phm_graph_agent"])},
         owner="graph", designs=DESIGNS)
