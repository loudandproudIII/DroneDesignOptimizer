# Drone Flight Time Optimizer V2: Standalone Tool Build Instructions

## Overview

Build a standalone, single-file Python tool that generates an interactive HTML interface for drone flight time optimization. The tool will feature a configuration input panel and a results dashboard similar to the original chat's HTML output.

**Key Requirements:**
- Single Python file that outputs an interactive HTML file
- Input UI for all optimization parameters
- Results dashboard with Pareto visualization and configuration comparisons
- 50+ airfoil profiles with AOA sweep data embedded
- Support for 1M+ design iterations
- All four drone configurations: Tandem, Flying Wing, Traditional, VTOL 4+1

---

## PART 1: USER INTERFACE SPECIFICATION

### 1.1 Input Panel (Configuration Tab)

The HTML output should include a collapsible input panel at the top allowing users to configure the optimization before running (or to re-run with different parameters).

**Design Space Controls:**

```html
<div class="config-panel">
    <h2>Optimization Configuration</h2>
    
    <!-- Plane Type Selection -->
    <div class="config-section">
        <h3>Aircraft Configurations</h3>
        <div class="checkbox-group">
            <label><input type="checkbox" id="cfg-tandem" checked> Tandem Wing</label>
            <label><input type="checkbox" id="cfg-flying" checked> Flying Wing</label>
            <label><input type="checkbox" id="cfg-traditional" checked> Traditional</label>
            <label><input type="checkbox" id="cfg-vtol" checked> VTOL 4+1</label>
        </div>
    </div>
    
    <!-- Sampling Resolution -->
    <div class="config-section">
        <h3>Optimization Resolution</h3>
        <div class="slider-group">
            <label>Points Per Variable: <span id="ppv-display">10</span></label>
            <input type="range" id="points-per-var" min="5" max="50" value="10">
            <p class="hint">Total iterations: <span id="total-iterations">1,000,000</span></p>
        </div>
        <div class="preset-buttons">
            <button onclick="setPreset('quick')">Quick (100k)</button>
            <button onclick="setPreset('standard')">Standard (1M)</button>
            <button onclick="setPreset('thorough')">Thorough (10M)</button>
        </div>
    </div>
    
    <!-- Constraint Overrides -->
    <div class="config-section">
        <h3>Design Constraints</h3>
        <div class="input-grid">
            <label>Max Span (m): <input type="number" id="max-span" value="1.0" step="0.05"></label>
            <label>Max Length (m): <input type="number" id="max-length" value="1.0" step="0.05"></label>
            <label>Min Stall Speed (mph): <input type="number" id="min-stall" value="12.5" step="0.5"></label>
            <label>VTOL Stall Speed (mph): <input type="number" id="vtol-stall" value="20" step="0.5"></label>
            <label>Cruise Speed (mph): <input type="number" id="cruise-speed" value="35" step="1"></label>
            <label>Min T/W Ratio: <input type="number" id="min-tw" value="1.5" step="0.1"></label>
        </div>
    </div>
    
    <!-- Battery Configuration -->
    <div class="config-section">
        <h3>Battery Options</h3>
        <div class="input-grid">
            <label>Min Series (S): <input type="number" id="min-series" value="2" min="1" max="8"></label>
            <label>Max Series (S): <input type="number" id="max-series" value="6" min="1" max="8"></label>
            <label>Min Parallel (P): <input type="number" id="min-parallel" value="1" min="1" max="6"></label>
            <label>Max Parallel (P): <input type="number" id="max-parallel" value="4" min="1" max="6"></label>
        </div>
    </div>
    
    <!-- Airfoil Selection -->
    <div class="config-section">
        <h3>Airfoil Database</h3>
        <select id="airfoil-set" multiple size="8">
            <optgroup label="Low Reynolds (Primary)">
                <option value="SD7032" selected>SD7032</option>
                <option value="SD7037" selected>SD7037</option>
                <option value="E387" selected>E387</option>
                <option value="AG24" selected>AG24</option>
                <option value="MH32" selected>MH32</option>
            </optgroup>
            <optgroup label="Flying Wing / Reflex">
                <option value="MH60" selected>MH60</option>
                <option value="MH78">MH78</option>
                <option value="HS520">HS520</option>
            </optgroup>
            <optgroup label="High Lift">
                <option value="S1223">S1223</option>
                <option value="FX63-137">FX 63-137</option>
            </optgroup>
        </select>
        <button onclick="selectAllAirfoils()">Select All</button>
    </div>
    
    <!-- Run Button -->
    <div class="run-section">
        <button id="run-optimization" class="run-btn">Run Optimization</button>
        <div id="progress-container" style="display:none;">
            <progress id="opt-progress" value="0" max="100"></progress>
            <span id="progress-text">0%</span>
        </div>
    </div>
</div>
```

### 1.2 Results Dashboard (Matching Original Style)

The results section should match the professional engineering dashboard from the original chat:

**Color Palette:**
- Primary Blue: #1e40af (headers, accents)
- Tandem: #2E86AB
- Flying Wing: #A23B72
- Traditional: #F18F01
- VTOL: #C73E1D
- Background: #f8fafc
- Cards: #ffffff
- Text: #1e293b (dark), #64748b (muted)

**Layout Structure:**
```html
<div class="results-container">
    <!-- Winner Banner -->
    <div class="winner-banner">
        <div class="winner-info">
            <h2>Winner: <span id="winner-name">Tandem Wing</span></h2>
            <p id="winner-reason">Highest flight time within constraints</p>
        </div>
        <div class="winner-stats">
            <div class="stat"><span class="value" id="win-time">145.2</span><span class="label">min</span></div>
            <div class="stat"><span class="value" id="win-range">136.4</span><span class="label">km</span></div>
            <div class="stat"><span class="value" id="win-ld">10.2</span><span class="label">L/D</span></div>
        </div>
    </div>
    
    <!-- Tab Navigation -->
    <div class="tabs">
        <button class="tab active" data-tab="summary">Results Summary</button>
        <button class="tab" data-tab="pareto">Pareto Analysis</button>
        <button class="tab" data-tab="configs">Configuration Details</button>
        <button class="tab" data-tab="drag">Drag Breakdown</button>
        <button class="tab" data-tab="sensitivity">Sensitivity</button>
    </div>
    
    <!-- Tab Content -->
    <div class="tab-content" id="tab-summary">
        <!-- Results table -->
        <!-- Comparison charts -->
    </div>
    
    <div class="tab-content" id="tab-pareto" style="display:none;">
        <!-- 3D Pareto scatter -->
        <!-- 2D projections -->
    </div>
    
    <!-- ... other tabs ... -->
</div>
```

### 1.3 Required Chart Types

Using Chart.js (CDN loaded), implement these visualizations:

1. **Results Summary Tab:**
   - Horizontal bar chart: Flight time comparison (all configs)
   - Grouped bar chart: Key metrics comparison (time, range, L/D, weight)
   - Results table with sortable columns

2. **Pareto Analysis Tab:**
   - Scatter plot: Flight Time vs L/D (color by config)
   - Scatter plot: Flight Time vs Weight
   - Scatter plot: Range vs Cruise Power
   - Slider to explore Pareto front trade-offs

3. **Configuration Details Tab:**
   - Spec cards for each configuration (matching original style)
   - Optimal geometry diagrams (SVG)
   - Component selection details

4. **Drag Breakdown Tab:**
   - Doughnut chart per configuration showing drag components
   - Stacked bar comparing drag sources across configs
   - Table with exact values

5. **Sensitivity Tab:**
   - Heatmap: Flight time sensitivity to span/chord
   - Line charts: Parameter sweeps
   - Tornado diagram: Most influential parameters

### 1.4 CSS Styling (Match Original)

```css
/* Base styles matching original dashboard */
:root {
    --primary: #1e40af;
    --primary-light: #3b82f6;
    --tandem: #2E86AB;
    --flying: #A23B72;
    --traditional: #F18F01;
    --vtol: #C73E1D;
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
}

header h1 {
    color: var(--primary);
    font-size: 2em;
    margin-bottom: 8px;
}

header .subtitle {
    color: var(--text-muted);
    font-size: 1.1em;
}

/* Winner banner */
.winner-banner {
    background: linear-gradient(135deg, #065f46 0%, #047857 100%);
    color: white;
    padding: 25px 35px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(4, 120, 87, 0.3);
}

.winner-stats {
    display: flex;
    gap: 40px;
}

.winner-stats .stat {
    text-align: center;
}

.winner-stats .value {
    font-size: 2.2em;
    font-weight: 700;
    display: block;
}

.winner-stats .label {
    font-size: 0.9em;
    opacity: 0.9;
}

/* Tabs */
.tabs {
    display: flex;
    gap: 5px;
    margin-bottom: 20px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 0;
}

.tab {
    padding: 12px 24px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 0.95em;
    color: var(--text-muted);
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
}

.tab:hover {
    color: var(--primary);
}

.tab.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
    font-weight: 600;
}

/* Cards */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card h3 {
    color: var(--primary);
    margin-top: 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

/* Spec cards (config details) */
.spec-card {
    border-left: 4px solid;
    padding-left: 20px;
}

.spec-card.tandem { border-color: var(--tandem); }
.spec-card.flying { border-color: var(--flying); }
.spec-card.traditional { border-color: var(--traditional); }
.spec-card.vtol { border-color: var(--vtol); }

.spec-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.spec-item:last-child {
    border-bottom: none;
}

.spec-label {
    color: var(--text-muted);
}

.spec-value {
    font-weight: 600;
    font-family: 'SF Mono', Monaco, monospace;
}

/* Results table */
.results-table {
    width: 100%;
    border-collapse: collapse;
}

.results-table th {
    background: var(--bg);
    padding: 12px;
    text-align: left;
    font-weight: 600;
    color: var(--text-muted);
    border-bottom: 2px solid var(--border);
}

.results-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border);
}

.results-table tr:hover {
    background: var(--bg);
}

/* Config panel (input section) */
.config-panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 30px;
}

.config-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.config-section:last-of-type {
    border-bottom: none;
    margin-bottom: 0;
}

.config-section h3 {
    color: var(--primary);
    font-size: 1.1em;
    margin-bottom: 15px;
}

.input-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
}

.input-grid label {
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 0.9em;
    color: var(--text-muted);
}

.input-grid input {
    padding: 8px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 1em;
}

.checkbox-group {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.checkbox-group label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.run-btn {
    background: var(--primary);
    color: white;
    border: none;
    padding: 14px 40px;
    border-radius: 8px;
    font-size: 1.1em;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.run-btn:hover {
    background: var(--primary-light);
}

/* Chart containers */
.chart-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.chart-container {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    min-height: 300px;
}

/* Constraints bar */
.constraints-bar {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 20px;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9em;
    margin-top: 30px;
}

.constraints-bar span {
    margin: 0 15px;
    color: var(--text);
}

/* Slider styling */
input[type="range"] {
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: var(--border);
    outline: none;
    -webkit-appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--primary);
    cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
    .winner-banner {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }
    
    .chart-grid {
        grid-template-columns: 1fr;
    }
    
    .tabs {
        flex-wrap: wrap;
    }
}
```

---

## PART 2: AIRFOIL DATABASE (EMBEDDED JSON)

### 2.1 Required Airfoils

Embed polar data for these airfoils with AOA sweeps from -10 to +20 degrees at Reynolds numbers [50000, 100000, 150000, 200000, 300000, 500000]:

**Low Reynolds Number (Primary):**
- SD7032, SD7037, SD7062, SD7080
- E387, E395, E423
- S1223, S7012
- AG04, AG08, AG12, AG14, AG16, AG18, AG24, AG25, AG27, AG35, AG36, AG37, AG38, AG40, AG455ct
- MH32, MH45, MH60, MH61, MH62, MH78, MH81, MH91, MH104, MH106, MH110, MH114, MH115
- RG15, RG14
- NACA 2412, NACA 4412, NACA 23012
- Clark-Y
- GOE 795, GOE 417A
- FX 63-137, FX 60-126, FX 61-184

**Flying Wing / Reflex:**
- MH45, MH60, MH61, MH78, MH104, MH106, MH110, MH114, MH115
- EH 1.5/9, EH 2.0/10
- HS520, HS522
- S5010, S5020

### 2.2 Data Structure

```python
AIRFOIL_DATABASE = {
    "SD7032": {
        "name": "Selig-Donovan SD7032",
        "category": "low_reynolds",
        "thickness": 0.10,
        "camber": 0.024,
        "reflex": False,
        "polars": {
            50000: {
                "alpha": [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                "cl": [...],  # 31 values
                "cd": [...],  # 31 values
                "cm": [...]   # 31 values
            },
            100000: {...},
            150000: {...},
            200000: {...},
            300000: {...},
            500000: {...}
        },
        "cl_max": {50000: 1.15, 100000: 1.25, 150000: 1.30, 200000: 1.35, 300000: 1.40, 500000: 1.42},
        "alpha_stall": {50000: 11, 100000: 12, 150000: 12, 200000: 13, 300000: 13, 500000: 14},
        "cl_alpha": 0.098,  # per degree
        "alpha_zero_lift": -3.0
    },
    # ... 50+ more airfoils
}
```

### 2.3 Interpolation Functions

```python
def interpolate_airfoil(airfoil_name: str, alpha_deg: float, reynolds: float) -> tuple:
    """
    Get Cl, Cd, Cm at arbitrary AOA and Reynolds number.
    Uses bilinear interpolation.
    
    Returns: (cl, cd, cm)
    """
    af = AIRFOIL_DATABASE[airfoil_name]
    polars = af['polars']
    
    # Get bracketing Reynolds numbers
    re_keys = sorted(polars.keys())
    re_low = max([r for r in re_keys if r <= reynolds], default=re_keys[0])
    re_high = min([r for r in re_keys if r >= reynolds], default=re_keys[-1])
    
    def interp_at_re(re):
        p = polars[re]
        cl = np.interp(alpha_deg, p['alpha'], p['cl'])
        cd = np.interp(alpha_deg, p['alpha'], p['cd'])
        cm = np.interp(alpha_deg, p['alpha'], p['cm'])
        return cl, cd, cm
    
    if re_low == re_high:
        return interp_at_re(re_low)
    
    # Log-linear interpolation between Reynolds numbers
    cl_low, cd_low, cm_low = interp_at_re(re_low)
    cl_high, cd_high, cm_high = interp_at_re(re_high)
    
    frac = np.log(reynolds / re_low) / np.log(re_high / re_low)
    
    cl = cl_low + frac * (cl_high - cl_low)
    cd = cd_low + frac * (cd_high - cd_low)
    cm = cm_low + frac * (cm_high - cm_low)
    
    return cl, cd, cm


def find_optimal_aoa(airfoil_name: str, reynolds: float, target: str = 'max_ld') -> tuple:
    """
    Find optimal angle of attack for given objective.
    
    Args:
        target: 'max_ld' (max L/D), 'max_cl' (max lift), 'design' (design Cl)
    
    Returns: (optimal_alpha, cl, cd, ld_ratio)
    """
    af = AIRFOIL_DATABASE[airfoil_name]
    
    best_alpha = 0
    best_metric = -np.inf
    best_cl, best_cd = 0, 1
    
    for alpha in np.arange(-5, 15, 0.5):
        cl, cd, cm = interpolate_airfoil(airfoil_name, alpha, reynolds)
        
        if cd <= 0:
            continue
            
        if target == 'max_ld':
            metric = cl / cd
        elif target == 'max_cl':
            metric = cl
        elif target == 'design':
            metric = -abs(cl - af.get('design_cl', 0.7))
        else:
            metric = cl / cd
        
        if metric > best_metric:
            best_metric = metric
            best_alpha = alpha
            best_cl = cl
            best_cd = cd
    
    return best_alpha, best_cl, best_cd, best_cl / best_cd if best_cd > 0 else 0
```

---

## PART 3: RESULTANT AOA AND COMPLETE DRAG MODEL

### 3.1 Effective Angle of Attack

```python
def calculate_effective_aoa(
    geometric_aoa_deg: float,
    cl: float,
    aspect_ratio: float,
    oswald_efficiency: float
) -> tuple:
    """
    Calculate effective AOA accounting for induced downwash.
    
    The induced angle reduces the effective AOA seen by the airfoil:
    alpha_induced = CL / (pi * AR * e)
    alpha_effective = alpha_geometric - alpha_induced
    """
    # Induced angle in radians
    alpha_i_rad = cl / (np.pi * aspect_ratio * oswald_efficiency)
    alpha_i_deg = np.degrees(alpha_i_rad)
    
    effective_aoa = geometric_aoa_deg - alpha_i_deg
    
    return effective_aoa, alpha_i_deg


def calculate_required_geometric_aoa(
    required_cl: float,
    airfoil_name: str,
    reynolds: float,
    aspect_ratio: float,
    oswald_efficiency: float,
    max_iterations: int = 20
) -> tuple:
    """
    Iteratively find the geometric AOA needed to achieve a target CL,
    accounting for the 3D downwash effect.
    
    Returns: (geometric_aoa, effective_aoa, actual_cl, cd)
    """
    af = AIRFOIL_DATABASE[airfoil_name]
    cl_alpha = af['cl_alpha']  # per degree
    alpha_0 = af['alpha_zero_lift']
    
    # Initial guess from 2D
    alpha_2d = alpha_0 + required_cl / cl_alpha
    
    for iteration in range(max_iterations):
        # Get actual Cl at this geometric AOA
        cl, cd, cm = interpolate_airfoil(airfoil_name, alpha_2d, reynolds)
        
        # Calculate induced AOA
        alpha_eff, alpha_i = calculate_effective_aoa(alpha_2d, cl, aspect_ratio, oswald_efficiency)
        
        # The effective AOA determines the 2D section Cl
        # If we need more Cl, increase geometric AOA
        cl_error = required_cl - cl
        
        if abs(cl_error) < 0.001:
            break
        
        # Adjust geometric AOA
        alpha_2d += cl_error / cl_alpha
        
        # Clamp to avoid stall
        alpha_stall = af['alpha_stall'].get(int(reynolds), 12)
        alpha_2d = min(alpha_2d, alpha_stall - 1)
    
    return alpha_2d, alpha_eff, cl, cd
```

### 3.2 Complete Drag Breakdown

```python
@dataclass
class DragComponents:
    """All drag components in Newtons"""
    # Induced (lift-dependent)
    induced: float = 0.0
    
    # Profile (airfoil)
    wing_profile: float = 0.0
    tail_profile: float = 0.0
    
    # Parasitic (form)
    fuselage: float = 0.0
    booms: float = 0.0
    landing_gear: float = 0.0
    
    # Interference
    wing_body: float = 0.0
    wing_wing: float = 0.0  # Tandem only
    tail_body: float = 0.0
    
    # Protuberance
    antennas: float = 0.0
    camera: float = 0.0
    stopped_props: float = 0.0
    
    # Trim
    trim: float = 0.0
    
    @property
    def total(self) -> float:
        return sum([
            self.induced, self.wing_profile, self.tail_profile,
            self.fuselage, self.booms, self.landing_gear,
            self.wing_body, self.wing_wing, self.tail_body,
            self.antennas, self.camera, self.stopped_props,
            self.trim
        ])
    
    @property
    def breakdown_dict(self) -> dict:
        return {
            'Induced': self.induced,
            'Wing Profile': self.wing_profile,
            'Tail Profile': self.tail_profile,
            'Fuselage': self.fuselage,
            'Booms': self.booms,
            'Interference': self.wing_body + self.wing_wing + self.tail_body,
            'Protuberance': self.antennas + self.camera + self.stopped_props,
            'Trim': self.trim
        }


def calculate_induced_drag(
    cl: float,
    wing_area: float,
    span: float,
    oswald_e: float,
    dynamic_pressure: float
) -> float:
    """
    CDi = CL^2 / (pi * AR * e)
    Di = CDi * q * S
    """
    ar = span**2 / wing_area
    cdi = cl**2 / (np.pi * ar * oswald_e)
    return cdi * dynamic_pressure * wing_area


def calculate_profile_drag(
    airfoil_name: str,
    alpha: float,
    reynolds: float,
    wetted_area: float,
    dynamic_pressure: float
) -> float:
    """
    Profile drag from airfoil polar data.
    Dp = Cd * q * S_wet
    """
    cl, cd, cm = interpolate_airfoil(airfoil_name, alpha, reynolds)
    return cd * dynamic_pressure * wetted_area


def calculate_fuselage_drag(
    length: float,
    width: float,
    height: float,
    velocity: float,
    dynamic_pressure: float
) -> float:
    """
    Fuselage drag using Hoerner method.
    """
    # Reynolds number
    nu = 1.5e-5
    re = velocity * length / nu
    
    # Skin friction (turbulent)
    cf = 0.455 / (np.log10(max(re, 1000)))**2.58
    
    # Form factor
    fineness = length / ((width + height) / 2)
    ff = 1 + 60/fineness**3 + 0.0025*fineness
    
    # Wetted area (elliptical cross-section approximation)
    avg_diameter = (width + height) / 2
    s_wet = np.pi * avg_diameter * length * 0.85  # 0.85 for nose/tail taper
    
    # Friction drag
    d_friction = cf * ff * dynamic_pressure * s_wet
    
    # Base drag
    frontal_area = np.pi * (width/2) * (height/2)
    cd_base = 0.029 / np.sqrt(max(cf, 0.001))
    d_base = cd_base * dynamic_pressure * frontal_area * 0.25  # Tapered tail
    
    return d_friction + d_base


def calculate_oswald_efficiency(
    aspect_ratio: float,
    taper_ratio: float = 1.0,
    sweep_deg: float = 0.0,
    config: str = 'traditional'
) -> float:
    """
    Oswald span efficiency using Nita-Scholz method with configuration corrections.
    """
    # Nita-Scholz taper factor
    f_taper = (0.0524 * taper_ratio**4 - 0.15 * taper_ratio**3 + 
               0.1659 * taper_ratio**2 - 0.0706 * taper_ratio + 0.0119)
    
    e_basic = 1 / (1 + f_taper * aspect_ratio)
    
    # Sweep correction
    sweep_rad = np.radians(sweep_deg)
    e_sweep = e_basic * np.cos(sweep_rad)**0.5
    
    # Configuration factors
    config_factors = {
        'traditional': 1.0,
        'tandem': 0.82,       # Rear wing in front wake
        'flying_wing': 0.90,  # No fuselage but tip effects
        'vtol': 0.78          # Boom interference
    }
    
    e_final = e_sweep * config_factors.get(config, 1.0) * 0.97  # Fuselage factor
    
    return np.clip(e_final, 0.50, 0.95)


def calculate_full_drag(
    config: dict,
    weight_n: float,
    velocity: float,
    config_type: str
) -> DragComponents:
    """
    Calculate complete drag breakdown for a configuration.
    
    Args:
        config: Design parameters dict
        weight_n: Aircraft weight in Newtons
        velocity: Flight velocity in m/s
        config_type: 'tandem', 'flying_wing', 'traditional', or 'vtol'
    
    Returns:
        DragComponents with all drag terms
    """
    drag = DragComponents()
    q = 0.5 * 1.225 * velocity**2  # Dynamic pressure
    
    # Wing parameters
    span = config['span']
    chord = config.get('chord', config.get('chord_front', 0.2))
    wing_area = span * chord
    if config_type == 'tandem':
        chord_rear = config.get('chord_rear', chord * 0.9)
        wing_area += span * chord_rear
    
    ar = span**2 / wing_area
    
    # Required CL for level flight
    cl_required = weight_n / (q * wing_area)
    
    # Oswald efficiency
    taper = config.get('taper_ratio', 1.0)
    sweep = config.get('sweep_deg', 0.0)
    e = calculate_oswald_efficiency(ar, taper, sweep, config_type)
    
    # Reynolds number
    nu = 1.5e-5
    re = velocity * chord / nu
    
    # Find operating AOA
    airfoil = config.get('airfoil', 'SD7032')
    geo_aoa, eff_aoa, actual_cl, cd_profile = calculate_required_geometric_aoa(
        cl_required, airfoil, re, ar, e
    )
    
    # Induced drag
    drag.induced = calculate_induced_drag(actual_cl, wing_area, span, e, q)
    
    # Wing profile drag
    s_wet_wing = 2.05 * wing_area  # Both surfaces + thickness
    drag.wing_profile = cd_profile * q * s_wet_wing
    
    # Fuselage drag
    fuse_length = config.get('fuselage_length', 0.5)
    fuse_width = config.get('fuselage_width', 0.08)
    fuse_height = config.get('fuselage_height', 0.06)
    drag.fuselage = calculate_fuselage_drag(fuse_length, fuse_width, fuse_height, velocity, q)
    
    # Tail drag (traditional and VTOL)
    if config_type in ['traditional', 'vtol']:
        h_tail_area = config.get('h_tail_area', 0.015)
        v_tail_area = config.get('v_tail_area', 0.008)
        s_wet_tail = 2.05 * (h_tail_area + v_tail_area)
        re_tail = velocity * np.sqrt(h_tail_area) / nu
        cf_tail = 0.455 / (np.log10(max(re_tail, 1000)))**2.58
        drag.tail_profile = cf_tail * 1.15 * q * s_wet_tail
    
    # Interference drag
    drag.wing_body = 0.006 * q * wing_area  # ~0.6% of wing reference
    
    # Tandem-specific
    if config_type == 'tandem':
        # Rear wing in front wing downwash
        stagger = config.get('tandem_stagger', 0.4)
        gap = config.get('tandem_gap', 0.08)
        downwash_factor = 0.02 * (1 - gap/0.2) * (1 - stagger/span)
        drag.wing_wing = downwash_factor * q * wing_area
    
    # VTOL-specific
    if config_type == 'vtol':
        # Boom drag
        boom_length = config.get('boom_length', 0.15)
        boom_diameter = config.get('boom_diameter', 0.012)
        n_booms = 4
        frontal_boom = n_booms * boom_length * boom_diameter
        drag.booms = 1.2 * q * frontal_boom  # Cylinder Cd ~ 1.2
        
        # Stopped prop drag
        vtol_prop_dia = config.get('vtol_prop_diameter', 0.15)
        n_props = 4
        prop_area = n_props * np.pi * (vtol_prop_dia/2)**2
        drag.stopped_props = 0.02 * q * prop_area
    
    # Protuberance drag estimate
    drag.antennas = 0.001 * q * 0.01  # Small antenna
    drag.camera = 0.002 * q * 0.005   # Streamlined camera pod
    
    # Trim drag (estimate 2% of induced)
    drag.trim = 0.02 * drag.induced
    
    return drag
```

---

## PART 4: FUSELAGE SIZING WITH BATTERY OPTIMIZATION

### 4.1 Battery Pack Arrangements

```python
@dataclass
class CellDimensions:
    """Molicel P50B 21700 dimensions"""
    diameter: float = 0.021   # m
    length: float = 0.070     # m
    mass: float = 0.070       # kg
    capacity_ah: float = 5.0
    nominal_voltage: float = 3.6
    energy_wh: float = 18.0


def enumerate_battery_layouts(series: int, parallel: int) -> list:
    """
    Generate all possible physical arrangements for a battery pack.
    Returns list of (layout_name, length, width, height) tuples.
    """
    cell = CellDimensions()
    total_cells = series * parallel
    layouts = []
    
    # Try cells oriented lengthwise (length = cell length)
    for stacks_high in range(1, total_cells + 1):
        if total_cells % stacks_high != 0:
            continue
        cells_per_stack = total_cells // stacks_high
        for cols in range(1, cells_per_stack + 1):
            if cells_per_stack % cols != 0:
                continue
            rows = cells_per_stack // cols
            
            pack_l = cell.length
            pack_w = cols * cell.diameter
            pack_h = rows * cell.diameter * stacks_high
            
            layouts.append({
                'orientation': 'lengthwise',
                'arrangement': f'{stacks_high}x{rows}x{cols}',
                'dims': (pack_l, pack_w, pack_h),
                'frontal_area': pack_w * pack_h
            })
    
    # Try cells oriented vertically (height = cell length)
    for layers_long in range(1, total_cells + 1):
        if total_cells % layers_long != 0:
            continue
        cells_per_layer = total_cells // layers_long
        for cols in range(1, cells_per_layer + 1):
            if cells_per_layer % cols != 0:
                continue
            rows = cells_per_layer // cols
            
            pack_l = layers_long * cell.diameter
            pack_w = cols * cell.diameter
            pack_h = cell.length
            
            layouts.append({
                'orientation': 'vertical',
                'arrangement': f'{layers_long}x{rows}x{cols}',
                'dims': (pack_l, pack_w, pack_h),
                'frontal_area': pack_w * pack_h
            })
    
    return layouts


def select_optimal_battery_layout(
    series: int,
    parallel: int,
    max_width: float = 0.12,
    max_height: float = 0.10
) -> dict:
    """
    Select battery arrangement that minimizes frontal area while fitting constraints.
    """
    layouts = enumerate_battery_layouts(series, parallel)
    
    valid_layouts = [
        l for l in layouts
        if l['dims'][1] <= max_width and l['dims'][2] <= max_height
    ]
    
    if not valid_layouts:
        # Relax constraints
        valid_layouts = layouts
    
    # Sort by frontal area (minimize drag)
    valid_layouts.sort(key=lambda x: x['frontal_area'])
    
    return valid_layouts[0] if valid_layouts else layouts[0]
```

### 4.2 Fuselage Sizing

```python
@dataclass
class FuselageDesign:
    """Complete fuselage design output"""
    length: float
    width: float
    height: float
    wetted_area: float
    frontal_area: float
    fineness_ratio: float
    battery_layout: dict
    component_positions: dict
    estimated_weight_kg: float


def design_fuselage(
    battery_series: int,
    battery_parallel: int,
    motor_power_w: float,
    avionics_volume_cm3: float = 50,
    margin: float = 1.15
) -> FuselageDesign:
    """
    Design minimum-drag fuselage to package all components.
    
    Args:
        battery_series: Number of cells in series
        battery_parallel: Number of cells in parallel
        motor_power_w: Motor power for sizing
        avionics_volume_cm3: Volume needed for flight controller, receiver, etc.
        margin: Safety margin multiplier on dimensions
    
    Returns:
        FuselageDesign with optimized geometry
    """
    cell = CellDimensions()
    
    # Get optimal battery layout
    battery_layout = select_optimal_battery_layout(battery_series, battery_parallel)
    pack_l, pack_w, pack_h = battery_layout['dims']
    
    # Motor dimensions (empirical scaling)
    motor_diameter = 0.022 + 0.008 * (motor_power_w / 100)  # ~22-38mm typical
    motor_length = 0.020 + 0.006 * (motor_power_w / 100)    # ~20-32mm typical
    
    # Avionics bay
    avionics_l = 0.06
    avionics_w = 0.04
    avionics_h = avionics_volume_cm3 / (6 * 4)  # cm to m
    
    # ESC and wiring
    esc_l = 0.04
    esc_w = 0.025
    esc_h = 0.01
    
    # Structure thickness
    wall = 0.004  # 4mm walls
    
    # Calculate fuselage dimensions
    # Length: motor + ESC + battery + avionics + nose taper
    fuse_length = (motor_length + esc_l + pack_l + avionics_l + 0.05) * margin
    
    # Width/height: max of components + walls
    fuse_width = max(pack_w, motor_diameter, avionics_w, esc_w) + 2*wall
    fuse_height = max(pack_h, motor_diameter, avionics_h, esc_h) + 2*wall
    
    fuse_width *= margin
    fuse_height *= margin
    
    # Optimize for fineness ratio (ideal 3-5)
    avg_diameter = (fuse_width + fuse_height) / 2
    fineness = fuse_length / avg_diameter
    
    # If fineness too low, extend length
    if fineness < 3:
        fuse_length = 3.5 * avg_diameter
        fineness = 3.5
    
    # Calculate areas
    frontal_area = np.pi * (fuse_width/2) * (fuse_height/2)
    wetted_area = np.pi * avg_diameter * fuse_length * 0.85
    
    # Component positions (from nose)
    positions = {
        'avionics': 0.03,
        'battery': 0.03 + avionics_l + 0.01,
        'esc': 0.03 + avionics_l + pack_l + 0.01,
        'motor': fuse_length - motor_length
    }
    
    # Weight estimate (LW-PLA shell)
    shell_thickness = 0.001  # 1mm
    shell_volume = wetted_area * shell_thickness
    fuselage_weight = shell_volume * 500 * 1.3  # 500 kg/m3 LW-PLA, 30% for ribs
    
    return FuselageDesign(
        length=fuse_length,
        width=fuse_width,
        height=fuse_height,
        wetted_area=wetted_area,
        frontal_area=frontal_area,
        fineness_ratio=fineness,
        battery_layout=battery_layout,
        component_positions=positions,
        estimated_weight_kg=fuselage_weight
    )
```

### 4.3 Iterative System Optimization

```python
def optimize_battery_fuselage_system(
    target_flight_time_min: float,
    cruise_velocity: float,
    wing_config: dict,
    config_type: str,
    max_iterations: int = 15,
    tolerance: float = 0.01
) -> dict:
    """
    Iteratively optimize battery size and fuselage together.
    
    The loop:
    1. Assume battery config
    2. Design fuselage
    3. Calculate total weight
    4. Calculate drag and power
    5. Calculate required energy for target flight time
    6. Adjust battery if needed
    7. Repeat until converged
    """
    cell = CellDimensions()
    
    # Initial guess
    battery_s = 3
    battery_p = 1
    
    history = []
    
    for iteration in range(max_iterations):
        prev_p = battery_p
        
        # Step 2: Design fuselage for current battery
        motor_power_est = 50  # Will refine
        fuselage = design_fuselage(battery_s, battery_p, motor_power_est)
        
        # Step 3: Calculate total weight
        battery_mass = battery_s * battery_p * cell.mass
        fuselage_mass = fuselage.estimated_weight_kg
        wing_mass = estimate_wing_mass(wing_config, config_type)
        motor_mass = 0.040  # Typical small motor
        avionics_mass = 0.080
        servo_mass = 0.010 * 4  # 4 servos
        
        total_mass = (battery_mass + fuselage_mass + wing_mass + 
                     motor_mass + avionics_mass + servo_mass)
        weight_n = total_mass * 9.81
        
        # Update wing config with fuselage
        full_config = {**wing_config}
        full_config['fuselage_length'] = fuselage.length
        full_config['fuselage_width'] = fuselage.width
        full_config['fuselage_height'] = fuselage.height
        
        # Step 4: Calculate drag
        drag = calculate_full_drag(full_config, weight_n, cruise_velocity, config_type)
        
        # Power required
        prop_efficiency = 0.70
        motor_efficiency = 0.85
        total_power = (drag.total * cruise_velocity) / (prop_efficiency * motor_efficiency)
        
        # Step 5: Energy for target flight time
        energy_needed_wh = total_power * (target_flight_time_min / 60)
        
        # Battery energy available
        battery_energy = battery_s * battery_p * cell.energy_wh
        usable_energy = battery_energy * 0.80  # 80% DOD
        
        # Step 6: Adjust battery
        if usable_energy < energy_needed_wh:
            # Need more cells
            cells_needed = int(np.ceil(energy_needed_wh / (cell.energy_wh * 0.80)))
            battery_p = max(1, int(np.ceil(cells_needed / battery_s)))
        elif usable_energy > energy_needed_wh * 1.3:
            # Can reduce cells (30% margin)
            cells_needed = int(np.ceil(energy_needed_wh / (cell.energy_wh * 0.80)))
            battery_p = max(1, int(np.ceil(cells_needed / battery_s)))
        
        history.append({
            'iteration': iteration,
            'battery_p': battery_p,
            'total_mass_kg': total_mass,
            'power_w': total_power,
            'energy_wh': battery_energy
        })
        
        # Check convergence
        if battery_p == prev_p:
            break
    
    # Calculate actual flight time with final config
    actual_flight_time = (usable_energy / total_power) * 60  # minutes
    
    return {
        'battery_series': battery_s,
        'battery_parallel': battery_p,
        'fuselage': fuselage,
        'total_mass_kg': total_mass,
        'cruise_power_w': total_power,
        'flight_time_min': actual_flight_time,
        'energy_wh': battery_energy,
        'iterations': len(history),
        'history': history
    }


def estimate_wing_mass(config: dict, config_type: str) -> float:
    """
    Estimate wing mass for 3D printed LW-PLA construction.
    """
    span = config['span']
    chord = config.get('chord', config.get('chord_front', 0.2))
    thickness_ratio = 0.10  # Typical
    
    # Areal density for LW-PLA wing (empirical)
    # ~120 g/m^2 for hollow wing with spar
    areal_density = 0.120  # kg/m^2
    
    wing_area = span * chord
    if config_type == 'tandem':
        chord_rear = config.get('chord_rear', chord * 0.9)
        wing_area += span * chord_rear
    
    base_mass = wing_area * areal_density
    
    # Add control surfaces (15% extra)
    # Add spar reinforcement for high AR (10% extra)
    ar = span**2 / wing_area
    ar_factor = 1 + 0.02 * max(0, ar - 5)
    
    return base_mass * 1.15 * ar_factor
```

---

## PART 5: HIGH-THROUGHPUT OPTIMIZATION ENGINE

### 5.1 Sampling Strategy

```python
from scipy.stats import qmc
import numpy as np

def create_design_sampler(n_samples: int, n_vars: int, method: str = 'sobol') -> np.ndarray:
    """
    Generate quasi-random samples for efficient design space exploration.
    
    Methods:
    - sobol: Best for high-dimensional, deterministic
    - halton: Good balance of coverage
    - lhs: Latin Hypercube, good for smaller sample sizes
    """
    if method == 'sobol':
        sampler = qmc.Sobol(d=n_vars, scramble=True)
        # Sobol needs power of 2 samples
        n_sobol = 2 ** int(np.ceil(np.log2(n_samples)))
        samples = sampler.random(n_sobol)[:n_samples]
    elif method == 'halton':
        sampler = qmc.Halton(d=n_vars, scramble=True)
        samples = sampler.random(n_samples)
    elif method == 'lhs':
        sampler = qmc.LatinHypercube(d=n_vars)
        samples = sampler.random(n_samples)
    else:
        # Random fallback
        samples = np.random.random((n_samples, n_vars))
    
    return samples


def calculate_grid_samples(points_per_var: int, n_vars: int) -> int:
    """Calculate total samples for a grid approach."""
    return points_per_var ** n_vars


def calculate_recommended_samples(config_types: list, points_per_var: int) -> dict:
    """
    Calculate recommended sample sizes based on configuration complexity.
    """
    var_counts = {
        'tandem': 12,      # span, 2 chords, taper, sweep, stagger, gap, battery(2), motor, prop(2)
        'flying_wing': 9,  # span, chord, taper, sweep, battery(2), motor, prop(2)
        'traditional': 10, # span, chord, taper, sweep, tail, battery(2), motor, prop(2)
        'vtol': 14         # All traditional + boom, vtol motors, vtol props
    }
    
    result = {}
    for cfg in config_types:
        n_vars = var_counts.get(cfg, 10)
        # Use Sobol sampling instead of full grid
        # Sobol converges much faster than grid
        # Rule of thumb: 1000-10000 samples per variable for good coverage
        samples = max(10000, points_per_var * 1000 * len(config_types))
        result[cfg] = {
            'n_variables': n_vars,
            'grid_samples': points_per_var ** n_vars,
            'recommended_samples': samples
        }
    
    return result
```

### 5.2 Parallel Evaluation

```python
import multiprocessing as mp
from functools import partial
import time

def evaluate_single_design(
    sample: np.ndarray,
    bounds: dict,
    config_type: str,
    constraints: dict
) -> dict:
    """
    Evaluate a single design point.
    
    Returns None if constraints violated, else performance dict.
    """
    # Decode sample to design variables
    design = decode_sample_to_design(sample, bounds, config_type)
    
    # Quick constraint checks (fast rejection)
    if design['span'] > constraints['max_span']:
        return None
    
    total_length = estimate_total_length(design, config_type)
    if total_length > constraints['max_length']:
        return None
    
    # Full evaluation
    try:
        # Build full configuration
        system = optimize_battery_fuselage_system(
            target_flight_time_min=120,  # Initial target
            cruise_velocity=constraints['cruise_speed_ms'],
            wing_config=design,
            config_type=config_type
        )
        
        weight_n = system['total_mass_kg'] * 9.81
        wing_area = calculate_wing_area(design, config_type)
        
        # Stall speed check
        cl_max = get_airfoil_cl_max(design.get('airfoil', 'SD7032'), 150000)
        v_stall = np.sqrt(2 * weight_n / (1.225 * wing_area * cl_max))
        
        min_stall = constraints['min_stall_speed_ms']
        if config_type == 'vtol':
            min_stall = constraints['vtol_stall_speed_ms']
        
        if v_stall > min_stall:
            return None
        
        # Thrust to weight check
        # (Would need propulsion model here)
        
        # Calculate performance metrics
        drag = calculate_full_drag(
            {**design, **system['fuselage'].__dict__},
            weight_n,
            constraints['cruise_speed_ms'],
            config_type
        )
        
        ld_ratio = weight_n / drag.total if drag.total > 0 else 0
        range_km = (system['flight_time_min'] / 60) * constraints['cruise_speed_ms'] * 3.6
        
        return {
            'design': design,
            'valid': True,
            'flight_time_min': system['flight_time_min'],
            'range_km': range_km,
            'ld_ratio': ld_ratio,
            'weight_kg': system['total_mass_kg'],
            'cruise_power_w': system['cruise_power_w'],
            'stall_speed_ms': v_stall,
            'drag_breakdown': drag.breakdown_dict,
            'battery_config': f"{system['battery_series']}S{system['battery_parallel']}P",
            'wing_area_m2': wing_area
        }
        
    except Exception as e:
        return None


def run_parallel_optimization(
    config_types: list,
    n_samples: int,
    constraints: dict,
    n_processes: int = None,
    progress_callback = None
) -> dict:
    """
    Run optimization across all configurations in parallel.
    """
    if n_processes is None:
        n_processes = max(1, mp.cpu_count() - 1)
    
    results = {}
    
    for config_type in config_types:
        print(f"\nOptimizing {config_type}...")
        
        # Get bounds for this config
        bounds = get_design_bounds(config_type)
        n_vars = len(bounds)
        
        # Generate samples
        samples = create_design_sampler(n_samples, n_vars, method='sobol')
        
        # Create evaluation function with fixed args
        eval_func = partial(
            evaluate_single_design,
            bounds=bounds,
            config_type=config_type,
            constraints=constraints
        )
        
        # Process in parallel
        start_time = time.time()
        
        with mp.Pool(n_processes) as pool:
            # Use imap for progress tracking
            batch_size = 1000
            all_results = []
            
            for i, result in enumerate(pool.imap(eval_func, samples, chunksize=batch_size)):
                if result is not None:
                    all_results.append(result)
                
                if progress_callback and (i + 1) % 10000 == 0:
                    progress_callback(config_type, i + 1, n_samples, len(all_results))
        
        elapsed = time.time() - start_time
        
        results[config_type] = {
            'all_valid': all_results,
            'n_evaluated': n_samples,
            'n_valid': len(all_results),
            'elapsed_seconds': elapsed,
            'rate': n_samples / elapsed
        }
        
        print(f"  {config_type}: {len(all_results):,} valid from {n_samples:,} "
              f"({100*len(all_results)/n_samples:.1f}%) in {elapsed:.1f}s")
    
    return results
```

### 5.3 Pareto Front Extraction

```python
def is_dominated(point_a: np.ndarray, point_b: np.ndarray) -> bool:
    """Check if point_a is dominated by point_b (all objectives maximized)."""
    return np.all(point_b >= point_a) and np.any(point_b > point_a)


def extract_pareto_front(
    results: list,
    objectives: list = ['flight_time_min', 'ld_ratio', 'range_km']
) -> list:
    """
    Extract Pareto-optimal solutions using non-dominated sorting.
    
    More efficient O(n log n) algorithm for 2 objectives,
    O(n^2) for 3+ objectives.
    """
    n = len(results)
    if n == 0:
        return []
    
    # Extract objective values (all maximized)
    obj_matrix = np.array([
        [r[obj] for obj in objectives]
        for r in results
    ])
    
    # Non-dominated sorting
    is_pareto = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not is_pareto[i]:
            continue
        
        for j in range(n):
            if i == j or not is_pareto[j]:
                continue
            
            if is_dominated(obj_matrix[i], obj_matrix[j]):
                is_pareto[i] = False
                break
    
    pareto_results = [r for r, p in zip(results, is_pareto) if p]
    
    # Sort by primary objective
    pareto_results.sort(key=lambda x: x[objectives[0]], reverse=True)
    
    return pareto_results


def compute_pareto_metrics(pareto_front: list, objectives: list) -> dict:
    """
    Compute metrics describing the Pareto front quality.
    """
    if not pareto_front:
        return {}
    
    obj_values = np.array([
        [r[obj] for obj in objectives]
        for r in pareto_front
    ])
    
    return {
        'n_pareto_points': len(pareto_front),
        'objective_ranges': {
            obj: {
                'min': float(obj_values[:, i].min()),
                'max': float(obj_values[:, i].max()),
                'spread': float(obj_values[:, i].max() - obj_values[:, i].min())
            }
            for i, obj in enumerate(objectives)
        },
        'best_per_objective': {
            obj: pareto_front[np.argmax(obj_values[:, i])]
            for i, obj in enumerate(objectives)
        }
    }
```

---

## PART 6: HTML GENERATION

### 6.1 Main HTML Template

```python
def generate_html_output(
    optimization_results: dict,
    config: dict,
    output_path: str = 'drone_optimizer_results.html'
) -> str:
    """
    Generate complete HTML dashboard with results.
    """
    
    # Prepare data for charts
    chart_data = prepare_chart_data(optimization_results)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drone Flight Time Optimizer V2</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
{CSS_STYLES}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Drone Flight Time Optimization</h1>
            <p class="subtitle">System-Level Analysis | {config['total_samples']:,} Configurations Evaluated</p>
        </header>
        
        {generate_winner_banner(optimization_results)}
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('summary')">Results Summary</button>
            <button class="tab" onclick="showTab('pareto')">Pareto Analysis</button>
            <button class="tab" onclick="showTab('configs')">Configuration Details</button>
            <button class="tab" onclick="showTab('drag')">Drag Breakdown</button>
            <button class="tab" onclick="showTab('sensitivity')">Sensitivity</button>
        </div>
        
        <div id="tab-summary" class="tab-content">
            {generate_summary_tab(optimization_results)}
        </div>
        
        <div id="tab-pareto" class="tab-content" style="display:none;">
            {generate_pareto_tab(optimization_results)}
        </div>
        
        <div id="tab-configs" class="tab-content" style="display:none;">
            {generate_configs_tab(optimization_results)}
        </div>
        
        <div id="tab-drag" class="tab-content" style="display:none;">
            {generate_drag_tab(optimization_results)}
        </div>
        
        <div id="tab-sensitivity" class="tab-content" style="display:none;">
            {generate_sensitivity_tab(optimization_results)}
        </div>
        
        {generate_constraints_bar(config)}
    </div>
    
    <script>
{generate_javascript(chart_data)}
    </script>
</body>
</html>'''
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path
```

### 6.2 Tab Content Generators

```python
def generate_winner_banner(results: dict) -> str:
    """Generate the winner announcement banner."""
    # Find best overall
    best_config = None
    best_time = 0
    
    for cfg_type, cfg_results in results.items():
        if cfg_results['pareto_front']:
            top = cfg_results['pareto_front'][0]
            if top['flight_time_min'] > best_time:
                best_time = top['flight_time_min']
                best_config = cfg_type
                best_design = top
    
    if not best_config:
        return '<div class="winner-banner"><h2>No valid configurations found</h2></div>'
    
    config_names = {
        'tandem': 'Tandem Wing',
        'flying_wing': 'Flying Wing',
        'traditional': 'Traditional',
        'vtol': 'VTOL 4+1'
    }
    
    return f'''
    <div class="winner-banner">
        <div class="winner-info">
            <h2>Winner: {config_names[best_config]}</h2>
            <p>Highest flight time within design constraints</p>
        </div>
        <div class="winner-stats">
            <div class="stat">
                <span class="value">{best_design['flight_time_min']:.1f}</span>
                <span class="label">min</span>
            </div>
            <div class="stat">
                <span class="value">{best_design['range_km']:.1f}</span>
                <span class="label">km</span>
            </div>
            <div class="stat">
                <span class="value">{best_design['ld_ratio']:.2f}</span>
                <span class="label">L/D</span>
            </div>
            <div class="stat">
                <span class="value">{best_design['weight_kg']*1000:.0f}</span>
                <span class="label">g</span>
            </div>
        </div>
    </div>'''


def generate_summary_tab(results: dict) -> str:
    """Generate the summary tab with comparison table and charts."""
    
    # Build results table
    table_rows = []
    for cfg_type in ['tandem', 'flying_wing', 'traditional', 'vtol']:
        if cfg_type not in results or not results[cfg_type]['pareto_front']:
            continue
        
        top = results[cfg_type]['pareto_front'][0]
        config_names = {
            'tandem': 'Tandem Wing',
            'flying_wing': 'Flying Wing',
            'traditional': 'Traditional',
            'vtol': 'VTOL 4+1'
        }
        
        table_rows.append(f'''
        <tr>
            <td><span class="config-dot {cfg_type}"></span>{config_names[cfg_type]}</td>
            <td>{top['flight_time_min']:.1f}</td>
            <td>{top['range_km']:.1f}</td>
            <td>{top['ld_ratio']:.2f}</td>
            <td>{top['weight_kg']*1000:.0f}</td>
            <td>{top['cruise_power_w']:.1f}</td>
            <td>{top['stall_speed_ms']*2.237:.1f}</td>
            <td>{top['wing_area_m2']:.3f}</td>
            <td>{top['battery_config']}</td>
        </tr>''')
    
    return f'''
    <div class="card">
        <h3>Configuration Comparison</h3>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Configuration</th>
                    <th>Flight Time (min)</th>
                    <th>Range (km)</th>
                    <th>L/D</th>
                    <th>Weight (g)</th>
                    <th>P<sub>cruise</sub> (W)</th>
                    <th>V<sub>stall</sub> (mph)</th>
                    <th>S<sub>wing</sub> (m<sup>2</sup>)</th>
                    <th>Battery</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    
    <div class="chart-grid">
        <div class="chart-container">
            <h4>Flight Time Comparison</h4>
            <canvas id="flightTimeChart"></canvas>
        </div>
        <div class="chart-container">
            <h4>Key Metrics</h4>
            <canvas id="metricsChart"></canvas>
        </div>
    </div>'''


def generate_pareto_tab(results: dict) -> str:
    """Generate Pareto analysis tab with scatter plots."""
    return '''
    <div class="card">
        <h3>Pareto Front Analysis</h3>
        <p>Each point represents a Pareto-optimal design. No design dominates another across all objectives.</p>
    </div>
    
    <div class="chart-grid">
        <div class="chart-container">
            <h4>Flight Time vs L/D</h4>
            <canvas id="paretoTimeLD"></canvas>
        </div>
        <div class="chart-container">
            <h4>Flight Time vs Weight</h4>
            <canvas id="paretoTimeWeight"></canvas>
        </div>
        <div class="chart-container">
            <h4>Range vs Cruise Power</h4>
            <canvas id="paretoRangePower"></canvas>
        </div>
        <div class="chart-container">
            <h4>L/D vs Wing Loading</h4>
            <canvas id="paretoLDLoading"></canvas>
        </div>
    </div>
    
    <div class="card">
        <h3>Pareto Trade-off Explorer</h3>
        <div class="slider-container">
            <label>Weight Priority: <span id="weightPriorityDisplay">50%</span></label>
            <input type="range" id="weightPriority" min="0" max="100" value="50" 
                   oninput="updateParetoSelection()">
            <p class="hint">Adjust to explore trade-offs between flight time and weight</p>
        </div>
        <div id="selectedDesign" class="spec-card">
            <p>Move slider to select a design from the Pareto front</p>
        </div>
    </div>'''


def generate_configs_tab(results: dict) -> str:
    """Generate detailed configuration specs tab."""
    cards = []
    
    for cfg_type in ['tandem', 'flying_wing', 'traditional', 'vtol']:
        if cfg_type not in results or not results[cfg_type]['pareto_front']:
            continue
        
        top = results[cfg_type]['pareto_front'][0]
        design = top['design']
        
        config_names = {
            'tandem': 'Tandem Wing',
            'flying_wing': 'Flying Wing',
            'traditional': 'Traditional',
            'vtol': 'VTOL 4+1'
        }
        
        specs = [
            ('Span', f"{design['span']*100:.1f} cm"),
            ('Wing Area', f"{top['wing_area_m2']*10000:.0f} cm<sup>2</sup>"),
            ('Aspect Ratio', f"{design['span']**2/top['wing_area_m2']:.2f}"),
            ('Airfoil', design.get('airfoil', 'SD7032')),
            ('Battery', top['battery_config']),
            ('MTOW', f"{top['weight_kg']*1000:.0f} g"),
            ('Wing Loading', f"{top['weight_kg']*9.81/top['wing_area_m2']:.1f} N/m<sup>2</sup>"),
        ]
        
        if cfg_type == 'tandem':
            specs.insert(1, ('Front Chord', f"{design.get('chord_front', 0.2)*100:.1f} cm"))
            specs.insert(2, ('Rear Chord', f"{design.get('chord_rear', 0.18)*100:.1f} cm"))
            specs.insert(5, ('Stagger', f"{design.get('tandem_stagger', 0.4)*100:.0f} cm"))
        else:
            specs.insert(1, ('Chord', f"{design.get('chord', 0.2)*100:.1f} cm"))
        
        spec_html = '\n'.join([
            f'<div class="spec-item"><span class="spec-label">{label}</span>'
            f'<span class="spec-value">{value}</span></div>'
            for label, value in specs
        ])
        
        cards.append(f'''
        <div class="card spec-card {cfg_type}">
            <h3>{config_names[cfg_type]}</h3>
            {spec_html}
        </div>''')
    
    return f'''
    <div class="config-grid">
        {''.join(cards)}
    </div>'''


def generate_drag_tab(results: dict) -> str:
    """Generate drag breakdown analysis tab."""
    return '''
    <div class="card">
        <h3>Drag Component Analysis</h3>
        <p>Breakdown of drag sources for each optimal configuration at cruise condition.</p>
    </div>
    
    <div class="chart-grid">
        <div class="chart-container">
            <h4>Tandem Wing</h4>
            <canvas id="dragTandem"></canvas>
        </div>
        <div class="chart-container">
            <h4>Flying Wing</h4>
            <canvas id="dragFlying"></canvas>
        </div>
        <div class="chart-container">
            <h4>Traditional</h4>
            <canvas id="dragTraditional"></canvas>
        </div>
        <div class="chart-container">
            <h4>VTOL 4+1</h4>
            <canvas id="dragVTOL"></canvas>
        </div>
    </div>
    
    <div class="card">
        <h3>Drag Comparison</h3>
        <canvas id="dragComparison" style="max-height: 400px;"></canvas>
    </div>'''
```

### 6.3 JavaScript for Interactivity

```python
def generate_javascript(chart_data: dict) -> str:
    """Generate JavaScript for charts and interactivity."""
    return f'''
// Tab switching
function showTab(tabId) {{
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabId).style.display = 'block';
    event.target.classList.add('active');
}}

// Chart colors
const COLORS = {{
    tandem: '#2E86AB',
    flying_wing: '#A23B72',
    traditional: '#F18F01',
    vtol: '#C73E1D'
}};

// Chart data
const chartData = {json.dumps(chart_data)};

// Flight Time Bar Chart
new Chart(document.getElementById('flightTimeChart'), {{
    type: 'bar',
    data: {{
        labels: chartData.configs,
        datasets: [{{
            label: 'Flight Time (min)',
            data: chartData.flightTimes,
            backgroundColor: chartData.configs.map(c => COLORS[c.toLowerCase().replace(' ', '_')])
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        plugins: {{
            legend: {{ display: false }}
        }}
    }}
}});

// Metrics Comparison Chart
new Chart(document.getElementById('metricsChart'), {{
    type: 'bar',
    data: {{
        labels: chartData.configs,
        datasets: [
            {{
                label: 'L/D Ratio',
                data: chartData.ldRatios,
                backgroundColor: 'rgba(30, 64, 175, 0.7)'
            }},
            {{
                label: 'Weight (100g)',
                data: chartData.weights.map(w => w/100),
                backgroundColor: 'rgba(100, 116, 139, 0.7)'
            }}
        ]
    }},
    options: {{
        responsive: true,
        scales: {{
            y: {{ beginAtZero: true }}
        }}
    }}
}});

// Pareto Scatter Plots
function createParetoScatter(canvasId, xKey, yKey, xLabel, yLabel) {{
    const datasets = Object.keys(chartData.pareto).map(cfg => ({{
        label: cfg,
        data: chartData.pareto[cfg].map(p => ({{ x: p[xKey], y: p[yKey] }})),
        backgroundColor: COLORS[cfg],
        pointRadius: 5
    }}));
    
    new Chart(document.getElementById(canvasId), {{
        type: 'scatter',
        data: {{ datasets }},
        options: {{
            responsive: true,
            scales: {{
                x: {{ title: {{ display: true, text: xLabel }} }},
                y: {{ title: {{ display: true, text: yLabel }} }}
            }}
        }}
    }});
}}

createParetoScatter('paretoTimeLD', 'flight_time_min', 'ld_ratio', 'Flight Time (min)', 'L/D');
createParetoScatter('paretoTimeWeight', 'flight_time_min', 'weight_kg', 'Flight Time (min)', 'Weight (kg)');
createParetoScatter('paretoRangePower', 'range_km', 'cruise_power_w', 'Range (km)', 'Cruise Power (W)');

// Drag Doughnut Charts
function createDragChart(canvasId, dragData) {{
    new Chart(document.getElementById(canvasId), {{
        type: 'doughnut',
        data: {{
            labels: Object.keys(dragData),
            datasets: [{{
                data: Object.values(dragData),
                backgroundColor: [
                    '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', 
                    '#047857', '#7C3AED', '#DB2777', '#64748B'
                ]
            }}]
        }},
        options: {{
            responsive: true,
            plugins: {{
                legend: {{ position: 'right' }}
            }}
        }}
    }});
}}

if (chartData.drag.tandem) createDragChart('dragTandem', chartData.drag.tandem);
if (chartData.drag.flying_wing) createDragChart('dragFlying', chartData.drag.flying_wing);
if (chartData.drag.traditional) createDragChart('dragTraditional', chartData.drag.traditional);
if (chartData.drag.vtol) createDragChart('dragVTOL', chartData.drag.vtol);

// Pareto slider
function updateParetoSelection() {{
    const priority = document.getElementById('weightPriority').value;
    document.getElementById('weightPriorityDisplay').textContent = priority + '%';
    // Find best design given weight priority
    // (Implementation depends on your trade-off logic)
}}
'''
```

---

## PART 7: MAIN EXECUTION FLOW

### 7.1 Entry Point

```python
def main():
    """Main entry point for the optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Drone Flight Time Optimizer V2')
    parser.add_argument('--samples', type=int, default=100000,
                        help='Samples per configuration')
    parser.add_argument('--points-per-var', type=int, default=10,
                        help='Resolution for grid-based sampling estimate')
    parser.add_argument('--configs', nargs='+', 
                        default=['tandem', 'flying_wing', 'traditional', 'vtol'],
                        help='Configurations to evaluate')
    parser.add_argument('--output', type=str, default='drone_optimizer_results.html',
                        help='Output HTML file')
    parser.add_argument('--processes', type=int, default=None,
                        help='Number of parallel processes')
    
    # Constraint overrides
    parser.add_argument('--max-span', type=float, default=1.0)
    parser.add_argument('--max-length', type=float, default=1.0)
    parser.add_argument('--min-stall', type=float, default=12.5,
                        help='Min stall speed in mph')
    parser.add_argument('--cruise-speed', type=float, default=35,
                        help='Cruise speed in mph')
    
    args = parser.parse_args()
    
    # Build constraints dict
    constraints = {
        'max_span': args.max_span,
        'max_length': args.max_length,
        'min_stall_speed_ms': args.min_stall * 0.44704,
        'vtol_stall_speed_ms': 20 * 0.44704,
        'cruise_speed_ms': args.cruise_speed * 0.44704,
        'min_thrust_to_weight': 1.5
    }
    
    print("=" * 60)
    print("DRONE FLIGHT TIME OPTIMIZER V2")
    print("=" * 60)
    print(f"Configurations: {args.configs}")
    print(f"Samples per config: {args.samples:,}")
    print(f"Constraints: {constraints}")
    print()
    
    # Run optimization
    results = run_parallel_optimization(
        config_types=args.configs,
        n_samples=args.samples,
        constraints=constraints,
        n_processes=args.processes
    )
    
    # Extract Pareto fronts
    for cfg_type in results:
        pareto = extract_pareto_front(results[cfg_type]['all_valid'])
        results[cfg_type]['pareto_front'] = pareto
        print(f"{cfg_type}: {len(pareto)} Pareto-optimal designs")
    
    # Generate HTML output
    config = {
        'total_samples': args.samples * len(args.configs),
        'constraints': constraints
    }
    
    output_path = generate_html_output(results, config, args.output)
    print(f"\nResults saved to: {output_path}")
    
    return results


if __name__ == '__main__':
    main()
```

---

## PART 8: IMPLEMENTATION CHECKLIST

### Phase 1: Core Physics (Days 1-2)
- [ ] Implement AIRFOIL_DATABASE with 50+ airfoils and AOA sweeps
- [ ] Implement interpolate_airfoil() function
- [ ] Implement calculate_effective_aoa() with downwash
- [ ] Implement DragComponents class
- [ ] Implement calculate_full_drag() for all 4 configurations
- [ ] Implement calculate_oswald_efficiency() with config corrections

### Phase 2: System Integration (Days 3-4)
- [ ] Implement battery layout enumeration
- [ ] Implement fuselage sizing
- [ ] Implement optimize_battery_fuselage_system() iterative solver
- [ ] Implement wing mass estimation
- [ ] Test individual component functions

### Phase 3: Optimization Engine (Days 5-6)
- [ ] Implement Sobol/LHS sampling
- [ ] Implement evaluate_single_design()
- [ ] Implement parallel evaluation with multiprocessing
- [ ] Implement Pareto front extraction
- [ ] Test on small sample sizes

### Phase 4: HTML Output (Days 7-8)
- [ ] Implement CSS styles (match original dashboard)
- [ ] Implement generate_winner_banner()
- [ ] Implement all tab generators
- [ ] Implement Chart.js integration
- [ ] Implement interactive elements (sliders, tabs)

### Phase 5: Integration and Testing (Days 9-10)
- [ ] Full integration test with 100k samples
- [ ] Validate results against original tool
- [ ] Performance optimization
- [ ] 1M sample stress test
- [ ] Final HTML polish

---

## APPENDIX A: KEY VALIDATION TARGETS

Compare V2 results against original V1:

| Metric | Original V1 | V2 Target | Notes |
|--------|-------------|-----------|-------|
| Tandem Flight Time | 132.3 min | >140 min | Better AOA selection |
| Flying Wing Flight Time | 99.6 min | >105 min | Improved drag model |
| Samples per config | 27,000 | 1,000,000 | 37x increase |
| Computation time | ~30 sec | <5 min | With parallelization |
| Valid design rate | ~5% | >3% | Tighter constraints |

---

## PART 9: ENHANCED GEOMETRY MODELS

### 9.1 Tandem Wing Extended Geometry

The tandem wing configuration requires detailed biplane interference modeling. Munk's stagger theorem and Prandtl's biplane theory provide the foundation for understanding how two wings interact.

```python
@dataclass
class TandemWingGeometry:
    """Complete tandem wing geometry specification"""
    # Front wing
    front_span: float           # m
    front_chord_root: float     # m
    front_chord_tip: float      # m (allows taper)
    front_sweep_deg: float      # Leading edge sweep
    front_dihedral_deg: float   # Dihedral angle
    front_incidence_deg: float  # Wing setting angle relative to fuselage
    front_twist_deg: float      # Washout (tip twist relative to root, negative = washout)
    front_airfoil_root: str     # Root airfoil name
    front_airfoil_tip: str      # Tip airfoil name (allows blending)
    
    # Rear wing
    rear_span: float            # Can differ from front
    rear_chord_root: float
    rear_chord_tip: float
    rear_sweep_deg: float
    rear_dihedral_deg: float
    rear_incidence_deg: float   # Decalage = rear_incidence - front_incidence
    rear_twist_deg: float
    rear_airfoil_root: str
    rear_airfoil_tip: str
    
    # Relative positioning
    stagger: float              # Horizontal distance, positive = rear wing aft
    gap: float                  # Vertical distance between wing planes
    gap_angle_deg: float        # Angle of gap line from horizontal (positive = rear higher)
    
    @property
    def decalage(self) -> float:
        """Incidence difference between wings (affects pitch trim)"""
        return self.rear_incidence_deg - self.front_incidence_deg
    
    @property
    def front_area(self) -> float:
        return self.front_span * (self.front_chord_root + self.front_chord_tip) / 2
    
    @property
    def rear_area(self) -> float:
        return self.rear_span * (self.rear_chord_root + self.rear_chord_tip) / 2
    
    @property
    def total_area(self) -> float:
        return self.front_area + self.rear_area
    
    @property
    def front_mac(self) -> float:
        """Mean aerodynamic chord of front wing"""
        taper = self.front_chord_tip / self.front_chord_root
        return self.front_chord_root * (2/3) * (1 + taper + taper**2) / (1 + taper)
    
    @property
    def rear_mac(self) -> float:
        taper = self.rear_chord_tip / self.rear_chord_root
        return self.rear_chord_root * (2/3) * (1 + taper + taper**2) / (1 + taper)
    
    @property
    def gap_ratio(self) -> float:
        """Gap / average chord (Prandtl biplane parameter)"""
        avg_chord = (self.front_mac + self.rear_mac) / 2
        return self.gap / avg_chord
    
    @property
    def stagger_ratio(self) -> float:
        """Stagger / gap (Munk stagger parameter)"""
        return self.stagger / self.gap if self.gap > 0 else 0


def calculate_biplane_interference_factor(
    gap_ratio: float,
    stagger_ratio: float,
    span_ratio: float = 1.0
) -> float:
    """
    Calculate Prandtl's biplane interference factor (sigma).
    
    This factor modifies the induced drag of a biplane system.
    sigma = 1 means no interference benefit (wings far apart)
    sigma < 1 means reduced induced drag from favorable interference
    
    Based on Prandtl-Munk biplane theory:
    CDi_biplane = CDi_monoplane * (1 + sigma) / 2 for equal lift sharing
    
    Args:
        gap_ratio: gap / chord
        stagger_ratio: stagger / gap  
        span_ratio: rear_span / front_span
    """
    # Prandtl's sigma approximation for unstaggered biplane
    # sigma approaches 0 for large gap, approaches 1 for zero gap
    if gap_ratio <= 0:
        return 1.0
    
    sigma_unstaggered = 1 / (1 + 2 * gap_ratio)
    
    # Munk's stagger correction
    # Positive stagger (rear wing behind) reduces interference
    stagger_factor = 1 - 0.1 * abs(stagger_ratio)
    stagger_factor = max(0.5, min(1.0, stagger_factor))
    
    sigma = sigma_unstaggered * stagger_factor
    
    # Span ratio correction (unequal spans change interference pattern)
    if span_ratio != 1.0:
        # Smaller rear wing has less effect on front wing
        span_correction = 2 * span_ratio / (1 + span_ratio**2)
        sigma *= span_correction
    
    return np.clip(sigma, 0.1, 1.0)


def calculate_tandem_downwash(
    front_cl: float,
    front_ar: float,
    stagger: float,
    gap: float,
    rear_span: float
) -> float:
    """
    Calculate downwash angle at rear wing due to front wing.
    
    The front wing creates a downwash field that reduces the effective
    AOA of the rear wing. This is the primary efficiency penalty of tandem designs.
    
    Returns downwash angle in degrees.
    """
    # Far-field downwash from lifting line theory
    # epsilon = 2 * CL / (pi * AR) for a single wing
    epsilon_inf = 2 * front_cl / (np.pi * front_ar)  # radians
    
    # Near-field correction based on position
    # Downwash decreases with distance behind wing
    x_normalized = stagger / (front_ar * 0.5)  # Normalize by half-span
    z_normalized = gap / (front_ar * 0.5)
    
    # Distance factor (downwash decays with distance)
    distance = np.sqrt(x_normalized**2 + z_normalized**2)
    distance_factor = 1 / (1 + 0.5 * distance)
    
    # Vertical position factor (downwash strongest directly behind, weaker above/below)
    vertical_factor = np.exp(-0.5 * z_normalized**2)
    
    epsilon = epsilon_inf * distance_factor * vertical_factor
    
    return np.degrees(epsilon)


def calculate_tandem_oswald_efficiency(
    front_geom: dict,
    rear_geom: dict,
    gap: float,
    stagger: float
) -> tuple:
    """
    Calculate effective Oswald efficiency for tandem wing system.
    
    Returns (e_front, e_rear, e_system) where e_system accounts for
    the combined induced drag of both wings including interference.
    """
    # Individual wing efficiencies
    e_front = calculate_oswald_efficiency(
        front_geom['ar'], front_geom['taper'], front_geom['sweep'], 'traditional'
    )
    e_rear = calculate_oswald_efficiency(
        rear_geom['ar'], rear_geom['taper'], rear_geom['sweep'], 'traditional'
    )
    
    # Biplane interference
    avg_chord = (front_geom['mac'] + rear_geom['mac']) / 2
    gap_ratio = gap / avg_chord
    stagger_ratio = stagger / gap if gap > 0 else 0
    span_ratio = rear_geom['span'] / front_geom['span']
    
    sigma = calculate_biplane_interference_factor(gap_ratio, stagger_ratio, span_ratio)
    
    # System Oswald efficiency
    # For a biplane, the effective span is increased by favorable interference
    # e_system = e_mono * (1 + sigma) / (2 * sigma) approximately
    e_system = (e_front + e_rear) / 2 * (1 - 0.3 * sigma)
    
    return e_front, e_rear, np.clip(e_system, 0.4, 0.85)
```

### 9.2 General Wing Geometry Enhancements

```python
@dataclass
class WingGeometry:
    """Enhanced wing geometry with twist, dihedral, and airfoil blending"""
    span: float
    chord_root: float
    chord_tip: float
    sweep_le_deg: float         # Leading edge sweep
    dihedral_deg: float
    twist_deg: float            # Washout at tip (negative = nose down)
    incidence_deg: float        # Wing setting angle
    airfoil_root: str
    airfoil_tip: str
    
    # Winglet parameters (optional)
    winglet_height: float = 0.0      # m, 0 = no winglet
    winglet_cant_deg: float = 75.0   # Angle from vertical
    winglet_sweep_deg: float = 35.0
    winglet_taper: float = 0.4
    
    @property
    def area(self) -> float:
        return self.span * (self.chord_root + self.chord_tip) / 2
    
    @property
    def aspect_ratio(self) -> float:
        return self.span**2 / self.area
    
    @property
    def taper_ratio(self) -> float:
        return self.chord_tip / self.chord_root
    
    @property
    def mac(self) -> float:
        """Mean aerodynamic chord"""
        tr = self.taper_ratio
        return self.chord_root * (2/3) * (1 + tr + tr**2) / (1 + tr)
    
    @property
    def mac_y_position(self) -> float:
        """Spanwise position of MAC from centerline"""
        tr = self.taper_ratio
        return (self.span / 6) * (1 + 2*tr) / (1 + tr)
    
    @property
    def sweep_quarter_chord_deg(self) -> float:
        """Convert LE sweep to quarter-chord sweep"""
        # tan(sweep_c/4) = tan(sweep_LE) - 4/AR * (1-taper)/(1+taper) * 1/4
        tan_le = np.tan(np.radians(self.sweep_le_deg))
        correction = (1 - self.taper_ratio) / (self.aspect_ratio * (1 + self.taper_ratio))
        tan_qc = tan_le - correction
        return np.degrees(np.arctan(tan_qc))


def calculate_twist_cl_distribution(
    wing: WingGeometry,
    total_cl: float,
    n_stations: int = 20
) -> np.ndarray:
    """
    Calculate spanwise Cl distribution accounting for twist.
    
    Twist (washout) reduces tip loading, moving the lift distribution
    away from elliptical but reducing tip stall tendency.
    
    Returns array of local Cl values at each spanwise station.
    """
    # Spanwise stations (normalized 0 to 1)
    eta = np.linspace(0, 1, n_stations)
    
    # Chord distribution (linear taper)
    chord = wing.chord_root * (1 - eta * (1 - wing.taper_ratio))
    
    # Twist distribution (linear from root to tip)
    twist = eta * wing.twist_deg
    
    # Base elliptical distribution
    cl_elliptical = total_cl * 4 / np.pi * np.sqrt(1 - eta**2)
    
    # Twist correction
    # Each degree of washout reduces local Cl by approximately cl_alpha * twist
    cl_alpha = 0.1  # per degree, typical
    twist_correction = cl_alpha * twist
    
    # Combine (twist reduces outboard Cl)
    cl_distribution = cl_elliptical - twist_correction
    
    # Renormalize to maintain total lift
    avg_cl = np.trapz(cl_distribution * chord, eta) / np.trapz(chord, eta)
    cl_distribution *= total_cl / avg_cl
    
    return cl_distribution


def calculate_winglet_benefit(
    wing: WingGeometry,
    cl: float
) -> dict:
    """
    Calculate induced drag reduction from winglets.
    
    Winglets reduce induced drag by diffusing the tip vortex,
    effectively increasing the span efficiency factor.
    
    Based on Whitcomb's winglet theory and empirical data.
    """
    if wing.winglet_height <= 0:
        return {'delta_e': 0, 'delta_cdi': 0, 'effective_span_increase': 0}
    
    # Winglet height ratio
    h_ratio = wing.winglet_height / (wing.span / 2)
    
    # Cant angle effect (90 deg = vertical, less cant = more like span extension)
    cant_rad = np.radians(wing.winglet_cant_deg)
    cant_factor = np.cos(cant_rad) + 0.5 * np.sin(cant_rad)
    
    # Effective span increase (Whitcomb approximation)
    # Vertical winglet of height h adds roughly 0.45*h to effective span
    span_increase_factor = 0.45 * h_ratio * cant_factor
    
    # This translates to Oswald efficiency improvement
    # e_new / e_old = (1 + span_increase)^2 approximately
    delta_e = 2 * span_increase_factor  # First order approximation
    
    # Induced drag reduction
    # CDi_new = CDi_old * (1 - delta_CDi)
    ar = wing.aspect_ratio
    base_cdi = cl**2 / (np.pi * ar * 0.8)  # Assume base e=0.8
    new_cdi = cl**2 / (np.pi * ar * (0.8 + delta_e))
    delta_cdi = (base_cdi - new_cdi) / base_cdi
    
    # Winglet also adds wetted area (parasitic drag penalty)
    winglet_area = wing.winglet_height * wing.chord_tip * wing.winglet_taper * 2  # Both sides
    parasitic_penalty = 0.01 * winglet_area  # Rough Cd * S estimate
    
    return {
        'delta_e': delta_e,
        'delta_cdi_percent': delta_cdi * 100,
        'effective_span_increase': span_increase_factor * wing.span,
        'winglet_area': winglet_area,
        'parasitic_penalty': parasitic_penalty,
        'net_benefit': delta_cdi * base_cdi > parasitic_penalty
    }


def blend_airfoil_coefficients(
    airfoil_root: str,
    airfoil_tip: str,
    eta: float,
    alpha: float,
    reynolds: float
) -> tuple:
    """
    Blend coefficients between root and tip airfoils.
    
    Args:
        eta: Spanwise position (0 = root, 1 = tip)
        
    Returns: (cl, cd, cm) blended coefficients
    """
    cl_root, cd_root, cm_root = interpolate_airfoil(airfoil_root, alpha, reynolds)
    cl_tip, cd_tip, cm_tip = interpolate_airfoil(airfoil_tip, alpha, reynolds)
    
    # Linear blend (could use other blending functions)
    cl = cl_root * (1 - eta) + cl_tip * eta
    cd = cd_root * (1 - eta) + cd_tip * eta
    cm = cm_root * (1 - eta) + cm_tip * eta
    
    return cl, cd, cm
```

---

## PART 10: STABILITY AND CONTROL

### 10.1 Center of Gravity Calculations

```python
@dataclass
class MassItem:
    """Individual mass item with position"""
    name: str
    mass_kg: float
    x: float  # Distance from nose, positive aft
    y: float  # Distance from centerline, positive right
    z: float  # Distance from reference, positive up


@dataclass
class CGResult:
    """Center of gravity calculation result"""
    total_mass_kg: float
    cg_x: float  # From nose
    cg_y: float  # From centerline
    cg_z: float  # From reference
    
    # Moments of inertia about CG
    ixx: float  # Roll
    iyy: float  # Pitch
    izz: float  # Yaw
    ixz: float  # Product of inertia
    
    # CG limits
    forward_limit_x: float
    aft_limit_x: float
    
    @property
    def cg_mac_percent(self) -> float:
        """CG position as percent of MAC (set externally)"""
        return self._cg_mac_percent
    
    @cg_mac_percent.setter
    def cg_mac_percent(self, value: float):
        self._cg_mac_percent = value


def calculate_cg(mass_items: list, wing_geometry: dict) -> CGResult:
    """
    Calculate center of gravity and moments of inertia.
    
    Args:
        mass_items: List of MassItem objects
        wing_geometry: Dict with mac, mac_x_position (x location of MAC LE)
    """
    total_mass = sum(item.mass_kg for item in mass_items)
    
    if total_mass <= 0:
        raise ValueError("Total mass must be positive")
    
    # CG position (mass-weighted average)
    cg_x = sum(item.mass_kg * item.x for item in mass_items) / total_mass
    cg_y = sum(item.mass_kg * item.y for item in mass_items) / total_mass
    cg_z = sum(item.mass_kg * item.z for item in mass_items) / total_mass
    
    # Moments of inertia about CG (parallel axis theorem)
    ixx = iyy = izz = ixz = 0
    
    for item in mass_items:
        dx = item.x - cg_x
        dy = item.y - cg_y
        dz = item.z - cg_z
        
        # Treat each item as point mass (could add item geometry for accuracy)
        ixx += item.mass_kg * (dy**2 + dz**2)
        iyy += item.mass_kg * (dx**2 + dz**2)
        izz += item.mass_kg * (dx**2 + dy**2)
        ixz += item.mass_kg * dx * dz
    
    # CG as percent MAC
    mac = wing_geometry['mac']
    mac_le_x = wing_geometry['mac_x_position']
    cg_mac_percent = (cg_x - mac_le_x) / mac * 100
    
    result = CGResult(
        total_mass_kg=total_mass,
        cg_x=cg_x,
        cg_y=cg_y,
        cg_z=cg_z,
        ixx=ixx,
        iyy=iyy,
        izz=izz,
        ixz=ixz,
        forward_limit_x=0,  # Set by stability analysis
        aft_limit_x=0
    )
    result.cg_mac_percent = cg_mac_percent
    
    return result


def build_mass_breakdown(
    config: dict,
    config_type: str,
    fuselage: FuselageDesign,
    battery_series: int,
    battery_parallel: int
) -> list:
    """
    Build complete mass breakdown with positions for CG calculation.
    
    Returns list of MassItem objects.
    """
    items = []
    cell = CellDimensions()
    
    # Fuselage reference: nose at x=0
    
    # Avionics (flight controller, receiver, GPS) - near nose
    items.append(MassItem(
        name='Avionics',
        mass_kg=0.080,
        x=0.05,
        y=0,
        z=0
    ))
    
    # Battery
    battery_mass = battery_series * battery_parallel * cell.mass
    battery_x = fuselage.component_positions['battery']
    items.append(MassItem(
        name='Battery',
        mass_kg=battery_mass,
        x=battery_x,
        y=0,
        z=0
    ))
    
    # ESC
    items.append(MassItem(
        name='ESC',
        mass_kg=0.025,
        x=fuselage.component_positions['esc'],
        y=0,
        z=0
    ))
    
    # Motor
    motor_mass = 0.040  # Typical for this power class
    items.append(MassItem(
        name='Motor',
        mass_kg=motor_mass,
        x=fuselage.component_positions['motor'],
        y=0,
        z=0
    ))
    
    # Propeller
    items.append(MassItem(
        name='Propeller',
        mass_kg=0.020,
        x=fuselage.length + 0.02,  # In front of motor
        y=0,
        z=0
    ))
    
    # Fuselage structure
    items.append(MassItem(
        name='Fuselage',
        mass_kg=fuselage.estimated_weight_kg,
        x=fuselage.length * 0.45,  # Approximate centroid
        y=0,
        z=0
    ))
    
    # Wings (position depends on configuration)
    wing_mass = estimate_wing_mass(config, config_type)
    wing_x = config.get('wing_x_position', fuselage.length * 0.35)
    
    if config_type == 'tandem':
        # Split mass between front and rear wings
        front_area = config['front_span'] * config.get('front_chord', 0.2)
        rear_area = config.get('rear_span', config['front_span']) * config.get('rear_chord', 0.18)
        total_area = front_area + rear_area
        
        front_mass = wing_mass * front_area / total_area
        rear_mass = wing_mass * rear_area / total_area
        
        items.append(MassItem(
            name='Front Wing',
            mass_kg=front_mass,
            x=wing_x,
            y=0,
            z=config.get('front_z', 0)
        ))
        items.append(MassItem(
            name='Rear Wing',
            mass_kg=rear_mass,
            x=wing_x + config.get('stagger', 0.4),
            y=0,
            z=config.get('gap', 0.08)
        ))
    else:
        items.append(MassItem(
            name='Wing',
            mass_kg=wing_mass,
            x=wing_x,
            y=0,
            z=0
        ))
    
    # Tail (traditional and VTOL)
    if config_type in ['traditional', 'vtol']:
        tail_mass = 0.030  # Typical
        tail_x = fuselage.length * 0.9
        items.append(MassItem(
            name='Tail',
            mass_kg=tail_mass,
            x=tail_x,
            y=0,
            z=0.02
        ))
    
    # Servos (distributed based on control surfaces)
    servo_mass = 0.010
    n_servos = 4 if config_type in ['traditional', 'vtol'] else 2
    
    for i in range(n_servos):
        items.append(MassItem(
            name=f'Servo_{i+1}',
            mass_kg=servo_mass,
            x=wing_x + 0.05 * i,  # Distributed
            y=0.1 * (1 if i % 2 == 0 else -1),  # Alternating sides
            z=0
        ))
    
    # VTOL-specific components
    if config_type == 'vtol':
        vtol_motor_mass = 0.055  # Larger motors for lift
        boom_positions = [
            (0.15, 0.15), (0.15, -0.15),
            (0.45, 0.15), (0.45, -0.15)
        ]
        
        for i, (bx, by) in enumerate(boom_positions):
            items.append(MassItem(
                name=f'VTOL_Motor_{i+1}',
                mass_kg=vtol_motor_mass,
                x=wing_x + bx,
                y=by,
                z=0.05
            ))
            items.append(MassItem(
                name=f'VTOL_Prop_{i+1}',
                mass_kg=0.015,
                x=wing_x + bx,
                y=by,
                z=0.08
            ))
            items.append(MassItem(
                name=f'VTOL_ESC_{i+1}',
                mass_kg=0.015,
                x=wing_x + bx - 0.03,
                y=by,
                z=0.02
            ))
    
    # Wiring harness
    items.append(MassItem(
        name='Wiring',
        mass_kg=0.025,
        x=fuselage.length * 0.5,
        y=0,
        z=0
    ))
    
    return items
```

### 10.2 Neutral Point and Static Stability

```python
def calculate_neutral_point(
    wing_geometry: WingGeometry,
    fuselage_geometry: FuselageDesign,
    config_type: str,
    tail_geometry: dict = None
) -> dict:
    """
    Calculate the neutral point (aerodynamic center of the aircraft).
    
    The neutral point is where the pitching moment is independent of AOA.
    CG must be forward of neutral point for static stability.
    
    Returns dict with neutral point location and stability derivatives.
    """
    # Wing aerodynamic center (approximately at quarter chord of MAC)
    mac = wing_geometry.mac
    sweep_qc = wing_geometry.sweep_quarter_chord_deg
    
    # Sweep shifts AC aft
    # x_ac = 0.25 * MAC for unswept wing
    # Shifts aft approximately 0.38 * tan(sweep) * MAC
    sweep_shift = 0.38 * np.tan(np.radians(sweep_qc)) * mac
    wing_ac_x = wing_geometry.mac_x_position + 0.25 * mac + sweep_shift
    
    if config_type == 'flying_wing':
        # Flying wing: AC is the neutral point (no tail)
        # But sweep and reflex affect it
        np_x = wing_ac_x
        
        # Flying wing stability comes from sweep and reflex
        # Reflex airfoil provides nose-up pitching moment
        cm_alpha_wing = -0.1 * np.cos(np.radians(sweep_qc))  # Negative = stable
        
        return {
            'neutral_point_x': np_x,
            'wing_ac_x': wing_ac_x,
            'cm_alpha': cm_alpha_wing,
            'volume_ratio': 0,  # No tail
            'static_margin_per_mac': 0  # Set by CG position
        }
    
    elif config_type == 'tandem':
        # Tandem: effective neutral point between two wings
        # Weighted by lift share and moment arm
        front_area = wing_geometry.area  # Assuming front wing geometry passed
        rear_area = tail_geometry['area'] if tail_geometry else front_area * 0.9
        
        front_x = wing_ac_x
        rear_x = front_x + tail_geometry.get('stagger', 0.4)
        
        # Lift share (approximately proportional to area)
        total_area = front_area + rear_area
        front_lift_share = front_area / total_area
        rear_lift_share = rear_area / total_area
        
        # Neutral point is lift-weighted average
        np_x = front_x * front_lift_share + rear_x * rear_lift_share
        
        # Tandem stability from wing decalage and stagger
        moment_arm = rear_x - front_x
        cm_alpha = -rear_lift_share * moment_arm / mac * 0.1
        
        return {
            'neutral_point_x': np_x,
            'front_ac_x': front_x,
            'rear_ac_x': rear_x,
            'cm_alpha': cm_alpha,
            'lift_share_front': front_lift_share,
            'lift_share_rear': rear_lift_share
        }
    
    else:  # Traditional or VTOL
        # Neutral point from wing + tail contribution
        tail_area = tail_geometry['h_tail_area'] if tail_geometry else 0.02
        tail_arm = tail_geometry.get('tail_arm', fuselage_geometry.length * 0.5)
        tail_x = wing_ac_x + tail_arm
        
        # Tail volume ratio
        v_h = (tail_area * tail_arm) / (wing_geometry.area * mac)
        
        # Tail lift curve slope (reduced by downwash)
        a_t = 0.08  # per degree, typical for tail
        downwash_factor = 0.4  # Tail sees reduced angle change
        a_t_effective = a_t * (1 - downwash_factor)
        
        # Wing lift curve slope
        ar = wing_geometry.aspect_ratio
        a_w = 2 * np.pi * ar / (ar + 2)  # per radian
        a_w_deg = a_w / 57.3  # per degree
        
        # Neutral point shift due to tail
        # x_np = x_ac_wing + V_h * (a_t/a_w) * (1 - de/da) * l_t
        np_shift = v_h * (a_t_effective / a_w_deg) * tail_arm
        np_x = wing_ac_x + np_shift
        
        # Pitch stability derivative
        cm_alpha = -v_h * a_t_effective * (1 - downwash_factor)
        
        return {
            'neutral_point_x': np_x,
            'wing_ac_x': wing_ac_x,
            'tail_ac_x': tail_x,
            'cm_alpha': cm_alpha,
            'tail_volume_ratio': v_h,
            'downwash_factor': downwash_factor
        }


def calculate_static_margin(
    cg_x: float,
    neutral_point_x: float,
    mac: float
) -> float:
    """
    Calculate static margin as percentage of MAC.
    
    Static Margin = (x_np - x_cg) / MAC * 100
    
    Positive = stable (CG forward of NP)
    Typical range: 5-15% for stability with reasonable control authority
    
    Too much SM (>20%): Hard to rotate, needs large elevator
    Too little SM (<5%): Twitchy, may be unstable
    Negative SM: Unstable, requires active stabilization
    """
    static_margin = (neutral_point_x - cg_x) / mac * 100
    return static_margin


def calculate_cg_limits(
    neutral_point_x: float,
    mac: float,
    wing_geometry: WingGeometry,
    tail_geometry: dict,
    config_type: str
) -> dict:
    """
    Calculate allowable CG range.
    
    Forward limit: Elevator authority to rotate for landing
    Aft limit: Minimum static margin for stability
    """
    # Aft limit: minimum 5% static margin (more for flying wing)
    if config_type == 'flying_wing':
        min_sm = 0.10  # Flying wings need more margin
    else:
        min_sm = 0.05
    
    aft_limit = neutral_point_x - min_sm * mac
    
    # Forward limit: elevator must be able to trim at stall speed
    # Simplified: assume forward limit is 25% MAC ahead of neutral point
    if config_type == 'flying_wing':
        forward_limit = neutral_point_x - 0.20 * mac  # Limited control authority
    else:
        forward_limit = neutral_point_x - 0.35 * mac  # Tail provides authority
    
    return {
        'forward_limit_x': forward_limit,
        'aft_limit_x': aft_limit,
        'forward_limit_mac_percent': (forward_limit - wing_geometry.mac_x_position) / mac * 100,
        'aft_limit_mac_percent': (aft_limit - wing_geometry.mac_x_position) / mac * 100,
        'cg_range_mac_percent': (aft_limit - forward_limit) / mac * 100
    }
```

### 10.3 Stability Derivatives and Dynamic Modes

```python
@dataclass
class StabilityDerivatives:
    """Dimensional stability derivatives"""
    # Longitudinal
    Xu: float = 0    # Speed damping
    Xw: float = 0    # 
    Zu: float = 0    # Speed-lift coupling
    Zw: float = 0    # Lift curve slope effect
    Zq: float = 0    # Pitch rate lift
    Mu: float = 0    # Speed-pitch coupling
    Mw: float = 0    # Pitch stiffness (cm_alpha)
    Mq: float = 0    # Pitch damping
    
    # Lateral-Directional
    Yv: float = 0    # Sideslip force
    Yp: float = 0    # Roll-sideslip coupling
    Yr: float = 0    # Yaw-sideslip coupling
    Lv: float = 0    # Dihedral effect (Cl_beta)
    Lp: float = 0    # Roll damping
    Lr: float = 0    # Roll-yaw coupling
    Nv: float = 0    # Weathercock (Cn_beta)
    Np: float = 0    # Adverse yaw
    Nr: float = 0    # Yaw damping


def calculate_stability_derivatives(
    wing: WingGeometry,
    cg: CGResult,
    velocity: float,
    altitude: float = 0
) -> StabilityDerivatives:
    """
    Calculate dimensional stability derivatives.
    
    These derivatives describe how forces and moments change with
    aircraft state variables (velocity, angular rates, etc.)
    """
    derivs = StabilityDerivatives()
    
    # Air properties
    rho = 1.225 * np.exp(-altitude / 8500)  # Simple atmosphere model
    q = 0.5 * rho * velocity**2
    
    S = wing.area
    b = wing.span
    c = wing.mac
    
    mass = cg.total_mass_kg
    
    # Lift curve slope
    AR = wing.aspect_ratio
    a = 2 * np.pi * AR / (AR + 2)  # per radian
    
    # Longitudinal derivatives
    CL = mass * 9.81 / (q * S)  # Trim lift coefficient
    CD = 0.02 + CL**2 / (np.pi * AR * 0.8)  # Estimate
    
    # Xu = -2 * CD * q * S / (m * V)
    derivs.Xu = -2 * CD * q * S / (mass * velocity)
    
    # Zw = -a * q * S / (m * V)  (lift curve slope effect)
    derivs.Zw = -a * q * S / (mass * velocity)
    
    # Mw = Cm_alpha * q * S * c / (Iyy * V)
    cm_alpha = -0.5  # Typical stable value, per radian
    derivs.Mw = cm_alpha * q * S * c / (cg.iyy * velocity)
    
    # Mq = Cm_q * q * S * c^2 / (2 * Iyy * V)
    cm_q = -15  # Typical pitch damping, per radian
    derivs.Mq = cm_q * q * S * c**2 / (2 * cg.iyy * velocity)
    
    # Lateral derivatives
    # Lv (dihedral effect)
    cl_beta = -0.1 * np.radians(wing.dihedral_deg)  # per radian sideslip
    derivs.Lv = cl_beta * q * S * b / cg.ixx
    
    # Lp (roll damping)
    cl_p = -0.4  # Typical, per radian
    derivs.Lp = cl_p * q * S * b**2 / (2 * cg.ixx * velocity)
    
    # Nv (weathercock stability)
    cn_beta = 0.05  # Typical, per radian (from vertical tail)
    derivs.Nv = cn_beta * q * S * b / cg.izz
    
    # Nr (yaw damping)
    cn_r = -0.1  # Typical, per radian
    derivs.Nr = cn_r * q * S * b**2 / (2 * cg.izz * velocity)
    
    return derivs


def analyze_dynamic_modes(
    derivs: StabilityDerivatives,
    cg: CGResult,
    velocity: float
) -> dict:
    """
    Analyze aircraft dynamic modes from stability derivatives.
    
    Longitudinal modes:
    - Phugoid: Long-period oscillation in speed/altitude
    - Short period: Quick pitch oscillation
    
    Lateral modes:
    - Dutch roll: Coupled yaw-roll oscillation
    - Roll subsidence: Pure roll damping
    - Spiral: Slow divergence/convergence in bank
    """
    modes = {}
    
    # Short period approximation
    # omega_sp = sqrt(-Mw * Zw - Mq * Zw / V)
    # Simplified: omega_sp ≈ sqrt(-Mw * V)
    omega_sp = np.sqrt(max(0.01, -derivs.Mw * velocity))
    zeta_sp = -derivs.Mq / (2 * omega_sp) if omega_sp > 0 else 0
    
    modes['short_period'] = {
        'frequency_hz': omega_sp / (2 * np.pi),
        'period_s': 2 * np.pi / omega_sp if omega_sp > 0 else float('inf'),
        'damping_ratio': np.clip(zeta_sp, 0, 2),
        'stable': zeta_sp > 0
    }
    
    # Phugoid approximation
    # omega_ph ≈ sqrt(2) * g / V
    g = 9.81
    omega_ph = np.sqrt(2) * g / velocity
    # zeta_ph ≈ CD / (sqrt(2) * CL)
    CL = cg.total_mass_kg * g / (0.5 * 1.225 * velocity**2 * 1)  # Rough
    CD = 0.03  # Typical cruise
    zeta_ph = CD / (np.sqrt(2) * max(CL, 0.1))
    
    modes['phugoid'] = {
        'frequency_hz': omega_ph / (2 * np.pi),
        'period_s': 2 * np.pi / omega_ph,
        'damping_ratio': np.clip(zeta_ph, 0, 1),
        'stable': zeta_ph > 0
    }
    
    # Dutch roll approximation
    # omega_dr ≈ sqrt(Nv * V)
    omega_dr = np.sqrt(max(0.01, derivs.Nv * velocity))
    zeta_dr = -derivs.Nr / (2 * omega_dr) if omega_dr > 0 else 0
    
    modes['dutch_roll'] = {
        'frequency_hz': omega_dr / (2 * np.pi),
        'period_s': 2 * np.pi / omega_dr if omega_dr > 0 else float('inf'),
        'damping_ratio': np.clip(zeta_dr, 0, 2),
        'stable': zeta_dr > 0
    }
    
    # Roll subsidence (first order)
    # tau_roll = -1 / Lp
    tau_roll = -1 / derivs.Lp if derivs.Lp < 0 else float('inf')
    
    modes['roll_subsidence'] = {
        'time_constant_s': tau_roll,
        'stable': derivs.Lp < 0
    }
    
    # Spiral mode
    # For stability: Lv * Nr > Lr * Nv
    spiral_criterion = derivs.Lv * derivs.Nr - derivs.Lr * derivs.Nv
    
    modes['spiral'] = {
        'criterion': spiral_criterion,
        'stable': spiral_criterion > 0,
        'time_to_double_s': abs(np.log(2) / spiral_criterion) if spiral_criterion != 0 else float('inf')
    }
    
    return modes
```

### 10.4 Trim Analysis

```python
def calculate_trim_state(
    weight_n: float,
    velocity: float,
    wing: WingGeometry,
    cg_x: float,
    neutral_point_x: float,
    config_type: str,
    tail_geometry: dict = None
) -> dict:
    """
    Calculate trim state: AOA and elevator deflection for level flight.
    
    At trim:
    - Lift = Weight
    - Pitching moment about CG = 0
    
    Returns trim AOA, elevator deflection, and trim drag penalty.
    """
    rho = 1.225
    q = 0.5 * rho * velocity**2
    S = wing.area
    mac = wing.mac
    
    # Required lift coefficient
    CL_required = weight_n / (q * S)
    
    # Wing pitching moment at this CL
    # Cm_ac is airfoil pitching moment (typically -0.05 to -0.1)
    cm_ac = -0.08  # Typical cambered airfoil
    
    # CG offset from AC creates moment
    static_margin = (neutral_point_x - cg_x) / mac
    cm_cg = cm_ac + CL_required * static_margin
    
    if config_type == 'flying_wing':
        # Flying wing trims with elevon deflection
        # Need to balance cm_cg with control surface moment
        
        # Elevon effectiveness (approximate)
        cm_delta_e = -0.01  # per degree
        
        # Required elevon deflection
        delta_e = -cm_cg / cm_delta_e
        
        # Elevon deflection creates drag
        # CD_trim ≈ k * delta_e^2
        k_trim = 0.0001  # Empirical
        cd_trim = k_trim * delta_e**2
        
        # AOA from lift requirement
        cl_alpha = 0.08  # per degree
        alpha_trim = CL_required / cl_alpha  # Simplified
        
    else:
        # Conventional: elevator trims the aircraft
        # Tail generates balancing moment
        
        tail_area = tail_geometry.get('h_tail_area', 0.02) if tail_geometry else 0.02
        tail_arm = tail_geometry.get('tail_arm', 0.4) if tail_geometry else 0.4
        
        # Elevator effectiveness
        tau = 0.5  # Elevator/stabilizer chord ratio effect
        a_t = 0.08  # Tail lift curve slope per degree
        cm_delta_e = -tail_area / S * tail_arm / mac * a_t * tau
        
        # Required elevator deflection
        delta_e = -cm_cg / cm_delta_e if abs(cm_delta_e) > 0.001 else 0
        
        # Trim drag from tail download/upload
        cl_tail = delta_e * a_t * tau
        cd_tail_induced = cl_tail**2 / (np.pi * 4 * 0.8)  # Low AR tail
        cd_trim = cd_tail_induced * tail_area / S
        
        # AOA
        cl_alpha = 0.08
        alpha_trim = CL_required / cl_alpha
    
    # Total trim drag coefficient
    # Add profile drag increase from deflected surface
    cd_profile_penalty = 0.001 * abs(delta_e)  # Small penalty
    cd_trim_total = cd_trim + cd_profile_penalty
    
    return {
        'alpha_trim_deg': alpha_trim,
        'elevator_deflection_deg': delta_e,
        'cl_trim': CL_required,
        'cd_trim': cd_trim_total,
        'trim_drag_n': cd_trim_total * q * S,
        'moment_balanced': abs(cm_cg + cm_delta_e * delta_e) < 0.001,
        'elevator_saturated': abs(delta_e) > 25  # Typical max deflection
    }
```

### 10.5 Lateral Stability Analysis

```python
def analyze_lateral_stability(
    wing: WingGeometry,
    fuselage: FuselageDesign,
    tail_geometry: dict,
    velocity: float,
    config_type: str
) -> dict:
    """
    Analyze lateral-directional stability.
    
    Key parameters:
    - Cl_beta (dihedral effect): Roll moment due to sideslip
    - Cn_beta (weathercock): Yaw moment due to sideslip
    
    For stability: Cn_beta > 0 (positive weathercock)
                   Cl_beta < 0 (negative dihedral effect)
    """
    results = {}
    
    # Dihedral effect contributions
    # 1. Geometric dihedral
    cl_beta_dihedral = -0.0002 * wing.dihedral_deg  # per degree sideslip, per degree dihedral
    
    # 2. Wing sweep contribution (sweep adds effective dihedral)
    cl_beta_sweep = -0.0001 * wing.sweep_quarter_chord_deg * wing.aspect_ratio / 10
    
    # 3. Wing position (high wing adds dihedral effect)
    wing_height = 0  # Assume mid-wing for now
    cl_beta_position = -0.0005 * wing_height / fuselage.height
    
    cl_beta_total = cl_beta_dihedral + cl_beta_sweep + cl_beta_position
    
    results['cl_beta'] = {
        'total': cl_beta_total,
        'dihedral_contribution': cl_beta_dihedral,
        'sweep_contribution': cl_beta_sweep,
        'position_contribution': cl_beta_position,
        'stable': cl_beta_total < 0
    }
    
    # Weathercock stability
    if config_type == 'flying_wing':
        # Flying wing relies on winglets or split elevons for yaw stability
        winglet_area = wing.winglet_height * wing.chord_tip * 0.5 * 2  # Both sides
        cn_beta = 0.001 * winglet_area / wing.area
    else:
        # Vertical tail contribution
        v_tail_area = tail_geometry.get('v_tail_area', 0.01)
        v_tail_arm = tail_geometry.get('v_tail_arm', fuselage.length * 0.8)
        
        cn_beta_tail = 0.05 * (v_tail_area / wing.area) * (v_tail_arm / wing.span)
        
        # Fuselage destabilizing effect
        cn_beta_fuse = -0.01 * (fuselage.length / wing.span)
        
        cn_beta = cn_beta_tail + cn_beta_fuse
    
    results['cn_beta'] = {
        'total': cn_beta,
        'stable': cn_beta > 0
    }
    
    # Dutch roll stability criterion
    # Want: Cn_beta > 0 and Cl_beta * Cn_beta < some_limit
    dutch_roll_criterion = cl_beta_total * cn_beta
    
    results['dutch_roll'] = {
        'criterion': dutch_roll_criterion,
        'stable': cn_beta > 0 and dutch_roll_criterion < 0
    }
    
    # Spiral stability criterion
    # For stability: Cl_beta * Cn_r > Cl_r * Cn_beta (approximately)
    # Simplified check: need enough dihedral relative to weathercock
    spiral_ratio = abs(cl_beta_total / cn_beta) if cn_beta != 0 else 0
    
    results['spiral'] = {
        'dihedral_weathercock_ratio': spiral_ratio,
        'likely_stable': 0.1 < spiral_ratio < 0.5
    }
    
    return results
```

---

## PART 11: CONTROL SURFACE SIZING

### 11.1 Elevator Sizing

```python
def size_elevator(
    wing: WingGeometry,
    cg_limits: dict,
    stall_speed: float,
    cruise_speed: float,
    weight_n: float
) -> dict:
    """
    Size elevator for adequate control authority.
    
    Requirements:
    1. Able to trim at all speeds in CG range
    2. Able to rotate for takeoff at forward CG
    3. Able to flare for landing
    4. Adequate pitch response
    """
    mac = wing.mac
    S = wing.area
    
    # Most critical case: forward CG at low speed
    forward_cg = cg_limits['forward_limit_x']
    
    # Required pitching moment coefficient at stall
    rho = 1.225
    q_stall = 0.5 * rho * stall_speed**2
    cl_stall = weight_n / (q_stall * S)
    
    # Moment to overcome with forward CG
    # Needs to generate enough nose-up moment to rotate
    cm_required = 0.3  # Typical rotation requirement
    
    # Elevator sizing
    # Cm_delta_e = -V_h * a_t * tau * (1 - de/da)
    # where V_h = S_t * l_t / (S * c)
    
    # Target: achieve cm_required with 20 deg elevator deflection
    max_deflection = 20  # degrees
    
    # Solve for required tail volume
    a_t = 0.08  # Tail lift curve slope, per degree
    tau = 0.5  # Elevator effectiveness factor
    downwash = 0.4
    
    cm_per_deg = cm_required / max_deflection
    v_h_required = cm_per_deg / (a_t * tau * (1 - downwash))
    
    # Assume tail arm is 2.5 * MAC
    tail_arm = 2.5 * mac
    
    # Required tail area
    tail_area = v_h_required * S * mac / tail_arm
    
    # Elevator is typically 30-40% of stabilizer chord
    elevator_chord_ratio = 0.35
    stabilizer_chord = np.sqrt(tail_area / 2)  # Assume AR=2
    stabilizer_span = tail_area / stabilizer_chord
    elevator_area = tail_area * elevator_chord_ratio
    
    return {
        'stabilizer_area_m2': tail_area,
        'stabilizer_span_m': stabilizer_span,
        'stabilizer_chord_m': stabilizer_chord,
        'elevator_area_m2': elevator_area,
        'elevator_chord_ratio': elevator_chord_ratio,
        'tail_volume_ratio': v_h_required,
        'tail_arm_m': tail_arm,
        'max_cm_available': cm_per_deg * 25,  # At 25 deg deflection
        'authority_adequate': cm_per_deg * 25 > cm_required * 1.5
    }


def size_aileron(
    wing: WingGeometry,
    roll_rate_requirement: float = 60  # deg/s at cruise
) -> dict:
    """
    Size ailerons for roll control.
    
    Requirements:
    1. Achieve specified roll rate at cruise
    2. Counter adverse yaw
    3. Maintain control in crosswind landing
    """
    b = wing.span
    S = wing.area
    
    # Roll rate equation (simplified)
    # p = (Cl_delta_a * delta_a * q * S * b) / (2 * Ixx)
    # Rearranging for aileron sizing
    
    # Aileron typically occupies 50-70% of outboard span
    aileron_span_ratio = 0.3  # 30% of semi-span
    aileron_start = 0.6  # Start at 60% semi-span
    
    aileron_span = aileron_span_ratio * b / 2 * 2  # Both sides
    
    # Aileron chord typically 20-30% of wing chord at that station
    local_chord = wing.chord_root * (1 - 0.7 * (1 - wing.taper_ratio))  # At 70% span
    aileron_chord_ratio = 0.25
    aileron_chord = local_chord * aileron_chord_ratio
    
    aileron_area = aileron_span * aileron_chord
    
    # Rolling moment coefficient
    # Cl_delta_a ≈ 2 * a * tau * (y_bar / b) * (c_a / c) * (b_a / b)
    a = 0.08  # Wing section lift curve slope per degree
    tau = 0.45  # Aileron effectiveness
    y_bar = 0.7 * b / 2  # Average spanwise position
    
    cl_delta_a = 2 * a * tau * (y_bar / (b/2)) * aileron_chord_ratio * aileron_span_ratio
    
    # Check if roll rate achievable
    # Need to estimate Ixx for this (rough approximation)
    mass = 0.5  # kg typical
    ixx_approx = 0.1 * mass * (b/2)**2
    
    q_cruise = 0.5 * 1.225 * 15**2  # At cruise speed
    max_deflection = 20  # degrees
    
    roll_rate_achievable = (cl_delta_a * max_deflection * q_cruise * S * b) / (2 * ixx_approx)
    roll_rate_achievable = np.degrees(roll_rate_achievable)
    
    return {
        'aileron_span_m': aileron_span,
        'aileron_chord_m': aileron_chord,
        'aileron_area_m2': aileron_area,
        'aileron_span_ratio': aileron_span_ratio,
        'cl_delta_a': cl_delta_a,
        'max_roll_rate_deg_s': roll_rate_achievable,
        'authority_adequate': roll_rate_achievable > roll_rate_requirement
    }


def size_rudder(
    wing: WingGeometry,
    fuselage: FuselageDesign,
    crosswind_requirement: float = 8  # m/s crosswind capability
) -> dict:
    """
    Size rudder for directional control.
    
    Requirements:
    1. Maintain coordinated flight
    2. Counter adverse yaw from ailerons
    3. Crosswind landing capability
    4. Engine-out control (if applicable)
    """
    b = wing.span
    S = wing.area
    
    # Vertical tail sizing
    # Typical vertical tail volume coefficient: V_v = S_v * l_v / (S * b) ≈ 0.02-0.04
    v_v_target = 0.03
    
    # Tail arm (distance from CG to vertical tail AC)
    tail_arm = fuselage.length * 0.75
    
    # Required vertical tail area
    v_tail_area = v_v_target * S * b / tail_arm
    
    # Vertical tail geometry (typical AR = 1.5-2)
    v_tail_ar = 1.8
    v_tail_height = np.sqrt(v_tail_area * v_tail_ar)
    v_tail_chord = v_tail_area / v_tail_height
    
    # Rudder is typically 30-40% of fin chord
    rudder_chord_ratio = 0.35
    rudder_area = v_tail_area * rudder_chord_ratio
    
    # Yawing moment coefficient
    cn_delta_r = 0.002 * (v_tail_area / S) * (tail_arm / b)
    
    # Crosswind check: need to sideslip to align with runway
    # Sideslip angle = atan(crosswind / approach_speed)
    approach_speed = 10  # m/s
    sideslip_required = np.degrees(np.arctan(crosswind_requirement / approach_speed))
    
    # Rudder must counter the yawing moment from sideslip
    cn_beta = 0.05  # Typical weathercock stability
    rudder_deflection_needed = cn_beta * sideslip_required / cn_delta_r
    
    return {
        'v_tail_area_m2': v_tail_area,
        'v_tail_height_m': v_tail_height,
        'v_tail_chord_m': v_tail_chord,
        'rudder_area_m2': rudder_area,
        'rudder_chord_ratio': rudder_chord_ratio,
        'tail_volume_ratio': v_v_target,
        'cn_delta_r': cn_delta_r,
        'crosswind_capability_ms': crosswind_requirement,
        'max_sideslip_deg': 25 * cn_delta_r / cn_beta,  # At 25 deg rudder
        'authority_adequate': rudder_deflection_needed < 25
    }
```

---

## PART 12: STRUCTURAL ANALYSIS

### 12.1 Wing Bending Analysis

```python
def calculate_wing_bending(
    wing: WingGeometry,
    weight_n: float,
    load_factor: float = 3.8,  # FAR 23 limit load
    n_stations: int = 20
) -> dict:
    """
    Calculate wing bending loads and required spar sizing.
    
    Uses beam theory with distributed lift load.
    """
    b = wing.span
    half_span = b / 2
    
    # Spanwise stations
    y = np.linspace(0, half_span, n_stations)
    dy = y[1] - y[0]
    
    # Chord distribution
    chord = wing.chord_root * (1 - y/half_span * (1 - wing.taper_ratio))
    
    # Lift distribution (assume elliptical for now)
    # Could use twist distribution from earlier
    eta = y / half_span
    lift_distribution = (4 * weight_n * load_factor) / (np.pi * b) * np.sqrt(1 - eta**2)
    
    # Shear force (integral of lift outboard)
    shear = np.zeros_like(y)
    for i in range(n_stations - 1):
        shear[i] = np.trapz(lift_distribution[i:], y[i:])
    
    # Bending moment (integral of shear outboard)
    moment = np.zeros_like(y)
    for i in range(n_stations - 1):
        moment[i] = np.trapz(shear[i:], y[i:])
    
    # Maximum bending moment at root
    max_moment = moment[0]
    
    # Spar sizing
    # Assume rectangular spar, height = 60% of max airfoil thickness
    thickness_ratio = 0.10  # Typical airfoil
    spar_height = chord[0] * thickness_ratio * 0.6
    
    # Required spar width for given stress limit
    # sigma = M * c / I, where I = (1/12) * b * h^3 for rectangle
    # Rearranging: b = 6 * M / (sigma * h^2)
    
    # LW-PLA properties
    sigma_allow = 25e6  # Pa (25 MPa for LW-PLA, with safety factor)
    
    spar_width = 6 * max_moment / (sigma_allow * spar_height**2)
    spar_width = max(spar_width, 0.002)  # Minimum 2mm
    
    # Spar weight
    spar_volume = spar_width * spar_height * half_span * 2  # Both wings
    spar_density = 500  # kg/m^3 for LW-PLA
    spar_weight = spar_volume * spar_density
    
    # Tip deflection (cantilever beam approximation)
    E = 1.5e9  # Pa, LW-PLA modulus
    I = (1/12) * spar_width * spar_height**3
    
    # Simplified: uniform load approximation
    w = weight_n * load_factor / b  # N/m
    tip_deflection = w * half_span**4 / (8 * E * I)
    
    return {
        'max_bending_moment_nm': max_moment,
        'max_shear_n': shear[0],
        'spar_height_m': spar_height,
        'spar_width_m': spar_width,
        'spar_weight_kg': spar_weight,
        'tip_deflection_m': tip_deflection,
        'tip_deflection_percent_span': tip_deflection / half_span * 100,
        'load_factor': load_factor,
        'bending_distribution': moment,
        'shear_distribution': shear,
        'spanwise_stations': y
    }


def calculate_torsional_loads(
    wing: WingGeometry,
    velocity_max: float,
    cm_airfoil: float = -0.08
) -> dict:
    """
    Calculate wing torsional loads and stiffness requirements.
    
    Torsion comes from:
    1. Airfoil pitching moment
    2. Offset between shear center and aerodynamic center
    """
    q = 0.5 * 1.225 * velocity_max**2
    
    chord = wing.chord_root  # Use root for conservative estimate
    
    # Pitching moment creates torsion
    # T_aero = Cm * q * c^2 per unit span
    torque_per_span = cm_airfoil * q * chord**2
    
    # Total torsion at root
    total_torque = torque_per_span * wing.span / 2
    
    # Torsional stiffness requirement
    # Limit twist to 2 degrees at tip for flutter margin
    max_twist_rad = np.radians(2)
    
    # GJ = T * L / theta
    required_gj = total_torque * (wing.span / 2) / max_twist_rad
    
    # For a thin-walled closed section (D-box spar)
    # GJ = 4 * A^2 * G * t / p
    # where A = enclosed area, t = wall thickness, p = perimeter
    
    G = 0.5e9  # Shear modulus for LW-PLA
    
    # Assume D-box is 25% chord deep, 10% chord tall
    dbox_width = 0.25 * chord
    dbox_height = 0.10 * chord
    enclosed_area = dbox_width * dbox_height
    perimeter = 2 * (dbox_width + dbox_height)
    
    # Required wall thickness
    wall_thickness = required_gj * perimeter / (4 * enclosed_area**2 * G)
    wall_thickness = max(wall_thickness, 0.001)  # Minimum 1mm
    
    # Weight of torsion box
    tbox_volume = perimeter * wall_thickness * wing.span
    tbox_weight = tbox_volume * 500  # kg
    
    return {
        'total_torque_nm': total_torque,
        'required_gj_nm2': required_gj,
        'dbox_width_m': dbox_width,
        'dbox_height_m': dbox_height,
        'wall_thickness_m': wall_thickness,
        'torsion_box_weight_kg': tbox_weight,
        'tip_twist_deg': np.degrees(max_twist_rad)
    }


def estimate_structural_weight(
    wing: WingGeometry,
    weight_n: float,
    load_factor: float = 3.8,
    velocity_max: float = 25
) -> dict:
    """
    Estimate total structural weight including all requirements.
    """
    bending = calculate_wing_bending(wing, weight_n, load_factor)
    torsion = calculate_torsional_loads(wing, velocity_max)
    
    # Skin weight (shell for aerodynamic shape)
    skin_thickness = 0.0008  # 0.8mm typical
    wetted_area = 2.05 * wing.area
    skin_volume = wetted_area * skin_thickness
    skin_weight = skin_volume * 300  # Lower density for skin
    
    # Rib weight (every 100mm)
    rib_spacing = 0.10
    n_ribs = int(wing.span / rib_spacing)
    rib_area = wing.mac * 0.10 * 0.002  # Approximate rib cross section
    rib_weight = n_ribs * rib_area * 500
    
    # Control surface weight (ailerons, flaps)
    control_fraction = 0.15  # 15% of wing area
    control_weight = control_fraction * wing.area * 120  # g/m^2
    
    # Hardware (hinges, servos, linkages)
    hardware_weight = 0.040  # kg
    
    total_wing_weight = (bending['spar_weight_kg'] + 
                        torsion['torsion_box_weight_kg'] +
                        skin_weight + 
                        rib_weight + 
                        control_weight +
                        hardware_weight)
    
    return {
        'spar_weight_kg': bending['spar_weight_kg'],
        'torsion_box_weight_kg': torsion['torsion_box_weight_kg'],
        'skin_weight_kg': skin_weight,
        'rib_weight_kg': rib_weight,
        'control_surface_weight_kg': control_weight,
        'hardware_weight_kg': hardware_weight,
        'total_wing_weight_kg': total_wing_weight,
        'wing_weight_per_area_kg_m2': total_wing_weight / wing.area
    }
```

---

## PART 13: PROPULSION REFINEMENTS

### 13.1 Motor/Prop Matching and Slipstream

```python
@dataclass
class PropellerData:
    """Real propeller test data structure"""
    name: str
    diameter_in: float
    pitch_in: float
    
    # Test data at various advance ratios
    advance_ratios: np.ndarray    # J = V / (n * D)
    ct_values: np.ndarray         # Thrust coefficient
    cp_values: np.ndarray         # Power coefficient
    efficiency: np.ndarray        # eta = J * CT / CP


# Example propeller database entry
APC_PROPS = {
    '10x7E': PropellerData(
        name='APC 10x7E',
        diameter_in=10,
        pitch_in=7,
        advance_ratios=np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]),
        ct_values=np.array([0.115, 0.110, 0.100, 0.088, 0.073, 0.055, 0.035, 0.012, -0.015]),
        cp_values=np.array([0.045, 0.044, 0.042, 0.039, 0.035, 0.030, 0.024, 0.017, 0.010]),
        efficiency=np.array([0.0, 0.25, 0.48, 0.68, 0.83, 0.92, 0.88, 0.49, 0.0])
    ),
    '11x7E': PropellerData(
        name='APC 11x7E',
        diameter_in=11,
        pitch_in=7,
        advance_ratios=np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]),
        ct_values=np.array([0.118, 0.113, 0.103, 0.091, 0.076, 0.058, 0.038, 0.015, -0.012]),
        cp_values=np.array([0.048, 0.047, 0.045, 0.042, 0.038, 0.033, 0.027, 0.019, 0.012]),
        efficiency=np.array([0.0, 0.24, 0.46, 0.65, 0.80, 0.88, 0.84, 0.55, 0.0])
    )
}


def interpolate_propeller_performance(
    prop: PropellerData,
    advance_ratio: float
) -> tuple:
    """
    Interpolate propeller coefficients at given advance ratio.
    
    Returns (CT, CP, efficiency)
    """
    ct = np.interp(advance_ratio, prop.advance_ratios, prop.ct_values)
    cp = np.interp(advance_ratio, prop.advance_ratios, prop.cp_values)
    eta = np.interp(advance_ratio, prop.advance_ratios, prop.efficiency)
    
    return ct, cp, eta


def calculate_propeller_performance(
    prop: PropellerData,
    rpm: float,
    velocity: float,
    altitude: float = 0
) -> dict:
    """
    Calculate propeller thrust and power at operating point.
    """
    rho = 1.225 * np.exp(-altitude / 8500)
    
    D = prop.diameter_in * 0.0254  # Convert to meters
    n = rpm / 60  # Rev per second
    
    # Advance ratio
    J = velocity / (n * D) if n > 0 else 0
    
    # Get coefficients
    CT, CP, eta = interpolate_propeller_performance(prop, J)
    
    # Thrust and power
    thrust = CT * rho * n**2 * D**4
    power = CP * rho * n**3 * D**5
    
    # Torque
    torque = power / (2 * np.pi * n) if n > 0 else 0
    
    return {
        'thrust_n': thrust,
        'power_w': power,
        'torque_nm': torque,
        'efficiency': eta,
        'advance_ratio': J,
        'rpm': rpm,
        'tip_speed_ms': np.pi * D * n
    }


def find_motor_prop_operating_point(
    motor_kv: float,
    motor_rm: float,  # Phase resistance in ohms
    motor_i0: float,  # No-load current
    prop: PropellerData,
    voltage: float,
    thrust_required: float,
    velocity: float
) -> dict:
    """
    Find the equilibrium operating point where motor torque = prop torque.
    
    Uses iterative solver to find RPM where system is balanced.
    """
    D = prop.diameter_in * 0.0254
    rho = 1.225
    
    def torque_balance(rpm):
        """Returns torque imbalance (motor - prop)"""
        # Motor torque
        back_emf = rpm / motor_kv
        current = (voltage - back_emf) / motor_rm
        current = max(current, motor_i0)  # Can't be less than no-load
        motor_torque = (current - motor_i0) / motor_kv * 60 / (2 * np.pi)
        
        # Prop torque
        n = rpm / 60
        J = velocity / (n * D) if n > 0 else 0
        CT, CP, eta = interpolate_propeller_performance(prop, J)
        prop_torque = CP * rho * n**2 * D**5 / (2 * np.pi)
        
        return motor_torque - prop_torque
    
    # Find equilibrium RPM
    from scipy.optimize import brentq
    
    rpm_max = voltage * motor_kv * 0.95
    rpm_min = 1000
    
    try:
        rpm_eq = brentq(torque_balance, rpm_min, rpm_max)
    except ValueError:
        rpm_eq = rpm_max * 0.8  # Fallback
    
    # Get performance at equilibrium
    n = rpm_eq / 60
    J = velocity / (n * D) if n > 0 else 0
    CT, CP, eta = interpolate_propeller_performance(prop, J)
    
    thrust = CT * rho * n**2 * D**4
    shaft_power = CP * rho * n**3 * D**5
    
    # Motor electrical
    back_emf = rpm_eq / motor_kv
    current = (voltage - back_emf) / motor_rm
    electrical_power = voltage * current
    motor_efficiency = shaft_power / electrical_power if electrical_power > 0 else 0
    
    return {
        'rpm': rpm_eq,
        'thrust_n': thrust,
        'shaft_power_w': shaft_power,
        'electrical_power_w': electrical_power,
        'current_a': current,
        'motor_efficiency': motor_efficiency,
        'prop_efficiency': eta,
        'system_efficiency': motor_efficiency * eta,
        'thrust_meets_requirement': thrust >= thrust_required * 0.95
    }


def calculate_slipstream_effect(
    prop_diameter: float,
    prop_thrust: float,
    wing_chord: float,
    wing_span: float,
    velocity: float
) -> dict:
    """
    Calculate propeller slipstream effect on wing.
    
    The propeller accelerates air, increasing dynamic pressure
    over the portion of wing in the slipstream.
    """
    rho = 1.225
    
    # Slipstream diameter (contracts slightly)
    slipstream_diameter = prop_diameter * 0.95
    
    # Slipstream velocity from momentum theory
    # T = m_dot * (V_slip - V_inf)
    # m_dot = rho * A_prop * (V_inf + V_slip) / 2
    # Solving: V_slip = V_inf * (1 + sqrt(1 + 2*T/(rho*A*V^2)))
    A_prop = np.pi * (prop_diameter / 2)**2
    
    if velocity > 0:
        term = 1 + 2 * prop_thrust / (rho * A_prop * velocity**2)
        v_ratio = (1 + np.sqrt(max(1, term))) / 2
        v_slipstream = velocity * v_ratio
    else:
        # Static case
        v_slipstream = np.sqrt(2 * prop_thrust / (rho * A_prop))
    
    # Dynamic pressure ratio
    q_ratio = (v_slipstream / velocity)**2 if velocity > 0 else 1
    
    # Fraction of wing span in slipstream
    span_in_slip = min(slipstream_diameter / wing_span, 1.0)
    
    # Effective dynamic pressure increase (blended)
    q_effective_ratio = 1 + (q_ratio - 1) * span_in_slip
    
    # This increases both lift and drag on the affected portion
    # Net effect on L/D depends on configuration
    
    return {
        'slipstream_velocity_ms': v_slipstream,
        'velocity_ratio': v_slipstream / velocity if velocity > 0 else float('inf'),
        'dynamic_pressure_ratio': q_ratio,
        'span_fraction_in_slipstream': span_in_slip,
        'effective_q_increase_percent': (q_effective_ratio - 1) * 100
    }
```

### 13.2 Motor Thermal Model

```python
@dataclass
class MotorThermal:
    """Motor thermal parameters"""
    # Thermal resistances (C/W)
    r_winding_case: float = 8.0     # Winding to case
    r_case_ambient: float = 25.0    # Case to ambient (natural convection)
    r_case_ambient_forced: float = 10.0  # With prop airflow
    
    # Thermal capacitances (J/C)
    c_winding: float = 5.0
    c_case: float = 20.0
    
    # Limits
    t_winding_max: float = 150.0    # C, typical enamel wire limit
    t_case_max: float = 80.0        # C, typical for handling
    
    # Ambient
    t_ambient: float = 25.0


def calculate_motor_thermal(
    electrical_power: float,
    shaft_power: float,
    motor_thermal: MotorThermal,
    airspeed: float,
    duration_s: float = float('inf')
) -> dict:
    """
    Calculate motor temperatures during operation.
    
    Heat generated = electrical_power - shaft_power (copper + iron losses)
    """
    # Heat generated
    losses = electrical_power - shaft_power
    
    # Copper losses dominate at high current, iron losses at high RPM
    # Simplified: assume all losses heat the winding
    
    # Thermal resistance to ambient (affected by airspeed)
    # Forced convection from prop wash
    if airspeed > 5:
        r_case_amb = motor_thermal.r_case_ambient_forced
    else:
        r_case_amb = motor_thermal.r_case_ambient
    
    # Total thermal resistance
    r_total = motor_thermal.r_winding_case + r_case_amb
    
    # Steady state temperatures
    t_winding_ss = motor_thermal.t_ambient + losses * r_total
    t_case_ss = motor_thermal.t_ambient + losses * r_case_amb
    
    # Time constant for winding
    tau_winding = motor_thermal.c_winding * motor_thermal.r_winding_case
    
    # Temperature at given duration (if not steady state)
    if duration_s < float('inf'):
        t_winding = motor_thermal.t_ambient + (t_winding_ss - motor_thermal.t_ambient) * (1 - np.exp(-duration_s / tau_winding))
    else:
        t_winding = t_winding_ss
    
    # Efficiency derating due to temperature
    # Copper resistance increases ~0.4% per C
    temp_rise = t_winding - 25
    resistance_factor = 1 + 0.004 * temp_rise
    efficiency_derating = 1 / resistance_factor
    
    return {
        'winding_temperature_c': t_winding,
        'case_temperature_c': t_case_ss,
        'power_dissipation_w': losses,
        'thermal_time_constant_s': tau_winding,
        'efficiency_derating': efficiency_derating,
        'winding_ok': t_winding < motor_thermal.t_winding_max,
        'case_ok': t_case_ss < motor_thermal.t_case_max,
        'continuous_rating_ok': t_winding_ss < motor_thermal.t_winding_max
    }
```

---

## PART 14: BATTERY PHYSICS

### 14.1 Peukert Effect and Discharge Modeling

```python
def calculate_peukert_capacity(
    nominal_capacity_ah: float,
    discharge_rate_c: float,
    peukert_exponent: float = 1.05
) -> float:
    """
    Calculate effective capacity accounting for Peukert effect.
    
    Higher discharge rates reduce effective capacity.
    
    Effective_Ah = Nominal_Ah * (C_nominal / C_actual)^(k-1)
    
    For lithium cells, k is typically 1.02-1.10
    Molicel P50B is relatively flat, k ≈ 1.05
    """
    # Reference rate is usually 0.2C for capacity rating
    c_reference = 0.2
    
    if discharge_rate_c <= c_reference:
        return nominal_capacity_ah
    
    # Peukert equation
    capacity_factor = (c_reference / discharge_rate_c) ** (peukert_exponent - 1)
    effective_capacity = nominal_capacity_ah * capacity_factor
    
    return effective_capacity


def molicel_p50b_ocv(soc: float) -> float:
    """
    Open circuit voltage vs SOC for Molicel P50B.
    
    Based on typical Li-ion NMC chemistry curve.
    """
    # Polynomial fit to datasheet curve
    # SOC from 0 to 1
    soc = np.clip(soc, 0, 1)
    
    # Piecewise linear approximation
    ocv_table = [
        (0.00, 2.50),
        (0.05, 3.00),
        (0.10, 3.30),
        (0.20, 3.50),
        (0.30, 3.60),
        (0.50, 3.65),
        (0.70, 3.75),
        (0.80, 3.85),
        (0.90, 4.00),
        (0.95, 4.10),
        (1.00, 4.20)
    ]
    
    socs = [p[0] for p in ocv_table]
    voltages = [p[1] for p in ocv_table]
    
    return np.interp(soc, socs, voltages)


def molicel_p50b_internal_resistance(
    soc: float,
    temperature_c: float = 25
) -> float:
    """
    Internal resistance vs SOC and temperature for P50B.
    
    IR increases at low SOC and low temperature.
    """
    # Base IR at 25C, 50% SOC
    ir_base = 0.015  # 15 milliohms
    
    # SOC factor (IR increases at low and high SOC)
    soc_factor = 1 + 0.3 * (1 - soc)**2 + 0.1 * soc**2
    
    # Temperature factor (IR increases at low temp)
    # Roughly doubles from 25C to 0C
    if temperature_c < 25:
        temp_factor = 1 + 0.04 * (25 - temperature_c)
    else:
        temp_factor = 1 - 0.005 * (temperature_c - 25)
    temp_factor = max(0.8, temp_factor)
    
    return ir_base * soc_factor * temp_factor


def simulate_battery_discharge(
    series: int,
    parallel: int,
    power_profile_w: list,  # List of power values over time
    dt_s: float = 1.0,
    temperature_c: float = 25,
    cutoff_voltage_per_cell: float = 3.0,
    soc_reserve: float = 0.10
) -> dict:
    """
    High-fidelity battery discharge simulation.
    
    Accounts for:
    - Voltage sag from IR
    - Peukert effect
    - Temperature effects on IR
    - Actual vs nominal capacity
    """
    cell_capacity_ah = 5.0
    pack_capacity_ah = cell_capacity_ah * parallel
    pack_capacity_as = pack_capacity_ah * 3600  # Amp-seconds
    
    # Initialize
    soc = 1.0
    charge_used_as = 0
    time_s = 0
    
    # History
    history = {
        'time_s': [],
        'soc': [],
        'voltage': [],
        'current': [],
        'power_actual': [],
        'cell_temperature': []
    }
    
    cell_temp = temperature_c
    
    for power_w in power_profile_w:
        if soc <= soc_reserve:
            break
        
        # Get cell parameters at current state
        cell_ocv = molicel_p50b_ocv(soc)
        cell_ir = molicel_p50b_internal_resistance(soc, cell_temp)
        
        pack_ocv = series * cell_ocv
        pack_ir = series * cell_ir / parallel
        
        # Calculate current for requested power
        # P = V * I = (OCV - I*R) * I
        # I^2 * R - I * OCV + P = 0
        # Quadratic formula
        a = pack_ir
        b = -pack_ocv
        c = power_w
        
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            # Can't deliver requested power
            current = pack_ocv / (2 * pack_ir)  # Max power point
        else:
            current = (-b - np.sqrt(discriminant)) / (2*a)
        
        current = max(0, current)
        
        # Actual voltage and power
        voltage = pack_ocv - current * pack_ir
        power_actual = voltage * current
        
        # Check voltage cutoff
        if voltage < series * cutoff_voltage_per_cell:
            break
        
        # Peukert-adjusted capacity usage
        c_rate = current / pack_capacity_ah
        capacity_factor = 1 / (1 + 0.02 * max(0, c_rate - 1))  # Simplified Peukert
        
        # Update SOC
        charge_used_as += current * dt_s / capacity_factor
        soc = 1 - charge_used_as / pack_capacity_as
        
        # Simple thermal model for cell
        # Heat generated = I^2 * R
        heat_w = current**2 * pack_ir
        # Assume some cooling
        cell_temp += (heat_w * 0.1 - (cell_temp - temperature_c) * 0.05) * dt_s
        
        # Record history
        history['time_s'].append(time_s)
        history['soc'].append(soc)
        history['voltage'].append(voltage)
        history['current'].append(current)
        history['power_actual'].append(power_actual)
        history['cell_temperature'].append(cell_temp)
        
        time_s += dt_s
    
    return {
        'flight_time_s': time_s,
        'flight_time_min': time_s / 60,
        'final_soc': soc,
        'final_voltage': history['voltage'][-1] if history['voltage'] else 0,
        'energy_used_wh': charge_used_as / 3600 * series * 3.6,
        'max_temperature_c': max(history['cell_temperature']) if history['cell_temperature'] else temperature_c,
        'history': history
    }
```

---

## PART 15: FLIGHT ENVELOPE AND MISSION MODELING

### 15.1 Performance Envelope

```python
def calculate_flight_envelope(
    wing: WingGeometry,
    weight_n: float,
    drag_model: callable,
    propulsion_model: callable,
    battery_config: tuple,
    altitude: float = 0
) -> dict:
    """
    Calculate complete flight envelope.
    
    Including:
    - Stall speed
    - Max speed (power limited and structural)
    - Best climb speed and rate
    - Best endurance speed
    - Best range speed
    - Service ceiling
    """
    rho = 1.225 * np.exp(-altitude / 8500)
    S = wing.area
    
    results = {}
    
    # Stall speed
    cl_max = 1.4  # Typical with flaps
    v_stall = np.sqrt(2 * weight_n / (rho * S * cl_max))
    results['v_stall_ms'] = v_stall
    
    # Minimum power speed (best endurance)
    # Occurs at CL for minimum drag coefficient
    # For parabolic polar: CL_mp = sqrt(3 * CD0 * pi * AR * e)
    cd0 = 0.025
    ar = wing.aspect_ratio
    e = 0.8
    cl_min_power = np.sqrt(3 * cd0 * np.pi * ar * e)
    v_min_power = np.sqrt(2 * weight_n / (rho * S * cl_min_power))
    v_min_power = max(v_min_power, v_stall * 1.1)  # Stay above stall
    results['v_best_endurance_ms'] = v_min_power
    
    # Maximum range speed
    # Occurs at CL for maximum L/D
    # CL_max_LD = sqrt(CD0 * pi * AR * e)
    cl_max_ld = np.sqrt(cd0 * np.pi * ar * e)
    v_max_ld = np.sqrt(2 * weight_n / (rho * S * cl_max_ld))
    v_max_ld = max(v_max_ld, v_stall * 1.2)
    results['v_best_range_ms'] = v_max_ld
    
    # Maximum L/D
    ld_max = 0.5 * np.sqrt(np.pi * ar * e / cd0)
    results['ld_max'] = ld_max
    
    # Maximum speed (power limited)
    # Find speed where thrust available = drag
    def excess_thrust(v):
        cl = 2 * weight_n / (rho * v**2 * S)
        cd = cd0 + cl**2 / (np.pi * ar * e)
        drag = 0.5 * rho * v**2 * S * cd
        thrust_available = propulsion_model(v)['thrust_n']
        return thrust_available - drag
    
    # Binary search for max speed
    v_max = v_stall
    for v_test in np.linspace(v_stall, 50, 50):
        if excess_thrust(v_test) > 0:
            v_max = v_test
        else:
            break
    
    results['v_max_ms'] = v_max
    
    # Best climb speed and rate
    # Excess power = (T - D) * V
    def climb_rate(v):
        if v < v_stall:
            return 0
        cl = 2 * weight_n / (rho * v**2 * S)
        cd = cd0 + cl**2 / (np.pi * ar * e)
        drag = 0.5 * rho * v**2 * S * cd
        thrust = propulsion_model(v)['thrust_n']
        excess_power = (thrust - drag) * v
        return excess_power / weight_n  # m/s climb rate
    
    # Find best climb speed
    velocities = np.linspace(v_stall * 1.1, v_max, 30)
    climb_rates = [climb_rate(v) for v in velocities]
    best_climb_idx = np.argmax(climb_rates)
    
    results['v_best_climb_ms'] = velocities[best_climb_idx]
    results['max_climb_rate_ms'] = max(climb_rates)
    results['climb_angle_deg'] = np.degrees(np.arcsin(max(climb_rates) / velocities[best_climb_idx]))
    
    # Service ceiling (where climb rate = 0.5 m/s)
    # Simplified: assume climb rate scales with density
    roc_sea_level = max(climb_rates)
    if roc_sea_level > 0.5:
        # Rough estimate: ceiling where roc = 0.5 m/s
        density_ratio_at_ceiling = 0.5 / roc_sea_level
        # rho/rho0 = exp(-h/H)
        results['service_ceiling_m'] = -8500 * np.log(density_ratio_at_ceiling)
    else:
        results['service_ceiling_m'] = 0
    
    return results


def calculate_gust_loads(
    wing: WingGeometry,
    weight_n: float,
    cruise_velocity: float,
    gust_velocity: float = 7.5  # m/s (moderate gust per FAR 23)
) -> dict:
    """
    Calculate gust load factors.
    
    Sharp-edged gust formula (simplified):
    Delta_n = (rho * V * a * U_de * K_g) / (2 * W/S)
    
    where K_g is gust alleviation factor
    """
    rho = 1.225
    S = wing.area
    W_S = weight_n / S  # Wing loading
    
    # Wing lift curve slope
    ar = wing.aspect_ratio
    a = 2 * np.pi * ar / (ar + 2)  # per radian
    
    # Mass ratio (gust alleviation factor)
    c = wing.mac
    mu_g = 2 * (weight_n / 9.81) / (rho * c * a * S)
    K_g = 0.88 * mu_g / (5.3 + mu_g)
    
    # Gust load increment
    delta_n = (rho * cruise_velocity * a * gust_velocity * K_g) / (2 * W_S)
    
    # Total load factors
    n_positive = 1 + delta_n
    n_negative = 1 - delta_n
    
    return {
        'gust_velocity_ms': gust_velocity,
        'gust_alleviation_factor': K_g,
        'mass_ratio': mu_g,
        'load_increment': delta_n,
        'max_positive_g': n_positive,
        'max_negative_g': n_negative,
        'design_limit_adequate': n_positive < 3.8  # Typical limit
    }


def calculate_vn_diagram(
    wing: WingGeometry,
    weight_n: float,
    v_max_design: float,
    n_limit_positive: float = 3.8,
    n_limit_negative: float = -1.5
) -> dict:
    """
    Calculate V-n (velocity-load factor) diagram.
    
    Shows the structural flight envelope.
    """
    rho = 1.225
    S = wing.area
    
    # Stall boundaries (curved)
    cl_max_positive = 1.4
    cl_max_negative = -0.8
    
    # Positive stall line: n = rho * V^2 * S * CL_max / (2 * W)
    v_range = np.linspace(0, v_max_design * 1.2, 100)
    n_stall_positive = rho * v_range**2 * S * cl_max_positive / (2 * weight_n)
    n_stall_negative = rho * v_range**2 * S * cl_max_negative / (2 * weight_n)
    
    # Maneuvering speed (corner speed)
    v_a = np.sqrt(2 * n_limit_positive * weight_n / (rho * S * cl_max_positive))
    
    # Dive speed
    v_d = v_max_design * 1.4  # Typical
    
    return {
        'velocities': v_range.tolist(),
        'n_stall_positive': np.clip(n_stall_positive, 0, n_limit_positive).tolist(),
        'n_stall_negative': np.clip(n_stall_negative, n_limit_negative, 0).tolist(),
        'n_limit_positive': n_limit_positive,
        'n_limit_negative': n_limit_negative,
        'maneuvering_speed_ms': v_a,
        'max_operating_speed_ms': v_max_design,
        'dive_speed_ms': v_d
    }
```

### 15.2 Mission Profile Simulation

```python
@dataclass
class MissionSegment:
    """Definition of a mission segment"""
    name: str
    segment_type: str  # 'takeoff', 'climb', 'cruise', 'loiter', 'descent', 'landing'
    duration_s: float = None      # For time-based segments
    distance_m: float = None      # For distance-based segments
    altitude_start_m: float = 0
    altitude_end_m: float = 0
    speed_ms: float = None        # None = optimize


def simulate_mission(
    mission_segments: list,
    aircraft_config: dict,
    wing: WingGeometry,
    propulsion: callable,
    battery_config: tuple
) -> dict:
    """
    Simulate complete mission profile with energy accounting.
    """
    weight_n = aircraft_config['weight_n']
    S = wing.area
    
    results = {
        'segments': [],
        'total_energy_wh': 0,
        'total_time_s': 0,
        'total_distance_m': 0
    }
    
    current_soc = 1.0
    series, parallel = battery_config
    cell_capacity_ah = 5.0
    pack_energy_wh = series * parallel * cell_capacity_ah * 3.6
    
    for segment in mission_segments:
        seg_result = {'name': segment.name, 'type': segment.segment_type}
        
        rho = 1.225 * np.exp(-segment.altitude_start_m / 8500)
        
        if segment.segment_type == 'takeoff':
            # Simplified takeoff (assume VTOL or hand launch)
            energy = 5  # Wh, minimal for small UAV
            time = 10  # seconds
            distance = 10
            
        elif segment.segment_type == 'climb':
            # Climb to altitude
            altitude_gain = segment.altitude_end_m - segment.altitude_start_m
            
            # Best climb speed
            v_climb = segment.speed_ms or 12  # m/s default
            
            # Climb rate from excess power
            # Simplified: assume 2 m/s climb rate
            climb_rate = 2.0
            time = altitude_gain / climb_rate
            distance = v_climb * time
            
            # Power required for climb
            # P_climb = D*V + W*climb_rate
            cl = 2 * weight_n / (rho * v_climb**2 * S)
            cd = 0.03 + cl**2 / (np.pi * wing.aspect_ratio * 0.8)
            drag = 0.5 * rho * v_climb**2 * S * cd
            power = drag * v_climb + weight_n * climb_rate
            power /= 0.7  # Propulsion efficiency
            
            energy = power * time / 3600
            
        elif segment.segment_type == 'cruise':
            # Level cruise
            v_cruise = segment.speed_ms or 15  # m/s
            
            if segment.distance_m:
                time = segment.distance_m / v_cruise
                distance = segment.distance_m
            else:
                time = segment.duration_s
                distance = v_cruise * time
            
            # Cruise power
            cl = 2 * weight_n / (rho * v_cruise**2 * S)
            cd = 0.025 + cl**2 / (np.pi * wing.aspect_ratio * 0.8)
            drag = 0.5 * rho * v_cruise**2 * S * cd
            power = drag * v_cruise / 0.7
            
            energy = power * time / 3600
            
        elif segment.segment_type == 'loiter':
            # Minimum power loiter
            # Fly at speed for minimum power
            cl_mp = np.sqrt(3 * 0.025 * np.pi * wing.aspect_ratio * 0.8)
            v_loiter = np.sqrt(2 * weight_n / (rho * S * cl_mp))
            v_loiter = segment.speed_ms or v_loiter
            
            time = segment.duration_s
            distance = v_loiter * time
            
            cl = 2 * weight_n / (rho * v_loiter**2 * S)
            cd = 0.025 + cl**2 / (np.pi * wing.aspect_ratio * 0.8)
            drag = 0.5 * rho * v_loiter**2 * S * cd
            power = drag * v_loiter / 0.7
            
            energy = power * time / 3600
            
        elif segment.segment_type == 'descent':
            # Gliding descent (minimal power)
            altitude_loss = segment.altitude_start_m - segment.altitude_end_m
            
            # Glide at best L/D
            v_glide = segment.speed_ms or 12
            ld = 10  # Approximate L/D
            glide_angle = np.arctan(1/ld)
            
            distance = altitude_loss / np.tan(glide_angle)
            time = distance / v_glide
            
            # Idle power
            power = 5  # W, just for avionics
            energy = power * time / 3600
            
        elif segment.segment_type == 'landing':
            # Landing (VTOL or glide)
            energy = 2  # Wh
            time = 15
            distance = 20
            
        else:
            energy = 0
            time = 0
            distance = 0
        
        seg_result['energy_wh'] = energy
        seg_result['time_s'] = time
        seg_result['distance_m'] = distance
        seg_result['power_w'] = energy * 3600 / time if time > 0 else 0
        
        results['segments'].append(seg_result)
        results['total_energy_wh'] += energy
        results['total_time_s'] += time
        results['total_distance_m'] += distance
    
    # Check if mission is achievable
    usable_energy = pack_energy_wh * 0.8  # 80% DOD
    results['energy_margin_percent'] = (usable_energy - results['total_energy_wh']) / usable_energy * 100
    results['mission_achievable'] = results['total_energy_wh'] < usable_energy
    results['reserve_time_min'] = (usable_energy - results['total_energy_wh']) / (results['total_energy_wh'] / results['total_time_s'] * 60) if results['total_energy_wh'] > 0 else 0
    
    return results
```

---

## PART 16: FLYING WING SPECIFIC

### 16.1 Twist Distribution for Trim

```python
def calculate_flying_wing_twist(
    span: float,
    chord_root: float,
    chord_tip: float,
    sweep_deg: float,
    cm_airfoil: float,
    cg_percent_mac: float,
    target_cl: float = 0.5
) -> dict:
    """
    Calculate required twist distribution for trimmed flying wing.
    
    Flying wings use twist (washout) and reflex airfoils to achieve
    pitch trim without a tail. The twist creates a nose-up pitching
    moment to balance the airfoil's nose-down moment.
    """
    # For a flying wing, trim requires:
    # Cm_cg = Cm_ac + CL * (x_cg - x_ac) / MAC = 0
    
    # The aerodynamic center of a swept wing is aft of the root
    sweep_rad = np.radians(sweep_deg)
    
    # MAC calculation
    taper = chord_tip / chord_root
    mac = chord_root * (2/3) * (1 + taper + taper**2) / (1 + taper)
    
    # AC location (shifts aft with sweep)
    # For swept wing: x_ac ≈ 0.25*MAC + 0.5*span*tan(sweep)*(1+2*taper)/(3*(1+taper))
    y_mac = (span/6) * (1 + 2*taper) / (1 + taper)
    x_ac_shift = y_mac * np.tan(sweep_rad)
    x_ac = 0.25 * mac + x_ac_shift
    
    # Required moment coefficient at AC for trim
    x_cg = cg_percent_mac / 100 * mac
    cm_required = -target_cl * (x_cg - x_ac) / mac
    
    # Twist contribution to pitching moment
    # Each degree of washout at the tips reduces Cm by approximately:
    cl_alpha = 0.1  # per degree
    moment_arm = span / 4  # Approximate moment arm of tip lift change
    
    # Simplified: washout at tips reduces tip lift, creating nose-up moment
    cm_per_deg_twist = cl_alpha * moment_arm / mac * 0.5  # 0.5 for taper effect
    
    # Required twist for trim
    cm_deficit = cm_required - cm_airfoil
    twist_required = -cm_deficit / cm_per_deg_twist
    
    # Practical limits
    twist_required = np.clip(twist_required, -8, 0)  # Washout only, max 8 deg
    
    # Reflex requirement
    # If twist alone can't trim, need reflex airfoil
    cm_with_twist = cm_airfoil + cm_per_deg_twist * twist_required
    reflex_needed = cm_with_twist < cm_required * 0.9
    
    return {
        'twist_deg': twist_required,
        'twist_distribution': 'linear',  # Linear from root to tip
        'cm_airfoil': cm_airfoil,
        'cm_from_twist': cm_per_deg_twist * twist_required,
        'cm_total': cm_airfoil + cm_per_deg_twist * twist_required,
        'cm_required_for_trim': cm_required,
        'trimmed': abs(cm_airfoil + cm_per_deg_twist * twist_required - cm_required) < 0.01,
        'reflex_airfoil_recommended': reflex_needed,
        'x_ac_percent_mac': x_ac / mac * 100,
        'neutral_point_percent_mac': x_ac / mac * 100  # For flying wing, NP ≈ AC
    }


def analyze_flying_wing_stability(
    span: float,
    chord_root: float,
    taper: float,
    sweep_deg: float,
    twist_deg: float,
    cg_percent_mac: float
) -> dict:
    """
    Analyze stability characteristics specific to flying wings.
    """
    mac = chord_root * (2/3) * (1 + taper + taper**2) / (1 + taper)
    ar = span**2 / (span * chord_root * (1 + taper) / 2)
    
    # Neutral point estimation for flying wing
    # Mainly determined by sweep
    sweep_rad = np.radians(sweep_deg)
    
    # AC shift due to sweep
    y_mac = (span/6) * (1 + 2*taper) / (1 + taper)
    ac_shift = y_mac * np.tan(sweep_rad)
    
    np_percent_mac = 25 + ac_shift / mac * 100
    
    # Static margin
    static_margin = np_percent_mac - cg_percent_mac
    
    # Pitch stability derivative
    # Cm_alpha for flying wing
    cl_alpha = 2 * np.pi * ar / (ar + 2) / 57.3  # per degree
    cm_alpha = -cl_alpha * static_margin / 100  # per degree, negative = stable
    
    # Minimum sweep for stability
    # Rule of thumb: need at least 15-20 deg sweep for positive static margin
    min_sweep = np.degrees(np.arctan(0.1 * mac / y_mac)) if y_mac > 0 else 15
    
    # Pitch damping (reduced for flying wing due to short tail arm)
    cm_q = -0.5 * cl_alpha * (span / mac)**2  # Approximate
    
    return {
        'neutral_point_percent_mac': np_percent_mac,
        'static_margin_percent': static_margin,
        'cm_alpha_per_deg': cm_alpha,
        'stable': static_margin > 5,
        'minimum_sweep_for_stability_deg': min_sweep,
        'current_sweep_adequate': sweep_deg >= min_sweep,
        'pitch_damping_cm_q': cm_q,
        'recommendations': []
    }
```

### 16.2 Elevon and Yaw Control

```python
def size_elevons(
    wing: WingGeometry,
    weight_n: float,
    cg_range_percent: float = 10,
    roll_rate_requirement: float = 60  # deg/s
) -> dict:
    """
    Size elevons for flying wing pitch and roll control.
    
    Elevons must provide:
    1. Pitch trim across CG range
    2. Adequate roll rate
    3. Pitch response for maneuvering
    """
    span = wing.span
    mac = wing.mac
    S = wing.area
    
    # Elevon span (typically 60-80% of semi-span)
    elevon_span_ratio = 0.7  # 70% of each semi-span
    elevon_span = elevon_span_ratio * span  # Total (both sides)
    
    # Elevon chord (typically 20-30% of local chord)
    # Use chord at 70% span (middle of elevon)
    local_chord = wing.chord_root * (1 - 0.7 * (1 - wing.taper_ratio))
    elevon_chord_ratio = 0.25
    elevon_chord = local_chord * elevon_chord_ratio
    
    elevon_area = elevon_span * elevon_chord
    
    # Pitch effectiveness
    # Cm_delta_e = d_Cm / d_delta_e
    # For elevon: Cm_delta_e ≈ -CL_alpha * tau * (S_e/S) * (l_e/c)
    cl_alpha = 0.08  # per degree
    tau = 0.5  # Control surface effectiveness
    l_e = 0.7 * span / 2 * np.tan(np.radians(wing.sweep_le_deg))  # Moment arm
    
    cm_delta_e = -cl_alpha * tau * (elevon_area / S) * (l_e / mac)
    
    # Maximum pitching moment available
    max_deflection = 25  # degrees
    cm_max = abs(cm_delta_e) * max_deflection
    
    # Required for CG range
    cm_required = 0.3 * cg_range_percent / 10  # Rough scaling
    
    # Roll effectiveness (differential elevon)
    # Using both elevons differentially
    y_elevon = 0.7 * span / 2  # Average spanwise position
    cl_delta_a = 2 * cl_alpha * tau * elevon_chord_ratio * (y_elevon / (span/2)) * elevon_span_ratio
    
    return {
        'elevon_span_m': elevon_span,
        'elevon_chord_m': elevon_chord,
        'elevon_area_m2': elevon_area,
        'elevon_span_ratio': elevon_span_ratio,
        'elevon_chord_ratio': elevon_chord_ratio,
        'pitch_effectiveness_cm_delta': cm_delta_e,
        'max_pitch_moment_coefficient': cm_max,
        'roll_effectiveness_cl_delta': cl_delta_a,
        'pitch_authority_adequate': cm_max > cm_required,
        'max_deflection_deg': max_deflection
    }


def analyze_flying_wing_yaw_control(
    wing: WingGeometry,
    velocity: float,
    options: list = ['split_elevon', 'winglet_rudder', 'drag_differential']
) -> dict:
    """
    Analyze yaw control options for flying wing.
    
    Flying wings lack a vertical tail, requiring alternative yaw control:
    1. Split elevons (drag differential)
    2. Winglet rudders
    3. Differential spoilers
    """
    results = {}
    
    span = wing.span
    S = wing.area
    
    q = 0.5 * 1.225 * velocity**2
    
    for option in options:
        if option == 'split_elevon':
            # Split elevon creates yaw through drag differential
            # One side up (more drag), other side down (less drag)
            
            # Drag increase from deflected elevon
            deflection = 15  # degrees
            cd_deflected = 0.02 * (deflection / 15)**2  # Approximate
            
            # Yawing moment from differential drag
            y_elevon = 0.7 * span / 2
            delta_drag = cd_deflected * q * S * 0.2  # 20% of wing in elevon
            yaw_moment = delta_drag * y_elevon
            
            cn = yaw_moment / (q * S * span)
            
            results['split_elevon'] = {
                'cn_per_deg': cn / deflection,
                'max_yaw_moment_nm': yaw_moment,
                'drag_penalty': 'Moderate',
                'effectiveness': 'Low to moderate'
            }
            
        elif option == 'winglet_rudder':
            # Rudder on winglet
            if wing.winglet_height > 0:
                winglet_area = wing.winglet_height * wing.chord_tip * 0.4
                rudder_fraction = 0.35
                rudder_area = winglet_area * rudder_fraction
                
                # Yaw effectiveness
                cl_rudder = 0.05  # per degree
                yaw_arm = span / 2
                cn_delta_r = cl_rudder * (rudder_area / S) * (yaw_arm / span)
                
                results['winglet_rudder'] = {
                    'rudder_area_m2': rudder_area,
                    'cn_per_deg': cn_delta_r,
                    'drag_penalty': 'Low',
                    'effectiveness': 'Moderate to good'
                }
            else:
                results['winglet_rudder'] = {
                    'available': False,
                    'reason': 'No winglets present'
                }
                
        elif option == 'drag_differential':
            # Spoilers or split drag devices
            spoiler_area = 0.05 * S  # 5% of wing area
            cd_spoiler = 0.8  # High drag coefficient
            
            y_spoiler = 0.6 * span / 2
            drag_one_side = cd_spoiler * q * spoiler_area
            yaw_moment = drag_one_side * y_spoiler
            
            cn = yaw_moment / (q * S * span)
            
            results['drag_differential'] = {
                'cn_available': cn,
                'drag_penalty': 'High when deployed',
                'effectiveness': 'Good but inefficient'
            }
    
    return results
```

---

## PART 17: VTOL SPECIFIC

### 17.1 Transition Corridor

```python
def calculate_transition_corridor(
    wing: WingGeometry,
    weight_n: float,
    vtol_thrust_max: float,
    cruise_thrust_max: float,
    stall_speed_ms: float
) -> dict:
    """
    Calculate safe transition corridor for VTOL aircraft.
    
    The transition corridor defines the speed range where:
    - Below minimum: must use VTOL motors (wing can't support weight)
    - Above maximum: can use wing lift only
    - Between: blended lift from motors and wing
    """
    rho = 1.225
    S = wing.area
    cl_max = 1.3  # Reduced during transition (dirty config)
    
    # Minimum transition speed: wing starts generating useful lift
    # Typically 1.1-1.2 times stall speed
    v_trans_min = stall_speed_ms * 0.8  # Can start transition below stall with motor assist
    
    # Maximum transition speed: wing can support full weight
    v_trans_max = stall_speed_ms * 1.3  # Complete transition above this
    
    # Lift sharing through corridor
    velocities = np.linspace(v_trans_min, v_trans_max, 20)
    motor_lift_fraction = []
    wing_lift_fraction = []
    
    for v in velocities:
        q = 0.5 * rho * v**2
        wing_lift_available = q * S * cl_max * 0.8  # Don't use full CL_max
        wing_fraction = min(1.0, wing_lift_available / weight_n)
        motor_fraction = 1.0 - wing_fraction
        
        wing_lift_fraction.append(wing_fraction)
        motor_lift_fraction.append(motor_fraction)
    
    # Power required through transition
    power_profile = []
    for v, motor_frac in zip(velocities, motor_lift_fraction):
        # VTOL motor power (hover-like)
        vtol_power = motor_frac * weight_n * v / 0.5  # Very rough
        
        # Forward thrust power
        cl = (1 - motor_frac) * weight_n / (0.5 * rho * v**2 * S)
        cd = 0.05 + cl**2 / (np.pi * wing.aspect_ratio * 0.7)  # High drag in transition
        drag = 0.5 * rho * v**2 * S * cd
        cruise_power = drag * v / 0.7
        
        total_power = vtol_power + cruise_power
        power_profile.append(total_power)
    
    # Find most demanding point
    max_power_idx = np.argmax(power_profile)
    
    return {
        'v_transition_start_ms': v_trans_min,
        'v_transition_complete_ms': v_trans_max,
        'velocities_ms': velocities.tolist(),
        'motor_lift_fraction': motor_lift_fraction,
        'wing_lift_fraction': wing_lift_fraction,
        'power_profile_w': power_profile,
        'max_power_w': max(power_profile),
        'max_power_velocity_ms': velocities[max_power_idx],
        'transition_time_estimate_s': (v_trans_max - v_trans_min) / 2,  # At 2 m/s^2 accel
        'corridor_width_ms': v_trans_max - v_trans_min
    }


def analyze_vtol_motor_out(
    motor_positions: list,  # List of (x, y, z) tuples
    motor_thrust_max: float,
    weight_n: float,
    moment_of_inertia: dict  # {'ixx': ..., 'iyy': ..., 'izz': ...}
) -> dict:
    """
    Analyze motor-out controllability for VTOL.
    
    Can the aircraft maintain control with one motor failed?
    """
    n_motors = len(motor_positions)
    
    results = {
        'motor_positions': motor_positions,
        'motor_out_cases': []
    }
    
    for failed_motor in range(n_motors):
        # Calculate moments with one motor out
        active_motors = [i for i in range(n_motors) if i != failed_motor]
        
        # Each remaining motor at max thrust
        total_thrust = (n_motors - 1) * motor_thrust_max
        
        # Can we still support weight?
        thrust_margin = total_thrust / weight_n
        can_hover = thrust_margin > 1.0
        
        # Calculate resulting moments
        cg = np.array([0, 0, 0])  # Assume CG at origin for simplicity
        
        total_moment = np.array([0.0, 0.0, 0.0])
        for i in active_motors:
            pos = np.array(motor_positions[i])
            thrust_vec = np.array([0, 0, motor_thrust_max])  # Thrust up
            moment = np.cross(pos - cg, thrust_vec)
            total_moment += moment
        
        # Can remaining motors counter this moment?
        # Need to redistribute thrust
        # Simplified: check if moment can be zeroed by thrust differential
        
        max_roll_moment = motor_thrust_max * max(abs(p[1]) for p in motor_positions) * 2
        max_pitch_moment = motor_thrust_max * max(abs(p[0]) for p in motor_positions) * 2
        
        roll_controllable = abs(total_moment[0]) < max_roll_moment * 0.8
        pitch_controllable = abs(total_moment[1]) < max_pitch_moment * 0.8
        
        results['motor_out_cases'].append({
            'failed_motor': failed_motor,
            'thrust_margin': thrust_margin,
            'can_hover': can_hover,
            'roll_moment_nm': total_moment[0],
            'pitch_moment_nm': total_moment[1],
            'roll_controllable': roll_controllable,
            'pitch_controllable': pitch_controllable,
            'survivable': can_hover and roll_controllable and pitch_controllable
        })
    
    # Overall assessment
    results['any_motor_out_survivable'] = all(
        case['survivable'] for case in results['motor_out_cases']
    )
    
    return results


def calculate_vtol_hover_efficiency(
    motor_positions: list,
    prop_diameter: float,
    weight_n: float
) -> dict:
    """
    Calculate VTOL hover efficiency and figure of merit.
    
    Disk loading and figure of merit are key metrics for hover efficiency.
    """
    n_motors = len(motor_positions)
    
    # Total disk area
    disk_area_per_motor = np.pi * (prop_diameter / 2)**2
    total_disk_area = n_motors * disk_area_per_motor
    
    # Disk loading (thrust per unit disk area)
    thrust_per_motor = weight_n / n_motors
    disk_loading = thrust_per_motor / disk_area_per_motor  # N/m^2
    
    # Ideal hover power (momentum theory)
    rho = 1.225
    induced_velocity = np.sqrt(disk_loading / (2 * rho))
    ideal_power_per_motor = thrust_per_motor * induced_velocity
    ideal_total_power = n_motors * ideal_power_per_motor
    
    # Actual power (assume 60% figure of merit)
    figure_of_merit = 0.60  # Typical for small props
    actual_power = ideal_total_power / figure_of_merit
    
    # Hover time estimate
    # Assume battery capacity
    battery_wh = 108  # 3S2P P50B
    usable_wh = battery_wh * 0.8
    hover_time_min = usable_wh / (actual_power / 1000) * 60
    
    return {
        'n_motors': n_motors,
        'disk_area_per_motor_m2': disk_area_per_motor,
        'total_disk_area_m2': total_disk_area,
        'disk_loading_n_m2': disk_loading,
        'induced_velocity_ms': induced_velocity,
        'ideal_hover_power_w': ideal_total_power,
        'figure_of_merit': figure_of_merit,
        'actual_hover_power_w': actual_power,
        'hover_time_estimate_min': hover_time_min,
        'efficiency_rating': 'Good' if disk_loading < 200 else 'Moderate' if disk_loading < 400 else 'Poor'
    }
```

---

## PART 18: UPDATED DESIGN VARIABLE SPACE

### 18.1 Extended Variables for Optimization

```python
@dataclass
class ExtendedDesignSpace:
    """Complete design variable ranges with all enhancements"""
    
    # Basic wing geometry
    span: tuple = (0.6, 0.98)
    chord_root: tuple = (0.12, 0.35)
    taper_ratio: tuple = (0.4, 1.0)
    sweep_deg: tuple = (0, 30)
    dihedral_deg: tuple = (0, 8)
    twist_deg: tuple = (-6, 0)  # Washout
    incidence_deg: tuple = (0, 4)
    
    # Tandem-specific
    rear_span: tuple = (0.5, 0.98)
    rear_chord_root: tuple = (0.10, 0.30)
    rear_taper_ratio: tuple = (0.4, 1.0)
    rear_sweep_deg: tuple = (0, 25)
    rear_dihedral_deg: tuple = (0, 6)
    rear_incidence_deg: tuple = (-3, 3)  # Decalage
    stagger: tuple = (0.25, 0.55)
    gap: tuple = (0.04, 0.15)
    gap_angle_deg: tuple = (-10, 10)
    
    # Winglet
    winglet_height: tuple = (0, 0.08)
    winglet_cant_deg: tuple = (60, 90)
    
    # Airfoil selection (indices into airfoil database)
    airfoil_root_idx: tuple = (0, 49)
    airfoil_tip_idx: tuple = (0, 49)
    
    # Battery
    battery_series: tuple = (2, 6)
    battery_parallel: tuple = (1, 4)
    
    # Propulsion
    motor_kv: tuple = (400, 1400)
    prop_diameter: tuple = (0.20, 0.35)
    prop_pitch: tuple = (0.10, 0.25)
    
    # CG position (as fraction of allowable range)
    cg_position_fraction: tuple = (0.3, 0.7)  # Within CG limits
    
    def get_variable_count(self, config_type: str) -> int:
        """Get number of variables for configuration type"""
        base_vars = 14  # Span through prop pitch
        
        if config_type == 'tandem':
            return base_vars + 9  # Add rear wing and positioning vars
        elif config_type == 'flying_wing':
            return base_vars + 2  # Add winglet vars
        elif config_type == 'vtol':
            return base_vars + 3  # Add VTOL-specific
        else:
            return base_vars


def decode_extended_design(
    sample: np.ndarray,
    design_space: ExtendedDesignSpace,
    config_type: str,
    airfoil_list: list
) -> dict:
    """
    Decode normalized sample to full design specification.
    """
    def scale(val, bounds):
        return bounds[0] + val * (bounds[1] - bounds[0])
    
    def scale_int(val, bounds):
        return int(round(scale(val, bounds)))
    
    i = 0  # Sample index
    
    design = {}
    
    # Basic wing
    design['span'] = scale(sample[i], design_space.span); i += 1
    design['chord_root'] = scale(sample[i], design_space.chord_root); i += 1
    design['taper_ratio'] = scale(sample[i], design_space.taper_ratio); i += 1
    design['chord_tip'] = design['chord_root'] * design['taper_ratio']
    design['sweep_deg'] = scale(sample[i], design_space.sweep_deg); i += 1
    design['dihedral_deg'] = scale(sample[i], design_space.dihedral_deg); i += 1
    design['twist_deg'] = scale(sample[i], design_space.twist_deg); i += 1
    design['incidence_deg'] = scale(sample[i], design_space.incidence_deg); i += 1
    
    # Airfoils
    design['airfoil_root'] = airfoil_list[scale_int(sample[i], design_space.airfoil_root_idx) % len(airfoil_list)]; i += 1
    design['airfoil_tip'] = airfoil_list[scale_int(sample[i], design_space.airfoil_tip_idx) % len(airfoil_list)]; i += 1
    
    # Winglet
    design['winglet_height'] = scale(sample[i], design_space.winglet_height); i += 1
    design['winglet_cant_deg'] = scale(sample[i], design_space.winglet_cant_deg); i += 1
    
    # Battery
    design['battery_series'] = scale_int(sample[i], design_space.battery_series); i += 1
    design['battery_parallel'] = scale_int(sample[i], design_space.battery_parallel); i += 1
    
    # Propulsion
    design['motor_kv'] = scale(sample[i], design_space.motor_kv); i += 1
    design['prop_diameter'] = scale(sample[i], design_space.prop_diameter); i += 1
    design['prop_pitch'] = scale(sample[i], design_space.prop_pitch); i += 1
    
    # CG
    design['cg_position_fraction'] = scale(sample[i], design_space.cg_position_fraction); i += 1
    
    # Configuration-specific
    if config_type == 'tandem':
        design['rear_span'] = scale(sample[i], design_space.rear_span); i += 1
        design['rear_chord_root'] = scale(sample[i], design_space.rear_chord_root); i += 1
        design['rear_taper_ratio'] = scale(sample[i], design_space.rear_taper_ratio); i += 1
        design['rear_chord_tip'] = design['rear_chord_root'] * design['rear_taper_ratio']
        design['rear_sweep_deg'] = scale(sample[i], design_space.rear_sweep_deg); i += 1
        design['rear_dihedral_deg'] = scale(sample[i], design_space.rear_dihedral_deg); i += 1
        design['rear_incidence_deg'] = scale(sample[i], design_space.rear_incidence_deg); i += 1
        design['stagger'] = scale(sample[i], design_space.stagger); i += 1
        design['gap'] = scale(sample[i], design_space.gap); i += 1
        design['gap_angle_deg'] = scale(sample[i], design_space.gap_angle_deg); i += 1
    
    return design
```

---

## PART 19: UPDATED UI FOR NEW PARAMETERS

### 19.1 Extended Configuration Panel

Add these sections to the HTML configuration panel:

```html
<!-- Wing Geometry Section (Extended) -->
<div class="config-section">
    <h3>Wing Geometry</h3>
    <div class="input-grid">
        <label>Span Range (m):
            <div class="range-input">
                <input type="number" id="span-min" value="0.6" step="0.05" style="width:60px">
                <span>to</span>
                <input type="number" id="span-max" value="0.98" step="0.05" style="width:60px">
            </div>
        </label>
        <label>Root Chord Range (m):
            <div class="range-input">
                <input type="number" id="chord-min" value="0.12" step="0.02">
                <span>to</span>
                <input type="number" id="chord-max" value="0.35" step="0.02">
            </div>
        </label>
        <label>Taper Ratio:
            <div class="range-input">
                <input type="number" id="taper-min" value="0.4" step="0.1">
                <span>to</span>
                <input type="number" id="taper-max" value="1.0" step="0.1">
            </div>
        </label>
        <label>Sweep (deg):
            <div class="range-input">
                <input type="number" id="sweep-min" value="0" step="5">
                <span>to</span>
                <input type="number" id="sweep-max" value="30" step="5">
            </div>
        </label>
        <label>Dihedral (deg):
            <div class="range-input">
                <input type="number" id="dihedral-min" value="0" step="1">
                <span>to</span>
                <input type="number" id="dihedral-max" value="8" step="1">
            </div>
        </label>
        <label>Twist/Washout (deg):
            <div class="range-input">
                <input type="number" id="twist-min" value="-6" step="1">
                <span>to</span>
                <input type="number" id="twist-max" value="0" step="1">
            </div>
        </label>
    </div>
</div>

<!-- Tandem-Specific Section -->
<div class="config-section" id="tandem-options" style="display:none;">
    <h3>Tandem Wing Parameters</h3>
    <div class="input-grid">
        <label>Rear Span Range (m):
            <div class="range-input">
                <input type="number" id="rear-span-min" value="0.5" step="0.05">
                <span>to</span>
                <input type="number" id="rear-span-max" value="0.98" step="0.05">
            </div>
        </label>
        <label>Stagger Range (m):
            <div class="range-input">
                <input type="number" id="stagger-min" value="0.25" step="0.05">
                <span>to</span>
                <input type="number" id="stagger-max" value="0.55" step="0.05">
            </div>
        </label>
        <label>Gap Range (m):
            <div class="range-input">
                <input type="number" id="gap-min" value="0.04" step="0.02">
                <span>to</span>
                <input type="number" id="gap-max" value="0.15" step="0.02">
            </div>
        </label>
        <label>Decalage Range (deg):
            <div class="range-input">
                <input type="number" id="decalage-min" value="-3" step="1">
                <span>to</span>
                <input type="number" id="decalage-max" value="3" step="1">
            </div>
        </label>
    </div>
</div>

<!-- Stability Section -->
<div class="config-section">
    <h3>Stability Requirements</h3>
    <div class="input-grid">
        <label>Min Static Margin (%MAC):
            <input type="number" id="min-static-margin" value="5" step="1">
        </label>
        <label>Max Static Margin (%MAC):
            <input type="number" id="max-static-margin" value="20" step="1">
        </label>
        <label>
            <input type="checkbox" id="check-dynamic-stability" checked>
            Verify Dynamic Stability
        </label>
        <label>
            <input type="checkbox" id="check-control-authority" checked>
            Verify Control Authority
        </label>
    </div>
</div>

<!-- Winglet Options -->
<div class="config-section">
    <h3>Winglet Options</h3>
    <div class="checkbox-group">
        <label>
            <input type="checkbox" id="enable-winglets" checked>
            Enable Winglet Optimization
        </label>
    </div>
    <div class="input-grid" id="winglet-params">
        <label>Max Height (m):
            <input type="number" id="winglet-max-height" value="0.08" step="0.01">
        </label>
        <label>Cant Angle Range (deg):
            <div class="range-input">
                <input type="number" id="cant-min" value="60" step="5">
                <span>to</span>
                <input type="number" id="cant-max" value="90" step="5">
            </div>
        </label>
    </div>
</div>
```

### 19.2 Additional Results Tabs

Add these tabs to the results dashboard:

```html
<!-- Stability Tab -->
<div id="tab-stability" class="tab-content" style="display:none;">
    <div class="card">
        <h3>Longitudinal Stability</h3>
        <div class="chart-grid">
            <div class="chart-container">
                <h4>Static Margin Comparison</h4>
                <canvas id="staticMarginChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>CG Envelope</h4>
                <canvas id="cgEnvelopeChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>Dynamic Modes</h3>
        <table class="results-table" id="dynamicModesTable">
            <thead>
                <tr>
                    <th>Mode</th>
                    <th>Tandem</th>
                    <th>Flying Wing</th>
                    <th>Traditional</th>
                    <th>VTOL</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Short Period (Hz)</td>
                    <td id="sp-tandem">-</td>
                    <td id="sp-flying">-</td>
                    <td id="sp-trad">-</td>
                    <td id="sp-vtol">-</td>
                </tr>
                <tr>
                    <td>Phugoid Period (s)</td>
                    <td id="ph-tandem">-</td>
                    <td id="ph-flying">-</td>
                    <td id="ph-trad">-</td>
                    <td id="ph-vtol">-</td>
                </tr>
                <tr>
                    <td>Dutch Roll (Hz)</td>
                    <td id="dr-tandem">-</td>
                    <td id="dr-flying">-</td>
                    <td id="dr-trad">-</td>
                    <td id="dr-vtol">-</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="card">
        <h3>Lateral Stability</h3>
        <div class="spec-grid">
            <div class="spec-card" id="lateralTandem">
                <h4>Tandem Wing</h4>
                <div class="spec-item">
                    <span class="spec-label">Cl_beta</span>
                    <span class="spec-value" id="clb-tandem">-</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Cn_beta</span>
                    <span class="spec-value" id="cnb-tandem">-</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Dutch Roll</span>
                    <span class="spec-value" id="dutch-tandem">Stable</span>
                </div>
            </div>
            <!-- Repeat for other configs -->
        </div>
    </div>
</div>

<!-- Structural Tab -->
<div id="tab-structure" class="tab-content" style="display:none;">
    <div class="card">
        <h3>Wing Structural Analysis</h3>
        <div class="chart-grid">
            <div class="chart-container">
                <h4>Bending Moment Distribution</h4>
                <canvas id="bendingChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>Shear Distribution</h4>
                <canvas id="shearChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>Structural Weight Breakdown</h3>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Tandem</th>
                    <th>Flying Wing</th>
                    <th>Traditional</th>
                    <th>VTOL</th>
                </tr>
            </thead>
            <tbody id="structuralWeightTable">
            </tbody>
        </table>
    </div>
    
    <div class="card">
        <h3>V-n Diagram</h3>
        <canvas id="vnDiagram" style="max-height: 400px;"></canvas>
    </div>
</div>

<!-- Flight Envelope Tab -->
<div id="tab-envelope" class="tab-content" style="display:none;">
    <div class="card">
        <h3>Performance Envelope</h3>
        <div class="chart-grid">
            <div class="chart-container">
                <h4>Speed Polar</h4>
                <canvas id="speedPolarChart"></canvas>
            </div>
            <div class="chart-container">
                <h4>Power Required vs Available</h4>
                <canvas id="powerCurveChart"></canvas>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h3>Key Speeds</h3>
        <table class="results-table" id="speedsTable">
            <thead>
                <tr>
                    <th>Speed</th>
                    <th>Tandem</th>
                    <th>Flying Wing</th>
                    <th>Traditional</th>
                    <th>VTOL</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>V_stall (m/s)</td>
                    <td id="vs-tandem">-</td>
                    <td id="vs-flying">-</td>
                    <td id="vs-trad">-</td>
                    <td id="vs-vtol">-</td>
                </tr>
                <tr>
                    <td>V_best_endurance (m/s)</td>
                    <td id="ve-tandem">-</td>
                    <td id="ve-flying">-</td>
                    <td id="ve-trad">-</td>
                    <td id="ve-vtol">-</td>
                </tr>
                <tr>
                    <td>V_best_range (m/s)</td>
                    <td id="vr-tandem">-</td>
                    <td id="vr-flying">-</td>
                    <td id="vr-trad">-</td>
                    <td id="vr-vtol">-</td>
                </tr>
                <tr>
                    <td>V_max (m/s)</td>
                    <td id="vm-tandem">-</td>
                    <td id="vm-flying">-</td>
                    <td id="vm-trad">-</td>
                    <td id="vm-vtol">-</td>
                </tr>
                <tr>
                    <td>Max Climb Rate (m/s)</td>
                    <td id="rc-tandem">-</td>
                    <td id="rc-flying">-</td>
                    <td id="rc-trad">-</td>
                    <td id="rc-vtol">-</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

---

## PART 20: UPDATED IMPLEMENTATION CHECKLIST

### Phase 1: Core Physics (Days 1-3)
- [ ] Implement AIRFOIL_DATABASE with 50+ airfoils and AOA sweeps
- [ ] Implement airfoil interpolation and blending functions
- [ ] Implement enhanced drag model with all components
- [ ] Implement Oswald efficiency with configuration corrections
- [ ] Implement wing twist and washout effects
- [ ] Implement winglet benefit calculations

### Phase 2: Stability and Control (Days 4-6)
- [ ] Implement CG calculation system
- [ ] Implement mass breakdown builder
- [ ] Implement neutral point calculations for all configs
- [ ] Implement static margin calculation
- [ ] Implement stability derivatives
- [ ] Implement dynamic mode analysis
- [ ] Implement trim state solver
- [ ] Implement lateral stability analysis
- [ ] Implement control surface sizing (elevator, aileron, rudder)

### Phase 3: Structural Analysis (Days 7-8)
- [ ] Implement wing bending analysis
- [ ] Implement torsional loads calculation
- [ ] Implement spar sizing
- [ ] Implement structural weight estimation
- [ ] Implement V-n diagram generation
- [ ] Implement gust load analysis

### Phase 4: Propulsion and Battery (Days 9-10)
- [ ] Implement real propeller database
- [ ] Implement motor/prop matching
- [ ] Implement slipstream effects
- [ ] Implement motor thermal model
- [ ] Implement Peukert effect
- [ ] Implement high-fidelity battery discharge simulation

### Phase 5: Flight Envelope (Days 11-12)
- [ ] Implement flight envelope calculation
- [ ] Implement mission profile simulation
- [ ] Implement climb performance
- [ ] Implement service ceiling estimation

### Phase 6: Configuration-Specific (Days 13-14)
- [ ] Implement tandem wing biplane theory
- [ ] Implement tandem downwash model
- [ ] Implement flying wing twist optimization
- [ ] Implement flying wing elevon sizing
- [ ] Implement flying wing yaw control analysis
- [ ] Implement VTOL transition corridor
- [ ] Implement VTOL motor-out analysis
- [ ] Implement VTOL hover efficiency

### Phase 7: Optimization Engine (Days 15-16)
- [ ] Update design space with all new variables
- [ ] Implement extended sample decoder
- [ ] Update constraint validation
- [ ] Update parallel evaluation
- [ ] Implement stability-constrained optimization
- [ ] Test with 100k samples per config

### Phase 8: UI and Output (Days 17-18)
- [ ] Update configuration panel with new inputs
- [ ] Add stability results tab
- [ ] Add structural analysis tab
- [ ] Add flight envelope tab
- [ ] Implement all new charts
- [ ] Polish styling

### Phase 9: Integration and Testing (Days 19-20)
- [ ] Full integration test
- [ ] Validate stability calculations
- [ ] Validate structural calculations
- [ ] Performance optimization
- [ ] 1M+ sample stress test
- [ ] Documentation review
