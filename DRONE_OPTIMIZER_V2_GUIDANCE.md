# Drone Flight Time Optimizer V2: Architecture and Methods Guide

## Overview

This document provides architectural guidance for building a drone flight time optimization application with a full graphical user interface. It covers the physics models, mathematical methods, and system architecture without prescribing specific code implementations.

**Application Type:** Desktop GUI application (recommended: PyQt, Tkinter, or similar framework)

**Scope:**
- 50+ embedded airfoil profiles with AOA sweep data
- Support for 1M+ design iterations
- Four configurations: Tandem Wing, Flying Wing, Traditional, VTOL 4+1
- Pareto-optimal design selection
- Real-time progress feedback during optimization

---

## PART 1: APPLICATION ARCHITECTURE

### 1.1 Recommended Framework Options

**Desktop GUI Options:**
- PyQt6 / PySide6: Full-featured, professional appearance, good charting via PyQtGraph or matplotlib integration
- Tkinter + ttkbootstrap: Lightweight, ships with Python, modern themes available
- Dear PyGui: GPU-accelerated, good for data visualization, immediate-mode GUI

**Hybrid Option:**
- Streamlit or Gradio: Web-based UI, runs locally, simpler to build but less control

### 1.2 Application Structure

```
Main Window
├── Menu Bar (File, Settings, Help)
├── Toolbar (Run/Calculate, Stop, Export, Reset)
├── Splitter Layout
│   ├── Left Panel: Configuration Input (collapsible)
│   │   ├── Mode Toggle (Optimization / Calculation)
│   │   ├── [Optimization Mode]
│   │   │   ├── Aircraft Selection (multi-select)
│   │   │   ├── Optimization Settings
│   │   │   ├── Constraints
│   │   │   ├── Battery Range Config
│   │   │   └── Airfoil Selection
│   │   └── [Calculation Mode]
│   │       ├── Configuration Type (single-select)
│   │       ├── Wing Geometry
│   │       ├── Config-Specific Inputs
│   │       ├── Fuselage Geometry
│   │       ├── Battery Config
│   │       ├── Propulsion Inputs
│   │       ├── Flight Conditions
│   │       └── Mass Overrides
│   └── Right Panel: Results Dashboard
│       ├── Tab Widget
│       │   ├── Summary Tab
│       │   ├── Pareto Tab (optimization only)
│       │   ├── Performance Tab
│       │   ├── Drag Breakdown Tab
│       │   ├── Stability Tab
│       │   ├── Structural Tab
│       │   ├── Propulsion Tab
│       │   ├── Mass Breakdown Tab
│       │   └── Geometry Tab
│       └── Winner Banner (optimization) / Summary Card (calculation)
└── Status Bar (progress, iteration count, elapsed time)
```

### 1.3 Input Panel Components

**Aircraft Configuration Section:**
- Checkbox group for enabling/disabling each configuration type
- Visual indicators showing which are active

**Optimization Resolution Section:**
- Slider: Points per variable (5-50)
- Computed display: Total iterations based on current settings
- Preset buttons: Quick (100k), Standard (1M), Thorough (10M)

**Design Constraints Section:**
- Numeric inputs with validation:
  - Max span: 0.5-2.0 m, default 1.0 m
  - Max length: 0.5-2.0 m, default 1.0 m
  - Min stall speed: 8-20 mph, default 12.5 mph
  - VTOL stall speed: 15-30 mph, default 20 mph
  - Cruise speed: 20-60 mph, default 35 mph
  - Min T/W ratio: 1.0-3.0, default 1.5

**Battery Configuration Section:**
- Spinboxes for series range (min/max, 1-8S)
- Spinboxes for parallel range (min/max, 1-6P)

**Airfoil Selection Section:**
- Tree view or grouped list with checkboxes
- Categories: Low Reynolds, Flying Wing/Reflex, High Lift
- Select All / Clear All buttons

### 1.4 Results Dashboard Tabs

Tabs available depend on the operating mode. Some tabs are shared, others are mode-specific.

**Tab 1 - Summary (Both Modes):**
- Optimization: Winner banner, comparison table, bar charts
- Calculation: Summary card with key metrics, pass/fail indicators

**Tab 2 - Pareto Analysis (Optimization Only):**
- Scatter plot: Flight Time vs L/D (color-coded by configuration)
- Scatter plot: Flight Time vs Weight
- Scatter plot: Range vs Cruise Power
- Interactive slider: trade-off explorer along Pareto front
- Click-to-select: clicking a point shows its full specs

**Tab 3 - Performance (Both Modes):**
- Power required vs airspeed curve
- Key speeds (stall, best endurance, best range, max)
- Climb rate vs airspeed
- Service ceiling estimate

**Tab 4 - Drag Breakdown (Both Modes):**
- Pie/doughnut chart showing drag components
- Table with exact values (N and %)
- Optimization mode: stacked bar comparing configurations

**Tab 5 - Stability (Both Modes):**
- Static margin display with visual indicator
- CG position and limits diagram
- Neutral point location
- Stability derivatives table
- Dynamic modes (short period, phugoid, dutch roll)
- Pass/fail for stability criteria

**Tab 6 - Structural (Both Modes):**
- Bending moment distribution plot
- Shear distribution plot
- Spar sizing results
- V-n diagram with current design point
- Safety margins

**Tab 7 - Propulsion (Both Modes):**
- Motor operating point (RPM, current, efficiency)
- Prop efficiency curve
- System efficiency
- Thermal analysis
- Battery discharge profile
- Thrust available vs required

**Tab 8 - Mass Breakdown (Both Modes):**
- Itemized component mass table
- Pie chart by category (structure, propulsion, avionics, battery)
- CG buildup visualization

**Tab 9 - Geometry (Both Modes):**
- Planform view (top)
- Side profile
- Front view
- Key dimensions annotated
- Optimization mode: overlay comparison of configurations

**Tab 10 - Sensitivity (Optimization Only):**
- Heatmap: flight time vs span/chord
- Line charts: parameter sweeps
- Tornado diagram: parameter influence ranking

### 1.5 Color Palette

| Element | Hex Code |
|---------|----------|
| Primary Blue | #1e40af |
| Tandem | #2E86AB |
| Flying Wing | #A23B72 |
| Traditional | #F18F01 |
| VTOL | #C73E1D |
| Background | #f8fafc |
| Cards/Panels | #ffffff |
| Text Primary | #1e293b |
| Text Muted | #64748b |
| Border | #e2e8f0 |

### 1.6 Threading Architecture

**Main Thread:** GUI only, never blocked

**Worker Thread(s):** Optimization computation
- Use QThread (PyQt) or threading module
- Emit progress signals back to main thread
- Support cancellation via flag

**Communication:**
- Progress updates: current iteration, valid count, rate (samples/sec)
- Results: emit when complete, pass data structure to main thread
- Status messages: phase changes, warnings

### 1.7 Suggested Module Structure

```
drone_optimizer/
├── main.py                 # Application entry point
├── ui/
│   ├── main_window.py      # Main window and layout
│   ├── input_panel.py      # Configuration input widgets (both modes)
│   ├── calc_input_panel.py # Calculation mode specific inputs
│   ├── results_tabs.py     # Tab widget and individual tabs
│   ├── charts.py           # Chart creation helpers
│   └── styles.py           # Color palette, stylesheets
├── core/
│   ├── airfoil_db.py       # Airfoil database and interpolation
│   ├── aerodynamics.py     # Drag, lift, efficiency calculations
│   ├── stability.py        # CG, neutral point, derivatives
│   ├── structures.py       # Bending, torsion, spar sizing
│   ├── propulsion.py       # Motor, prop, battery models
│   ├── evaluator.py        # Single design evaluation (used by both modes)
│   └── configs/            # Configuration-specific models
│       ├── tandem.py
│       ├── flying_wing.py
│       ├── traditional.py
│       └── vtol.py
├── optimization/
│   ├── sampler.py          # Sobol sequence generation
│   ├── optimizer.py        # Optimization loop orchestration
│   ├── pareto.py           # Pareto front extraction
│   └── worker.py           # Background thread wrapper
├── export/
│   ├── pdf_report.py       # PDF generation
│   ├── csv_export.py       # Spreadsheet export
│   └── geometry_export.py  # DXF/SVG output
└── data/
    ├── airfoils.json       # Embedded airfoil polar data
    └── propellers.json     # Propeller performance tables
```

### 1.8 Operating Modes

The application should support two distinct modes, selectable via toggle or radio buttons at the top of the input panel:

**Mode 1: Optimization Mode**
- Searches design space to find Pareto-optimal configurations
- Uses sampling and parallel evaluation
- Outputs multiple candidate designs ranked by objectives
- This is the default mode described throughout most of this document

**Mode 2: Calculation Mode (Single-Point Analysis)**
- User defines a specific configuration manually
- Application evaluates that exact design
- Outputs full performance breakdown for the defined aircraft
- No optimization, just direct calculation

### 1.9 Calculation Mode Input Panel

When Calculation Mode is selected, the input panel changes to show direct geometry inputs:

**Configuration Type Selection:**
- Radio buttons: Tandem, Flying Wing, Traditional, VTOL 4+1
- Only one active at a time

**Wing Geometry Inputs:**

| Parameter | Units | Typical Range |
|-----------|-------|---------------|
| Span | m | 0.5 - 2.0 |
| Root chord | m | 0.10 - 0.40 |
| Tip chord | m | 0.05 - 0.30 |
| Dihedral | deg | 0 - 10 |
| Twist (washout) | deg | 0 - 6 |
| Sweep (LE) | deg | 0 - 30 |
| Airfoil (root) | dropdown | from database |
| Airfoil (tip) | dropdown | from database |

**Tandem-Specific Inputs (when Tandem selected):**

| Parameter | Units | Description |
|-----------|-------|-------------|
| Front wing chord | m | Front wing mean chord |
| Rear wing chord | m | Rear wing mean chord |
| Stagger | m | Longitudinal separation |
| Gap | m | Vertical separation |
| Decalage | deg | Incidence difference (front - rear) |
| Area split | % | Front wing area as % of total |

**Flying Wing-Specific Inputs:**

| Parameter | Units | Description |
|-----------|-------|-------------|
| Sweep angle | deg | Leading edge sweep |
| Elevon chord ratio | % | Elevon chord as % of local chord |
| Elevon span ratio | % | Elevon span as % of semi-span |
| CG position | % MAC | For stability calculation |

**Traditional-Specific Inputs:**

| Parameter | Units | Description |
|-----------|-------|-------------|
| H-tail area | m² | Horizontal tail area |
| H-tail arm | m | Distance from wing AC to tail AC |
| V-tail area | m² | Vertical tail area |
| V-tail height | m | Vertical tail span |

**VTOL-Specific Inputs:**

| Parameter | Units | Description |
|-----------|-------|-------------|
| VTOL motor count | - | Typically 4 |
| VTOL prop diameter | m | Lifting prop diameter |
| Boom length | m | Motor arm length from CG |
| Pusher prop diameter | m | Cruise prop diameter |

**Fuselage Inputs:**

| Parameter | Units | Typical Range |
|-----------|-------|---------------|
| Length | m | 0.3 - 0.8 |
| Width | m | 0.05 - 0.15 |
| Height | m | 0.04 - 0.12 |

**Battery Inputs:**

| Parameter | Units | Options |
|-----------|-------|---------|
| Cell type | dropdown | Molicel P50B, Samsung 50E, etc. |
| Series count | S | 2 - 8 |
| Parallel count | P | 1 - 6 |

**Propulsion Inputs:**

| Parameter | Units | Description |
|-----------|-------|-------------|
| Motor Kv | RPM/V | Motor velocity constant |
| Motor Rm | Ohms | Phase resistance |
| Motor I0 | A | No-load current |
| Prop diameter | in | Cruise propeller |
| Prop pitch | in | Cruise propeller |

**Flight Condition Inputs:**

| Parameter | Units | Default |
|-----------|-------|---------|
| Cruise speed | m/s | 15.6 (35 mph) |
| Altitude | m | 0 (sea level) |
| Payload mass | kg | 0 |

**Component Mass Overrides (optional):**
- Avionics mass
- Servo mass (per servo)
- Wiring/misc mass
- Structural mass override (or let it calculate)

### 1.10 Calculation Mode Output

When the user clicks "Calculate" in this mode, the application runs a single evaluation and displays:

**Summary Card:**
- Total mass
- Flight time (estimated)
- Range
- L/D ratio
- Stall speed
- Cruise power

**Detailed Results Tabs (same tabs as optimization mode, but for single design):**

1. **Performance Tab:**
   - Power required vs speed curve
   - Best endurance speed
   - Best range speed
   - Max speed (power limited)
   - Climb rate vs speed

2. **Drag Breakdown Tab:**
   - Pie chart of drag components
   - Table with exact values (N and %)
   - Drag vs speed curve

3. **Stability Tab:**
   - CG location (calculated from component positions)
   - Neutral point location
   - Static margin (%)
   - Stability derivatives table
   - CG limits diagram
   - Pass/Fail indicators for stability criteria

4. **Structural Tab:**
   - Bending moment distribution
   - Required spar dimensions
   - Estimated structural weight
   - V-n diagram with design point marked
   - Safety margin assessment

5. **Propulsion Tab:**
   - Motor operating point (RPM, current, efficiency)
   - Prop efficiency at cruise
   - System efficiency
   - Thermal margin
   - Battery discharge profile
   - Thrust available vs required

6. **Mass Breakdown Tab:**
   - Itemized mass table
   - Pie chart by category
   - CG buildup showing each component's contribution

7. **Geometry Tab:**
   - Planform drawing (top view)
   - Side profile
   - Front view
   - Key dimensions annotated

### 1.11 Calculation Mode Validation

Before running calculation, validate inputs and warn user:

**Hard Errors (block calculation):**
- Tip chord > root chord (invalid taper)
- Negative dimensions
- Battery config impossible (0S or 0P)
- Missing required fields

**Warnings (allow calculation but flag):**
- Static margin out of recommended range
- Wing loading very high or very low
- Aspect ratio outside typical range (< 5 or > 15)
- Stall speed exceeds cruise speed
- Thrust insufficient for level flight

### 1.12 Mode Switching

- Switching from Optimization to Calculation mode should preserve any shared parameters
- "Load from Optimization" button: takes the winning design from last optimization run and populates Calculation mode inputs
- This allows user to optimize first, then tweak the winner manually

---

## PART 2: AIRFOIL DATABASE ARCHITECTURE

### 2.1 Required Airfoils (50+ profiles)

**Low Reynolds Number (Primary):**
SD7032, SD7037, SD7062, SD7080, E387, E395, E423, S1223, S7012, AG04, AG08, AG12, AG14, AG16, AG18, AG24, AG25, AG27, AG35, AG36, AG37, AG38, AG40, AG455ct, MH32, MH45, MH60, MH61, MH62, MH78, MH81, MH91, MH104, MH106, MH110, MH114, MH115, RG15, RG14, NACA 2412, NACA 4412, NACA 23012, Clark-Y, GOE 795, GOE 417A, FX 63-137, FX 60-126, FX 61-184

**Flying Wing / Reflex:**
MH45, MH60, MH61, MH78, MH104, MH106, MH110, MH114, MH115, EH 1.5/9, EH 2.0/10, HS520, HS522, S5010, S5020

### 2.2 Data Structure Per Airfoil

Each airfoil entry requires:
- Metadata: name, category, thickness ratio, camber, reflex flag
- Polar data at Reynolds numbers: 50k, 100k, 150k, 200k, 300k, 500k
- Per Reynolds: AOA array (-10 to +20 deg), Cl array, Cd array, Cm array
- Cl_max vs Reynolds lookup
- Alpha_stall vs Reynolds lookup
- Cl_alpha (lift curve slope, per degree)
- Alpha_zero_lift

### 2.3 Interpolation Methods

**Bilinear Interpolation Approach:**
1. Bracket the target Reynolds number between available data points
2. Interpolate Cl, Cd, Cm at target AOA for both bracketing Reynolds numbers
3. Use log-linear interpolation between Reynolds numbers:
   ```
   frac = ln(Re_target / Re_low) / ln(Re_high / Re_low)
   Cl = Cl_low + frac * (Cl_high - Cl_low)
   ```

**Optimal AOA Finding:**
- Sweep AOA from -5 to +15 degrees in 0.5 degree increments
- For max L/D: maximize Cl/Cd
- For max Cl: maximize Cl directly
- For design point: minimize deviation from target Cl

---

## PART 3: AERODYNAMIC MODELS

### 3.1 Effective Angle of Attack

The induced angle reduces effective AOA seen by the airfoil:

```
α_induced = CL / (π × AR × e)
α_effective = α_geometric - α_induced
```

To find geometric AOA for a target CL, iterate:
1. Initial guess from 2D: α_2D = α_0 + CL_required / Cl_α
2. Get actual Cl at this AOA from polar
3. Calculate induced AOA
4. Compute Cl error and adjust geometric AOA
5. Repeat until convergence (|error| < 0.001)

### 3.2 Drag Component Breakdown

Total drag consists of:

**Induced Drag:**
```
CDi = CL² / (π × AR × e)
Di = CDi × q × S
```

**Profile Drag (from airfoil polar):**
```
Dp = Cd_airfoil × q × S_wet
S_wet ≈ 2.05 × S_ref  (both surfaces + thickness)
```

**Fuselage Drag (Hoerner Method):**
```
Cf = 0.455 / (log₁₀(Re))^2.58  (turbulent skin friction)
Form Factor: FF = 1 + 60/FR³ + 0.0025×FR  (FR = fineness ratio)
S_wet_fuse = π × d_avg × L × 0.85
D_fuse = Cf × FF × q × S_wet + base_drag
```

**Interference Drag:**
- Wing-body: approximately 0.6% of wing reference drag
- Wing-wing (tandem): function of stagger and gap
- Tail-body: similar to wing-body

**Protuberance Drag:**
- Antennas, camera pods, stopped props (VTOL)
- Use flat plate or cylinder Cd values with frontal area

**Trim Drag:**
- Estimate as 2% of induced drag

### 3.3 Oswald Efficiency Factor

Base value depends on aspect ratio:
```
e_base = 1.78 × (1 - 0.045 × AR^0.68) - 0.64
```

Configuration corrections:
- Tandem: -0.05 to -0.10 due to interference
- Flying Wing: -0.03 due to twist requirements
- Traditional: reference value
- VTOL: -0.08 due to booms and prop wake

Taper ratio correction:
```
e_taper = 1 - 0.08 × (1 - λ)²  (optimal λ ≈ 0.4-0.5)
```

---

## PART 4: FUSELAGE AND BATTERY OPTIMIZATION

### 4.1 Battery Pack Geometry

For Molicel P50B 21700 cells:
- Diameter: 21 mm
- Length: 70 mm
- Mass: 70 g
- Capacity: 5.0 Ah
- Nominal voltage: 3.6 V
- Energy: 18 Wh

**Layout Enumeration:**
Systematically generate all possible arrangements for S×P configuration:
- Cells lengthwise (length = cell length)
- Cells vertical (height = cell length)
- Vary stacks, rows, columns

Select layout that minimizes frontal area while meeting width/height constraints.

### 4.2 Fuselage Sizing Method

**Component Volume Requirements:**
- Battery pack (from layout)
- Motor (scale with power: d ≈ 22 + 0.08×P_watts mm)
- ESC (approximately 40×25×10 mm)
- Avionics bay (approximately 60×40×h mm)
- Wall thickness: 4 mm

**Fuselage Dimensions:**
```
Length = (motor + ESC + battery + avionics + nose_taper) × margin
Width = max(component_widths) + 2×wall
Height = max(component_heights) + 2×wall
```

**Fineness Ratio Target:** 3.0-5.0 (extend length if needed)

**Weight Estimate:**
```
Shell volume = S_wet × thickness
Mass = volume × density × 1.3  (30% for ribs/structure)
```

---

## PART 5: OPTIMIZATION ENGINE

### 5.1 Sampling Strategy

**Design Variables by Configuration:**
- Common: span, chord, airfoil, battery S/P, motor selection
- Tandem: front/rear chord, stagger, gap, decalage
- Flying Wing: sweep, twist distribution, elevon chord
- Traditional: tail volume, tail arm
- VTOL: boom length, VTOL motor size, transition speed

**Sampling Method:** Sobol sequences (quasi-random, low-discrepancy)
- Better coverage than pure random
- Converges faster than grid sampling
- Rule of thumb: 1000-10000 samples per variable for good coverage

**Iteration Scaling:**
```
For N variables with P points per variable:
Grid samples = P^N
Recommended Sobol samples ≈ P × 1000 × N_configs
```

### 5.2 Constraint Filtering

Apply fast rejection filters in order of computational cost:

1. Geometric constraints (immediate):
   - Span ≤ max_span
   - Total length ≤ max_length

2. Performance constraints (require calculation):
   - Stall speed ≥ minimum
   - Thrust/weight ≥ minimum
   - Static margin within limits

3. Full evaluation only for passing designs

### 5.3 Parallel Evaluation

- Use process pool (N_cores - 1)
- Chunk size of 1000 samples for progress tracking
- Return None for constraint violations (memory efficient)
- Track evaluation rate (samples/second)

### 5.4 Pareto Front Extraction

**Non-dominated Sorting:**
Point A is dominated by B if B is better in all objectives and strictly better in at least one.

**Objectives (all maximized):**
- Flight time
- L/D ratio
- Range

**Algorithm:**
1. Extract objective matrix from valid results
2. For each point, check if dominated by any other
3. Keep non-dominated points
4. Sort by primary objective

**Pareto Metrics:**
- Number of Pareto points
- Objective ranges and spreads
- Best design per objective

---

## PART 6: STABILITY AND CONTROL

### 6.1 Center of Gravity Calculation

**Mass Items Required:**
- Avionics (FC, receiver, GPS): typically 80g at nose
- Battery: at fuselage component position
- ESC: between battery and motor
- Motor: at fuselage rear
- Wing structure: at wing centroid
- Tail structure (if applicable)
- Payload

**CG Position:**
```
x_cg = Σ(m_i × x_i) / Σm_i
```

**Moments of Inertia (parallel axis theorem):**
```
Ixx = Σ m_i × (dy² + dz²)
Iyy = Σ m_i × (dx² + dz²)
Izz = Σ m_i × (dx² + dy²)
```

### 6.2 Neutral Point and Static Margin

**Traditional/VTOL Configuration:**
```
Tail volume ratio: V_h = (S_tail × l_tail) / (S_wing × MAC)
Downwash factor: ε ≈ 0.4 (tail sees reduced angle change)
NP shift = V_h × (a_tail/a_wing) × (1 - dε/dα) × l_tail
x_np = x_ac_wing + NP_shift
```

**Tandem Configuration:**
```
Front lift share: based on area ratio and decalage
Rear wing in front wing downwash
NP is area-weighted average of wing ACs with downwash correction
```

**Flying Wing:**
```
NP ≈ 0.25 MAC (near aerodynamic center)
Requires careful CG placement
```

**Static Margin:**
```
SM = (x_np - x_cg) / MAC × 100%
Target: 5-15% for stability with control authority
```

### 6.3 Stability Derivatives

**Longitudinal:**
- Xu: Speed damping = -2×CD×q×S / (m×V)
- Zw: Lift curve slope effect = -a×q×S / (m×V)
- Mw: Pitch stiffness = Cm_α × q×S×c / (Iyy×V)
- Mq: Pitch damping = Cm_q × q×S×c² / (2×Iyy×V)

**Lateral-Directional:**
- Lv: Dihedral effect = Cl_β × q×S×b / Ixx
- Lp: Roll damping = Cl_p × q×S×b² / (2×Ixx×V)
- Nv: Weathercock stability = Cn_β × q×S×b / Izz
- Nr: Yaw damping = Cn_r × q×S×b² / (2×Izz×V)

### 6.4 Dynamic Modes

**Short Period (pitch oscillation):**
```
ω_sp ≈ √(-Mw × V)
ζ_sp = -Mq / (2 × ω_sp)
```

**Phugoid (long-period altitude/speed):**
```
ω_ph ≈ √2 × g / V
ζ_ph ≈ CD / (√2 × CL)
```

**Dutch Roll (coupled yaw-roll):**
```
ω_dr ≈ √(Nv × V)
ζ_dr = -Nr / (2 × ω_dr)
```

---

## PART 7: CONTROL SURFACE SIZING

### 7.1 Elevator Sizing

**Requirements:**
1. Trim at all flight speeds
2. Rotate for takeoff
3. Flare for landing

**Horizontal Tail Volume:**
```
V_h = (S_h × l_h) / (S × MAC)
Target: 0.35-0.50
```

**Elevator Area:**
```
Elevator chord ratio: 25-35% of tail chord
Elevator span: 90-100% of tail span
```

**Pitch Authority Check:**
```
Cm_δe = -a_tail × τ × V_h × (1 - dε/dα)
τ ≈ 0.5 (elevator effectiveness)
```

### 7.2 Aileron Sizing

**Requirements:**
1. Achieve target roll rate (typically 60+ deg/s)
2. Counter adverse yaw
3. Crosswind control

**Geometry:**
- Span: 50-70% of outboard semi-span
- Start: 60% semi-span
- Chord: 20-30% of local wing chord

**Roll Moment Coefficient:**
```
Cl_δa = 2 × a × τ × (y_bar/b) × (c_a/c) × (b_a/b)
```

### 7.3 Rudder Sizing

**Vertical Tail Volume:**
```
V_v = (S_v × l_v) / (S × b)
Target: 0.02-0.04
```

**Rudder Chord Ratio:** 30-40% of fin chord

**Crosswind Capability:**
```
Sideslip required = atan(V_crosswind / V_approach)
Rudder deflection needed = Cn_β × β / Cn_δr
```

---

## PART 8: STRUCTURAL ANALYSIS

### 8.1 Wing Bending

**Load Distribution (elliptical assumption):**
```
L(y) = (4 × W × n) / (π × b) × √(1 - (2y/b)²)
```
where n = load factor (3.8 for FAR 23)

**Shear and Bending Moment:**
```
V(y) = ∫[y to tip] L(y) dy
M(y) = ∫[y to tip] V(y) dy
```

**Spar Sizing (rectangular spar):**
```
Spar height ≈ 0.6 × (airfoil thickness × chord)
Required width = 6×M_max / (σ_allow × h²)
```
For LW-PLA: σ_allow ≈ 25 MPa

**Tip Deflection:**
```
δ_tip = w × L⁴ / (8 × E × I)
Target: < 5% of semi-span
```

### 8.2 Torsional Analysis

**Aerodynamic Torque:**
```
T_per_span = Cm × q × c²
T_total = T_per_span × (b/2)
```

**Torsional Stiffness Requirement:**
```
GJ_required = T × L / θ_max
θ_max ≈ 2 degrees (for flutter margin)
```

### 8.3 V-n Diagram

**Key Speeds:**
- V_stall (1g): √(2W / (ρ×S×CL_max))
- V_A (maneuvering): V_stall × √n_max
- V_C (cruise): design cruise speed
- V_D (dive): 1.25 × V_C
- V_NE (never exceed): V_D

**Load Factor Limits:**
- Positive: +3.8 (FAR 23)
- Negative: -1.5 (FAR 23)

**Gust Loads:**
```
n_gust = 1 + (ρ × V × a × K_g × U_de) / (2 × W/S)
K_g = gust alleviation factor
U_de = derived gust velocity
```

---

## PART 9: PROPULSION SYSTEM

### 9.1 Propeller Performance

**Advance Ratio:**
```
J = V / (n × D)
where n = rev/s, D = diameter
```

**Thrust and Power:**
```
T = CT × ρ × n² × D⁴
P = CP × ρ × n³ × D⁵
η = (T × V) / P = J × CT / CP
```

Store CT, CP, η tables vs J for each propeller.

### 9.2 Motor-Propeller Matching

**Motor Model:**
```
Back EMF = RPM / Kv
Current = (V_batt - Back_EMF) / R_m
Torque = (I - I_0) / Kv × (60/2π)
```

**Operating Point:** Find RPM where motor torque = propeller torque

Use root-finding (Brent's method) to solve torque balance equation.

### 9.3 Slipstream Effects

**Slipstream Velocity (momentum theory):**
```
V_slip = V × (1 + √(1 + 2T/(ρ×A×V²))) / 2
```

**Dynamic Pressure Ratio:**
```
q_ratio = (V_slip / V)²
```

**Wing Effect:**
- Increased lift and drag on portion in slipstream
- Span fraction affected = D_slip / b

### 9.4 Motor Thermal Model

**Thermal Resistances:**
- Winding to case: ~8 C/W
- Case to ambient (natural): ~25 C/W
- Case to ambient (forced): ~10 C/W

**Steady State Temperature:**
```
T_winding = T_ambient + Losses × R_total
Losses = P_electrical - P_shaft
```

**Temperature Limits:**
- Winding: 150°C (enamel wire)
- Case: 80°C (handling)

---

## PART 10: BATTERY DISCHARGE MODEL

### 10.1 Peukert Effect

Effective capacity decreases at high discharge rates:

```
C_effective = C_rated × (C_rated / I)^(k-1)
```
where k ≈ 1.05-1.10 for Li-ion

### 10.2 Voltage Sag Model

```
V_cell = V_OCV(SOC) - I × R_internal - V_polarization
```

**Open Circuit Voltage (typical Li-ion):**
- 100% SOC: 4.2V
- 80% SOC: 4.0V
- 50% SOC: 3.7V
- 20% SOC: 3.4V
- 0% SOC: 3.0V

### 10.3 Flight Time Integration

1. Start at 100% SOC
2. Calculate power required at cruise
3. Determine current draw from battery
4. Apply Peukert correction
5. Integrate SOC depletion over time
6. Stop at minimum voltage (3.3V/cell typical)

---

## PART 11: CONFIGURATION-SPECIFIC METHODS

### 11.1 Tandem Wing

**Downwash on Rear Wing:**
```
ε = (2 × CL_front) / (π × AR_front)
α_rear_effective = α_rear - ε
```

**Gap/Stagger Effects:**
- Larger gap reduces interference
- Positive stagger (front wing forward) improves efficiency
- Typical: gap = 0.5-1.0 × chord, stagger = 0.3-0.5 × span

**Lift Distribution:**
```
Front share = S_front × CL_front / (S_front × CL_front + S_rear × CL_rear)
```

### 11.2 Flying Wing

**Twist Requirements:**
- Washout needed for pitch stability (CG forward of NP)
- Typical: 3-6 degrees tip washout
- Reflex airfoils reduce required twist

**Elevon Sizing:**
Combined elevator and aileron function:
- Chord: 15-25% of wing chord
- Span: 30-50% of semi-span each side

**Yaw Control Options:**
- Split elevons (drag rudders)
- Winglets with rudders
- Differential thrust

### 11.3 VTOL 4+1

**Hover Efficiency:**
```
Figure of Merit: FM = T^1.5 / (P × √(2×ρ×A))
Typical: FM = 0.5-0.7
```

**Transition Corridor:**
Plot available thrust vs required thrust across speed range:
- Hover: VTOL motors only
- Transition: blended thrust
- Cruise: pusher motor only

**Motor-Out Analysis:**
With one VTOL motor failed:
- Remaining thrust capacity
- CG shift limits
- Control authority with 3 motors

**Stopped Prop Drag:**
```
D_prop = 0.02 × q × A_disk × N_props
```

---

## PART 12: DATA MANAGEMENT AND EXPORT

### 12.1 Internal Data Structures

**Optimization Results Object:**
- Per configuration: all valid designs, Pareto front, best per objective
- Metadata: iteration count, elapsed time, constraint settings
- Timestamps for session tracking

**Design Record:**
- Geometry parameters (span, chord, taper, etc.)
- Performance metrics (flight time, range, L/D, weight)
- Drag breakdown dictionary
- Stability data (CG, static margin, derivatives)
- Battery and propulsion specs

### 12.2 File Export Options

**Project Save (.json or .pkl):**
- Full optimization results for later reload
- All input parameters
- Allows resuming or comparing sessions

**Report Export (.pdf):**
- Summary page with winner and comparison table
- Charts embedded as images
- Detailed specs for top designs
- Use reportlab or similar library

**Data Export (.csv / .xlsx):**
- Results table with all metrics
- Pareto front points
- Sensitivity data matrices

**Geometry Export (.dxf or .svg):**
- Wing planform outline
- Fuselage profile
- For CAD import

### 12.3 Chart Rendering

**Recommended Libraries:**
- Matplotlib: Standard, good for static charts and PDF export
- PyQtGraph: Fast, good for interactive plots in PyQt
- Plotly: Interactive, can embed in reports

**Chart Data Preparation:**
- Extract arrays from results structure
- Normalize where needed for comparison charts
- Color mapping by configuration type

### 12.4 Session Management

- Auto-save results on completion
- Recent sessions list
- Compare multiple sessions side-by-side

---

## PART 13: IMPLEMENTATION PHASES

### Phase 1: Application Framework (Days 1-2)
- Set up GUI framework (PyQt6 recommended)
- Create main window layout
- Implement mode toggle (Optimization / Calculation)
- Set up tab widget for results
- Basic styling with color palette

### Phase 2: Calculation Mode Input Panel (Days 3-4)
- Build all geometry input fields
- Configuration-specific input sections (show/hide based on selection)
- Input validation with error/warning system
- Flight condition inputs
- Component mass inputs

### Phase 3: Core Physics Engine (Days 5-7)
- Airfoil database with interpolation
- Drag model with all components
- Oswald efficiency calculations
- Lift and performance calculations
- Single-design evaluator function (core of both modes)

### Phase 4: Calculation Mode Results (Days 8-9)
- Wire up Calculate button to evaluator
- Performance results display
- Drag breakdown tab
- Mass breakdown tab
- Geometry visualization

### Phase 5: Stability and Control (Days 10-12)
- CG calculation system
- Neutral point calculations
- Stability derivatives
- Control surface sizing
- Dynamic mode analysis
- Stability results tab for calculation mode

### Phase 6: Structural Analysis (Days 13-14)
- Wing bending analysis
- Spar sizing
- V-n diagram generation
- Structural results tab

### Phase 7: Propulsion and Battery (Days 15-16)
- Propeller database and interpolation
- Motor-prop matching solver
- Battery discharge model with Peukert effect
- Propulsion results tab

### Phase 8: Optimization Mode Input Panel (Days 17-18)
- Constraint inputs
- Sampling resolution controls
- Airfoil multi-select
- Battery range inputs

### Phase 9: Optimization Engine (Days 19-21)
- Sobol sampling implementation
- Worker thread for parallel evaluation
- Progress reporting to GUI
- Pareto extraction algorithm
- Cancellation support

### Phase 10: Optimization Results Display (Days 22-24)
- Winner banner
- Comparison tables and charts
- Pareto scatter plots with interaction
- Sensitivity analysis
- "Load to Calculation Mode" feature

### Phase 11: Export and Polish (Days 25-27)
- PDF report generation
- CSV/Excel export
- Project save/load
- Geometry export (DXF/SVG)
- Error handling refinement
- Final UI polish

### Phase 12: Testing and Validation (Days 28-30)
- Unit tests for physics models
- Integration testing
- Validate against known aircraft data
- Performance optimization for 1M+ iterations
- Cross-check calculation mode vs optimization mode results
- User acceptance testing

---

## APPENDIX A: KEY FORMULAS REFERENCE

### Aerodynamics
| Parameter | Formula |
|-----------|---------|
| Lift | L = CL × q × S |
| Drag | D = CD × q × S |
| Dynamic pressure | q = 0.5 × ρ × V² |
| Induced drag coeff | CDi = CL² / (π × AR × e) |
| Aspect ratio | AR = b² / S |
| Reynolds number | Re = ρ × V × c / μ |
| Stall speed | V_s = √(2W / (ρ × S × CL_max)) |

### Stability
| Parameter | Formula |
|-----------|---------|
| Static margin | SM = (x_np - x_cg) / MAC |
| Tail volume (horiz) | V_h = S_h × l_h / (S × MAC) |
| Tail volume (vert) | V_v = S_v × l_v / (S × b) |

### Propulsion
| Parameter | Formula |
|-----------|---------|
| Advance ratio | J = V / (n × D) |
| Thrust | T = CT × ρ × n² × D⁴ |
| Power | P = CP × ρ × n³ × D⁵ |
| Propeller efficiency | η = J × CT / CP |

### Structures
| Parameter | Formula |
|-----------|---------|
| Bending stress | σ = M × y / I |
| Section modulus | Z = I / y_max |
| Beam deflection | δ = w × L⁴ / (8 × E × I) |

---

## APPENDIX B: TYPICAL VALUES

### Material Properties (LW-PLA)
- Density: 500 kg/m³
- Tensile strength: 25 MPa (with safety factor)
- Elastic modulus: 1.5 GPa
- Shear modulus: 0.5 GPa

### Air Properties (Sea Level)
- Density: 1.225 kg/m³
- Kinematic viscosity: 1.5×10⁻⁵ m²/s

### Typical Design Values
- Oswald efficiency: 0.75-0.85
- Skin friction (turbulent): Cf ≈ 0.455 / (log₁₀(Re))^2.58
- Wing CL_max (clean): 1.2-1.5
- Airfoil Cl_α: 0.1 per degree
- Propeller efficiency (cruise): 0.7-0.8
- Motor efficiency: 0.80-0.88
