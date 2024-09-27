import math


# Function for Forward Kinematics
def forward_kinematics(L1, L2, L3, theta1, theta2, theta3):
    # Convert angles from degrees to radians
    theta1 = math.radians(theta1)
    theta2 = math.radians(theta2)
    theta3 = math.radians(theta3)

    # Calculate coordinates x, y, z
    x = L2 * math.cos(theta1) * math.cos(theta2) + L3 * math.cos(theta1) * math.cos(theta2 + theta3)
    y = L2 * math.sin(theta1) * math.cos(theta2) + L3 * math.sin(theta1) * math.cos(theta2 + theta3)
    z = L1 + L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3)

    return x, y, z


# Function for Inverse Kinematics
def inverse_kinematics(L1, L2, L3, x, y, z):
    # Calculate angle theta1
    theta1 = math.atan2(y, x)

    # Calculate the distance from the origin to the projection of the end-effector on the XY plane
    d = math.sqrt(x ** 2 + y ** 2)

    # Calculate the distance from the origin to the end-effector on the Z plane
    r = math.sqrt(d ** 2 + (z - L1) ** 2)

    # Check the condition for the existence of a solution
    if r > (L2 + L3) or r < abs(L2 - L3):
        raise ValueError("The coordinates cannot be reached with the current robot structure.")

    # Calculate the angle between segment L2 and the vertical axis from the origin to the end-effector
    phi = math.atan2(z - L1, d)

    # Use the cosine law to calculate theta2 and theta3
    cos_theta2 = (L2 ** 2 + r ** 2 - L3 ** 2) / (2 * L2 * r)
    if not (-1 <= cos_theta2 <= 1):
        raise ValueError("Invalid angle calculation for theta2.")

    theta2 = phi + math.acos(cos_theta2)

    cos_theta3 = (L2 ** 2 + L3 ** 2 - r ** 2) / (2 * L2 * L3)
    if not (-1 <= cos_theta3 <= 1):
        raise ValueError("Invalid angle calculation for theta3.")

    theta3 = math.acos(cos_theta3) - math.pi

    # Convert angles from radians to degrees
    theta1 = math.degrees(theta1)
    theta2 = math.degrees(theta2)
    theta3 = math.degrees(theta3)

    return theta1, theta2, theta3

def is_within_workspace(L1, L2, L3, x, y, z):
    # Calculate the distance squared between the base and the target point
    distance_squared = x ** 2 + y ** 2 + (z - L1) ** 2

    # Calculate the minimum and maximum reach squared
    min_reach_squared = (L2 - L3) ** 2
    max_reach_squared = (L2 + L3) ** 2

    # Check if the point is within the range
    return min_reach_squared <= distance_squared <= max_reach_squared


# Main function for the program
def main():
    L1 = 30
    L2 = 30
    L3 = 30

    # Input the end-effector coordinates from the user
    x = float(input("Enter x coordinate: "))
    y = float(input("Enter y coordinate: "))
    z = float(input("Enter z coordinate: "))

    # Check if the target position is within the robot's workspace
    if is_within_workspace(L1, L2, L3, x, y, z):
        # Calculate joint angles using inverse kinematics
        try:
            theta1, theta2, theta3 = inverse_kinematics(L1, L2, L3, x, y, z)
            print(f"\nCalculated joint angles:")
            print(f"Theta1 = {theta1:.2f} degrees")
            print(f"Theta2 = {theta2:.2f} degrees")
            print(f"Theta3 = {theta3:.2f} degrees")

            # Recalculate end-effector position using forward kinematics
            x_fwd, y_fwd, z_fwd = forward_kinematics(L1, L2, L3, theta1, theta2, theta3)
            print(f"\nRecalculated coordinates from joint angles:")
            print(f"x = {x_fwd:.2f}, y = {y_fwd:.2f}, z = {z_fwd:.2f}")

            # Check accuracy
            if math.isclose(x, x_fwd, abs_tol=0.01) and math.isclose(y, y_fwd, abs_tol=0.01) and math.isclose(z, z_fwd, abs_tol=0.01):
                print("\nThe result is accurate!")
            else:
                print("\nThe result does not match; please check again.")

        except ValueError as e:
            print(e)
    else:
        print("The point is outside the robot's reachable workspace.")

if __name__ == "__main__":
    main()

