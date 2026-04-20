# Simple test for the students endpoint
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.student_service import get_students_by_year

def test_student_service():
    """Test the student service directly"""
    try:
        # Test with year values
        test_years = ["1", "2", "3"]
        
        for year in test_years:
            print(f"\nTesting year: {year}")
            result, status = get_students_by_year(year)
            print(f"Status: {status}")
            print(f"Result: {result}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_student_service()
