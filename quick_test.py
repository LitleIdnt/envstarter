#!/usr/bin/env python3
"""
Quick test to verify basic functionality works
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.envstarter.core.models import Environment, Application
from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer

async def quick_test():
    print("🧪 QUICK FUNCTIONALITY TEST")
    print("=" * 40)
    
    # Create simple environment
    test_env = Environment(
        name="QUICK_TEST",
        description="Quick functionality test",
        applications=[
            Application(
                name="Calculator",
                path="calc.exe"
            )
        ]
    )
    
    print(f"✅ Created environment: {test_env.name}")
    
    # Create container
    container = SimpleEnvironmentContainer(test_env, "quick_test_container")
    print(f"✅ Created container: {container.container_id}")
    
    try:
        # Start container
        print("🚀 Starting container...")
        success = await container.start_container()
        
        if success:
            print("✅ Container started successfully!")
            print(f"   Tracked processes: {len(container.tracked_processes)}")
            
            # Check title injector
            if hasattr(container, 'title_injector'):
                stats = container.title_injector.get_injection_stats()
                print(f"   Title injector: {stats['environment_name']}")
                print(f"   Monitoring: {stats['monitoring_active']}")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Stop container
            print("🛑 Stopping container...")
            await container.stop_container()
            print("✅ Container stopped successfully!")
            
            return True
            
        else:
            print("❌ Container failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    if result:
        print("\n🎉 BASIC FUNCTIONALITY WORKS!")
    else:
        print("\n💥 STILL HAS ISSUES!")