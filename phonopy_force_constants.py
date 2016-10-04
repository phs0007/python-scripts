fc_and_atom_types = read_force_constant_vasprun_xml(filename)

def parse_FORCE_CONSTANTS(filename="FORCE_CONSTANTS"):
    fcfile = open(filename)
    num = int((fcfile.readline().strip().split())[0])
    force_constants = np.zeros((num, num, 3, 3), dtype=float)
    for i in range(num):
        for j in range(num):
            fcfile.readline()
            tensor = []
            for k in range(3):
                tensor.append([float(x) for x in fcfile.readline().strip().split()])
            force_constants[i, j] = np.array(tensor)

    return force_constants


def write_FORCE_CONSTANTS(force_constants, filename='FORCE_CONSTANTS'):
    w = open(filename, 'w')
    fc_shape = force_constants.shape
    w.write("%4d\n" % (fc_shape[0]))
    for i in range(fc_shape[0]):
        for j in range(fc_shape[1]):
            w.write("%4d%4d\n" % (i+1, j+1))
            for vec in force_constants[i][j]:
                w.write(("%22.15f"*3 + "\n") % tuple(vec))
    w.close()

def read_force_constant_vasprun_xml(filename):
    vasprun = _parse_vasprun_xml(filename)
    return get_force_constants_vasprun_xml(vasprun)

def get_force_constants_vasprun_xml(vasprun):
    fc_tmp = None
    num_atom = 0
    for event, element in vasprun:
        if num_atom == 0:
            atomtypes = _get_atomtypes_from_vasprun_xml(element)
            if atomtypes:
                num_atoms, elements, elem_masses = atomtypes[:3]
                num_atom = np.sum(num_atoms)
                masses = []
                for n, m in zip(num_atoms, elem_masses):
                    masses += [m] * n

        # Get Hessian matrix (normalized by masses)
        if element.tag == 'varray':
            if element.attrib['name'] == 'hessian':
                fc_tmp = []
                for v in element.findall('./v'):
                    fc_tmp.append([float(x) for x in v.text.strip().split()])

    if fc_tmp is None:
        return False
    else:
        fc_tmp = np.array(fc_tmp)
        if fc_tmp.shape != (num_atom * 3, num_atom * 3):
            return False
        # num_atom = fc_tmp.shape[0] / 3
        force_constants = np.zeros((num_atom, num_atom, 3, 3), dtype='double')

        for i in range(num_atom):
            for j in range(num_atom):
                force_constants[i, j] = fc_tmp[i*3:(i+1)*3, j*3:(j+1)*3]

        # Inverse normalization by atomic weights
        for i in range(num_atom):
            for j in range(num_atom):
                force_constants[i, j] *= -np.sqrt(masses[i] * masses[j])

        return force_constants, elements

def _parse_vasprun_xml(filename):
    if _is_version528(filename):
        return _iterparse(VasprunWrapper(filename))
    else:
        return _iterparse(filename)

def _iterparse(fname, tag=None):
    try:
        import xml.etree.cElementTree as etree
        for event, elem in etree.iterparse(fname):
            if tag is None or elem.tag == tag:
                yield event, elem
    except ImportError:
        print("Python 2.5 or later is needed.")
        print("For creating FORCE_SETS file with Python 2.4, you can use "
              "phonopy 1.8.5.1 with python-lxml .")
        sys.exit(1)
