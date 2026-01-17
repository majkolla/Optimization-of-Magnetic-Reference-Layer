# Co:Ti Composition Optimization Investigation

**Date**: 2026-01-16  
**Issue**: Optimizer converges to 100% Co for all capping materials  
**Status**: Root cause identified ✓

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Investigation Summary](#investigation-summary)
- [Key Findings](#key-findings)
- [Root Cause Analysis](#root-cause-analysis)
- [Test Results](#test-results)
- [Physics Explanation](#physics-explanation)
- [Recommendations](#recommendations)
- [Generated Test Scripts](#generated-test-scripts)

---

## Problem Statement

Running `optimize_coti_ratio.py` produces unexpected results where all three capping materials converge to **100% Co (x_coti = 1.0)**:

| Capping Material | TSF Score | x_Co | d_MRL (Ų) | d_cap (Ų) |
|------------------|-----------|------|-----------|-----------|
| MgO | 0.197 | **1.0** | 31.39 | 15.71 |
| Au | 0.185 | **1.0** | 31.19 | 19.50 |
| TiO2_rutile | 0.179 | **1.0** | 30.54 | 21.25 |

This contradicts:
- Literature values (typically 60-80% Co)
- Original fixed composition (73% Co)
- PNR physics requiring BOTH nuclear and magnetic contrast

### Initial Concerns

1. ❓ Individual cap optima not clearly shown
2. ❓ 100% Co seems physically unrealistic
3. ❓ Possible bug in `physics/magnetic_sld.py`

---

## Investigation Summary

### Phase 1: Magnetic SLD Verification ✓

**Test**: `test_magnetic_sld.py`

Verified that `coti_magnetic_sld()` function works correctly:

```
x_Co    Magnetic SLD (×10⁻⁶ Ų⁻²)   Notes
================================================
0.00    0.000                      (Pure Ti - non-magnetic)
0.73    2.589                      (Original - 228% higher than old!)
1.00    4.119                      (Pure Co - maximum magnetic SLD)
```

**Key findings**:
- ✅ Function is monotonically increasing (derivative: 2.59-6.54)
- ✅ Pure Ti gives 0.0 (correct - Ti is non-magnetic)
- ✅ Pure Co gives maximum magnetic SLD (correct physics)
- ✅ New physical model gives **2.589** vs old linear's **0.788** at x=0.73 (228% higher!)

**Conclusion**: `magnetic_sld.py` is working correctly. The physics is sound.

---

### Phase 2: Nuclear vs Magnetic Trade-off 🔍

**Test**: `test_nuclear_magnetic_tradeoff.py`

The critical insight: **Co and Ti have OPPOSITE-SIGN nuclear SLDs!**

```python
# Material properties
rho_n_Co = +1.21  # Positive
rho_n_Ti = -1.94  # NEGATIVE!
rho_n_Si = +2.07  # Substrate

# Linear mixing
rho_n_mrl = x_co * 1.21 + (1 - x_co) * (-1.94)
```

**Nuclear vs Magnetic SLD at key compositions**:

| x_Co | Nuclear SLD | Magnetic SLD | Notes |
|------|-------------|--------------|-------|
| 0.00 | -1.94 | 0.00 | Pure Ti: negative nuclear, no magnetic |
| 0.73 | **+0.36** | 2.59 | Original: near-zero nuclear (excellent!) |
| 1.00 | +1.21 | 4.12 | Pure Co: high nuclear mismatch |

**Spin-dependent SLDs**:

| x_Co | Spin-Up (ρ_n + ρ_m) | Spin-Down (ρ_n - ρ_m) |
|------|---------------------|------------------------|
| 0.73 | +2.95 | -2.23 |
| 1.00 | +5.33 | -2.91 |

**Nuclear contrast with Si substrate (ρ_Si = +2.07)**:

| x_Co | Contrast (Spin-Up) | Contrast (Spin-Down) | Average |
|------|--------------------|----------------------|---------|
| 0.73 | **0.88** | 4.30 | 2.59 | ← Excellent match! |
| 1.00 | 3.26 | 4.98 | 4.12 | ← Poor match |

**Critical realization**:  
At 73% Co, the nuclear SLD (+0.36) is very close to zero, providing:
- Excellent matching with various SOI nuclear SLDs
- Good contrast with Si substrate
- Still strong magnetic moment (2.59)

This is a **"Goldilocks" composition** - balanced for ALL contrast mechanisms!

---

### Phase 3: Direct TSF Calculation 🎯

**Test**: `test_tsf_vs_composition.py`

**The smoking gun**: Direct TSF measurements confirm optimizer is mathematically correct!

#### Fixed Thickness Test
Using d_MRL = 31.39 Ų, d_cap = 15.71 Ų (from 100% Co optimum):

| x_Co | TSF Score | Nuclear SLD | Magnetic SLD |
|------|-----------|-------------|--------------|
| 0.00 | 0.000000 | -1.94 | 0.00 |
| 0.73 | 0.011464 | +0.36 | 2.59 |
| 1.00 | **0.012679** | +1.21 | 4.12 | ← Optimizer choice |

#### Co-optimized Thickness Test
Allowing both d_MRL and d_cap to optimize at each composition:

| x_Co | TSF Score | d_MRL (Ų) | d_cap (Ų) | Notes |
|------|-----------|-----------|-----------|-------|
| 0.00 | 0.000000 | 30.00 | 15.00 | Pure Ti (no magnetic moment) |
| 0.40 | 0.009336 | 36.53 | 18.59 | |
| 0.73 | 0.011909 | 36.91 | 16.61 | Original composition |
| 1.00 | **0.012899** | 34.11 | 20.24 | **Pure Co - 8% higher!** |

**Conclusion**: Pure Co DOES give higher TSF (0.012899 vs 0.011909). The optimizer is **mathematically correct** but **physically questionable**.

---

## Root Cause Analysis

### The TSF Formula

Current implementation in `physics/fom.py`:

```python
def tsf(foms_over_types):
    # foms_over_types: iterable of (SFM_up, SFM_down, MCF) per SOI type
    return sum(0.5 * abs(Su - Sd) + 0.5 * Mcf for (Su, Sd, Mcf) in foms_over_types)
```

**Formula**: `TSF = Σ [0.5 * |SFM_up - SFM_down| + 0.5 * MCF]`

Where:
- **SFM** (Squared Fringe Metric): `∫ |S(Q)| dQ` 
- **MCF** (Magnetic Contrast Function): `∫ |S_up - S_down| dQ`
- **S** (Sensitivity): `S = (R_sub - R_full) / (R_sub + R_full)`

### The Problem: Positive Feedback Loop

The formula gives **equal weight (0.5 each)** to:
1. Spin asymmetry: `|SFM_up - SFM_down|`
2. Magnetic contrast: `MCF`

However, **BOTH terms increase with magnetic SLD**:
- Higher ρ_m → Bigger spin splitting → Higher `|SFM_up - SFM_down|`
- Higher ρ_m → Bigger MCF

This creates a **positive feedback loop** that favors maximum magnetic SLD, regardless of nuclear contrast optimization!

### What's Missing?

Real PNR experiments need:
1. ✅ **Nuclear contrast** MRL ↔ substrate (for base reflectivity)
2. ✅ **Nuclear contrast** MRL ↔ SOI (for sensitivity to SOI)
3. ✅ **Magnetic contrast** spin-up ↔ spin-down (for magnetic info)

Current TSF formula strongly emphasizes #3, but under-weights #1 and #2.

### Why 73% Co Makes Physical Sense

The 73% composition creates:
- Nuclear SLD = +0.36 (near zero → flexible matching)
- Magnetic SLD = 2.59 (strong magnetic signal)
- **Balanced trade-off** between nuclear and magnetic requirements

Pure Co creates:
- Nuclear SLD = +1.21 (fixed value → poor matching flexibility)
- Magnetic SLD = 4.12 (maximum)
- **Imbalanced** - maximizes one at expense of the other

---

## Physics Explanation

### Understanding Nuclear SLD Mixing

Co-Ti alloys have a special property:

```
Co: ρ_n = +1.21 × 10⁻⁶ Ų⁻²  (positive)
Ti: ρ_n = -1.94 × 10⁻⁶ Ų⁻²  (NEGATIVE!)

Linear mixing:
ρ_n(x) = x * (+1.21) + (1-x) * (-1.94)
       = x * 1.21 - (1-x) * 1.94
       = 3.15*x - 1.94
```

**Zero crossing at**: x = 1.94 / 3.15 ≈ **0.62** (62% Co)

This means:
- x < 0.62: Nuclear SLD is **negative**
- x = 0.62: Nuclear SLD is **zero** (matches vacuum!)
- x > 0.62: Nuclear SLD is **positive**
- x = 0.73: Nuclear SLD ≈ +0.36 (near zero, good flexibility)

### Understanding Magnetic SLD (Non-linear)

The new physical calculation accounts for:
1. **Density changes** as Co and Ti mix (non-linear)
2. **Atomic packing** changes with composition
3. **Magnetic moment per atom** (only Co contributes)

Result: Magnetic SLD increases non-linearly, with derivative ranging from 2.59 (at x=0) to 6.54 (at x=1).

### The Reflectivity Connection

Reflectivity depends on **total SLD contrast**:
- Spin-up: ρ_total = ρ_nuclear + ρ_magnetic
- Spin-down: ρ_total = ρ_nuclear - ρ_magnetic

At 73% Co:
- Good nuclear matching (ρ_n ≈ 0)
- Good magnetic splitting (Δρ = 2 * 2.59 = 5.18)
- **Balanced performance**

At 100% Co:
- Poor nuclear matching (ρ_n = +1.21)
- Maximum magnetic splitting (Δρ = 2 * 4.12 = 8.24)
- **Imbalanced - magnetic dominates**

---

## Recommendations

### Option 1: Modify TSF Weights ⭐ (Recommended)

Change the weighting to better balance nuclear and magnetic:

```python
# Current (may over-emphasize magnetic)
TSF = Σ [0.5 * |SFM_up - SFM_down| + 0.5 * MCF]

# Proposed (emphasizes total sensitivity)
TSF = Σ [0.7 * (SFM_up + SFM_down) + 0.3 * MCF]
```

**Rationale**: Reward good overall reflectivity (nuclear contrast) while still valuing magnetic information.

**Action needed**:
1. Research PNR literature for proper weighting
2. Test different weight combinations
3. Verify 73% Co emerges as optimal with corrected weights

### Option 2: Add Composition Constraints

Simple band-aid solution:

```python
# In optimize_coti_ratio.py
bounds_x = Bounds(0.6, 0.85)  # Limit to practical range
```

**Pros**: Immediately constrains to realistic values  
**Cons**: Doesn't fix underlying physics issue

### Option 3: Multi-Objective Optimization

Explicitly optimize multiple objectives:
1. Total sensitivity (nuclear + magnetic)
2. Magnetic contrast (spin asymmetry)
3. Composition practicality

Use Pareto optimization to explore trade-offs.

### Option 4: Review Sensitivity Formula

Verify that:
```python
S = (R_sub - R_full) / (R_sub + R_full)
```

Properly accounts for nuclear contrast effects in reflectivity calculation.

**Diagnostic**: Plot R_sub and R_full vs Q for 73% vs 100% Co to visualize differences.

---

## Generated Test Scripts

Three diagnostic scripts were created in `src/Scripts/`:

### 1. `test_magnetic_sld.py`
- Tests `coti_magnetic_sld()` across full composition range
- Compares new physical calculation vs old linear approximation
- Generates plot: `magnetic_sld_analysis.png`
- **Result**: Function working correctly ✓

### 2. `test_nuclear_magnetic_tradeoff.py`
- Analyzes nuclear AND magnetic SLD together
- Shows spin-up / spin-down SLD
- Calculates contrasts with Si substrate
- Generates plot: `nuclear_vs_magnetic_tradeoff.png`
- **Result**: Revealed critical trade-off ✓

### 3. `test_tsf_vs_composition.py`
- Direct TSF calculation at different compositions
- Co-optimizes thicknesses for fair comparison
- **Result**: Confirmed 100% Co has higher TSF ✓

All scripts can be run with:
```bash
cd src/Scripts
../../.venv/bin/python test_<name>.py
```

---

## Next Steps

### Immediate Actions

1. **Literature Review**: Check PNR papers for TSF formula weights
   - Anton Devishvili's papers?
   - GenX documentation?
   - Other MRL optimization papers?

2. **Consult Experimentalist**: Ask about practical Co:Ti composition ranges
   - Film stability constraints?
   - Oxidation resistance?
   - Grain structure requirements?

3. **Test Modified TSF**: Implement and test different weighting schemes
   ```python
   # Try multiple formulations
   TSF_v1 = 0.7 * (SFM_up + SFM_down) + 0.3 * MCF
   TSF_v2 = 0.6 * (SFM_up + SFM_down) + 0.4 * MCF
   # etc.
   ```

4. **Reflectivity Analysis**: Create plots showing R vs Q for different compositions

### Long-term Considerations

- Document the "correct" TSF formula once determined
- Update `physics/fom.py` with proper physics justification
- Add composition constraints as safety check
- Consider multi-objective framework for future work

---

## Summary

### What We Found

1. ✅ `physics/magnetic_sld.py` is **correct** - new calculation is 228% higher at x=0.73
2. ✅ Optimizer is **mathematically correct** - pure Co does give higher TSF (0.012899 vs 0.011909)
3. ❌ TSF formula **weighting is questionable** - creates positive feedback loop favoring maximum magnetic SLD
4. ✅ **Nuclear vs magnetic trade-off exists** - 73% Co balances both, pure Co maximizes only magnetic

### The Core Issue

**The TSF formula doesn't properly weight the importance of nuclear contrast.** By giving equal weight to magnetic-dominated terms, it creates a positive feedback loop that always favors maximum Co content, ignoring the need for good nuclear matching.

### The Solution

**Most likely**: Adjust TSF weights to better reflect PNR physics  
**Quick fix**: Add composition constraints (60-85% Co)  
**Long-term**: Develop proper multi-objective framework

---

**Investigation complete** ✓  
**Root cause identified** ✓  
**Recommendations provided** ✓
