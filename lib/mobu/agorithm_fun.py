# -*- coding: utf-8 -*-#

from pyfbsdk import *
import math

class Quaternion:
    def __init__(self, FBVector):
        self.x = FBVector[0]
        self.y = FBVector[1]
        self.z = FBVector[2]
        self.w = FBVector[3]

    @staticmethod
    def Identity():
        return Quaternion([0, 0, 0, 1])

    def xyzw(self):
        return FBVector4d(self.x, self.y, self.z, self.w)

    def xyz(self):
        return FBVector3d(self.x, self.y, self.z)

    def __getitem__(self, key):  # 索引器
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        elif key == 3:
            return self.w

    def __add__(self, quaternion):
        result = Quaternion(self.xyzw())
        result.x += quaternion.x
        result.y += quaternion.y
        result.z += quaternion.z
        result.w += quaternion.w
        return result

    def __sub__(self, quaternion):
        result = Quaternion(self.xyzw())
        result.x -= quaternion.x
        result.y -= quaternion.y
        result.z -= quaternion.z
        result.w -= quaternion.w
        return result

    def __mul__(self, quaternion):
        result = Quaternion(self.xyzw())
        result.x = self.w * quaternion.x + self.x * quaternion.w - self.y * quaternion.z + self.z * quaternion.y
        result.y = self.w * quaternion.y + self.y * quaternion.w + self.x * quaternion.z - self.z * quaternion.x
        result.z = self.w * quaternion.z + self.z * quaternion.w - self.x * quaternion.y + self.y * quaternion.x
        result.w = self.w * quaternion.w - self.x * quaternion.x - self.y * quaternion.y - self.z * quaternion.z
        return result

    def Divides(self, quaternion):
        result = Quaternion(self.xyzw())
        return result * (quaternion.Inversed())

    def MagnitudeSqr(self):
        return pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2) + pow(self.w, 2)

    def Magnituded(self):
        return pow(self.MagnitudeSqr(), 0.5)

    def Star(self):
        result = Quaternion(self.xyzw())
        result.x = -self.x
        result.y = -self.y
        result.z = -self.z
        result.w = self.w
        return result

    def Inversed(self):
        result = Quaternion(self.xyzw())
        result = result.Star()
        moder = self.MagnitudeSqr()
        if moder > 0.00001:
            result.x /= moder
            result.y /= moder
            result.z /= moder
            result.w /= moder
            return result
        else:
            return self.Identity()

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z) + " " + str(self.w)

    def Normalize(self):
        moder = self.Magnituded()
        if moder > 0.00001:
            self.x /= moder
            self.y /= moder
            self.z /= moder
            self.w /= moder
        else:
            return self.Identity()

    def Normalized(self):
        result = Quaternion(self.xyzw())
        moder = result.Magnituded()
        if moder > 0.00001:
            result.x /= moder
            result.y /= moder
            result.z /= moder
            result.w /= moder
            return result
        else:
            return self.Identity()

    @staticmethod
    def FromToRotation(fromDirection, toDirection):
        if fromDirection == FBVector3d(0, 0, 0) or toDirection == FBVector3d(0, 0, 0):
            return Quaternion.Identity()
        fromDirection.Normalize()
        toDirection.Normalize()
        if FBVector3d.IsEqual(fromDirection, toDirection):
            return Quaternion.Identity()
        aixs = FBVector3d.CrossProduct(fromDirection, toDirection)
        sinA = aixs.Length()
        cosA = FBVector3d.DotProduct(fromDirection, toDirection)
        sinHalfA = pow(((1 - cosA) * 0.5), 0.5)
        cosHalfA = sinA / (2.0 * sinHalfA)
        aixs.Normalize()
        aixs = aixs * sinHalfA
        return Quaternion(FBVector4d(aixs[0], aixs[1], aixs[2], cosHalfA))

    @staticmethod
    def FromEular(eular):
        Deg2Rad = math.pi / 180.0
        Cx = math.cos(eular[0] / 2.0 * Deg2Rad)
        Cy = math.cos(eular[1] / 2.0 * Deg2Rad)
        Cz = math.cos(eular[2] / 2.0 * Deg2Rad)

        Sx = math.sin(eular[0] / 2.0 * Deg2Rad)
        Sy = math.sin(eular[1] / 2.0 * Deg2Rad)
        Sz = math.sin(eular[2] / 2.0 * Deg2Rad)

        qX = Quaternion(FBVector4d(Sx, 0.0, 0.0, Cx))
        qY = Quaternion(FBVector4d(0.0, Sy, 0.0, Cy))
        qZ = Quaternion(FBVector4d(0.0, 0.0, Sz, Cz))
        result = qX * qY * qZ  # MotionBulider RotateOrder xyz
        return result

    def RotateDirection(self, direction):  # multi vector3 使得Vector3经过该四元数变换得到新的vector3
        result = Quaternion(self.xyzw())
        result.Normalize()
        qDirection = Quaternion(FBVector4d(direction[0], direction[1], direction[2], 0))
        resultDirection = result.Inversed() * qDirection * result
        return FBVector3d(resultDirection.x, resultDirection.y, resultDirection.z)



    def Euler(self):  # 四元数转欧拉角  按照xyz的旋转顺序进行计算
        euler = FBVector3d(0.0, 0.0, 0.0)
        q = Quaternion(self.xyzw())
        q.Normalize()
        euler[0] = math.atan2(2 * (q.w * q.x + q.y * q.z), 1 - 2 * (q.x * q.x + q.y * q.y))
        euler[1] = math.asin(clamp(2 * (q.w * q.y - q.x * q.z), -1, 1))
        euler[2] = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        Rad2Deg = 180.0 / math.pi
        euler *= Rad2Deg
        return euler


def clamp(value, minValue, maxValue):
    # type: (float, float, float) -> float
    return max(minValue, min(maxValue, value))


def clamp01(value):
    # type: (float) -> float
    return clamp(value, 0, 1)





