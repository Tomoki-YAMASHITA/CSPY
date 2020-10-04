'''
Collect results in Quantum ESPRESSO
'''

import numpy as np
from pymatgen.core.units import Energy

from . import structure as qe_structure
from ...IO import read_input as rin


def collect_qe(current_id, work_path):
    # ---------- check optimization in previous stage
    try:
        with open(work_path+rin.qe_outfile, 'r') as fpout:
            lines = fpout.readlines()
        check_opt = 'not_yet'
        for line in lines:
            if 'End final coordinates' in line:
                check_opt = 'done'
    except:
        check_opt = 'no_file'

    # ---------- obtain energy and magmom
    try:
        with open(work_path+rin.qe_outfile, 'r') as fpout:
            lines = fpout.readlines()
        energy = np.nan
        for line in reversed(lines):
            if line.startswith('!'):
                energy = float(line.split()[-2])    # in Ry
                energy = float(Energy(energy, 'Ry').to('eV'))    # Ry --> eV
                energy = energy/float(rin.natot)    # eV/cell --> eV/atom
                break
        magmom = np.nan    # implemented by H. Sawahata 2020/10/04
        for line in reversed(lines):
            if line.find("total magnetization") >= 0:
                muB = line.split()
                magmom = float(muB[3])
                break
    except:
        energy = np.nan    # error
        magmom = np.nan    # error
        print('    Structure ID {0}, could not obtain energy from {1}'.format(
            current_id, rin.qe_outfile))

    # ---------- collect the last structure
    try:
        lines_cell = qe_structure.extract_cell_parameters(
            work_path+rin.qe_outfile)
        if lines_cell is None:
            lines_cell = qe_structure.extract_cell_parameters(
                work_path+rin.qe_infile)
        lines_atom = qe_structure.extract_atomic_positions(
            work_path+rin.qe_outfile)
        if lines_atom is None:
            lines_atom = qe_structure.extract_atomic_positions(
                work_path+rin.qe_infile)
        opt_struc = qe_structure.from_lines(lines_cell, lines_atom)

        # ------ opt_qe-structure
        with open('./data/opt_qe-structure', 'a') as fstruc:
            fstruc.write('# ID {0:d}\n'.format(current_id))
        qe_structure.write(opt_struc, './data/opt_qe-structure', mode='a')
    except:
        opt_struc = None

    # ---------- check
    if np.isnan(energy):
        opt_struc = None
    if opt_struc is None:
        energy = np.nan
        magmom = np.nan

    # ---------- return
    return opt_struc, energy, magmom, check_opt
