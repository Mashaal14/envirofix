"""
RAG Scheduler - Runs your existing scraper on startup and every 6 hours
"""

import threading
import time
import logging
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, '/app')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGScheduler:
    def __init__(self, interval_hours=6):
        self.interval_seconds = interval_hours * 3600
        self.running = False
        self.thread = None
        self.last_scrape_result = None
        
    def run_scrape(self):
        """Run your existing scraper"""
        logger.info(f"📡 Running scheduled RAG scrape at {datetime.now()}")
        
        try:
            # Import your existing scraper function
            from ai.scraper import run_full_scrape
            
            # Run the scrape
            run_full_scrape()
            
            # Read the results
            metadata_file = "/app/ai/envirofix_knowledge/last_scrape.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    chunks = metadata.get("chunks", 0)
            else:
                chunks = 0
            
            self.last_scrape_result = {
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "chunks_indexed": chunks
            }
            logger.info(f"✅ Scrape complete - {chunks} chunks indexed")
            return self.last_scrape_result
            
        except Exception as e:
            logger.error(f"❌ Scrape failed: {e}")
            self.last_scrape_result = {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            return self.last_scrape_result
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        
        # Run initial scrape on startup
        logger.info("🚀 Running initial RAG scrape on startup...")
        self.run_scrape()
        
        # Start background thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"✅ RAG scheduler started (interval: {self.interval_seconds // 3600} hours)")
    
    def _run_loop(self):
        """Background loop"""
        while self.running:
            time.sleep(self.interval_seconds)
            if self.running:
                self.run_scrape()
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("RAG scheduler stopped")
    
    def get_status(self):
        """Get current scheduler status"""
        # Get ChromaDB status
        chroma_status = {"indexed_chunks": 0, "last_scrape": "Never"}
        
        try:
            import chromadb
            chroma_client = chromadb.PersistentClient(path="/app/ai/envirofix_knowledge")
            try:
                collection = chroma_client.get_collection("kali_docs")
                chroma_status["indexed_chunks"] = collection.count()
            except:
                chroma_status["indexed_chunks"] = 0
                
            # Check for metadata file
            metadata_file = "/app/ai/envirofix_knowledge/last_scrape.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    chroma_status["last_scrape"] = metadata.get("timestamp", "Unknown")
                    chroma_status["chunks_in_last_scrape"] = metadata.get("chunks", 0)
        except Exception as e:
            chroma_status["error"] = str(e)
        
        return {
            "scheduler_running": self.running,
            "interval_hours": self.interval_seconds // 3600,
            "last_scrape_attempt": self.last_scrape_result.get("timestamp") if self.last_scrape_result else None,
            "last_scrape_success": self.last_scrape_result.get("success") if self.last_scrape_result else False,
            "last_scrape_chunks": self.last_scrape_result.get("chunks_indexed") if self.last_scrape_result else 0,
            "chromadb": chroma_status
        }

# Global scheduler instance
_scheduler = None

def start_rag_scheduler(interval_hours=6):
    """Start the global RAG scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = RAGScheduler(interval_hours)
        _scheduler.start()
    return _scheduler

def get_rag_scheduler():
    """Get the global RAG scheduler"""
    return _scheduler

def get_rag_status():
    """Get RAG status (for API endpoint)"""
    if _scheduler:
        return _scheduler.get_status()
    else:
        # Return basic status from ChromaDB
        try:
            import chromadb
            import os
            import json
            chroma_client = chromadb.PersistentClient(path="/app/ai/envirofix_knowledge")
            collection = chroma_client.get_collection("kali_docs")
            count = collection.count()
            
            metadata_file = "/app/ai/envirofix_knowledge/last_scrape.json"
            last_scrape = "Never"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    last_scrape = metadata.get("timestamp", "Unknown")
            
            return {
                "scheduler_running": False,
                "chromadb": {
                    "indexed_chunks": count,
                    "last_scrape": last_scrape
                }
            }
        except:
            return {"scheduler_running": False, "error": "Unable to read ChromaDB"}
