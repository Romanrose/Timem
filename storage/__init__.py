"""
TiMem Storage Module
Provides vector storage, graph storage, SQL storage, and cache management functionality, as well as unified storage adapter interfaces
"""

# Unified storage interface
from .storage_adapter import StorageAdapter

# Storage adapter implementations
from .sql_adapter import SQLAdapter
from .postgres_adapter import PostgreSQLAdapter, get_postgres_adapter
from .vector_adapter import VectorAdapter, get_vector_adapter
try:
    from .cache_adapter import CacheAdapter, get_cache_adapter
    from .cache_manager import CacheManager, get_cache_manager
except ModuleNotFoundError as exc:
    if exc.name != "redis":
        raise
    _cache_import_error = exc
    CacheAdapter = None
    CacheManager = None

    def get_cache_adapter(*args, **kwargs):
        raise ModuleNotFoundError("redis is required to use CacheAdapter") from _cache_import_error

    def get_cache_manager(*args, **kwargs):
        raise ModuleNotFoundError("redis is required to use CacheManager") from _cache_import_error
try:
    from .graph_adapter import GraphAdapter, get_graph_adapter
    from .graph_store import GraphStore, GraphNode, GraphRelationship, GraphPath, GraphQueryResult, get_graph_store
except ModuleNotFoundError as exc:
    if exc.name != "neo4j":
        raise
    _graph_import_error = exc
    GraphAdapter = None
    GraphStore = None
    GraphNode = None
    GraphRelationship = None
    GraphPath = None
    GraphQueryResult = None

    def get_graph_adapter(*args, **kwargs):
        raise ModuleNotFoundError("neo4j is required to use GraphAdapter") from _graph_import_error

    def get_graph_store(*args, **kwargs):
        raise ModuleNotFoundError("neo4j is required to use GraphStore") from _graph_import_error

# Storage manager
from .memory_storage_manager import MemoryStorageManager, get_memory_storage_manager, get_memory_storage_manager_async

# Low-level storage implementations
from .vector_store import VectorStore, VectorPoint, VectorSearchResult, get_vector_store
from .sql_store import SQLStore, get_sql_store
from .postgres_store import PostgreSQLStore, get_postgres_store

# Backward compatibility support
from .database import Database, get_database, init_database, close_database, get_mysql_session, get_neo4j_session, get_qdrant_client, get_redis_client

__all__ = [
    # Unified storage interface
    'StorageAdapter',
    
    # Storage adapters
    'SQLAdapter',
    'PostgreSQLAdapter',
    'VectorAdapter',
    'GraphAdapter',
    'CacheAdapter',
    'get_sql_adapter',
    'get_postgres_adapter',
    'get_vector_adapter',
    'get_graph_adapter',
    'get_cache_adapter',
    
    # Storage manager
    'MemoryStorageManager',
    'get_memory_storage_manager',
    'get_memory_storage_manager_async',
    
    # Vector storage
    'VectorStore',
    'VectorPoint', 
    'VectorSearchResult',
    'get_vector_store',
    
    # Graph storage
    'GraphStore',
    'GraphNode',
    'GraphRelationship', 
    'GraphPath',
    'GraphQueryResult',
    'get_graph_store',
    
    # SQL storage
    'SQLStore',
    'get_sql_store',
    
    # PostgreSQL storage
    'PostgreSQLStore',
    'get_postgres_store',
    
    # Cache
    'CacheManager',
    'get_cache_manager',
    
    # Backward compatibility support
    'Database',
    'get_database',
    'init_database',
    'close_database',
    'get_mysql_session',
    'get_neo4j_session',
    'get_qdrant_client',
    'get_redis_client'
]
