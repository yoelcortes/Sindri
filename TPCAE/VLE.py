import sympy as sp
import numpy as np
from numba import njit, float64

from polyEqSolver import solve_cubic
from constants import R_IG, DBL_EPSILON

vle_options = {"Peng and Robinson (1976)": "peng_and_robinson_1976"}


class InterfaceEosVLE(object):
    def __init__(self):
        self.k = None

    def bm(self, y):
        s = 0
        for i in range(len(y)):
            s += y[i] * self.bi(i)
        return s

    def thetam(self, y, T):
        s1 = 0
        for i in range(len(y)):
            s2 = 0
            for j in range(len(y)):
                s2 += (
                    y[i]
                    * y[j]
                    * np.sqrt(self.thetai(i, T) * self.thetai(j, T))
                    * (1 - self.k[i][j])
                )
            s1 += s2
        return s1

    def thetaij(self, i, j, T):
        return np.sqrt(self.thetai(i, T) * self.thetai(j, T)) * (1 - self.k[i][j])


class VLE_PR1976(InterfaceEosVLE):
    def __init__(self, mix, k):
        super().__init__()
        self.mix = np.atleast_1d(mix)
        self.k = k

    def bi(self, i):
        return 0.07780 / (self.mix[i].Pc / (R_IG * self.mix[i].Tc))

    def thetai(self, i, T):
        alpha = (
            1.0
            + (0.37464 + 1.54226 * self.mix[i].omega - 0.2699 * self.mix[i].omega ** 2)
            * (1.0 - (T / self.mix[i].Tc) ** 0.5)
        ) ** 2
        return alpha * 0.45724 * (R_IG * self.mix[i].Tc) ** 2 / self.mix[i].Pc

    def getZfromPT(self, P, T, y):
        A = self.thetam(y, T) * P / (R_IG * T) ** 2
        B = self.bm(y) * P / (R_IG * T)

        roots = np.asarray(
            solve_cubic(
                1.0, -(1.0 - B), (A - 3 * B * B - 2.0 * B), -(A * B - B * B - B ** 3)
            )
        )
        real_values = roots[roots > 0]
        return real_values

    def phi_i(self, i, y, P, T, Z):
        b = self.bm(y)
        a = self.thetam(y, T)

        bi = self.bi(i)
        A = a * P / (R_IG * T) ** 2
        B = b * P / (R_IG * T)

        aji = 0
        for j in range(len(y)):
            aji += y[j] * self.thetaij(j, i, T)

        lnphi = (
            bi * (Z - 1) / b
            - np.log(Z - B)
            - A
            / (2 * B * np.sqrt(2))
            * (2 * aji / a - bi / b)
            * np.log((Z + 2.414 * B) / (Z - 0.414 * B))
        )
        return np.exp(lnphi)


class VLE(object):
    def __init__(self, mix, eos, k=None):

        self.mix = mix
        self.eos = eos
        self.eosval = vle_options[self.eos]
        self.bm = None
        self.b = None
        self.n = len(mix)
        self.eoseq = None

        self.Vcs = np.zeros(self.n)
        self.Pcs = np.zeros(self.n)
        self.Tcs = np.zeros(self.n)
        self.omegas = np.zeros(self.n)

        for i in range(self.n):
            self.Vcs[i] = self.mix[i].Vc
            self.Tcs[i] = self.mix[i].Tc
            self.Pcs[i] = self.mix[i].Pc
            self.omegas[i] = self.mix[i].omega

        if k is None:
            self.k = np.empty((self.n, self.n))
            for i in range(self.n):
                for j in range(self.n):
                    self.k[i][j] = 0.0
        else:
            self.k = k

        self.setup()

    def setup(self):
        if self.eosval == "peng_and_robinson_1976":
            self.eoseq = VLE_PR1976(self.mix, self.k)

    def getZ(self, P, T, y):
        return self.eoseq.getZfromPT(P, T, y)

    def getPhi_i(self, i, y, P, T, Z):
        return self.eoseq.phi_i(i, y, P, T, Z)

    def _getPb_guess(self, x, T):
        x = np.atleast_1d(x)
        return np.sum(
            x * self.Pcs * np.exp(5.373 * (1 + self.omegas) * (1 - self.Tcs / T))
        )

    def _getPd_guess(self, y, T):
        y = np.atleast_1d(y)
        return np.sum(
            y / (self.Pcs * np.exp(5.373 * (1 + self.omegas) * (1 - self.Tcs / T)))
        )

    def getBubblePointPressure(self, x, T, tol=1e3 * DBL_EPSILON, kmax=10000):

        assert len(x) == self.n
        assert np.sum(x) == 1.0

        x = np.atleast_1d(x)
        pb = self._getPb_guess(x, T)

        k = np.log(self.Pcs / pb) + 5.373 * (1 + self.omegas) * (1.0 - self.Tcs / T)
        y = x * k / np.sum(x * k)
        # y = np.full(self.n, 1.0/self.n)

        err = 100
        ite = 0

        phivap = np.empty(self.n, dtype=np.float64)
        philiq = np.empty(self.n, dtype=np.float64)

        while err > tol and ite < kmax:
            ite += 1

            zsvap = self.getZ(pb, T, y)
            zsliq = self.getZ(pb, T, x)

            zvap = np.max(zsvap)
            zliq = np.min(zsliq)

            for i in range(self.n):
                phivap[i] = self.getPhi_i(i, y, pb, T, zvap)
                philiq[i] = self.getPhi_i(i, x, pb, T, zliq)

            k = philiq / phivap
            y = x * k
            yt = np.sum(y)
            pb = pb * yt
            err = np.abs(1.0 - yt)

        return y, pb, ite

    def getFlash(self, z, P, T, tol=DBL_EPSILON, kmax=10000):

        assert self.n == len(z)
        z = np.atleast_1d(z)
        assert np.sum(z) == 1.0

        pb = self._getPb_guess(z, T)
        pd = self._getPd_guess(z, T)

        # v = - (pb - P)/(pb - pd)
        v = 0.5

        err = 100
        ite = 0

        phivap = np.empty(self.n, dtype=np.float64)
        philiq = np.empty(self.n, dtype=np.float64)

        y = np.full(self.n, 1.0 / self.n)
        x = np.full(self.n, 1.0 / self.n)

        while err > tol and ite < kmax:

            ite += 1

            zsvap = self.getZ(P, T, y)
            zsliq = self.getZ(P, T, x)

            zvap = np.max(zsvap)
            zliq = np.min(zsliq)

            for i in range(self.n):
                phivap[i] = self.getPhi_i(i, y, P, T, zvap)
                philiq[i] = self.getPhi_i(i, x, P, T, zliq)

            k = philiq / phivap

            vold = v
            v = _RachfordRice(v, k, z)
            x = z / (1 + v * (k - 1))
            y = k * x
            err = np.abs(v - vold)

        return x, y, v


@njit(cache=True)
def _RachfordRice(v, k, z, tol=DBL_EPSILON, kmax=10000):

    v0 = v
    v1 = 999
    err = 1000

    iter = 0
    while err > tol or iter > kmax:
        iter += 1
        f = np.sum(z * (k - 1) / (1 + v0 * (k - 1)))
        dfdv = -np.sum(z * (k - 1) ** 2 / (1 + v0 * (k - 1) ** 2))
        v1 = v0 - f / dfdv
        err = np.abs(v0 - v1)
        v0 = v1
    return v1
