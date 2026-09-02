from arq import cron
from arq.connections import RedisSettings
from app.workers.functions import start_crawl_job
from app.settings.config import settings

class WorkerSettings:
    functions = [start_crawl_job]
    
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
    )
    
    max_jobs = 10
    job_timeout = 3600
    handle_signals = False