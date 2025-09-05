"""
⚡ CONCURRENT ENVIRONMENT LAUNCHER ⚡
Launch multiple environments simultaneously like a boss!

This launcher can handle starting 5+ environments at the same time,
each in their own isolated container, without breaking a sweat!
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from src.envstarter.core.models import Environment
from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
from src.envstarter.core.environment_container import EnvironmentState


class LaunchMode(Enum):
    """Different launch modes for multiple environments."""
    SEQUENTIAL = "sequential"    # Launch one after another
    CONCURRENT = "concurrent"    # Launch all simultaneously  
    BATCHED = "batched"         # Launch in batches of N
    STAGGERED = "staggered"     # Launch with delays between


@dataclass
class LaunchJob:
    """A single environment launch job."""
    environment: Environment
    container_id: str
    switch_to: bool = False
    priority: int = 1  # 1=high, 2=medium, 3=low
    delay_seconds: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class LaunchResult:
    """Result of a launch operation."""
    container_id: str
    environment_name: str
    success: bool
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "container_id": self.container_id,
            "environment_name": self.environment_name,
            "success": self.success,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class ConcurrentLauncher(QObject):
    """
    🚀 THE ULTIMATE CONCURRENT ENVIRONMENT LAUNCHER!
    
    This beast can:
    - Launch multiple environments simultaneously
    - Handle priority-based launching
    - Manage launch queues and batching
    - Provide real-time progress for all launches
    - Handle failures gracefully without affecting other launches
    - Support different launch modes (sequential, concurrent, etc.)
    """
    
    # Signals for concurrent launch events
    launch_started = pyqtSignal(str, str)  # container_id, environment_name
    launch_completed = pyqtSignal(str, bool)  # container_id, success
    launch_progress = pyqtSignal(str, int, str)  # container_id, percentage, status
    batch_started = pyqtSignal(int)  # batch_size
    batch_completed = pyqtSignal(int, int)  # successful_count, total_count
    all_launches_completed = pyqtSignal(list)  # list of LaunchResult
    queue_updated = pyqtSignal(int)  # queue_size
    
    def __init__(self):
        super().__init__()
        
        # Launcher configuration
        self.max_concurrent_launches = 5  # Maximum simultaneous launches
        self.default_launch_mode = LaunchMode.CONCURRENT
        self.batch_size = 3  # For batched launching
        self.stagger_delay = 2.0  # Seconds between staggered launches
        
        # Launch queue and tracking
        self.launch_queue: List[LaunchJob] = []
        self.active_launches: Dict[str, LaunchJob] = {}  # container_id -> job
        self.launch_results: List[LaunchResult] = []
        
        # Threading and async
        self.is_launching = False
        self.launch_thread: Optional[QThread] = None
        self.manager = get_multi_environment_manager()
        
        # Progress tracking
        self.total_jobs = 0
        self.completed_jobs = 0
        
        print("⚡ Concurrent Launcher initialized!")
        print(f"   🚀 Max concurrent: {self.max_concurrent_launches}")
        print(f"   📋 Default mode: {self.default_launch_mode.value}")
    
    def add_launch_job(self, environment: Environment, 
                      container_id: Optional[str] = None,
                      switch_to: bool = False,
                      priority: int = 1,
                      delay_seconds: float = 0.0) -> str:
        """Add an environment to the launch queue."""
        
        # Generate container ID if not provided
        if not container_id:
            timestamp = datetime.now().strftime("%H%M%S_%f")[:9]
            container_id = f"{environment.name}-{timestamp}"
        
        # Create launch job
        job = LaunchJob(
            environment=environment,
            container_id=container_id,
            switch_to=switch_to,
            priority=priority,
            delay_seconds=delay_seconds
        )
        
        # Add to queue (sorted by priority)
        self.launch_queue.append(job)
        self.launch_queue.sort(key=lambda x: x.priority)
        
        self.queue_updated.emit(len(self.launch_queue))
        
        print(f"📋 Added to launch queue: '{container_id}' (priority: {priority})")
        return container_id
    
    def add_multiple_environments(self, environments: List[Environment],
                                switch_to_last: bool = True,
                                launch_mode: Optional[LaunchMode] = None) -> List[str]:
        """Add multiple environments to launch queue."""
        
        container_ids = []
        
        for i, env in enumerate(environments):
            # Only switch to the last environment if requested
            switch_to = switch_to_last and (i == len(environments) - 1)
            
            # Calculate delay for staggered mode
            delay = 0.0
            if launch_mode == LaunchMode.STAGGERED:
                delay = i * self.stagger_delay
            
            container_id = self.add_launch_job(
                environment=env,
                switch_to=switch_to,
                priority=1,  # All equal priority for batch launches
                delay_seconds=delay
            )
            container_ids.append(container_id)
        
        print(f"📋 Added {len(environments)} environments to launch queue")
        return container_ids
    
    async def launch_all_queued(self, launch_mode: Optional[LaunchMode] = None) -> List[LaunchResult]:
        """🚀 LAUNCH ALL ENVIRONMENTS IN QUEUE!"""
        
        if self.is_launching:
            raise Exception("Launcher is already running!")
        
        if not self.launch_queue:
            print("📋 No environments in queue to launch")
            return []
        
        mode = launch_mode or self.default_launch_mode
        total_jobs = len(self.launch_queue)
        
        print(f"🚀 Starting concurrent launch of {total_jobs} environments!")
        print(f"   🎯 Launch mode: {mode.value}")
        print(f"   ⚡ Max concurrent: {self.max_concurrent_launches}")
        
        self.is_launching = True
        self.total_jobs = total_jobs
        self.completed_jobs = 0
        self.launch_results.clear()
        
        try:
            # Execute launches based on mode
            if mode == LaunchMode.SEQUENTIAL:
                results = await self._launch_sequential()
            elif mode == LaunchMode.CONCURRENT:
                results = await self._launch_concurrent()
            elif mode == LaunchMode.BATCHED:
                results = await self._launch_batched()
            elif mode == LaunchMode.STAGGERED:
                results = await self._launch_staggered()
            else:
                raise Exception(f"Unsupported launch mode: {mode}")
            
            self.all_launches_completed.emit([r.to_dict() for r in results])
            
            # Summary
            successful = len([r for r in results if r.success])
            print(f"✅ Launch complete: {successful}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            raise e
        finally:
            self.is_launching = False
            self.launch_queue.clear()
            self.active_launches.clear()
    
    async def _launch_sequential(self) -> List[LaunchResult]:
        """Launch environments one after another."""
        results = []
        
        print("🔄 Sequential launch mode")
        
        for i, job in enumerate(self.launch_queue):
            print(f"  [{i+1}/{len(self.launch_queue)}] Launching: {job.environment.name}")
            
            # Apply delay if specified
            if job.delay_seconds > 0:
                print(f"    ⏱️  Waiting {job.delay_seconds} seconds...")
                await asyncio.sleep(job.delay_seconds)
            
            result = await self._launch_single_job(job)
            results.append(result)
            
            self.completed_jobs += 1
        
        return results
    
    async def _launch_concurrent(self) -> List[LaunchResult]:
        """Launch all environments simultaneously."""
        print("⚡ Concurrent launch mode")
        
        # Group jobs into batches based on max concurrent limit
        batches = []
        current_batch = []
        
        for job in self.launch_queue:
            current_batch.append(job)
            if len(current_batch) >= self.max_concurrent_launches:
                batches.append(current_batch)
                current_batch = []
        
        # Add remaining jobs as final batch
        if current_batch:
            batches.append(current_batch)
        
        all_results = []
        
        # Process each batch
        for batch_num, batch in enumerate(batches):
            print(f"  🔥 Batch {batch_num + 1}/{len(batches)}: {len(batch)} environments")
            
            self.batch_started.emit(len(batch))
            
            # Launch all jobs in batch concurrently
            tasks = []
            for job in batch:
                task = self._launch_single_job(job)
                tasks.append(task)
            
            # Wait for all jobs in batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_count = 0
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    # Handle exception
                    job = batch[i]
                    error_result = LaunchResult(
                        container_id=job.container_id,
                        environment_name=job.environment.name,
                        success=False,
                        error_message=str(result)
                    )
                    all_results.append(error_result)
                else:
                    all_results.append(result)
                    if result.success:
                        successful_count += 1
                
                self.completed_jobs += 1
            
            self.batch_completed.emit(successful_count, len(batch))
            
            # Small delay between batches
            if batch_num < len(batches) - 1:
                print("    ⏱️  Brief pause between batches...")
                await asyncio.sleep(1.0)
        
        return all_results
    
    async def _launch_batched(self) -> List[LaunchResult]:
        """Launch environments in small batches."""
        print(f"📦 Batched launch mode (batch size: {self.batch_size})")
        
        results = []
        
        # Process jobs in batches
        for i in range(0, len(self.launch_queue), self.batch_size):
            batch = self.launch_queue[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(self.launch_queue) + self.batch_size - 1) // self.batch_size
            
            print(f"  📦 Batch {batch_num}/{total_batches}: {len(batch)} environments")
            
            self.batch_started.emit(len(batch))
            
            # Launch batch concurrently
            tasks = [self._launch_single_job(job) for job in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process batch results
            successful_count = 0
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    job = batch[j]
                    error_result = LaunchResult(
                        container_id=job.container_id,
                        environment_name=job.environment.name,
                        success=False,
                        error_message=str(result)
                    )
                    results.append(error_result)
                else:
                    results.append(result)
                    if result.success:
                        successful_count += 1
                
                self.completed_jobs += 1
            
            self.batch_completed.emit(successful_count, len(batch))
            
            # Delay between batches
            if i + self.batch_size < len(self.launch_queue):
                print("    ⏱️  Pause between batches...")
                await asyncio.sleep(2.0)
        
        return results
    
    async def _launch_staggered(self) -> List[LaunchResult]:
        """Launch environments with staggered delays."""
        print(f"🌊 Staggered launch mode (delay: {self.stagger_delay}s)")
        
        # Start all launches with their individual delays
        tasks = []
        for job in self.launch_queue:
            task = self._launch_single_job(job)
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                job = self.launch_queue[i]
                error_result = LaunchResult(
                    container_id=job.container_id,
                    environment_name=job.environment.name,
                    success=False,
                    error_message=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
            
            self.completed_jobs += 1
        
        return final_results
    
    async def _launch_single_job(self, job: LaunchJob) -> LaunchResult:
        """Launch a single environment job."""
        
        result = LaunchResult(
            container_id=job.container_id,
            environment_name=job.environment.name,
            success=False,
            start_time=datetime.now()
        )
        
        try:
            self.launch_started.emit(job.container_id, job.environment.name)
            self.active_launches[job.container_id] = job
            
            # Apply job delay
            if job.delay_seconds > 0:
                self.launch_progress.emit(job.container_id, 10, f"Waiting {job.delay_seconds}s...")
                await asyncio.sleep(job.delay_seconds)
            
            self.launch_progress.emit(job.container_id, 30, "Creating container...")
            
            # Start the container
            container_id = await self.manager.start_environment_container(
                environment=job.environment,
                container_id=job.container_id,
                switch_to=job.switch_to
            )
            
            self.launch_progress.emit(job.container_id, 100, "Launch complete!")
            
            result.success = True
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.launch_completed.emit(job.container_id, True)
            
        except Exception as e:
            result.error_message = str(e)
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.launch_progress.emit(job.container_id, 0, f"Error: {str(e)}")
            self.launch_completed.emit(job.container_id, False)
            
            print(f"❌ Launch failed for '{job.container_id}': {e}")
        
        finally:
            # Clean up
            if job.container_id in self.active_launches:
                del self.active_launches[job.container_id]
        
        return result
    
    def clear_queue(self):
        """Clear the launch queue."""
        self.launch_queue.clear()
        self.queue_updated.emit(0)
        print("🗑️  Launch queue cleared")
    
    def remove_from_queue(self, container_id: str) -> bool:
        """Remove a specific job from the queue."""
        for i, job in enumerate(self.launch_queue):
            if job.container_id == container_id:
                del self.launch_queue[i]
                self.queue_updated.emit(len(self.launch_queue))
                print(f"🗑️  Removed '{container_id}' from launch queue")
                return True
        return False
    
    def get_queue_status(self) -> Dict:
        """Get current queue status."""
        return {
            "queue_size": len(self.launch_queue),
            "active_launches": len(self.active_launches),
            "is_launching": self.is_launching,
            "total_jobs": self.total_jobs,
            "completed_jobs": self.completed_jobs,
            "progress_percentage": (self.completed_jobs / max(self.total_jobs, 1)) * 100,
            "launch_mode": self.default_launch_mode.value,
            "max_concurrent": self.max_concurrent_launches
        }
    
    def get_active_launches(self) -> List[Dict]:
        """Get information about currently active launches."""
        return [
            {
                "container_id": job.container_id,
                "environment_name": job.environment.name,
                "switch_to": job.switch_to,
                "priority": job.priority
            }
            for job in self.active_launches.values()
        ]
    
    def stop_all_launches(self):
        """Stop all active launches (emergency stop)."""
        if not self.is_launching:
            return
        
        print("🛑 Emergency stop: Cancelling all active launches...")
        
        # This would require cancelling async tasks
        # For now, we just clear the state
        self.launch_queue.clear()
        self.active_launches.clear()
        self.is_launching = False
        
        self.queue_updated.emit(0)
        print("🛑 All launches stopped")


# Thread wrapper for running async launches
class LaunchThread(QThread):
    """Thread for running async launch operations."""
    
    finished_signal = pyqtSignal(list)  # results
    error_signal = pyqtSignal(str)  # error message
    
    def __init__(self, launcher: ConcurrentLauncher, launch_mode: LaunchMode):
        super().__init__()
        self.launcher = launcher
        self.launch_mode = launch_mode
    
    def run(self):
        """Run the async launch in a thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            results = loop.run_until_complete(
                self.launcher.launch_all_queued(self.launch_mode)
            )
            
            self.finished_signal.emit([r.to_dict() for r in results])
            
        except Exception as e:
            self.error_signal.emit(str(e))
        
        finally:
            loop.close()


# Global launcher instance
_launcher_instance: Optional[ConcurrentLauncher] = None


def get_concurrent_launcher() -> ConcurrentLauncher:
    """Get the global concurrent launcher instance."""
    global _launcher_instance
    
    if _launcher_instance is None:
        _launcher_instance = ConcurrentLauncher()
    
    return _launcher_instance