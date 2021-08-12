from enum import Enum
from functools import partial

from qiskit_nature.drivers import Molecule


class MolecularVariation(str, Enum):
    absolute_stretching = 0
    relative_stretching = 1
    absolute_bending = 2
    relative_bending = 3


def callable_to_MolecularVariation_and_atom_pair(callable):
    if not isinstance(callable, partial):
        raise RuntimeError("callable must be an instance of functools.partial")

    # Get the original function
    func = callable.func
    args = callable.args
    keywords = callable.keywords

    if func == Molecule.absolute_stretching:
        moleculare_variation = MolecularVariation.absolute_stretching
    elif func == Molecule.relative_stretching:
        moleculare_variation = MolecularVariation.relative_stretching
    elif func == Molecule.absolute_bending:
        moleculare_variation = MolecularVariation.absolute_bending
    elif func == Molecule.relative_bending:
        moleculare_variation = MolecularVariation.relative_bending
    else:
        moleculare_variation = None

    atom_pair = keywords['atom_pair']

    return moleculare_variation, atom_pair


def molecule_to_dict(molecule: Molecule) -> str:
    if len(molecule._degrees_of_freedom) != 1:
        raise NotImplementedError(
            'serialize_molecule does not currently support more than one degree of freedom'
        )

    molecular_variation, atom_pair = callable_to_MolecularVariation_and_atom_pair(
        molecule._degrees_of_freedom[0]
    )

    molecule_dict = {
        'geometry': molecule._geometry,
        'multiplicity': molecule.multiplicity,
        'charge': molecule.charge,
        'molecular_variation': molecular_variation,
        'atom_pair': atom_pair,
        'masses': molecule.masses
    }

    return molecule_dict


