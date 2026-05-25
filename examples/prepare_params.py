import logging
from openff.toolkit import ForceField, Molecule, Topology
from openmm import XmlSerializer

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Molecule Preparation ---
toy_smiles = "CC1NC(=O)CNC(=O)CNC(=O)C(C(=O)NCNC(=O)C(=O)[O-])NC1=O"
logger.info("Generating molecule from SMILES...")
mol = Molecule.from_smiles(toy_smiles, allow_undefined_stereo=True)
mol.generate_conformers(n_conformers=1)
topology = Topology.from_molecules([mol])

# --- 2. Force Field Application ---
logger.info("Applying Force Field...")
sage = ForceField("openff-2.2.0.offxml")
interchange = sage.create_interchange(topology)

# --- 3. Export to OpenMM System ---
# Convert to OpenMM System and serialize to XML
omm_system = interchange.to_openmm(combine_nonbonded_forces=True)
omm_topology = interchange.topology.to_openmm()
omm_positions = interchange.positions.to_openmm()

# Save system and structural data
with open("system.xml", "w") as f:
    f.write(XmlSerializer.serialize(omm_system))

# Save topology/positions for reference (using native format)
interchange.to_pdb("system.pdb")

logger.info("System successfully serialized to 'system.xml' and 'system.pdb'")
