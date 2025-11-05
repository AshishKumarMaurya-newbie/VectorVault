"""
Monitoring and Observability Module
"""

from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
import logging
from typing import Callable
from datetime import datetime

# ============= Logging Configuration =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= Prometheus Metrics =============
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)
active_users = Gauge(
    'active_users_total',
    'Number of active users in the system'
)
knowledge_bases_total = Gauge(
    'knowledge_bases_total',
    'Total number of knowledge bases'
)
documents_processed_total = Counter(
    'documents_processed_total',
    'Total number of documents processed',
    ['status']  # success or failed
)
vector_search_duration_seconds = Histogram(
    'vector_search_duration_seconds',
    'Vector search operation duration in seconds'
)
embeddings_created_total = Counter(
    'embeddings_created_total',
    'Total number of embeddings created'
)
errors_total = Counter(
    'errors_total',
    'Total number of errors encountered',
    ['error_type']
)

# ============= Metrics Middleware =============
class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=status_code
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
                
                logger.info(
                    f"{method} {path} {status_code} {duration:.3f}s"
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# ============= Performance Tracking Decorators =============
def track_time(metric_name: str = None):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                name = metric_name or f"{func.__name__}_duration_seconds"
                logger.info(f"{name}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                errors_total.labels(error_type=type(e).__name__).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                name = metric_name or f"{func.__name__}_duration_seconds"
                logger.info(f"{name}: {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                errors_total.labels(error_type=type(e).__name__).inc()
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

def track_error(error_type: str = None):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_name = error_type or type(e).__name__
                errors_total.labels(error_type=error_name).inc()
                logger.error(f"{func.__name__} error: {error_name} - {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_name = error_type or type(e).__name__
                errors_total.labels(error_type=error_name).inc()
                logger.error(f"{func.__name__} error: {error_name} - {str(e)}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

# ============= Metrics Collector =============
class MetricsCollector:
    @staticmethod
    def track_document_processing(success: bool, duration: float):
        status = "success" if success else "failed"
        documents_processed_total.labels(status=status).inc()
        logger.info(
            f"Document processing {status} in {duration:.2f}s"
        )
    
    @staticmethod
    def track_vector_search(duration: float, results_count: int):
        vector_search_duration_seconds.observe(duration)
        logger.info(
            f"Vector search completed in {duration:.3f}s, "
            f"returned {results_count} results"
        )
    
    @staticmethod
    def track_embeddings_created(count: int):
        embeddings_created_total.inc(count)
        logger.info(f"Created {count} embeddings")
    
    @staticmethod
    def update_user_count(db):
        try:
            count = db.query(object).count() # Placeholder
            active_users.set(count)
        except Exception as e:
            logger.error(f"Failed to update user count: {e}")
    
    @staticmethod
    def update_kb_count(db):
        try:
            count = db.query(object).count() # Placeholder
            knowledge_bases_total.set(count)
        except Exception as e:
            logger.error(f"Failed to update KB count: {e}")

# ============= Structured Logging =============
class StructuredLogger:
    def __init__(self, component: str):
        self.component = component
        self.logger = logging.getLogger(component)
    
    def _log(self, level: str, message: str, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": self.component,
            "message": message,
            **kwargs
        }
        log_message = " | ".join(f"{k}={v}" for k, v in log_data.items())
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "error":
            self.logger.error(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "debug":
            self.logger.debug(log_message)
    
    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

# ============= Health Check System =============
class HealthCheck:
    def __init__(self, db, chroma_client):
        self.db = db
        self.chroma_client = chroma_client
    
    def check_database(self) -> dict:
        try:
            self.db.execute("SELECT 1")
            return {
                "status": "healthy",
                "message": "Database connection OK"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }
    
    def check_chromadb(self) -> dict:
        try:
            self.chroma_client.heartbeat() # This requires a real client
            return {
                "status": "healthy",
                "message": "ChromaDB connection OK"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"ChromaDB error: {str(e)}"
            }
    
    def check_disk_space(self) -> dict:
        import shutil
        try:
            usage = shutil.disk_usage("/")
            percent_used = (usage.used / usage.total) * 100
            
            if percent_used > 90:
                status = "unhealthy"
            elif percent_used > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "message": f"Disk space: {percent_used:.1f}% used",
                "percent_used": round(percent_used, 1)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"Could not check disk space: {str(e)}"
            }
    
    def check_memory(self) -> dict:
        try:
            import psutil
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            if percent_used > 90:
                status = "unhealthy"
            elif percent_used > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "message": f"Memory: {percent_used:.1f}% used",
                "percent_used": round(percent_used, 1)
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not installed, cannot check memory"
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"Could not check memory: {str(e)}"
            }
    
    def get_health_status(self) -> dict:
        checks = {
            "database": self.check_database(),
            "chromadb": self.check_chromadb(),
            "disk": self.check_disk_space(),
            "memory": self.check_memory()
        }
        
        statuses = [check["status"] for check in checks.values()]
        
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        elif "unknown" in statuses:
            overall_status = "partial"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }

# ============= Module Info =============
__version__ = "1.0.0"
__all__ = [
    'MetricsMiddleware',
    'MetricsCollector',
    'StructuredLogger',
    'HealthCheck',
    'track_time',
    'track_error'
]