import sys
import os
# Add the backend src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from services.simulation.workforce import get_effective_recruitment_value, get_effective_churn_value

def test_get_effective_recruitment_value():
    class Dummy:
        pass

    # Test 1: Absolute value present
    obj1 = Dummy()
    setattr(obj1, 'recruitment_abs_1', 20)
    value = get_effective_recruitment_value(obj1, 1)
    assert value == 20, f"Expected 20, got {value}"

    # Test 2: No absolute value present
    obj2 = Dummy()
    value = get_effective_recruitment_value(obj2, 1)
    assert value == 0, f"Expected 0, got {value}"

    # Test 3: Different month
    obj3 = Dummy()
    setattr(obj3, 'recruitment_abs_6', 15)
    value = get_effective_recruitment_value(obj3, 6)
    assert value == 15, f"Expected 15, got {value}"

    print("All get_effective_recruitment_value tests passed.")

def test_get_effective_churn_value():
    class Dummy:
        pass

    # Test 1: Absolute value present
    obj1 = Dummy()
    setattr(obj1, 'churn_abs_1', 10)
    value = get_effective_churn_value(obj1, 1)
    assert value == 10, f"Expected 10, got {value}"

    # Test 2: No absolute value present
    obj2 = Dummy()
    value = get_effective_churn_value(obj2, 1)
    assert value == 0, f"Expected 0, got {value}"

    # Test 3: Different month
    obj3 = Dummy()
    setattr(obj3, 'churn_abs_12', 8)
    value = get_effective_churn_value(obj3, 12)
    assert value == 8, f"Expected 8, got {value}"

    print("All get_effective_churn_value tests passed.")

if __name__ == "__main__":
    test_get_effective_recruitment_value()
    test_get_effective_churn_value() 