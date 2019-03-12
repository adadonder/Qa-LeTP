""" @package updateControlModule The update control API test

    Set of functions to test the le_updateCtrl_LockProbation
"""
import os
import time
import swilog
import pytest

__copyright__ = 'Copyright (C) Sierra Wireless Inc.'
# ==================================================================================================
# Constants and Globals
# ==================================================================================================
# Determine the resources folder (legato apps)
TEST_RESOURCES = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'resources')
APP_PATH_00 = os.path.join(TEST_RESOURCES, "updateCtrlApi")

APP_NAME_01 = "testUpdateCtrl"
APP_PATH_01 = os.path.join(APP_PATH_00, "testUpdateCtrlApp")


# ==================================================================================================
# Local fixtures
# ==================================================================================================
@pytest.fixture()
def init_UpdateCrtl(request, legato, clean_test):
    """
    Initial and build app

    Args:
        request: object to access data
        legato: fixture to call useful functions regarding legato
        clean_test: fixture to clean up environment

    """

    test_name = request.node.name.split("[")[0]
    if test_name != "L_UpdateCtrl_LockProbation_0002":
        # Since the test framework would change the probation period to 1ms,
        # it is necessary to change it
        # back to the default (30mins) because this test case is required to
        # run under probation
        legato.reset_probation_timer()

    # Make install application
    legato.make_install(APP_NAME_01, APP_PATH_01)
    swilog.info("[PASSED] Make and install the test app successfully.")


# ==================================================================================================
# Test functions
# ==================================================================================================
def L_UpdateCtrl_LockProbation_0001(target, legato, init_UpdateCrtl):
    """
    Verify that le_updateCtrl_LockProbation()
    prevents the probation period from ending

    Initial Condition:
        1. Probation period is 20 seconds

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation()
        onto the target device
        2. During the probation period, run the app
        3. Check the system is under probation after 20 seconds

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to initial and build app

    """

    swilog.step("Test L_UpdateCtrl_LockProbation_0001")

    # Set the probation period to 20s for verification convenience
    legato.set_probation_timer(20)

    # Set the parameter of the testUpdateCtrl app to
    # "lockProbation" "1" to run this test case
    target.run("config set apps/%s/procs/%s/args/1"
               " lockProbation" % (APP_NAME_01, APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2"
               " 1" % (APP_NAME_01, APP_NAME_01))

    target.run("app start %s" % APP_NAME_01, withexitstatus=1)

    # Wait for 25s before checking the system status
    time.sleep(25)

    # Store the current system status after le_updateCtrl_LockProbation()
    # is called during
    # the probation period for verification
    system_status = legato.get_current_system_status()

    # After le_updateCtrl_LockProbation() is called during
    # the probation period,
    # if the current system is not under probation after
    # the pre-set 20s probation period
    # then, there is no such process holds the probation lock in
    # the system. Mark this test case failed

    assert system_status != "tried", "[FAILED] LockProbation() doesn't prevent\
     the probation period from ending"
    swilog.info("[PASSED] LockProbation() prevents the"
                " probation period from ending")

    # After Start TC, the current system is marked as "good' and
    # the current system holds a probation lock
    # reboot the system to clear the probation lock before
    # performing the clean up on the target
    target.reboot(120)
    swilog.info("[PASSED] L_UpdateCtrl_LockProbation_0001")
    # End of this TC


def L_UpdateCtrl_LockProbation_0002(target, legato, init_UpdateCrtl):
    """
    Verify that le_updateCtrl_LockProbation() is ignored if
    the probation period has already ended

    Initial Conditions:
        1. Probation period is 10ms
           Current system index is "N"

    Test Procedures:

        1. Install the app that invokes le_updateCtrl_LockProbation()
        onto the target device
        2. After the probation period, check
        the current system index is "N + 1" and run the app
        3. Check the current system is marked as "good"
        4. Check the current system index is "N + 1"

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to initial and build app

    """

    swilog.step("Test L_UpdateCtrl_LockProbation_0002")

    # Set the probation period to 1s so that
    # the system status can turn into 'good'
    legato.set_probation_timer(1)

    # Wait 3s to allow the probation period to pass
    time.sleep(3)

    # Set the parameter of the testUpdateCtrl app to
    # "lockProbation" "2" to run this test case
    target.run("config set apps/%s/procs/%s/args/1"
               " lockProbation" % (APP_NAME_01, APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 2" % (APP_NAME_01,
                                                         APP_NAME_01))

    # Store the system index before before le_updateCtrl_LockProbation()
    # is called for verification
    old_sys_index = legato.get_current_system_index()

    target.run("app start %s" % APP_NAME_01, withexitstatus=1)

    # Store the current system index after le_updateCtrl_LockProbation()
    # is called when the system
    # is already marked as 'good' for verification
    new_sys_index = legato.get_current_system_index()

    # Store the system status after le_updateCtrl_LockProbation()
    # is called when the system
    # is already marked as 'good' for verification
    system_status = legato.get_current_system_status()

    # After le_updateCtrl_LockProbation() is called when
    # the system is already marked as 'good',
    # if the current system status is not "good" or
    # the system indexes are different before and after
    # le_updateCtrl_LockProbation() is called, mark this test case failed
    is_tc_passed = False
    if system_status != "good":
        swilog.error("[FAILED] LockProbation() modifies the current system"
                     " status when the system is already marked as 'good'")
    elif old_sys_index != new_sys_index:
        swilog.error("[FAILED] LockProbation() modifies the system"
                     " index when the system is already marked as 'good'")
    else:
        swilog.info("[PASSED] lockProbation() is ignored when "
                    "the current system is already marked as 'good'")
        is_tc_passed = True

    if is_tc_passed is False:
        target.reboot(120)

    assert is_tc_passed is True, "[FAILEd] L_UpdateCtrl_LockProbation_0001"
    swilog.info("[PASSED] L_UpdateCtrl_LockProbation_0002")


def L_UpdateCtrl_LockProbation_0003(target, legato, init_UpdateCrtl):
    """
    Verify that the target device will reboot after the client (process)
    who called le_updateCtrl_LockProbation() is dead

    Initial Condition:
        1. Current system state is marked as "good"

    Test Procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation()
        and kills its own process onto the target device
        2. Run the app
        3. Check the target device is rebooting

    (Notes: the current system index, the current system state and
    the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to initial and build app

    """

    swilog.step("Test L_UpdateCtrl_LockProbation_0003")

    # Set the parameter of the testUpdateCtrl app
    # to "lockProbation" "3" to run this test case
    target.run("config set apps/%s/procs/%s/args/1"
               " lockProbation" % (APP_NAME_01, APP_NAME_01))
    target.run("config set apps/%s/procs/%s/args/2 3" % (APP_NAME_01,
                                                         APP_NAME_01))
    target.run("app start %s" % APP_NAME_01, withexitstatus=1)
    time.sleep(5)
    # Wait 10s to check whether the device is shutting down after
    # the process who called
    # le_updateCtrl_LockProbation() is dead
    is_device_shutdown = False
    if target.wait_for_device_down(10) is 0:
        is_device_shutdown = True

    # After the process who called le_updateCtrl_LockProbation() is dead,
    # if the target device is not shutting down then,
    # the target device it is not rebooting.
    # Marked this test case failed
    is_tc_passed = False
    if is_device_shutdown is False:
        swilog.error("[FAILED] the target device is not rebooting"
                     " when a process who called LockProbation() is dead")
    else:
        swilog.info("[PASSED] the target device is rebooting"
                    " when a process who called LockProbation() is dead")
        is_tc_passed = True

    # If TC is not passed, reboot the system to clear
    # the probation lock counter
    # before performing the clean up on the target
    if is_tc_passed is False:
        target.reboot()
    else:
        # Wait for target to finish reboot
        target.wait_for_reboot(120)

    assert is_tc_passed is True, "[FAILED] L_UpdateCtrl_LockProbation_0003"
    swilog.info("[PASSED] L_UpdateCtrl_LockProbation_0003")


def L_UpdateCtrl_LockProbation_0004(target, legato, init_UpdateCrtl):
    """
    Verify that the target device will reboot after stopping the client
    (process) who called le_updateCtrl_LockProbation()

    Initial Condition:
        1. Current system is marked as "good"

    Test procedures:
        1. Install the app that invokes le_updateCtrl_LockProbation()
        onto the target device
        2. Run the app
        3. Stop the app
        4. Check the target device is rebooting

    (Notes: the current system index, the current system state
    and the current system status can be verified by
    the command line "legato status")

    Args:
        target: fixture to communicate with the target
        legato: fixture to call useful functions regarding legato
        init_UpdateCrtl: fixture to initial and build app

    """

    swilog.step("Test L_UpdateCtrl_LockProbation_0004")

    target.run("config set apps/%s/procs/%s/args/1"
               " lockProbation" % (APP_NAME_01, APP_NAME_01))

    target.run("config set apps/%s/procs/%s/args/2 4" % (APP_NAME_01,
                                                         APP_NAME_01))
    target.run("app start %s" % APP_NAME_01, withexitstatus=1)

    # Stop the testUpdateCtrl app who called le_updateCtrl_LockProbation()
    # when the system is under probation
    target.run("app stop %s" % APP_NAME_01, withexitstatus=1)
    time.sleep(5)
    # Wait 10s to check whether the device is shutting down
    is_device_shutdown = False
    if target.wait_for_device_down(10) is 0:
        is_device_shutdown = True

    # After the process who called le_updateCtrl_LockProbation()is terminated,
    # if the target device is not shutting down then,
    # the target device it is not rebooting.
    # Marked this test case failed
    is_tc_passed = False
    if is_device_shutdown is False:
        swilog.error("[FAILED] the target device is not rebooting"
                     " after stopping a process who called LockProbation()")
    else:
        swilog.info("[PASSED] the target device is rebooting"
                    " after stopping a process who called LockProbation()")
        is_tc_passed = True

    # If TC is not passed, reboot the system to
    # clear the probation lock counter
    # before performing the clean up on the target
    if is_tc_passed is False:
        target.reboot()
    else:
        # Wait for target to finish reboot
        target.wait_for_reboot(120)

    assert is_tc_passed is True, "[FAILED] L_UpdateCtrl_LockProbation_0004"
    swilog.info("[PASSED] L_UpdateCtrl_LockProbation_0004")
