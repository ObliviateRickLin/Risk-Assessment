# This file is responsible for calculating the severity of a potential collision.
# It is dependent on the output from an upstream "prediction" module.

import math

def calculate_severity(mass, beta, velocity):
    """
    Calculate the severity of a potential collision.
    
    Parameters:
    - mass (float): The mass involved in the collision (in kg)
    - beta (float): The scaling factor
    - velocity (float): The estimated velocity at time t + Delta t (in m/s)
    
    Returns:
    - float: The calculated severity
    """
    severity = 0.5 * mass * math.pow(beta, 2) * math.pow(velocity, 2)
    return severity

if __name__ == "__main__":
    # Example usage
    mass = 1000  # Mass in kg
    beta = 1.5  # Scaling factor
    velocity = 20  # Velocity in m/s
    
    severity_value = calculate_severity(mass, beta, velocity)
    print(f"The calculated severity is: {severity_value}")