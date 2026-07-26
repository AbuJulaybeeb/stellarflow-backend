import pytest
import math
from src.analytics.math_scaler import (
    rate_to_log_scaled,
    add_log_scaled,
    log_scaled_to_rate,
    SCALE_14
)

def test_logarithmic_pathing():
    # Test converting a series of rates to logs, adding them, and converting back
    rates = [1.5, 0.9, 1.1]
    
    # Expected product
    expected_product = 1.5 * 0.9 * 1.1
    
    # Logarithmic conversion
    logs = [rate_to_log_scaled(r) for r in rates]
    
    # Addition
    total_log = add_log_scaled(*logs)
    
    # Convert back to rate
    final_rate = log_scaled_to_rate(total_log)
    
    # Check if they are close enough (tolerance depends on precision)
    assert math.isclose(final_rate, expected_product, rel_tol=1e-9)

def test_rate_to_log_scaled_invalid():
    with pytest.raises(ValueError):
        rate_to_log_scaled(0)
    
    with pytest.raises(ValueError):
        rate_to_log_scaled(-1.5)
