import os
import sys
import logging
from openff.toolkit import ForceField, Molecule, Topology
from openmm import openmm
from openmm.app import Simulation, DCDReporter, StateDataReporter
from openmm.unit import kelvin, picoseconds

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# --- Resource Configuration ---
# Use CPU count for threading, but limit for stability if needed
n_procs = os.cpu_count() or 1
os.environ["OMP_NUM_THREADS"] = str(n_procs)
os.environ["MKL_NUM_THREADS"] = str(n_procs)
logger.info(f"Using {n_procs} threads for CPU-based operations.")

# --- 1. Molecule Preparation ---
toy_smiles = "CC1NC(=O)CNC(=O)CNC(=O)C(C(=O)NCNC(=O)C(=O)[O-])NC1=O"
logger.info("Generating molecule from SMILES...")
mol = Molecule.from_smiles(toy_smiles, allow_undefined_stereo=True)
mol.generate_conformers(n_conformers=1)

# --- 2. Topology Setup ---
topology = Topology.from_molecules([mol])

# --- 3. Force Field Application ---
logger.info("Calculating force field parameters and partial charges...")
sage = ForceField("openff-2.2.0.offxml")
interchange = sage.create_interchange(topology)

# --- 4. OpenMM Conversion ---
omm_topology = interchange.to_openmm_topology()
omm_positions = interchange.positions.to_openmm()
omm_system = interchange.to_openmm(combine_nonbonded_forces=True)

# --- 5. Simulation Initialization ---
integrator = openmm.LangevinMiddleIntegrator(
    300 * kelvin, 1 / picoseconds, 0.002 * picoseconds
)
simulation = Simulation(omm_topology, omm_system, integrator)
simulation.context.setPositions(omm_positions)

# Verify Platform
current_platform = simulation.context.getPlatform().getName()
logger.info(f"Running simulation on platform: {current_platform}")

# --- 6. Energy Minimization ---
logger.info("Running energy minimization...")
simulation.minimizeEnergy(maxIterations=1000)

# --- 7. Production MD Simulation ---
simulation.context.setVelocitiesToTemperature(300 * kelvin)

# Reporters
total_steps = 500000
report_interval = 10000

simulation.reporters.append(
    StateDataReporter(
        sys.stdout,
        report_interval,
        step=True,
        potentialEnergy=True,
        temperature=True,
        progress=True,
        totalSteps=total_steps,
    )
)
simulation.reporters.append(DCDReporter("production.dcd", report_interval))

logger.info(f"Starting MD simulation for {total_steps} steps...")
simulation.step(total_steps)
logger.info("Simulation completed successfully. Output: production.dcd")
