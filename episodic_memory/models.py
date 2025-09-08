from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# --- Data Models (minimal typing + validation) ---


@dataclass
class SystemConfiguration:
    similarity_threshold: float = 0.7
    max_retrieval_results: int = 5
    auto_clustering_enabled: bool = False
    temporal_decay_factor: float = 0.95

    @staticmethod
    def from_dict(d: dict) -> "SystemConfiguration":
        return SystemConfiguration(
            similarity_threshold=float(d.get("similarity_threshold", 0.7)),
            max_retrieval_results=int(d.get("max_retrieval_results", 5)),
            auto_clustering_enabled=bool(d.get("auto_clustering_enabled", False)),
            temporal_decay_factor=float(d.get("temporal_decay_factor", 0.95)),
        )


@dataclass
class SystemMetadata:
    version: str
    created_at: str
    updated_at: str
    embedding_dimension: int
    total_memories: int
    storage_path: str
    configuration: SystemConfiguration

    @staticmethod
    def from_dict(d: dict) -> "SystemMetadata":
        cfg = SystemConfiguration.from_dict(d.get("configuration", {}))
        return SystemMetadata(
            version=str(d.get("version", "0.0.1")),
            created_at=str(d.get("created_at", "")),
            updated_at=str(d.get("updated_at", "")),
            embedding_dimension=int(d.get("embedding_dimension", 4)),
            total_memories=int(d.get("total_memories", 0)),
            storage_path=str(d.get("storage_path", ".")),
            configuration=cfg,
        )


@dataclass
class GovernanceProvenance:
    step: str
    actor: str
    time: str
    hash: str

    @staticmethod
    def from_dict(d: dict) -> "GovernanceProvenance":
        return GovernanceProvenance(
            step=str(d.get("step", "")),
            actor=str(d.get("actor", "")),
            time=str(d.get("time", "")),
            hash=str(d.get("hash", "")),
        )


@dataclass
class GovernanceRetentionPolicy:
    class_: str
    review_after: str
    decay: str

    @staticmethod
    def from_dict(d: dict) -> "GovernanceRetentionPolicy":
        return GovernanceRetentionPolicy(
            class_=str(d.get("class", "normal")),
            review_after=str(d.get("review_after", "")),
            decay=str(d.get("decay", "linear")),
        )


@dataclass
class GovernanceAccessControl:
    read: List[str]
    write: List[str]

    @staticmethod
    def from_dict(d: dict) -> "GovernanceAccessControl":
        return GovernanceAccessControl(
            read=[str(x) for x in d.get("read", [])],
            write=[str(x) for x in d.get("write", [])],
        )


@dataclass
class Governance:
    provenance_chain: List[GovernanceProvenance] = field(default_factory=list)
    retention_policy: Optional[GovernanceRetentionPolicy] = None
    access_control: Optional[GovernanceAccessControl] = None

    @staticmethod
    def from_dict(d: dict) -> "Governance":
        return Governance(
            provenance_chain=[GovernanceProvenance.from_dict(x) for x in d.get("provenance_chain", [])],
            retention_policy=GovernanceRetentionPolicy.from_dict(d.get("retention_policy", {})) if d.get("retention_policy") else None,
            access_control=GovernanceAccessControl.from_dict(d.get("access_control", {})) if d.get("access_control") else None,
        )


@dataclass
class Emotion:
    emotion: str
    intensity: float

    @staticmethod
    def from_dict(d: dict) -> "Emotion":
        return Emotion(emotion=str(d.get("emotion", "unknown")), intensity=float(d.get("intensity", 0.0)))


@dataclass
class EncodedExperience:
    raw_text: str
    vector_embedding: List[float]
    reward_signal: float
    emotional_tone: str
    context_tags: List[str]
    importance_score: float
    associated_emotions: List[Emotion] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict) -> "EncodedExperience":
        return EncodedExperience(
            raw_text=str(d.get("raw_text", "")),
            vector_embedding=list(map(float, d.get("vector_embedding", []))),
            reward_signal=float(d.get("reward_signal", 0.0)),
            emotional_tone=str(d.get("emotional_tone", "neutral")),
            context_tags=[str(x) for x in d.get("context_tags", [])],
            importance_score=float(d.get("importance_score", 0.0)),
            associated_emotions=[Emotion.from_dict(x) for x in d.get("associated_emotions", [])],
        )


@dataclass
class MemoryStamp:
    timestamp: str
    event_id: str
    location: str
    source: str
    signature_hash: str
    session_id: str
    user_id: str

    @staticmethod
    def from_dict(d: dict) -> "MemoryStamp":
        return MemoryStamp(
            timestamp=str(d.get("timestamp", "")),
            event_id=str(d.get("event_id", "")),
            location=str(d.get("location", "")),
            source=str(d.get("source", "unknown")),
            signature_hash=str(d.get("signature_hash", "")),
            session_id=str(d.get("session_id", "")),
            user_id=str(d.get("user_id", "")),
        )


@dataclass
class RelatedNode:
    target_node_id: str
    connection_strength: float
    connection_type: str
    created_at: str

    @staticmethod
    def from_dict(d: dict) -> "RelatedNode":
        return RelatedNode(
            target_node_id=str(d.get("target_node_id", "")),
            connection_strength=float(d.get("connection_strength", 0.0)),
            connection_type=str(d.get("connection_type", "semantic")),
            created_at=str(d.get("created_at", "")),
        )


@dataclass
class GraphNode:
    node_id: str
    connections: List[RelatedNode]
    centrality_score: float
    clustering_coefficient: float

    @staticmethod
    def from_dict(d: dict) -> "GraphNode":
        return GraphNode(
            node_id=str(d.get("node_id", "")),
            connections=[RelatedNode.from_dict(x) for x in d.get("connections", [])],
            centrality_score=float(d.get("centrality_score", 0.0)),
            clustering_coefficient=float(d.get("clustering_coefficient", 0.0)),
        )


@dataclass
class IndexMap:
    semantic_cluster_id: str
    time_index: str
    graph_node_id: str
    related_nodes: List[str]
    hierarchical_path: List[str]
    access_frequency: int
    last_accessed: str

    @staticmethod
    def from_dict(d: dict) -> "IndexMap":
        return IndexMap(
            semantic_cluster_id=str(d.get("semantic_cluster_id", "cluster_0")),
            time_index=str(d.get("time_index", "")),
            graph_node_id=str(d.get("graph_node_id", "")),
            related_nodes=[str(x) for x in d.get("related_nodes", [])],
            hierarchical_path=[str(x) for x in d.get("hierarchical_path", [])],
            access_frequency=int(d.get("access_frequency", 0)),
            last_accessed=str(d.get("last_accessed", "")),
        )


@dataclass
class IntegrationPlan:
    augmentation_target: str
    confidence_score: float
    integration_notes: str
    priority_weight: float
    staleness_factor: float
    context_relevance: float

    @staticmethod
    def from_dict(d: dict) -> "IntegrationPlan":
        return IntegrationPlan(
            augmentation_target=str(d.get("augmentation_target", "LLM_context")),
            confidence_score=float(d.get("confidence_score", 0.0)),
            integration_notes=str(d.get("integration_notes", "")),
            priority_weight=float(d.get("priority_weight", 0.0)),
            staleness_factor=float(d.get("staleness_factor", 0.0)),
            context_relevance=float(d.get("context_relevance", 0.0)),
        )


@dataclass
class MemoryEntry:
    memory_stamp: MemoryStamp
    encoded_experience: EncodedExperience
    index_map: IndexMap
    integration_plan: IntegrationPlan

    @staticmethod
    def from_dict(d: dict) -> "MemoryEntry":
        return MemoryEntry(
            memory_stamp=MemoryStamp.from_dict(d.get("memory_stamp", {})),
            encoded_experience=EncodedExperience.from_dict(d.get("encoded_experience", {})),
            index_map=IndexMap.from_dict(d.get("index_map", {})),
            integration_plan=IntegrationPlan.from_dict(d.get("integration_plan", {})),
        )


@dataclass
class SemanticCluster:
    cluster_id: str
    centroid_embedding: List[float]
    member_count: int
    memory_ids: List[str]
    creation_timestamp: str
    last_updated: str
    cluster_quality_score: float

    @staticmethod
    def from_dict(d: dict) -> "SemanticCluster":
        return SemanticCluster(
            cluster_id=str(d.get("cluster_id", "cluster_0")),
            centroid_embedding=[float(x) for x in d.get("centroid_embedding", [])],
            member_count=int(d.get("member_count", 0)),
            memory_ids=[str(x) for x in d.get("memory_ids", [])],
            creation_timestamp=str(d.get("creation_timestamp", "")),
            last_updated=str(d.get("last_updated", "")),
            cluster_quality_score=float(d.get("cluster_quality_score", 0.0)),
        )


@dataclass
class IndexingStructures:
    semantic_clusters: Dict[str, SemanticCluster]
    temporal_index: Dict[str, dict]
    graph_connections: Dict[str, GraphNode]

    @staticmethod
    def from_dict(d: dict) -> "IndexingStructures":
        return IndexingStructures(
            semantic_clusters={k: SemanticCluster.from_dict(v) for k, v in d.get("semantic_clusters", {}).items()},
            temporal_index=d.get("temporal_index", {}),
            graph_connections={k: GraphNode.from_dict(v) for k, v in d.get("graph_connections", {}).items()},
        )


@dataclass
class LLMContextFormat:
    template: str
    max_memory_count: int
    context_window_size: int
    include_metadata: bool
    confidence_threshold: float

    @staticmethod
    def from_dict(d: dict) -> "LLMContextFormat":
        return LLMContextFormat(
            template=str(d.get("template", ">>> {memory.raw_text}")),
            max_memory_count=int(d.get("max_memory_count", 5)),
            context_window_size=int(d.get("context_window_size", 2048)),
            include_metadata=bool(d.get("include_metadata", True)),
            confidence_threshold=float(d.get("confidence_threshold", 0.7)),
        )


@dataclass
class PlannerInputFormat:
    schema_version: str
    required_fields: List[str]
    aggregation_method: str
    temporal_weighting: bool

    @staticmethod
    def from_dict(d: dict) -> "PlannerInputFormat":
        return PlannerInputFormat(
            schema_version=str(d.get("schema_version", "1.0")),
            required_fields=[str(x) for x in d.get("required_fields", [])],
            aggregation_method=str(d.get("aggregation_method", "recency_weighted")),
            temporal_weighting=bool(d.get("temporal_weighting", True)),
        )


@dataclass
class RLReplayFormat:
    state_representation: str
    reward_normalization: bool
    batch_size: int
    priority_sampling: bool

    @staticmethod
    def from_dict(d: dict) -> "RLReplayFormat":
        return RLReplayFormat(
            state_representation=str(d.get("state_representation", "hybrid")),
            reward_normalization=bool(d.get("reward_normalization", True)),
            batch_size=int(d.get("batch_size", 32)),
            priority_sampling=bool(d.get("priority_sampling", False)),
        )


@dataclass
class IntegrationSpecifications:
    llm_context_format: LLMContextFormat
    planner_input_format: PlannerInputFormat
    rl_replay_format: RLReplayFormat

    @staticmethod
    def from_dict(d: dict) -> "IntegrationSpecifications":
        return IntegrationSpecifications(
            llm_context_format=LLMContextFormat.from_dict(d.get("llm_context_format", {})),
            planner_input_format=PlannerInputFormat.from_dict(d.get("planner_input_format", {})),
            rl_replay_format=RLReplayFormat.from_dict(d.get("rl_replay_format", {})),
        )


@dataclass
class EpisodicMemorySystem:
    system_metadata: SystemMetadata
    memory_entries: Dict[str, MemoryEntry]
    indexing_structures: IndexingStructures
    integration_specifications: IntegrationSpecifications
    governance: Optional[Governance] = None

    @staticmethod
    def from_dict(d: dict) -> "EpisodicMemorySystem":
        obj = EpisodicMemorySystem(
            system_metadata=SystemMetadata.from_dict(d.get("system_metadata", {})),
            memory_entries={k: MemoryEntry.from_dict(v) for k, v in d.get("memory_entries", {}).items()},
            indexing_structures=IndexingStructures.from_dict(d.get("indexing_structures", {})),
            integration_specifications=IntegrationSpecifications.from_dict(d.get("integration_specifications", {})),
            governance=Governance.from_dict(d.get("governance", {})) if d.get("governance") else None,
        )
        return obj
