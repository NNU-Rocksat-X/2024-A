import numpy as np
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import Pose
import math

# Note: quaternions in this module all use JPL convention

def quaternion_multiply(q0, q1):
    if isinstance(q0, Quaternion) and isinstance(q1, Quaternion):
        q_type = 'q'
        x0 = q0.x
        y0 = q0.y 
        z0 = q0.z 
        w0 = q0.w 

        x1 = q1.x 
        y1 = q1.y 
        z1 = q1.z 
        w1 = q1.w 
    elif isinstance(q0, list) and isinstance(q1, list):
        q_type = 'l'
        x0 = q0[0]
        y0 = q0[1]
        z0 = q0[2]
        w0 = q0[3]

        x1 = q1[0]
        y1 = q1[1]
        z1 = q1[2]
        w1 = q1[3]
    elif isinstance(q0, np.ndarray) and isinstance(q1, np.ndarray):
        q_type = 'a'
        x0 = q0[0]
        y0 = q0[1]
        z0 = q0[2]
        w0 = q0[3]

        x1 = q1[0]
        y1 = q1[1]
        z1 = q1[2]
        w1 = q1[3]
    else:
        print(type(q0), type(q1))
        raise
        

    Q0Q1_w = w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1
    Q0Q1_x = w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1
    Q0Q1_y = w0 * y1 - x0 * z1 + y0 * w1 + z0 * x1
    Q0Q1_z = w0 * z1 + x0 * y1 - y0 * x1 + z0 * w1

    if q_type == 'q':
        return Quaternion(Q0Q1_x, Q0Q1_y, Q0Q1_z, Q0Q1_w)
    if q_type == 'l':
        return [Q0Q1_x, Q0Q1_y, Q0Q1_z, Q0Q1_w]
    if q_type == 'a':
        return np.array([Q0Q1_x, Q0Q1_y, Q0Q1_z, Q0Q1_w])
        
def normalize_quat(q: Quaternion):
    n_q = Quaternion()
    magnitude = math.sqrt(q.x**2 + q.y**2 + q.z**2 + q.w**2)
    if magnitude == 0:
        n_q.w = 1
        return n_q
    n_q.x = q.x / magnitude
    n_q.y = q.y / magnitude
    n_q.z = q.z / magnitude
    n_q.w = q.w / magnitude
    return n_q

def quat_conjugate(q):
    q_conj = np.array([-q[0], -q[1], -q[2], q[3]])
    return q_conj

def rotate(v: list, q: list or Quaternion):
    """
    Rotates vector by quaternion

    Input
    :param v: list with (x, y, z) for vector
    :param q: list with (x, y, z, w) or geometry_msgs quaternion
    """
    if isinstance(q, Quaternion):
        q = [q.x, q.y, q.z, q.w]
    v = np.array(v)
    q = np.array(q)

    qv = np.hstack((v, 0))
    q_conj = quat_conjugate(q)
    q_qv = quaternion_multiply(q, qv)
    q_qv_qconj = quaternion_multiply(q_qv, q_conj)
    vec = q_qv_qconj[:-1]
    return vec




def angle_axis_to_quat(ax, ay, az, theta):
    qx = ax * np.sin(theta/2)
    qy = ay * np.sin(theta/2)
    qz = az * np.sin(theta/2)
    qw = np.cos(theta/2)
    q = Quaternion(qx, qy, qz, qw)
    return q

def euler_to_quat(roll, pitch, yaw):
    """
    Convert an Euler angle to a quaternion.

    Input
    :param roll: The roll (rotation around x-axis) angle in radians.
    :param pitch: The pitch (rotation around y-axis) angle in radians.
    :param yaw: The yaw (rotation around z-axis) angle in radians.

    Output
    :return qx, qy, qz, qw: The orientation in quaternion [x,y,z,w] format
    """

    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    q = Quaternion(qx, qy, qz, qw)
    return q

def quat_to_euler(q: Quaternion):
    t0 = 2 * (q.w * q.x + q.y * q.z)
    t1 = 1 - 2 * (q.x * q.x + q.y * q.y)
    roll_x = math.atan2(t0, t1)

    t2 = 2 * (q.w * q.y - q.z * q.x)
    t2 = 1 if t2 > 1 else t2 
    t2 = -1 if t2 < -1 else t2 
    pitch_y = math.asin(t2)

    t3 = 2.0 * (q.w * q.z + q.x * q.y)
    t4 = 1 - 2 * (q.y * q.y + q.z * q.z)
    yaw_z = math.atan2(t3, t4)

    return [roll_x, pitch_y, yaw_z]

def translate_vect(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.add(v1, v2)

# unit test
if __name__ == "__main__":
    v = [0.005959, -0.022452, 0.054853]
    q = [-0.09264467, -0.01128014, -0.1928348, 0.95655258]
    r_v = rotate(v, q)

    print(r_v)