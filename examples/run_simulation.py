import logging
from openmm import app, unit, Platform, XmlSerializer, LangevinMiddleIntegrator
from openmm.app import PDBFile

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Configuration ---
# Choose: 'CUDA', 'OpenCL', or 'CPU'
platform_name = "CUDA"

# --- 2. Load System ---
logger.info("Loading system from files...")
with open("system.xml", "r") as f:
    omm_system = XmlSerializer.deserialize(f.read())

pdb = PDBFile("system.pdb")
omm_topology = pdb.topology

# --- 3. Initialize Simulation ---
integrator = LangevinMiddleIntegrator(
    300 * unit.kelvin, 1 / unit.picoseconds, 0.002 * unit.picoseconds
)

# Set platform
platform = Platform.getPlatformByName(platform_name)
simulation = app.Simulation(omm_topology, omm_system, integrator, platform)
simulation.context.setPositions(pdb.positions)

# --- 4. Execution ---
logger.info(f"Running simulation on: {platform.getName()}")
logger.info("Minimizing energy...")
simulation.minimizeEnergy(maxIterations=1000)
simulation.context.setVelocitiesToTemperature(300 * unit.kelvin)

simulation.reporters.append(app.DCDReporter("production.dcd", 10000))
logger.info("Starting production MD...")
simulation.step(500000)
logger.info("Simulation finished.")
