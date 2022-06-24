from pymavlink import mavutil
import time

print('starting...')

master = mavutil.mavlink_connection('/dev/serial0', 912600, 255)

master.wait_heartbeat()

time.sleep(2)

def send_cmd(command, p1, p2, p3, p4, p5, p6, p7, target_sysid=None, target_compid=None):
    """Send a MAVLink command long."""
    master.mav.command_long_send(target_sysid, target_compid, command, 1,  # confirmation
                                   p1, p2, p3, p4, p5, p6, p7)


def run_cmd(command, p1, p2, p3, p4, p5, p6, p7, want_result=mavutil.mavlink.MAV_RESULT_ACCEPTED,
            target_sysid=master.target_system, target_compid=master.target_component, timeout=10, quiet=False):
    print('running cmd')
    send_cmd(command, p1, p2, p3, p4, p5, p6, p7, target_sysid=target_sysid, target_compid=target_compid)
    run_cmd_get_ack(command, want_result, timeout, quiet=quiet)


def run_cmd_get_ack(command, want_result, timeout, quiet=False):
    #tstart = get_sim_time_cached()
    while True:
        #delta_time = get_sim_time_cached() - tstart
        #if delta_time > timeout:
        #    raise AutoTestTimeoutException("Did not get good COMMAND_ACK within %fs" % timeout)
        #    print('ERROR', "Did not get good COMMAND_ACK within %fs" % timeout)
        m = master.recv_match(type='COMMAND_ACK',
                                blocking=True,
                                timeout=0.1)
        if m is None:
            continue
        if not quiet:
            print("ACK received: %s" % (str(m)))
        if m.command == command:
            if m.result != want_result:
                raise ValueError("Expected %s got %s" % (want_result,
                                                         m.result))
            break


print('motors armed?', master.motors_armed())

time.sleep(1)

print('arming throttle...')

p2 = 0


run_cmd(
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
    1,  # param1 (1 to indicate arm)
    p2,  # param2  (all other params meaningless)
    0,  # param3
    0,  # param4
    0,  # param5
    0,  # param6
    0
)

master.motors_armed_wait()

print('motors armed:', master.motors_armed())

#p2 = 21196 # to force disarm
p2 = 0

time.sleep(2)

print('attempt to disarm rover')

run_cmd(
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
    0,  # param1 (1 to indicate arm)
    p2,  # param2  (all other params meaningless)
    0,  # param3
    0,  # param4
    0,  # param5
    0,  # param6
    0
)


master.motors_disarmed_wait()

print('motors armed:', master.motors_armed())