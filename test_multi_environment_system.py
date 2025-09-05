#!/usr/bin/env python3
"""
🧪 MULTI-ENVIRONMENT SYSTEM TEST SCRIPT 🧪
Test the revolutionary multi-environment container system!

This script demonstrates and tests:
- Multiple environments running simultaneously
- Container isolation and switching
- Resource monitoring
- Concurrent launching
- VM-like management
"""

import sys
import os
import time
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.envstarter.core.models import Environment, Application, Website
from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
from src.envstarter.core.concurrent_launcher import get_concurrent_launcher, LaunchMode
from src.envstarter.core.simple_environment_container import EnvironmentState


def create_test_environments():
    """Create test environments for demonstrating the system."""
    print("🧪 Creating test environments...")
    
    environments = []
    
    # Test Environment 1: Development Setup
    dev_env = Environment(
        name="Test-Development", 
        description="Development environment with code editors and browsers",
        applications=[
            Application(name="Notepad", path="notepad.exe", arguments=""),
            Application(name="Calculator", path="calc.exe", arguments=""),
        ],
        websites=[
            Website(name="GitHub", url="https://github.com"),
            Website(name="Stack Overflow", url="https://stackoverflow.com"),
            Website(name="Google", url="https://google.com"),
        ],
        startup_delay=2,
        use_virtual_desktop=True,
        auto_switch_desktop=True
    )
    environments.append(dev_env)
    
    # Test Environment 2: Productivity Suite
    productivity_env = Environment(
        name="Test-Productivity",
        description="Productivity tools and communication apps",
        applications=[
            Application(name="Notepad", path="notepad.exe", arguments=""),
            Application(name="Paint", path="mspaint.exe", arguments=""),
        ],
        websites=[
            Website(name="Gmail", url="https://mail.google.com"),
            Website(name="Calendar", url="https://calendar.google.com"),
        ],
        startup_delay=1,
        use_virtual_desktop=True,
        auto_switch_desktop=False
    )
    environments.append(productivity_env)
    
    # Test Environment 3: Research & Documentation
    research_env = Environment(
        name="Test-Research",
        description="Research tools and documentation sites",
        applications=[
            Application(name="Notepad", path="notepad.exe", arguments=""),
        ],
        websites=[
            Website(name="Wikipedia", url="https://wikipedia.org"),
            Website(name="Google Scholar", url="https://scholar.google.com"),
            Website(name="Mozilla MDN", url="https://developer.mozilla.org"),
        ],
        startup_delay=0,
        use_virtual_desktop=True,
        auto_switch_desktop=False
    )
    environments.append(research_env)
    
    # Test Environment 4: Multimedia
    multimedia_env = Environment(
        name="Test-Multimedia",
        description="Multimedia and entertainment applications",
        applications=[
            Application(name="Paint", path="mspaint.exe", arguments=""),
            Application(name="Calculator", path="calc.exe", arguments=""),
        ],
        websites=[
            Website(name="YouTube", url="https://youtube.com"),
            Website(name="Spotify Web", url="https://open.spotify.com"),
        ],
        startup_delay=1,
        use_virtual_desktop=True,
        auto_switch_desktop=False
    )
    environments.append(multimedia_env)
    
    # Test Environment 5: Testing & QA
    testing_env = Environment(
        name="Test-QA",
        description="Testing and quality assurance tools", 
        applications=[
            Application(name="Calculator", path="calc.exe", arguments=""),
        ],
        websites=[
            Website(name="Test Site 1", url="https://httpbin.org"),
            Website(name="Test Site 2", url="https://jsonplaceholder.typicode.com"),
        ],
        startup_delay=0,
        use_virtual_desktop=True,
        auto_switch_desktop=False
    )
    environments.append(testing_env)
    
    print(f"✅ Created {len(environments)} test environments")
    return environments


async def test_single_environment_launch():
    """Test launching a single environment."""
    print("\n" + "="*60)
    print("🧪 TEST 1: Single Environment Launch")
    print("="*60)
    
    manager = get_multi_environment_manager()
    
    # Create test environment
    test_env = Environment(
        name="Single-Test-Env",
        description="Single environment test",
        applications=[
            Application(name="Notepad", path="notepad.exe", arguments=""),
            Application(name="Calculator", path="calc.exe", arguments=""),
        ],
        websites=[
            Website(name="Google", url="https://google.com"),
        ],
        use_virtual_desktop=True,
        auto_switch_desktop=True
    )
    
    print(f"🚀 Launching environment: {test_env.name}")
    
    try:
        container_id = await manager.start_environment_container(
            environment=test_env,
            switch_to=True
        )
        
        print(f"✅ Environment launched successfully!")
        print(f"   📦 Container ID: {container_id}")
        
        # Wait and monitor
        print("⏱️  Monitoring for 10 seconds...")
        for i in range(10):
            await asyncio.sleep(1)
            
            containers = manager.get_all_containers()
            if container_id in containers:
                info = containers[container_id]
                stats = info.get("stats", {})
                print(f"   📊 [{i+1}/10] State: {info['state']}, "
                      f"Processes: {stats.get('total_processes', 0)}, "
                      f"Memory: {stats.get('total_memory_mb', 0):.1f}MB")
        
        # Stop the environment
        print("🛑 Stopping environment...")
        success = await manager.stop_environment_container(container_id)
        
        if success:
            print("✅ Environment stopped successfully")
        else:
            print("❌ Failed to stop environment")
        
        return True
        
    except Exception as e:
        print(f"❌ Single environment test failed: {e}")
        return False


async def test_multiple_environments_concurrent():
    """Test launching multiple environments concurrently."""
    print("\n" + "="*60)
    print("🧪 TEST 2: Multiple Environments Concurrent Launch")
    print("="*60)
    
    manager = get_multi_environment_manager()
    launcher = get_concurrent_launcher()
    
    # Create test environments
    test_environments = create_test_environments()
    
    print(f"🚀 Adding {len(test_environments)} environments to launch queue")
    
    # Add environments to launcher
    container_ids = launcher.add_multiple_environments(
        test_environments,
        switch_to_last=True,
        launch_mode=LaunchMode.CONCURRENT
    )
    
    print(f"📋 Environments queued: {container_ids}")
    
    try:
        print("⚡ Starting concurrent launch...")
        results = await launcher.launch_all_queued(LaunchMode.CONCURRENT)
        
        successful = len([r for r in results if r.success])
        print(f"✅ Concurrent launch completed: {successful}/{len(results)} successful")
        
        # Monitor all containers
        print("\n📊 Monitoring all containers for 15 seconds...")
        for i in range(15):
            await asyncio.sleep(1)
            
            containers = manager.get_all_containers()
            running_containers = [c for c in containers.values() if c["state"] == "running"]
            
            total_processes = sum(c.get("stats", {}).get("total_processes", 0) for c in running_containers)
            total_memory = sum(c.get("stats", {}).get("total_memory_mb", 0) for c in running_containers)
            
            print(f"   📊 [{i+1}/15] Running: {len(running_containers)} containers, "
                  f"Total Processes: {total_processes}, Total Memory: {total_memory:.1f}MB")
        
        # Test container switching
        print("\n🔄 Testing container switching...")
        running_container_ids = [cid for cid, info in containers.items() if info["state"] == "running"]
        
        for i, container_id in enumerate(running_container_ids[:3]):  # Test first 3
            print(f"   🔄 [{i+1}] Switching to container: {container_id}")
            success = await manager.switch_to_container(container_id)
            if success:
                print(f"      ✅ Switched successfully")
                await asyncio.sleep(2)  # Wait to see the switch
            else:
                print(f"      ❌ Switch failed")
        
        # Stop all containers
        print("\n🛑 Stopping all containers...")
        stopped_count = await manager.stop_all_containers()
        
        print(f"✅ Stopped {stopped_count} containers")
        return True
        
    except Exception as e:
        print(f"❌ Multiple environments test failed: {e}")
        return False


async def test_sequential_launch():
    """Test sequential environment launching."""
    print("\n" + "="*60) 
    print("🧪 TEST 3: Sequential Environment Launch")
    print("="*60)
    
    launcher = get_concurrent_launcher()
    
    # Create smaller test environments for sequential testing
    environments = create_test_environments()[:3]  # Just first 3
    
    print(f"🚀 Adding {len(environments)} environments for sequential launch")
    
    # Add to queue
    container_ids = launcher.add_multiple_environments(
        environments,
        switch_to_last=True,
        launch_mode=LaunchMode.SEQUENTIAL
    )
    
    try:
        print("🔄 Starting sequential launch...")
        results = await launcher.launch_all_queued(LaunchMode.SEQUENTIAL)
        
        successful = len([r for r in results if r.success])
        print(f"✅ Sequential launch completed: {successful}/{len(results)} successful")
        
        # Brief monitoring
        print("\n📊 Brief monitoring...")
        await asyncio.sleep(5)
        
        manager = get_multi_environment_manager()
        containers = manager.get_all_containers()
        print(f"   📦 Final containers: {len(containers)}")
        
        # Stop all
        stopped_count = await manager.stop_all_containers()
        print(f"🛑 Stopped {stopped_count} containers")
        
        return True
        
    except Exception as e:
        print(f"❌ Sequential launch test failed: {e}")
        return False


async def test_container_pause_resume():
    """Test container pause and resume functionality."""
    print("\n" + "="*60)
    print("🧪 TEST 4: Container Pause/Resume")
    print("="*60)
    
    manager = get_multi_environment_manager()
    
    # Create simple test environment
    test_env = Environment(
        name="Pause-Resume-Test",
        description="Test environment for pause/resume",
        applications=[
            Application(name="Notepad", path="notepad.exe", arguments=""),
            Application(name="Calculator", path="calc.exe", arguments=""),
        ],
        use_virtual_desktop=True
    )
    
    try:
        print("🚀 Launching test environment...")
        container_id = await manager.start_environment_container(test_env)
        
        print("⏱️  Waiting for environment to fully start...")
        await asyncio.sleep(5)
        
        print("⏸️  Pausing container...")
        success = await manager.pause_container(container_id)
        if success:
            print("   ✅ Container paused")
        else:
            print("   ❌ Failed to pause container")
            return False
        
        print("⏱️  Waiting while paused...")
        await asyncio.sleep(3)
        
        print("▶️  Resuming container...")
        success = await manager.resume_container(container_id)
        if success:
            print("   ✅ Container resumed")
        else:
            print("   ❌ Failed to resume container")
            return False
        
        print("⏱️  Monitoring resumed container...")
        await asyncio.sleep(3)
        
        print("🛑 Stopping test container...")
        await manager.stop_environment_container(container_id)
        
        print("✅ Pause/Resume test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Pause/Resume test failed: {e}")
        return False


async def test_system_resources_monitoring():
    """Test system resources monitoring."""
    print("\n" + "="*60)
    print("🧪 TEST 5: System Resources Monitoring")
    print("="*60)
    
    manager = get_multi_environment_manager()
    
    print("📊 Testing resource monitoring with multiple containers...")
    
    # Launch a few environments
    environments = create_test_environments()[:3]
    
    container_ids = []
    for env in environments:
        try:
            print(f"🚀 Launching {env.name}...")
            container_id = await manager.start_environment_container(env, switch_to=False)
            container_ids.append(container_id)
            await asyncio.sleep(2)  # Stagger launches
        except Exception as e:
            print(f"⚠️  Failed to launch {env.name}: {e}")
    
    if not container_ids:
        print("❌ No containers launched for monitoring test")
        return False
    
    print(f"\n📊 Monitoring {len(container_ids)} containers for 20 seconds...")
    
    for i in range(20):
        await asyncio.sleep(1)
        
        # Get system status
        system_status = manager.get_system_status()
        resources = system_status.get("system_resources", {})
        
        print(f"   📈 [{i+1}/20] "
              f"Containers: {resources.get('running_containers', 0)}, "
              f"Processes: {resources.get('total_processes', 0)}, "
              f"Memory: {resources.get('total_memory_mb', 0):.1f}MB, "
              f"CPU: {resources.get('total_cpu_percent', 0):.1f}%, "
              f"Desktops: {len(resources.get('active_desktops', []))}")
    
    # Stop all containers
    print("\n🛑 Cleaning up test containers...")
    stopped_count = await manager.stop_all_containers()
    
    print(f"✅ Resource monitoring test completed - stopped {stopped_count} containers")
    return True


async def run_all_tests():
    """Run all multi-environment system tests.""" 
    print("🎮 MULTI-ENVIRONMENT SYSTEM TEST SUITE")
    print("="*80)
    print()
    print("This test suite will demonstrate:")
    print("  🧪 Single environment launching")
    print("  ⚡ Multiple concurrent environment launching")
    print("  🔄 Sequential environment launching")
    print("  ⏸️  Container pause/resume functionality")
    print("  📊 System resources monitoring")
    print()
    
    # Check requirements
    if os.name != 'nt':
        print("⚠️  Warning: Tests designed for Windows")
        print("   Some features may not work properly on other platforms")
        print()
    
    try:
        # Verify imports work
        from src.envstarter.core.multi_environment_manager import get_multi_environment_manager
        print("✅ Multi-environment system imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🚀 Starting test suite...")
    
    tests = [
        ("Single Environment Launch", test_single_environment_launch),
        ("Multiple Concurrent Launch", test_multiple_environments_concurrent),
        ("Sequential Launch", test_sequential_launch),
        ("Container Pause/Resume", test_container_pause_resume),
        ("System Resources Monitoring", test_system_resources_monitoring),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
            
            # Brief pause between tests
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Final cleanup - make sure everything is stopped
    print("\n🧹 Final cleanup...")
    try:
        manager = get_multi_environment_manager()
        await manager.stop_all_containers(force=True)
        print("✅ Cleanup completed")
    except:
        pass
    
    # Results summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Multi-environment system is working perfectly!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. System needs attention.")
        return False


def main():
    """Main test function.""" 
    print("🧪 ENVSTARTER MULTI-ENVIRONMENT SYSTEM TESTS")
    print("Version 2.0 - VM-like Environment Containers")
    print()
    
    # Run async tests
    try:
        result = asyncio.run(run_all_tests())
        
        if result:
            print("\n🎊 TESTING COMPLETE - SYSTEM READY!")
            print("\n💡 Next steps:")
            print("   1. Run: python src/envstarter/enhanced_main.py")
            print("   2. Try the new Multi-Environment Dashboard")
            print("   3. Launch multiple environments simultaneously!")
            sys.exit(0)
        else:
            print("\n💥 TESTING FAILED - SYSTEM NEEDS FIXES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()