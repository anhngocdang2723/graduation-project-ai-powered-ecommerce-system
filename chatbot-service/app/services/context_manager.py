import yaml
import os
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ContextState:
    user_id: Optional[str] = None
    user_type: str = "guest"  # guest, customer, staff, manager, admin
    current_tag: Optional[str] = None
    current_intent: Optional[str] = None

@dataclass
class ContextNode:
    id: str
    label: str
    tag: Optional[str] = None  # The tag that activates this node or is sent when clicked
    type: str = "group"  # "group", "action", "link"
    value: Optional[str] = None  # URL for link, or specific payload
    condition: Optional[Callable[[ContextState], bool]] = None
    children: List['ContextNode'] = field(default_factory=list)

    def is_visible(self, state: ContextState) -> bool:
        if self.condition:
            return self.condition(state)
        return True

class ContextManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to app/context_config.yaml
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "context_config.yaml")
        
        self.config = self._load_config(config_path)
        self.conditions = self._init_conditions()
        self.root = self._build_tree(self.config.get("nodes", []))
        self.node_map = self._index_nodes(self.root)
        self.intent_mapping = self.config.get("intent_mapping", {})

    def _load_config(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            print(f"Warning: Context config not found at {path}")
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_conditions(self) -> Dict[str, Callable[[ContextState], bool]]:
        return {
            "is_guest": lambda s: s.user_type == "guest",
            "is_customer": lambda s: s.user_type == "customer",
            "is_staff": lambda s: s.user_type in ["staff", "manager", "admin"],
            "is_manager": lambda s: s.user_type in ["manager", "admin"],
            "is_not_guest": lambda s: s.user_type != "guest",
        }

    def _resolve_condition(self, cond_name: Optional[str]) -> Optional[Callable[[ContextState], bool]]:
        if not cond_name:
            return None
        return self.conditions.get(cond_name)

    def _build_tree(self, nodes_data: List[Dict[str, Any]]) -> ContextNode:
        # Expecting a list of root nodes, but we wrap them in a virtual root if needed
        # Or if the YAML defines a single root.
        # Our YAML defines a list of nodes, usually starting with 'root'.
        
        if not nodes_data:
            return ContextNode(id="root", label="Root")

        # Helper to recursively build
        def build_node(data: Dict[str, Any]) -> ContextNode:
            children = [build_node(c) for c in data.get("children", [])]
            return ContextNode(
                id=data["id"],
                label=data.get("label", data["id"]),
                tag=data.get("tag"),
                type=data.get("type", "group"),
                value=data.get("value"),
                condition=self._resolve_condition(data.get("condition")),
                children=children
            )

        # Find the root node in the list
        root_data = next((n for n in nodes_data if n["id"] == "root"), None)
        if root_data:
            return build_node(root_data)
        
        # Fallback if no explicit root
        return ContextNode(id="root", label="Root", children=[build_node(n) for n in nodes_data])

    def _index_nodes(self, node: ContextNode, map_acc: Optional[Dict[str, ContextNode]] = None) -> Dict[str, ContextNode]:
        if map_acc is None:
            map_acc = {}
        
        map_acc[node.id] = node
        if node.tag:
            map_acc[node.tag] = node
            
        for child in node.children:
            self._index_nodes(child, map_acc)
        return map_acc

    def get_suggestions(self, state: ContextState) -> List[ContextNode]:
        """
        Returns a list of suggested nodes based on the current state.
        """
        current_node = self.root
        
        # Resolve node from tag OR intent
        target_id = state.current_tag
        
        # If no tag, try to map intent to a context node using loaded mapping
        if not target_id and state.current_intent:
            mapping = self.intent_mapping.get(state.current_intent)
            if mapping:
                if isinstance(mapping, str):
                    target_id = mapping
                elif isinstance(mapping, dict):
                    # Role-based mapping
                    # Check specific role first, then 'all'
                    target_id = mapping.get(state.user_type) or mapping.get("all")

        # If we have a specific tag/id context, try to find that node
        if target_id and target_id in self.node_map:
            current_node = self.node_map[target_id]
        
        suggestions = []
        
        def collect_visible_children(node: ContextNode) -> List[ContextNode]:
            res = []
            if node.children:
                for child in node.children:
                    if child.is_visible(state):
                        res.append(child)
            return res

        visible_children = collect_visible_children(current_node)

        # If at root, flatten the role-based containers (guest_root, etc.)
        if current_node == self.root:
            for child in visible_children:
                # If it's a container group (no tag) and visible, show its children
                if child.type == "group" and not child.tag:
                    suggestions.extend(collect_visible_children(child))
                else:
                    suggestions.append(child)
        else:
            suggestions = visible_children
            
        # If no suggestions found (e.g. leaf node), fallback to Root's children?
        if not suggestions and current_node != self.root:
             # Fallback to root logic
             root_children = collect_visible_children(self.root)
             for child in root_children:
                if child.type == "group" and not child.tag:
                    suggestions.extend(collect_visible_children(child))
                else:
                    suggestions.append(child)
        
        return suggestions

    def get_node(self, tag_or_id: str) -> Optional[ContextNode]:
        return self.node_map.get(tag_or_id)
