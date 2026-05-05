"""
Orchestrator Graph
Defines the DAG (Directed Acyclic Graph) for the pipeline workflow
"""

from typing import Dict, Any, Callable, List
from dataclasses import dataclass


@dataclass
class Node:
    """Represents a node in the pipeline graph"""
    name: str
    execute: Callable
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PipelineGraph:
    """
    Defines the execution graph for the CineAI pipeline

    The graph structure is:
    START -> Story Generation -> Audio Generation -> Video Generation -> END
                                                    ↓
                                            Edit Agent (can modify any phase)
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.execution_order: List[str] = []

    def add_node(self, name: str, execute_fn: Callable, dependencies: List[str] = None):
        """Add a node to the graph"""
        if dependencies is None:
            dependencies = []

        node = Node(name=name, execute=execute_fn, dependencies=dependencies)
        self.nodes[name] = node

    def build(self):
        """Build the execution order using topological sort"""
        # Simple implementation: assume linear pipeline for now
        self.execution_order = [
            "story_generation",
            "audio_generation",
            "video_generation"
        ]

    def get_execution_order(self) -> List[str]:
        """Get the nodes in execution order"""
        if not self.execution_order:
            self.build()
        return self.execution_order

    def get_node(self, name: str) -> Node:
        """Get a specific node"""
        return self.nodes.get(name)
