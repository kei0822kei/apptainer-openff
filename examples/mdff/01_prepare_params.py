import logging
from openff.toolkit import ForceField, Topology, Molecule
from openmm import XmlSerializer
from openmm.app import PDBFile
import MDAnalysis as mda
from rdkit import Chem

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. Extract Ligand ---
u = mda.Universe("1AJV-processed.pdb")
ligands_only = u.select_atoms("not protein and not resname HOH and not resname CL")
resname = ligands_only.residues[0].resname
ligands_only.write("ligand.pdb")

# RDKitで読み込み、立体化学情報を付与した状態でMoleculeに変換
# PDBからRDKit分子を生成し、それをOpenFFのMoleculeへ変換する安全なルート
rd_mol = Chem.MolFromPDBFile("ligand.pdb", sanitize=True, removeHs=False)
# 立体化学が定義されていない場合、ここで補完を試みる
Chem.AssignStereochemistry(rd_mol, force=True, cleanIt=True)

ligand_mol = Molecule.from_rdkit(rd_mol, allow_undefined_stereo=True)
ligand_mol.name = resname
ligand_mol.assign_partial_charges(partial_charge_method="am1bcc")

# --- 2. Topology Construction ---
pdbfile = PDBFile("1AJV-processed.pdb")
# ここでTopologyにMoleculeを明示的に関連付ける
topology = Topology.from_openmm(pdbfile.topology, unique_molecules=[ligand_mol])

# --- 3. Force Field Application ---
logger.info("Applying Force Field...")
forcefield = ForceField(
    "openff-2.2.0.offxml",
    "amber/ff14sb.offxml",
    "amber/tip3p.offxml",
)

interchange = forcefield.create_interchange(topology)
interchange.positions = pdbfile.positions

# --- 4. Export ---
omm_system = interchange.to_openmm(combine_nonbonded_forces=True)

with open("system.xml", "w") as f:
    f.write(XmlSerializer.serialize(omm_system))

interchange.to_pdb("system.pdb")
logger.info("Success: system.xml and system.pdb created.")
