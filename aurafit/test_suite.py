"""
AuraFit Test Suite
Validates core functionality without requiring user input
"""

import sys
import os
import logging
from io import BytesIO

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from src.core.llm_provider import get_llm_provider
from src.core.database import AuraFitDatabase
from src.core.function_executor import parse_function_call, FunctionExecutor
from src.utils.image_processor import validate_image, get_image_dimensions
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test database operations"""
    print("\n🧪 Testing Database...")
    
    db = AuraFitDatabase("data/test.db")
    
    # Insert test incident
    test_data = {
        "incident_type": "BUILDING_COLLAPSE",
        "incident_priority": "RED_IMMEDIATE",
        "casualty_count_estimate": 5,
        "hazards_detected": ["UNSTABLE_STRUCTURE", "DUST"],
        "recommended_actions": ["Stay back", "Call emergency"],
        "evacuation_required": True,
        "emergency_services_required": ["FIRE_SERVICE", "AMBULANCE"],
        "confidence_score": 0.85,
        "location_description": "Lagos Commercial Ave",
        "medical_summary": "5 trapped under rubble"
    }
    
    incident_id = db.insert_incident(test_data)
    print(f"✅ Incident stored: #{incident_id}")
    
    # Retrieve
    incidents = db.get_all_incidents()
    print(f"✅ Retrieved {len(incidents)} incidents")
    
    # Analytics
    analytics = db.get_incident_analytics()
    print(f"✅ Analytics: {analytics}")
    
    return True

def test_function_executor():
    """Test function call parsing"""
    print("\n🧪 Testing Function Executor...")
    
    # Test valid input
    valid_data = {
        "incident_type": "FLOOD",
        "incident_priority": "YELLOW_DELAYED",
        "casualty_count_estimate": 2,
        "hazards_detected": ["RISING_WATER"],
        "recommended_actions": ["Move to higher ground"],
        "evacuation_required": True,
        "emergency_services_required": ["RESCUE_BOAT"],
        "confidence_score": 0.9,
        "location_description": "River crossing",
        "medical_summary": "Stable patients"
    }
    
    result = FunctionExecutor.validate_and_execute(valid_data)
    print(f"✅ Valid data parsed: {result['incident_type']}")
    
    # Test invalid input with fallback
    invalid_data = {
        "incident_type": "INVALID_TYPE",
        "casualty_count_estimate": "not_a_number"
    }
    
    result = FunctionExecutor.validate_and_execute(invalid_data)
    print(f"✅ Invalid data handled gracefully: {result['incident_type']}")
    
    return True

def test_image_processing():
    """Test image processing"""
    print("\n🧪 Testing Image Processing...")
    
    # Create test image
    img = Image.new('RGB', (2000, 2000), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes = img_bytes.getvalue()
    
    # Validate
    is_valid = validate_image(img_bytes)
    print(f"✅ Image validation: {is_valid}")
    
    # Get dimensions
    dims = get_image_dimensions(img_bytes)
    print(f"✅ Image dimensions: {dims}")
    
    return True

def test_llm_provider():
    """Test LLM provider initialization"""
    print("\n🧪 Testing LLM Provider...")
    
    try:
        llm = get_llm_provider()
        print(f"✅ LLM Provider initialized: {type(llm).__name__}")
        print(f"✅ Model: {llm.model_name}")
        return True
    except Exception as e:
        print(f"⚠️ LLM Provider error (expected if no API key): {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 AURAFIT TEST SUITE")
    print("=" * 50)
    
    results = {
        "Database": test_database(),
        "Function Executor": test_function_executor(),
        "Image Processing": test_image_processing(),
        "LLM Provider": test_llm_provider(),
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} passed")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
