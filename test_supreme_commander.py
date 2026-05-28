#!/usr/bin/env python3
"""
Test Supreme Commander JARVIS
"""

import asyncio
import sys
sys.path.insert(0, r'D:\jarvis\ecosystem')

async def main():
    print("="*70)
    print("SUPREME COMMANDER JARVIS - TEST")
    print("="*70)
    
    # Import și inițializare
    try:
        from agents.d_agents.supreme_commander import SupremeCommander
        
        print("\n🚀 Initializing Supreme Commander...")
        commander = SupremeCommander(None, None)
        
        # Boot
        await commander.boot()
        
        # Trimite comandă de test
        print("\n🎯 Sending test order...")
        order = {
            'command': 'implement_features_from_videos',
            'target': 'd:/pj-for-jarvis-implement-features',
            'requirements': {
                'analyze_all_videos': True,
                'extract_ui_designs': True,
                'implement_features': True,
                'replicate_interfaces': True
            },
            'priority': 'critical'
        }
        
        mission_id = await commander.receive_order(order)
        
        print(f"\n✅ TEST COMPLETE")
        print(f"   Mission ID: {mission_id}")
        print(f"   Status: Mission accepted and processing")
        
        # Așteaptă puțin pentru a vedea progresul
        print("\n⏳ Waiting for mission execution...")
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST END")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
