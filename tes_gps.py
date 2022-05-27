connection_string = "/dev/serial0"

# Import DroneKit-Python
from dronekit import connect, VehicleMode

try:
    # Connect to the Vehicle.
    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, baud=230400, wait_ready=True)

    # Get some vehicle attributes (state)
    print("Get some vehicle attribute values:")
    print (" GPS: %s" % vehicle.gps_0)
    print (" Battery: %s" % vehicle.battery)
    print (" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print (" Is Armable?: %s" % vehicle.is_armable)
    print (" System status: %s" % vehicle.system_status.state)
    print (" Mode: %s" % vehicle.mode.name)

    while True:
        print(vehicle.location.global_relative_frame.lat)
        print(vehicle.location.global_relative_frame.lon)
except KeyboardInterrupt:
    # Close vehicle object before exiting script
    vehicle.close()

    print("Completed")