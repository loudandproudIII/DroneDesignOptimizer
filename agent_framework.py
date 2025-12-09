"""
Drone Design Optimizer - Multi-Agent Framework Implementation
==============================================================

This module implements the multi-agent system defined in agent_configurations.yaml.
Each agent is a specialized processor with focused responsibilities and clear interfaces.

Usage:
    from agent_framework import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    results = orchestrator.run_optimization(config)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import json
import time
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ConfigType(Enum):
    """Aircraft configuration types."""
    TANDEM = "tandem"
    FLYING_WING = "flying_wing"
    TRADITIONAL = "traditional"
    VTOL = "vtol"


class MessageType(Enum):
    """Inter-agent message types."""
    TASK_REQUEST = "task_request"
    TASK_COMPLETE = "task_complete"
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    ERROR = "error"
    PROGRESS = "progress"


class AgentStatus(Enum):
    """Agent operational status."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication."""
    source: str
    target: str
    message_type: MessageType
    payload: Dict[str, Any]
    task_id: str = ""
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""


@dataclass
class ToolDefinition:
    """Definition of a tool available to an agent."""
    name: str
    description: str
    parameters: Dict[str, str]
    handler: Callable = None


@dataclass
class HandoffProtocol:
    """Defines how agents hand off work to each other."""
    target: str
    trigger: str
    data_fields: List[str]
    condition: Optional[Callable] = None


# =============================================================================
# BASE AGENT CLASS
# =============================================================================

class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(name)
        self.tools: Dict[str, ToolDefinition] = {}
        self.outbound_protocols: List[HandoffProtocol] = []
        self.inbound_handlers: Dict[str, Callable] = {}
        self.message_queue: List[AgentMessage] = []

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results."""
        pass

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool with this agent."""
        self.tools[tool.name] = tool

    def add_outbound_protocol(self, protocol: HandoffProtocol) -> None:
        """Add a handoff protocol for outbound communication."""
        self.outbound_protocols.append(protocol)

    def register_inbound_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for incoming messages of a specific type."""
        self.inbound_handlers[message_type] = handler

    def send_message(self, target: str, message_type: MessageType,
                     payload: Dict[str, Any], task_id: str = "") -> AgentMessage:
        """Create and queue an outbound message."""
        msg = AgentMessage(
            source=self.name,
            target=target,
            message_type=message_type,
            payload=payload,
            task_id=task_id
        )
        return msg

    def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message and optionally return a response."""
        handler = self.inbound_handlers.get(message.message_type.value)
        if handler:
            result = handler(message.payload)
            if result:
                return self.send_message(
                    target=message.source,
                    message_type=MessageType.TASK_COMPLETE,
                    payload=result,
                    task_id=message.task_id
                )
        return None


# =============================================================================
# COORDINATOR AGENT
# =============================================================================

class CoordinatorAgent(BaseAgent):
    """Central orchestrator that manages the optimization workflow."""

    def __init__(self):
        super().__init__("coordinator", "orchestrator")
        self.workflow_state: Dict[str, Any] = {}
        self.agent_registry: Dict[str, BaseAgent] = {}
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Workflow Coordinator for the Drone Design Optimizer system.

Your Responsibilities:
1. Parse user configuration requests (aircraft types, constraints, sample sizes)
2. Orchestrate the optimization workflow by delegating to specialized agents
3. Manage data flow between agents and ensure proper sequencing
4. Aggregate results from all agents into a cohesive output
5. Handle errors gracefully with appropriate fallbacks
6. Provide progress updates to the user

Workflow Sequence:
1. VALIDATION: Validate user inputs and constraints
2. INITIALIZATION: Initialize airfoil database via Airfoil Agent
3. GEOMETRY: Generate design space via Geometry Agent
4. OPTIMIZATION: Run parallel optimization via Optimization Engine Agent
5. ANALYSIS: Extract Pareto fronts and identify winners
6. VISUALIZATION: Generate HTML output via UI Agent"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="dispatch_task",
            description="Send task to a specialized agent",
            parameters={"target_agent": "string", "task_type": "string", "payload": "object"}
        ))
        self.register_tool(ToolDefinition(
            name="aggregate_results",
            description="Collect and merge results from multiple agents",
            parameters={"sources": "array[string]", "merge_strategy": "string"}
        ))
        self.register_tool(ToolDefinition(
            name="validate_workflow_state",
            description="Check that all prerequisites are met for next step",
            parameters={"required_completions": "array[string]"}
        ))

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a specialized agent with the coordinator."""
        self.agent_registry[agent.name] = agent

    def dispatch_to_agent(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a task to a specific agent and wait for result."""
        agent = self.agent_registry.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent.process_task(task)

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete optimization workflow."""
        self.logger.info("Starting optimization workflow")
        self.status = AgentStatus.PROCESSING

        try:
            # Phase 1: Validate inputs
            self._validate_inputs(task)

            # Phase 2: Initialize airfoils
            airfoil_result = self.dispatch_to_agent("airfoil_agent", {
                "action": "initialize",
                "airfoil_selection": task.get("airfoils", []),
                "reynolds_range": task.get("reynolds_range", [50000, 500000])
            })

            # Phase 3: Setup geometry
            geometry_result = self.dispatch_to_agent("geometry_agent", {
                "action": "setup_design_space",
                "config_types": task.get("config_types", ["tandem", "flying_wing", "traditional", "vtol"]),
                "constraints": task.get("constraints", {})
            })

            # Phase 4: Run optimization
            optimization_result = self.dispatch_to_agent("optimization_agent", {
                "action": "run_optimization",
                "design_space": geometry_result.get("design_space"),
                "n_samples": task.get("n_samples", 100000),
                "config_types": task.get("config_types"),
                "constraints": task.get("constraints")
            })

            # Phase 5: Generate output
            ui_result = self.dispatch_to_agent("ui_agent", {
                "action": "generate_output",
                "results": optimization_result,
                "config": task
            })

            self.status = AgentStatus.IDLE
            return {
                "success": True,
                "output_path": ui_result.get("output_path"),
                "summary": optimization_result.get("summary")
            }

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Workflow failed: {e}")
            return {"success": False, "error": str(e)}

    def _validate_inputs(self, task: Dict[str, Any]) -> None:
        """Validate user inputs before processing."""
        required = ["config_types"]
        for field in required:
            if field not in task:
                raise ValueError(f"Missing required field: {field}")


# =============================================================================
# AIRFOIL DATABASE AGENT
# =============================================================================

class AirfoilAgent(BaseAgent):
    """Manages the airfoil database and provides polar interpolation."""

    def __init__(self):
        super().__init__("airfoil_agent", "specialist")
        self.database: Dict[str, Any] = {}
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Airfoil Database Manager for the Drone Design Optimizer.

Your Expertise:
- Low Reynolds number aerodynamics (Re = 50,000 to 500,000)
- Airfoil polar data interpretation (Cl, Cd, Cm vs AOA)
- Multi-Reynolds interpolation techniques
- Stall behavior and maximum lift prediction

Your Responsibilities:
1. Load and validate the embedded airfoil database
2. Provide Cl, Cd, Cm interpolation at arbitrary AOA and Reynolds numbers
3. Find optimal operating points (max L/D, max Cl, design Cl)
4. Classify airfoils by application (low-Re, reflex, high-lift)
5. Recommend airfoils for specific configuration types"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="interpolate_polar",
            description="Get Cl, Cd, Cm at specific AOA and Reynolds number",
            parameters={"airfoil_name": "string", "alpha_deg": "number", "reynolds": "number"}
        ))
        self.register_tool(ToolDefinition(
            name="find_optimal_aoa",
            description="Find optimal angle of attack for given objective",
            parameters={"airfoil_name": "string", "reynolds": "number", "objective": "string"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process airfoil-related tasks."""
        action = task.get("action")

        if action == "initialize":
            return self._initialize_database(task)
        elif action == "interpolate":
            return self._interpolate_polar(task)
        elif action == "find_optimal":
            return self._find_optimal_aoa(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _initialize_database(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the airfoil database."""
        # In production, this would load the embedded database
        self.logger.info("Initializing airfoil database")
        return {
            "status": "initialized",
            "available_airfoils": ["SD7032", "SD7037", "E387", "MH60", "S1223"],
            "categories": {
                "low_reynolds": ["SD7032", "SD7037", "E387"],
                "reflex": ["MH60"],
                "high_lift": ["S1223"]
            }
        }

    def _interpolate_polar(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Interpolate airfoil polar at given conditions."""
        # Placeholder implementation
        return {
            "airfoil": task.get("airfoil_name"),
            "alpha_deg": task.get("alpha_deg"),
            "reynolds": task.get("reynolds"),
            "cl": 0.8,  # Placeholder
            "cd": 0.015,
            "cm": -0.08,
            "ld_ratio": 53.3
        }

    def _find_optimal_aoa(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Find optimal angle of attack."""
        return {
            "airfoil": task.get("airfoil_name"),
            "optimal_alpha_deg": 5.0,
            "cl_at_optimal": 0.9,
            "cd_at_optimal": 0.012,
            "max_ld": 75.0
        }


# =============================================================================
# AERODYNAMICS AGENT
# =============================================================================

class AerodynamicsAgent(BaseAgent):
    """Calculates drag breakdown and aerodynamic performance."""

    def __init__(self):
        super().__init__("aerodynamics_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Aerodynamics Calculator for the Drone Design Optimizer.

Your Expertise:
- Induced drag modeling (lifting line theory, Oswald efficiency)
- Profile drag from airfoil polars
- Parasitic drag estimation (Hoerner methods)
- Interference drag for multi-surface configurations
- Tandem wing downwash and biplane interference

Drag Components You Calculate:
- Induced, Wing Profile, Tail Profile
- Fuselage, Booms, Landing Gear
- Wing-Body, Wing-Wing, Tail-Body Interference
- Antennas, Camera, Stopped Props
- Trim Drag"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="calculate_full_drag",
            description="Calculate complete drag breakdown",
            parameters={"config": "object", "weight_n": "number", "velocity_ms": "number"}
        ))
        self.register_tool(ToolDefinition(
            name="calculate_oswald_efficiency",
            description="Calculate Oswald span efficiency factor",
            parameters={"aspect_ratio": "number", "taper_ratio": "number", "config_type": "string"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process aerodynamics calculations."""
        action = task.get("action")

        if action == "full_drag":
            return self._calculate_full_drag(task)
        elif action == "oswald":
            return self._calculate_oswald(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _calculate_full_drag(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate complete drag breakdown."""
        # Placeholder implementation
        config_type = task.get("config_type", "traditional")
        weight_n = task.get("weight_n", 10.0)
        velocity = task.get("velocity_ms", 15.0)

        # Simplified drag model
        induced = 0.15  # N
        profile = 0.08
        parasitic = 0.05
        total = induced + profile + parasitic

        return {
            "total_drag_n": total,
            "breakdown": {
                "induced": induced,
                "wing_profile": profile,
                "fuselage": parasitic * 0.6,
                "interference": parasitic * 0.3,
                "trim": parasitic * 0.1
            },
            "ld_ratio": weight_n / total,
            "power_required_w": total * velocity / 0.6
        }

    def _calculate_oswald(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Oswald efficiency."""
        ar = task.get("aspect_ratio", 8.0)
        config_type = task.get("config_type", "traditional")

        # Base efficiency
        e_base = 0.85

        # Configuration corrections
        corrections = {
            "tandem": 0.82,
            "flying_wing": 0.90,
            "traditional": 1.00,
            "vtol": 0.78
        }

        e = e_base * corrections.get(config_type, 1.0)

        return {"oswald_efficiency": e}


# =============================================================================
# FUSELAGE/BATTERY AGENT
# =============================================================================

class FuselageBatteryAgent(BaseAgent):
    """Optimizes battery configuration and fuselage sizing."""

    def __init__(self):
        super().__init__("fuselage_battery_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Fuselage & Battery Optimizer for the Drone Design Optimizer.

Your Expertise:
- Battery pack layout optimization (21700 cell arrangements)
- Fuselage aerodynamic shaping (minimum drag envelopes)
- System integration (avionics, ESC, motor packaging)
- Iterative mass-energy convergence

Battery Cell: Molicel P50B 21700
- Diameter: 21 mm, Length: 70 mm
- Mass: 70 g, Capacity: 5.0 Ah
- Nominal voltage: 3.6 V, Energy: 18.0 Wh"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="enumerate_battery_layouts",
            description="Generate all physical arrangements for a battery pack",
            parameters={"series": "number", "parallel": "number"}
        ))
        self.register_tool(ToolDefinition(
            name="design_fuselage",
            description="Size fuselage for given battery and components",
            parameters={"battery_series": "number", "battery_parallel": "number"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process fuselage/battery optimization tasks."""
        action = task.get("action")

        if action == "optimize_system":
            return self._optimize_system(task)
        elif action == "enumerate_layouts":
            return self._enumerate_layouts(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _optimize_system(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run iterative battery-fuselage optimization."""
        target_time = task.get("target_flight_time_min", 120)

        # Simplified optimization
        battery_s = 3
        battery_p = 2

        return {
            "battery_series": battery_s,
            "battery_parallel": battery_p,
            "battery_config": f"{battery_s}S{battery_p}P",
            "battery_mass_kg": battery_s * battery_p * 0.070,
            "battery_energy_wh": battery_s * battery_p * 18.0,
            "fuselage": {
                "length_m": 0.35,
                "width_m": 0.08,
                "height_m": 0.06,
                "fineness_ratio": 4.4
            },
            "total_mass_kg": 0.85,
            "iterations": 5
        }

    def _enumerate_layouts(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enumerate possible battery layouts."""
        series = task.get("series", 3)
        parallel = task.get("parallel", 2)
        total_cells = series * parallel

        layouts = []
        # Simplified layout enumeration
        layouts.append({
            "orientation": "lengthwise",
            "arrangement": f"1x{series}x{parallel}",
            "dims": (0.070, parallel * 0.021, series * 0.021),
            "frontal_area": parallel * 0.021 * series * 0.021
        })

        return {"layouts": layouts, "recommended": layouts[0]}


# =============================================================================
# OPTIMIZATION ENGINE AGENT
# =============================================================================

class OptimizationAgent(BaseAgent):
    """High-throughput optimization with parallel evaluation."""

    def __init__(self):
        super().__init__("optimization_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the High-Throughput Optimization Engine for the Drone Design Optimizer.

Your Expertise:
- Quasi-random sampling (Sobol, Halton, Latin Hypercube)
- Parallel design evaluation with multiprocessing
- Constraint handling and fast rejection
- Multi-objective Pareto front extraction

You process 1M+ design configurations and extract Pareto-optimal solutions."""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="create_design_sampler",
            description="Generate quasi-random samples for design space",
            parameters={"n_samples": "number", "n_variables": "number", "method": "string"}
        ))
        self.register_tool(ToolDefinition(
            name="extract_pareto_front",
            description="Extract non-dominated solutions",
            parameters={"results": "array", "objectives": "array"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process optimization tasks."""
        action = task.get("action")

        if action == "run_optimization":
            return self._run_optimization(task)
        elif action == "extract_pareto":
            return self._extract_pareto(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _run_optimization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the optimization."""
        config_types = task.get("config_types", ["tandem"])
        n_samples = task.get("n_samples", 1000)

        self.logger.info(f"Running optimization with {n_samples} samples per config")

        results = {}
        for config_type in config_types:
            # Simplified: generate mock results
            pareto_front = [
                {
                    "flight_time_min": 132.5,
                    "range_km": 124.2,
                    "ld_ratio": 12.3,
                    "weight_kg": 0.85
                },
                {
                    "flight_time_min": 128.0,
                    "range_km": 130.5,
                    "ld_ratio": 11.8,
                    "weight_kg": 0.90
                }
            ]

            results[config_type] = {
                "n_evaluated": n_samples,
                "n_valid": int(n_samples * 0.03),
                "pareto_front": pareto_front
            }

        return {
            "results": results,
            "summary": {
                "total_evaluated": n_samples * len(config_types),
                "best_flight_time": 132.5,
                "best_config": "tandem"
            }
        }

    def _extract_pareto(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Pareto front from results."""
        results = task.get("results", [])
        objectives = task.get("objectives", ["flight_time_min", "ld_ratio"])

        # Simplified Pareto extraction
        return {
            "pareto_front": results[:10],
            "n_pareto_points": min(10, len(results))
        }


# =============================================================================
# STABILITY AGENT
# =============================================================================

class StabilityAgent(BaseAgent):
    """Analyzes static and dynamic stability."""

    def __init__(self):
        super().__init__("stability_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Stability & Control Analyst for the Drone Design Optimizer.

Your Expertise:
- Center of gravity calculation with component buildups
- Neutral point and static margin analysis
- Longitudinal trim and elevator sizing
- Lateral-directional stability (dutch roll, spiral, roll)
- Dynamic mode analysis (short period, phugoid)

Static Margin Requirements:
| Config Type | Min SM | Max SM | Target |
|-------------|--------|--------|--------|
| Traditional | 5%     | 25%    | 10-15% |
| Flying Wing | 8%     | 18%    | 12%    |
| Tandem      | 5%     | 20%    | 10%    |
| VTOL        | 5%     | 20%    | 12%    |"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="calculate_cg",
            description="Calculate CG and moments of inertia",
            parameters={"mass_items": "array", "wing_geometry": "object"}
        ))
        self.register_tool(ToolDefinition(
            name="calculate_neutral_point",
            description="Determine aerodynamic neutral point",
            parameters={"wing_geometry": "object", "config_type": "string"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process stability analysis tasks."""
        action = task.get("action")

        if action == "full_check":
            return self._full_stability_check(task)
        elif action == "cg":
            return self._calculate_cg(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _full_stability_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete stability analysis."""
        config_type = task.get("config_type", "traditional")

        # Simplified stability check
        static_margin = 12.0  # percent

        return {
            "cg": {"x_m": 0.15, "mac_percent": 28.0},
            "neutral_point": {"x_m": 0.18, "mac_percent": 40.0},
            "static_margin_percent": static_margin,
            "stability_status": "stable" if 5 < static_margin < 25 else "unstable",
            "trim": {"alpha_deg": 3.5, "elevator_deg": -2.0, "trim_drag_n": 0.005},
            "lateral": {"cl_beta": -0.0008, "cn_beta": 0.0012, "dutch_roll_stable": True},
            "feasible": True,
            "warnings": []
        }

    def _calculate_cg(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate center of gravity."""
        return {
            "cg_x": 0.15,
            "cg_y": 0.0,
            "cg_z": 0.0,
            "total_mass_kg": 0.85
        }


# =============================================================================
# GEOMETRY AGENT
# =============================================================================

class GeometryAgent(BaseAgent):
    """Defines wing geometry and design bounds."""

    def __init__(self):
        super().__init__("geometry_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the Geometry & Configuration Modeler for the Drone Design Optimizer.

Your Expertise:
- Wing planform geometry (span, chord, taper, sweep, twist)
- Mean aerodynamic chord and aerodynamic center calculation
- Tandem wing arrangement (stagger, gap, decalage)
- Winglet geometry and induced drag reduction
- Design space bounds and variable scaling

Key Formulas:
- Area: S = span × (chord_root + chord_tip) / 2
- Aspect Ratio: AR = span² / S
- MAC: c̄ = (2/3) × c_root × (1 + λ + λ²) / (1 + λ)"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="create_wing_geometry",
            description="Create wing geometry from parameters",
            parameters={"span": "number", "chord_root": "number", "taper_ratio": "number"}
        ))
        self.register_tool(ToolDefinition(
            name="get_design_bounds",
            description="Get variable bounds for a configuration type",
            parameters={"config_type": "string"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process geometry tasks."""
        action = task.get("action")

        if action == "setup_design_space":
            return self._setup_design_space(task)
        elif action == "create_geometry":
            return self._create_geometry(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _setup_design_space(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Set up the design space bounds."""
        config_types = task.get("config_types", ["tandem"])

        bounds = {
            "tandem": {
                "n_variables": 12,
                "variables": {
                    "span": [0.6, 1.0],
                    "chord_front": [0.10, 0.25],
                    "chord_rear": [0.08, 0.22],
                    "stagger": [0.3, 0.6],
                    "gap": [0.05, 0.20]
                }
            },
            "flying_wing": {
                "n_variables": 9,
                "variables": {
                    "span": [0.6, 1.0],
                    "chord": [0.15, 0.30],
                    "sweep_deg": [15, 35]
                }
            },
            "traditional": {
                "n_variables": 10,
                "variables": {
                    "span": [0.6, 1.0],
                    "chord": [0.10, 0.25],
                    "tail_area": [0.01, 0.03]
                }
            },
            "vtol": {
                "n_variables": 14,
                "variables": {
                    "span": [0.6, 1.0],
                    "chord": [0.10, 0.25],
                    "boom_length": [0.10, 0.25]
                }
            }
        }

        return {
            "design_space": {ct: bounds.get(ct, bounds["traditional"]) for ct in config_types}
        }

    def _create_geometry(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create wing geometry from parameters."""
        span = task.get("span", 1.0)
        chord_root = task.get("chord_root", 0.2)
        taper_ratio = task.get("taper_ratio", 1.0)

        chord_tip = chord_root * taper_ratio
        area = span * (chord_root + chord_tip) / 2
        ar = span ** 2 / area
        mac = (2/3) * chord_root * (1 + taper_ratio + taper_ratio**2) / (1 + taper_ratio)

        return {
            "span_m": span,
            "chord_root_m": chord_root,
            "chord_tip_m": chord_tip,
            "area_m2": area,
            "aspect_ratio": ar,
            "mac_m": mac
        }


# =============================================================================
# UI AGENT
# =============================================================================

class UIAgent(BaseAgent):
    """Generates HTML dashboard output."""

    def __init__(self):
        super().__init__("ui_agent", "specialist")
        self._setup_tools()

    @property
    def system_prompt(self) -> str:
        return """You are the UI & Visualization Generator for the Drone Design Optimizer.

Your Expertise:
- HTML5 structure and semantic markup
- CSS styling for professional engineering dashboards
- Chart.js integration for data visualization
- JavaScript for interactivity (tabs, sliders, tooltips)
- Responsive design for various screen sizes

Color Palette:
- Primary Blue: #1e40af
- Tandem: #2E86AB
- Flying Wing: #A23B72
- Traditional: #F18F01
- VTOL: #C73E1D"""

    def _setup_tools(self):
        self.register_tool(ToolDefinition(
            name="generate_html_output",
            description="Generate complete HTML dashboard",
            parameters={"results": "object", "config": "object", "output_path": "string"}
        ))

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process UI generation tasks."""
        action = task.get("action")

        if action == "generate_output":
            return self._generate_output(task)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _generate_output(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML output."""
        output_path = task.get("output_path", "drone_optimizer_results.html")

        # In production, this would generate the full HTML
        self.logger.info(f"Generating HTML output to {output_path}")

        return {
            "output_path": output_path,
            "file_size_bytes": 125000,
            "status": "generated"
        }


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class AgentOrchestrator:
    """Main orchestrator that initializes and coordinates all agents."""

    def __init__(self):
        self.logger = logging.getLogger("orchestrator")
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all specialized agents."""
        self.coordinator = CoordinatorAgent()
        self.airfoil_agent = AirfoilAgent()
        self.aerodynamics_agent = AerodynamicsAgent()
        self.fuselage_battery_agent = FuselageBatteryAgent()
        self.optimization_agent = OptimizationAgent()
        self.stability_agent = StabilityAgent()
        self.geometry_agent = GeometryAgent()
        self.ui_agent = UIAgent()

        # Register all agents with coordinator
        for agent in [
            self.airfoil_agent,
            self.aerodynamics_agent,
            self.fuselage_battery_agent,
            self.optimization_agent,
            self.stability_agent,
            self.geometry_agent,
            self.ui_agent
        ]:
            self.coordinator.register_agent(agent)

        self.logger.info("All agents initialized and registered")

    def run_optimization(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete optimization workflow."""
        self.logger.info("Starting optimization with config: %s", config)
        return self.coordinator.process_task(config)

    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents."""
        return {
            "coordinator": self.coordinator.status.value,
            "airfoil_agent": self.airfoil_agent.status.value,
            "aerodynamics_agent": self.aerodynamics_agent.status.value,
            "fuselage_battery_agent": self.fuselage_battery_agent.status.value,
            "optimization_agent": self.optimization_agent.status.value,
            "stability_agent": self.stability_agent.status.value,
            "geometry_agent": self.geometry_agent.status.value,
            "ui_agent": self.ui_agent.status.value
        }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main entry point for running the multi-agent optimizer."""
    import argparse

    parser = argparse.ArgumentParser(description='Drone Design Optimizer - Multi-Agent System')
    parser.add_argument('--configs', nargs='+',
                        default=['tandem', 'flying_wing', 'traditional', 'vtol'],
                        help='Configuration types to evaluate')
    parser.add_argument('--samples', type=int, default=100000,
                        help='Number of samples per configuration')
    parser.add_argument('--output', type=str, default='drone_optimizer_results.html',
                        help='Output HTML file path')

    args = parser.parse_args()

    # Create orchestrator and run
    orchestrator = AgentOrchestrator()

    config = {
        "config_types": args.configs,
        "n_samples": args.samples,
        "output_path": args.output,
        "constraints": {
            "max_span": 1.0,
            "max_length": 1.0,
            "min_stall_speed_ms": 5.59,
            "cruise_speed_ms": 15.65
        }
    }

    result = orchestrator.run_optimization(config)

    if result["success"]:
        print(f"\nOptimization complete!")
        print(f"Results saved to: {result.get('output_path')}")
    else:
        print(f"\nOptimization failed: {result.get('error')}")

    return result


if __name__ == "__main__":
    main()
