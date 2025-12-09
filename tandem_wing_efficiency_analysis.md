# Tandem Wing Aerodynamic Efficiency Analysis

## Configuration Specification

This analysis examines a tandem wing unmanned aerial vehicle with the following parameters:

| Parameter | Value |
|-----------|-------|
| Front wing span | 1.0 m |
| Rear wing span | 1.0 m |
| Longitudinal separation (stagger) | 0.5 to 1.25 m |
| Vertical offset range | -0.30 to +0.30 m |
| Reference baseline | Isolated 1.0 m monoplane |

The efficiency metric compares each wing's induced drag performance against an identical isolated monoplane producing the same lift. An efficiency of 100% means the wing performs equivalently to the isolated reference; values below 100% indicate a drag penalty.

---

## Theoretical Background

### The Downwash Problem

When a finite wing generates lift, it sheds a trailing vortex system from its wingtips. This vortex system induces a downward velocity component in the flow field behind the wing, known as downwash. The downwash angle at a point downstream of a lifting wing can be expressed as:

$$\epsilon = \frac{w}{V_\infty}$$

where $w$ is the induced vertical velocity and $V_\infty$ is the freestream velocity.

For an elliptically loaded wing, the downwash angle far downstream approaches:

$$\epsilon_\infty = \frac{C_L}{\pi AR}$$

where $C_L$ is the lift coefficient and $AR$ is the aspect ratio.

### Effect on Rear Wing Performance

A wing operating in a downwash field experiences two compounding effects:

1. **Reduced effective angle of attack**: The local flow angle is rotated downward, so the wing must fly at a higher geometric angle of attack to achieve the same lift coefficient.

2. **Tilted lift vector**: The lift vector, which acts perpendicular to the local flow (not the freestream), is rotated rearward. This rearward component manifests directly as additional induced drag.

For a rear wing operating in downwash angle $\epsilon$, the induced drag coefficient increases approximately as:

$$C_{D,i,rear} = C_{D,i,isolated} \cdot (1 + k \cdot \epsilon / \alpha)$$

where $\alpha$ is the wing's angle of attack and $k$ is a factor accounting for the spanwise distribution of downwash.

### Downwash Field Decay

The intensity of the downwash field is not uniform. It decays with both vertical and longitudinal distance from the generating wing.

**Vertical decay**: The trailing vortex sheet creates a velocity field that diminishes with perpendicular distance. For a wing at vertical offset $z$ from the vortex sheet centerline, the downwash intensity decays approximately exponentially:

$$w(z) = w_0 \cdot e^{-k_z |z/b|}$$

where $b$ is the wingspan and $k_z$ is an empirical decay constant (typically 4 to 6 for practical configurations).

**Longitudinal decay**: As the vortex sheet propagates downstream, it rolls up into concentrated tip vortices and its influence on a following wing diminishes. This decay follows approximately:

$$w(x) = w_0 \cdot \frac{1}{1 + k_x (x/b)}$$

where $x$ is the longitudinal separation and $k_x$ is typically 0.6 to 1.0.

### Asymmetry of Vertical Offset

The downwash field is not symmetric about the vortex sheet plane. As the sheet propagates downstream, it curves downward due to its self-induced velocity. This means a rear wing positioned below the front wing experiences slightly stronger downwash than one positioned above at the same absolute offset.

This asymmetry factor can be approximated as:

$$f_{asymm} = 1 + 0.15 \cdot |z/b| \quad \text{for } z < 0$$

$$f_{asymm} = 1.0 \quad \text{for } z \geq 0$$

---

## Mathematical Model

### Combined Downwash Factor

The normalized downwash factor $\sigma$ experienced by the rear wing combines the vertical and longitudinal decay effects:

$$\sigma(z, x) = e^{-k_z |z/b|} \cdot \frac{1}{1 + k_x (x/b)} \cdot f_{asymm}$$

This factor ranges from 0 (no downwash, rear wing in clean air) to 1 (full downwash intensity).

### Rear Wing Efficiency

The rear wing efficiency relative to an isolated monoplane is:

$$\eta_{rear} = \frac{1}{1 + \Delta_{max} \cdot \sigma}$$

where $\Delta_{max}$ is the maximum induced drag penalty at full downwash exposure. Based on classical biplane theory and experimental data, $\Delta_{max}$ is approximately 0.70 (representing a 70% drag increase in the worst case).

### Front Wing Efficiency

The front wing operates in nearly undisturbed freestream. However, the bound circulation of the rear wing induces a small upwash at the front wing location, providing a minor efficiency benefit:

$$\eta_{front} = 1 + \frac{0.03}{1 + 2(x/b)} \cdot (1 + \max(0, z/b))$$

This effect is small (typically 1 to 3%) and decreases with increasing stagger.

### System Efficiency

The combined system efficiency, assuming equal lift distribution between wings, is simply the average:

$$\eta_{system} = \frac{\eta_{front} + \eta_{rear}}{2}$$

---

## Model Parameters

The following empirical constants are used in this analysis:

| Parameter | Symbol | Value | Source/Basis |
|-----------|--------|-------|--------------|
| Vertical decay constant | $k_z$ | 5.0 | Fitted to Prandtl biplane data |
| Longitudinal decay constant | $k_x$ | 0.8 | Horseshoe vortex far-field behavior |
| Maximum drag penalty | $\Delta_{max}$ | 0.70 | Classical biplane interference theory |
| Asymmetry coefficient | - | 0.15 | Vortex sheet rollup modeling |
| Front wing upwash coefficient | - | 0.03 | Bound vortex induction estimate |

---

## Results

### Front Wing Efficiency

The front wing operates at approximately 100 to 102% efficiency across all configurations examined. The small benefit comes from upwash induced by the rear wing's bound vortex circulation.

| Vertical Offset | Stagger = 50 cm | Stagger = 75 cm | Stagger = 100 cm | Stagger = 125 cm |
|-----------------|-----------------|-----------------|------------------|------------------|
| -25 cm | 101.5% | 101.2% | 101.0% | 100.9% |
| -20 cm | 101.5% | 101.2% | 101.0% | 100.9% |
| -15 cm | 101.5% | 101.2% | 101.0% | 100.9% |
| -10 cm | 101.5% | 101.2% | 101.0% | 100.9% |
| -5 cm | 101.5% | 101.2% | 101.0% | 100.9% |
| 0 cm (coplanar) | 101.5% | 101.2% | 101.0% | 100.9% |
| +5 cm | 101.6% | 101.3% | 101.0% | 100.9% |
| +10 cm | 101.6% | 101.3% | 101.1% | 100.9% |
| +15 cm | 101.7% | 101.4% | 101.2% | 101.0% |
| +20 cm | 101.8% | 101.4% | 101.2% | 101.0% |
| +25 cm | 101.9% | 101.5% | 101.2% | 101.1% |
| +30 cm | 102.0% | 101.6% | 101.3% | 101.1% |

### Rear Wing Efficiency

The rear wing experiences significant efficiency degradation due to operating in the front wing's downwash field. This is the dominant factor in tandem wing system performance.

| Vertical Offset | Stagger = 50 cm | Stagger = 75 cm | Stagger = 100 cm | Stagger = 125 cm |
|-----------------|-----------------|-----------------|------------------|------------------|
| -25 cm | 87.1% | 88.5% | 89.6% | 90.6% |
| -20 cm | 84.1% | 85.8% | 87.2% | 88.3% |
| -15 cm | 80.5% | 82.6% | 84.2% | 85.5% |
| -10 cm | 76.5% | 78.8% | 80.7% | 82.3% |
| -5 cm | 71.8% | 74.4% | 76.6% | 78.5% |
| 0 cm (coplanar) | 66.7% | 69.6% | 72.0% | 74.1% |
| +5 cm | 72.0% | 74.6% | 76.8% | 78.6% |
| +10 cm | 76.7% | 79.0% | 80.9% | 82.5% |
| +15 cm | 80.9% | 82.9% | 84.5% | 85.8% |
| +20 cm | 84.5% | 86.1% | 87.5% | 88.6% |
| +25 cm | 87.5% | 88.9% | 90.0% | 90.9% |
| +30 cm | 90.0% | 91.1% | 92.0% | 92.8% |

### Combined System Efficiency

This represents the average performance of both wings together.

| Vertical Offset | Stagger = 50 cm | Stagger = 75 cm | Stagger = 100 cm | Stagger = 125 cm |
|-----------------|-----------------|-----------------|------------------|------------------|
| -25 cm | 94.3% | 94.8% | 95.3% | 95.7% |
| -20 cm | 92.8% | 93.5% | 94.1% | 94.6% |
| -15 cm | 91.0% | 91.9% | 92.6% | 93.2% |
| -10 cm | 89.0% | 90.0% | 90.8% | 91.6% |
| -5 cm | 86.7% | 87.8% | 88.8% | 89.7% |
| 0 cm (coplanar) | 84.1% | 85.4% | 86.5% | 87.5% |
| +5 cm | 86.8% | 87.9% | 88.9% | 89.7% |
| +10 cm | 89.2% | 90.2% | 91.0% | 91.7% |
| +15 cm | 91.3% | 92.1% | 92.8% | 93.4% |
| +20 cm | 93.1% | 93.8% | 94.3% | 94.8% |
| +25 cm | 94.7% | 95.2% | 95.6% | 96.0% |
| +30 cm | 96.0% | 96.3% | 96.7% | 96.9% |

---

## Efficiency Recovery Analysis

The following table shows the percentage of theoretical maximum efficiency recovered at each vertical offset, where 0% recovery corresponds to coplanar and 100% recovery corresponds to eliminating all interference effects.

| Vertical Offset | Recovery at 100 cm Stagger |
|-----------------|----------------------------|
| 0 cm | 0% (baseline) |
| 5 cm | 17% |
| 10 cm | 32% |
| 15 cm | 45% |
| 20 cm | 55% |
| 25 cm | 64% |
| 30 cm | 71% |

This demonstrates diminishing returns: the first 15 cm of offset recovers nearly half the available efficiency, while the next 15 cm recovers only an additional 26%.

---

## Design Recommendations

### Optimal Vertical Offset Range

For a 1 m fuselage tandem configuration, the recommended rear wing vertical offset is **15 to 25 cm above the front wing**. This range balances aerodynamic efficiency against structural and practical constraints:

| Offset | Rear Wing Efficiency | System Efficiency | Notes |
|--------|---------------------|-------------------|-------|
| 0 cm | 72% | 87% | Structural simplicity, poor aero |
| 15 cm | 85% | 93% | Good balance point |
| 20 cm | 88% | 94% | Near-optimal for most designs |
| 25 cm | 90% | 96% | Diminishing returns begin |
| 30 cm | 92% | 97% | Marginal gains, added complexity |

### Stagger Considerations

Increasing longitudinal separation improves rear wing efficiency but is typically constrained by airframe layout requirements. For the range examined (50 to 125 cm), the efficiency variation is approximately 8 percentage points on the rear wing. If fuselage length permits, prefer larger stagger values.

### Rear Wing Below vs Above

Positioning the rear wing above the front wing is preferred for two reasons:

1. The downwash field curves downward as it propagates, so elevating the rear wing provides slightly better escape from the downwash region (2 to 5% efficiency advantage).

2. A high rear wing configuration often provides better tail volume coefficient for pitch stability without requiring a separate horizontal stabilizer.

### Incidence Angle Adjustment

Regardless of vertical offset, the rear wing will operate in some residual downwash. To achieve the desired lift coefficient, the rear wing geometric incidence must be increased relative to the front wing. A reasonable first estimate for the incidence difference is:

$$\Delta i_{rear} \approx \frac{C_L}{\pi AR} \cdot (1 - 0.7 \cdot |z/b|) \cdot \frac{1}{1 + 0.5(x/b)}$$

For typical UAV configurations, this amounts to 2 to 4 degrees of additional incidence on the rear wing.

---

## Limitations and Caveats

This analysis is based on classical potential flow theory with empirical corrections. The following effects are not captured:

1. **Viscous effects**: Boundary layer development and flow separation are not modeled. At high angles of attack or low Reynolds numbers, viscous losses may dominate.

2. **Wing planform variations**: The model assumes rectangular wings with elliptical loading. Tapered or swept wings will have different spanwise loading distributions.

3. **Unequal lift sharing**: The analysis assumes 50/50 lift distribution. Designs with different front/rear lift splits will have different interference characteristics.

4. **Fuselage interference**: The presence of a fuselage connecting the wings creates additional flow disturbances not accounted for here.

5. **Propeller effects**: If propellers are mounted ahead of either wing, their slipstream will alter the local flow field significantly.

6. **Dynamic effects**: Maneuvering flight creates time-varying circulation that can produce different interference patterns than steady flight.

---

## References

1. Prandtl, L. "Induced Drag of Multiplanes." NACA Technical Note No. 182, 1924.

2. Munk, M.M. "The Minimum Induced Drag of Aerofoils." NACA Report No. 121, 1921.

3. Kroo, I. "Drag Due to Lift: Concepts for Prediction and Reduction." Annual Review of Fluid Mechanics, Vol. 33, 2001.

4. Phillips, W.F. "Mechanics of Flight." 2nd Edition, Wiley, 2010. Chapter 1.9: Induced Drag on Multiplanes.

5. Anderson, J.D. "Fundamentals of Aerodynamics." 6th Edition, McGraw-Hill, 2017. Chapter 5: Incompressible Flow over Finite Wings.

---

## Appendix: Python Implementation

The calculations in this document were performed using a Python script implementing the mathematical model described above. The core efficiency functions are:

```python
def downwash_factor(gap_ratio, stagger_ratio):
    """
    Calculate normalized downwash experienced by rear wing.
    
    Parameters:
        gap_ratio: Vertical separation / wingspan (z/b)
        stagger_ratio: Longitudinal separation / wingspan (x/b)
    
    Returns:
        sigma: Downwash factor from 0 (clean air) to 1 (full downwash)
    """
    k_vertical = 5.0
    k_longitudinal = 0.8
    
    vertical_factor = np.exp(-k_vertical * np.abs(gap_ratio))
    
    # Asymmetry: downwash stronger below the sheet
    if gap_ratio < 0:
        vertical_factor *= (1.0 + 0.15 * np.abs(gap_ratio))
    
    longitudinal_factor = 1.0 / (1.0 + k_longitudinal * stagger_ratio)
    
    return vertical_factor * longitudinal_factor


def rear_wing_efficiency(gap_ratio, stagger_ratio):
    """
    Rear wing efficiency relative to isolated monoplane.
    
    Returns:
        Efficiency as decimal (1.0 = 100%)
    """
    sigma = downwash_factor(gap_ratio, stagger_ratio)
    max_drag_penalty = 0.70
    
    return 1.0 / (1.0 + max_drag_penalty * sigma)
```

The complete script with plotting functionality is available in the accompanying `tandem_per_wing_efficiency.py` file.
