"""
Black-Scholes-Merton Pricer & Greeks
=====================================

Autoria y licencia
------------------
Autor       : Eduardo Ramos, CFA (github.com/EERamos)
Repositorio : https://github.com/EERamos/bsm-calculator
Licencia    : MIT - Copyright (c) 2026 Eduardo Ramos
Conserva este aviso de autoria en cualquier copia o version derivada.

Production-quality, fully vectorized BSM implementation with:
- European Call / Put pricing (Merton's dividend-yield extension)
- First-order Greeks:  Delta, Vega, Theta, Rho
- Second-order Greeks: Gamma, Vanna, Volga (Vomma), Charm
- Abramowitz & Stegun (1964) CDF approximation (educational reference)
- scipy.stats.norm CDF (production reference)
- Put-Call parity validator
- Finite-difference Greek validator

Conventions
-----------
S    : spot
K    : strike
r    : risk-free rate (continuous)
q    : continuous dividend yield
sigma: volatility (annualized)
tau  : time to maturity in years (T - t)

Author: Eduardo Ramos, CFA
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Abramowitz & Stegun (1964) CDF approximation
# ---------------------------------------------------------------------------
def cdf_abramowitz_stegun(x: float) -> float:
    """
    Approximation of the standard normal CDF accurate to ~6 decimals.
    Classic textbook formulation used in quantitative finance coursework.
    """
    a1, a2, a3, a4, a5 = (0.319381530, -0.356563782, 1.781477937,
                          -1.821255978, 1.330274429)
    sign = 1.0 if x >= 0 else -1.0
    z = abs(x)
    k = 1.0 / (1.0 + 0.2316419 * z)
    n = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * z * z)
    N = 1.0 - n * (a1 * k + a2 * k**2 + a3 * k**3 + a4 * k**4 + a5 * k**5)
    return N if sign > 0 else 1.0 - N


# ---------------------------------------------------------------------------
# Vectorized BSM with Greeks
# ---------------------------------------------------------------------------
@dataclass
class BSMResult:
    price: np.ndarray | float
    delta: np.ndarray | float
    gamma: np.ndarray | float
    vega: np.ndarray | float
    theta: np.ndarray | float
    rho: np.ndarray | float
    vanna: np.ndarray | float
    volga: np.ndarray | float
    charm: np.ndarray | float

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("price", "delta", "gamma", "vega", "theta",
                 "rho", "vanna", "volga", "charm")}


def _d1_d2(S, K, r, q, sigma, tau):
    sigma_sqrt_tau = sigma * np.sqrt(tau)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * tau) / sigma_sqrt_tau
    d2 = d1 - sigma_sqrt_tau
    return d1, d2, sigma_sqrt_tau


def _degenerate_result(S, K, r, q, tau, option):
    """
    Closed-form limits when the BSM formula is undefined.

    * tau -> 0:   price collapses to intrinsic; delta collapses to a Heaviside
                  step (1 if ITM, 0 if OTM, 0.5 ATM); higher-order Greeks are
                  either zero or unbounded (we return 0 by convention).
    * sigma -> 0: option becomes a deterministic forward, price is the
                  discounted intrinsic of the forward.
    """
    S, K, r, q, tau = (np.asarray(x, dtype=float) for x in (S, K, r, q, tau))
    disc_r = np.exp(-r * tau)
    disc_q = np.exp(-q * tau)
    fwd = S * disc_q - K * disc_r  # discounted intrinsic for sigma=0

    if option == "call":
        price = np.maximum(fwd, 0.0)
        delta = disc_q * np.where(S > K, 1.0, np.where(S < K, 0.0, 0.5))
    else:
        price = np.maximum(-fwd, 0.0)
        delta = -disc_q * np.where(S < K, 1.0, np.where(S > K, 0.0, 0.5))

    zero = np.zeros_like(price)
    return BSMResult(price=price, delta=delta, gamma=zero, vega=zero,
                     theta=zero, rho=zero, vanna=zero, volga=zero, charm=zero)


def black_scholes(
    S: float | np.ndarray,
    K: float | np.ndarray,
    r: float | np.ndarray,
    q: float | np.ndarray,
    sigma: float | np.ndarray,
    tau: float | np.ndarray,
    option: Literal["call", "put"] = "call",
) -> BSMResult:
    """
    Vectorized Black-Scholes-Merton pricer & Greeks.

    All inputs broadcast under NumPy rules. Greeks returned in 'natural' units:
    - vega per 1.00 in vol (divide by 100 for per-1% units)
    - theta per year (divide by 365 for per-day)
    - rho per 1.00 in rate (divide by 100 for per-1% units)

    Degenerate inputs (tau <= 0 or sigma <= 0) are handled with their
    closed-form limits. S must be strictly positive.
    """
    S, K, r, q, sigma, tau = map(np.asarray,
                                  (S, K, r, q, sigma, tau))

    if np.any(S <= 0) or np.any(K <= 0):
        raise ValueError("S and K must be strictly positive")
    if option not in ("call", "put"):
        raise ValueError("option must be 'call' or 'put'")

    if np.any(np.asarray(tau) <= 0) or np.any(np.asarray(sigma) <= 0):
        return _degenerate_result(S, K, r, q, tau, option)

    d1, d2, sst = _d1_d2(S, K, r, q, sigma, tau)
    Nd1, Nd2 = norm.cdf(d1), norm.cdf(d2)
    nd1 = norm.pdf(d1)
    disc_r = np.exp(-r * tau)
    disc_q = np.exp(-q * tau)

    if option == "call":
        price = S * disc_q * Nd1 - K * disc_r * Nd2
        delta = disc_q * Nd1
        theta = (-S * disc_q * nd1 * sigma / (2 * np.sqrt(tau))
                 - r * K * disc_r * Nd2 + q * S * disc_q * Nd1)
        rho = K * tau * disc_r * Nd2
        charm = (-disc_q * (nd1 * (2 * (r - q) * tau - d2 * sst)
                            / (2 * tau * sst) - q * Nd1))
    else:  # put (validated above)
        price = K * disc_r * norm.cdf(-d2) - S * disc_q * norm.cdf(-d1)
        delta = -disc_q * norm.cdf(-d1)
        theta = (-S * disc_q * nd1 * sigma / (2 * np.sqrt(tau))
                 + r * K * disc_r * norm.cdf(-d2) - q * S * disc_q * norm.cdf(-d1))
        rho = -K * tau * disc_r * norm.cdf(-d2)
        charm = (-disc_q * (nd1 * (2 * (r - q) * tau - d2 * sst)
                            / (2 * tau * sst) + q * norm.cdf(-d1)))

    # Greeks identical for call & put
    gamma = disc_q * nd1 / (S * sst)
    vega = S * disc_q * nd1 * np.sqrt(tau)
    vanna = -disc_q * nd1 * d2 / sigma
    volga = vega * d1 * d2 / sigma

    return BSMResult(price=price, delta=delta, gamma=gamma, vega=vega,
                     theta=theta, rho=rho, vanna=vanna, volga=volga,
                     charm=charm)


# ---------------------------------------------------------------------------
# Put-Call Parity check:  C - P = S*e^{-q*tau} - K*e^{-r*tau}
# ---------------------------------------------------------------------------
def put_call_parity_residual(S, K, r, q, sigma, tau) -> float:
    c = black_scholes(S, K, r, q, sigma, tau, "call").price
    p = black_scholes(S, K, r, q, sigma, tau, "put").price
    rhs = S * np.exp(-q * tau) - K * np.exp(-r * tau)
    return float(np.max(np.abs((c - p) - rhs)))


# ---------------------------------------------------------------------------
# Finite-difference Greek validator (sanity check vs analytic)
# ---------------------------------------------------------------------------
def fd_greeks(S, K, r, q, sigma, tau, h=1e-4, option="call"):
    def price(**kw):
        params = dict(S=S, K=K, r=r, q=q, sigma=sigma, tau=tau, option=option)
        params.update(kw)
        return black_scholes(**params).price

    delta = (price(S=S + h) - price(S=S - h)) / (2 * h)
    gamma = (price(S=S + h) - 2 * price() + price(S=S - h)) / h**2
    vega = (price(sigma=sigma + h) - price(sigma=sigma - h)) / (2 * h)
    theta = -(price(tau=tau + h) - price(tau=tau - h)) / (2 * h)
    rho = (price(r=r + h) - price(r=r - h)) / (2 * h)
    return dict(delta=float(delta), gamma=float(gamma), vega=float(vega),
                theta=float(theta), rho=float(rho))


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("Black-Scholes-Merton Calculator")
    print("=" * 70)
    # Default contract
    S, K, r, q, sigma, tau = 100.0, 100.0, 0.05, 0.02, 0.20, 1.0

    call = black_scholes(S, K, r, q, sigma, tau, "call")
    put = black_scholes(S, K, r, q, sigma, tau, "put")

    print(f"\nInputs:  S={S}  K={K}  r={r:.2%}  q={q:.2%}  "
          f"sigma={sigma:.2%}  tau={tau}y\n")

    fmt = "{:<8}{:>14.6f}{:>14.6f}"
    print(f"{'Greek':<8}{'Call':>14}{'Put':>14}")
    print("-" * 36)
    print(fmt.format("Price",  call.price,  put.price))
    print(fmt.format("Delta",  call.delta,  put.delta))
    print(fmt.format("Gamma",  call.gamma,  put.gamma))
    print(fmt.format("Vega",   call.vega,   put.vega))
    print(fmt.format("Theta",  call.theta,  put.theta))
    print(fmt.format("Rho",    call.rho,    put.rho))
    print(fmt.format("Vanna",  call.vanna,  put.vanna))
    print(fmt.format("Volga",  call.volga,  put.volga))
    print(fmt.format("Charm",  call.charm,  put.charm))

    # Put-call parity check
    residual = put_call_parity_residual(S, K, r, q, sigma, tau)
    print(f"\nPut-Call parity max residual: {residual:.2e}")

    # FD vs analytic for the call
    fd = fd_greeks(S, K, r, q, sigma, tau, option="call")
    print("\nFinite-difference vs analytic (Call):")
    for g in ("delta", "gamma", "vega", "theta", "rho"):
        analytic = getattr(call, g)
        print(f"  {g:<6} FD={fd[g]:+.6f}  analytic={float(analytic):+.6f}  "
              f"diff={fd[g]-float(analytic):+.2e}")

    # CDF approximation vs scipy
    print("\nA&S CDF approximation vs scipy.stats.norm.cdf:")
    for x in (-2, -1, 0, 1, 2):
        as_val = cdf_abramowitz_stegun(x)
        sp_val = float(norm.cdf(x))
        print(f"  N({x:+d})  A&S={as_val:.6f}  scipy={sp_val:.6f}  "
              f"diff={as_val-sp_val:+.2e}")
