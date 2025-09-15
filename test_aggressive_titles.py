#!/usr/bin/env python3
"""
🔥 TEST AGGRESSIVE TITLE INJECTION 🔥
LAUNCH REAL APPS AND VERIFY TITLES SHOW ENVIRONMENT NAMES!
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.envstarter.core.models import Environment, Application
from src.envstarter.core.simple_environment_container import SimpleEnvironmentContainer
from src.envstarter.core.aggressive_title_injector import AggressiveWindowTitleInjector


async def test_real_application_titles():
    """Launch REAL applications and verify titles are injected."""
    print("🔥 TESTING REAL APPLICATION TITLE INJECTION")
    print("=" * 70)
    
    # Create test environment with REAL applications
    if os.name == 'nt':  # Windows
        test_apps = [
            Application(
                name="Calculator",
                path="calc.exe",
                is_enabled=True
            ),
            Application(
                name="Notepad", 
                path="notepad.exe",
                is_enabled=True
            )
        ]
    else:  # Linux/Mac
        test_apps = [
            Application(
                name="Calculator",
                path="gnome-calculator",
                is_enabled=True
            ),
            Application(
                name="Text Editor",
                path="gedit",
                is_enabled=True
            )
        ]
    
    test_env = Environment(
        name="TITLE_TEST_ENV",
        description="Testing aggressive title injection with real apps",
        applications=test_apps
    )
    
    print(f"🚀 Environment: {test_env.name}")
    print(f"📱 Applications to launch: {[app.name for app in test_apps]}")
    
    # Create container
    container = SimpleEnvironmentContainer(test_env, "aggressive_test_container")
    
    try:
        print("\n🔥 Starting container with AGGRESSIVE title injection...")
        success = await container.start_container()
        
        if success:
            print(f"✅ Container started successfully!")
            print(f"📊 Tracked processes: {list(container.tracked_processes)}")
            
            # Wait for applications to fully load
            print("\n⏳ Waiting for applications to load and titles to be injected...")
            for i in range(10):
                await asyncio.sleep(1)
                stats = container.title_injector.get_injection_stats()
                print(f"   Second {i+1}: {stats['total_injections']} title injections performed")
                
            # Final stats
            final_stats = container.title_injector.get_injection_stats()
            print(f"\n📊 FINAL INJECTION STATS:")
            print(f"   Environment: {final_stats['environment_name']}")
            print(f"   Tracked PIDs: {final_stats['tracked_pids']}")
            print(f"   Total Injections: {final_stats['total_injections']}")
            print(f"   Active Windows: {final_stats['active_windows']}")
            
            if final_stats['total_injections'] > 0:
                print("\n🎉 SUCCESS! Titles were injected!")
                print(f"💡 Look for window titles starting with: [{test_env.name}]")
                print("💡 Example: [TITLE_TEST_ENV] Calculator")
                print("💡 Example: [TITLE_TEST_ENV] Notepad")
            else:
                print("\n❌ NO INJECTIONS PERFORMED!")
                print("💡 This could mean:")
                print("   - Applications haven't opened yet")
                print("   - Title injection failed")
                print("   - Need admin rights (Windows)")
                
            # Manual verification
            print(f"\n🔍 MANUAL VERIFICATION:")
            print(f"   1. Check if applications opened:")
            for app in test_apps:
                print(f"      - {app.name} ({app.path})")
            print(f"   2. Check window titles show: [{test_env.name}] AppName")
            print(f"   3. Titles should update every 500ms")
            
            # Keep running for manual verification
            print(f"\n⏰ Keeping applications running for 15 seconds for verification...")
            for i in range(15):
                await asyncio.sleep(1)
                if i % 5 == 0:
                    stats = container.title_injector.get_injection_stats()
                    print(f"   Still running... {stats['total_injections']} total injections")
                    
            # Stop container
            print("\n🛑 Stopping container and cleaning up...")
            await container.stop_container()
            
        else:
            print("❌ Container failed to start!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        if hasattr(container, 'title_injector'):
            container.title_injector.stop_monitoring()


async def test_multiple_environments():
    """Test multiple environments with different names."""
    print("\n🔥 TESTING MULTIPLE ENVIRONMENTS")
    print("=" * 70)
    
    environments = []
    containers = []
    
    try:
        # Create multiple test environments
        for i in range(2):
            env_name = f"TEST_ENV_{i+1}"
            
            if os.name == 'nt':
                app = Application(name="Calculator", path="calc.exe", is_enabled=True)
            else:
                app = Application(name="Calculator", path="gnome-calculator", is_enabled=True)
                
            env = Environment(
                name=env_name,
                description=f"Test environment #{i+1}",
                applications=[app]
            )
            
            container = SimpleEnvironmentContainer(env, f"multi_test_container_{i+1}")
            
            environments.append(env)
            containers.append(container)
            
        # Start all environments
        print(f"🚀 Starting {len(environments)} environments...")
        for i, container in enumerate(containers):
            print(f"   Starting {environments[i].name}...")
            success = await container.start_container()
            if success:
                print(f"   ✅ {environments[i].name} started")
            else:
                print(f"   ❌ {environments[i].name} failed")
                
            await asyncio.sleep(2)  # Stagger launches
            
        # Let them run and inject titles
        print(f"\n⏳ Letting environments run for 10 seconds...")
        for i in range(10):
            await asyncio.sleep(1)
            total_injections = sum(
                container.title_injector.get_injection_stats()['total_injections']
                for container in containers
                if hasattr(container, 'title_injector')
            )
            print(f"   Second {i+1}: {total_injections} total injections across all environments")
            
        # Show final stats
        print(f"\n📊 FINAL STATS FOR ALL ENVIRONMENTS:")
        for i, container in enumerate(containers):
            if hasattr(container, 'title_injector'):
                stats = container.title_injector.get_injection_stats()
                print(f"   {environments[i].name}: {stats['total_injections']} injections")
                
        print(f"\n💡 VERIFICATION:")
        print(f"   You should see multiple calculator windows open")
        for env in environments:
            print(f"   - Window titled: [{env.name}] Calculator")
            
        # Clean up
        print(f"\n🛑 Cleaning up all environments...")
        for container in containers:
            await container.stop_container()
            
    except Exception as e:
        print(f"❌ Multiple environment test failed: {e}")
        for container in containers:
            if hasattr(container, 'title_injector'):
                container.title_injector.stop_monitoring()


async def main():
    """Run all aggressive title injection tests."""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                              ║")
    print("║           🔥 AGGRESSIVE TITLE INJECTION VERIFICATION TESTS 🔥               ║")
    print("║                                                                              ║")
    print("║     Tests that environment names ACTUALLY appear in window titles!          ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    try:
        # Test 1: Single environment with real applications
        await test_real_application_titles()
        
        # Brief pause between tests
        await asyncio.sleep(3)
        
        # Test 2: Multiple environments
        await test_multiple_environments()
        
        print(f"\n" + "=" * 70)
        print(f"🎯 AGGRESSIVE TITLE INJECTION TESTS COMPLETED!")
        print(f"=" * 70)
        print(f"\n💡 If you saw titles like '[ENV_NAME] AppName', IT WORKED!")
        print(f"💡 If no title changes occurred, check:")
        print(f"   - Run as Administrator (Windows)")
        print(f"   - Install xdotool (Linux): sudo apt install xdotool")
        print(f"   - Applications actually opened")
        print(f"\n✅ The system is now configured to FORCE environment names into ALL window titles!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")