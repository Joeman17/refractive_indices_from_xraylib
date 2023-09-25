import argparse
import sys
sys.path.append("/beegfs/desy/user/jentscht/xraylib/build/lib/python3.6/site-packages/")
sys.path.append("/beegfs/desy/user/jentscht/xraylib/build/lib64/python3.6/site-packages/")

import xraylib
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(
                    prog = 'refractive_indices',
                    description = 'Calculates complex refractive indices and saves them into a .txt file. The calculation is based on xraylib which uses Crossections from NIST database. For more information see: https://github.com/tschoonj/xraylib/wiki/The-xraylib-API-list-of-all-functions#nist-compound-catalog',
                    epilog = '')
    parser.add_argument("--density", type=float, nargs='+', help="Set density manual. Default is None to get densities from NIST-database", default=None)
    parser.add_argument("--material", type=str, nargs='+', help="Set Materials. Possible are Elements, ElementCompounds and Compounds from NIST-database", default=None)
    parser.add_argument("--e_0", type=float, help="Set lower energy band limit in keV")
    parser.add_argument("--e_n", type=float, help="Set upper energy band limit in keV")
    parser.add_argument("--delta_e", type=float, help="Set energy resolution in keV")
    parser.add_argument("--output", type=str, help="Output directory for .txt file containing refractive indices. Format: E[keV], delta, beta", default="./")    
    return parser.parse_args()

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
    
def get_filename(energies, material_name):
    material_name = material_name.replace(" ", "_")
    forbidden_characters = ",()"
    for character in forbidden_characters:
        material_name = material_name.replace(character, "")
    return material_name + ".txt"

def get_absorption_edges_in_interval(atomic_number, energy_interval):
    absorption_edges = []
    for i in range(32):
        energy = xraylib.EdgeEnergy(atomic_number, i)
        if energy > energy_interval[1]:
            break
        elif energy > energy_interval[0]:
            absorption_edges.append(energy)
    return absorption_edges

def get_refractive_index_from_xraylib(energies, material_name, output=None, density=None):
    try:
        material_compound = xraylib.CompoundParser(material_name)
        material_type = "elements"
    except ValueError as ve:
        matching_compound_list = []
        for nist_material in nist_material_list:
            if nist_material.lower() == material_name.lower():
                material_type = "nist"
                matching_compound_list = [nist_material]
                break
            elif nist_material.lower().find(material_name.lower())>=0:
                matching_compound_list.append(nist_material)
        if len(matching_compound_list) == 1:
            if material_type == "nist":
                material_compound = xraylib.GetCompoundDataNISTByName(matching_compound_list[0])
            else:
                accepted = query_yes_no("Found no matching material compound. Did you mean " + matching_compound_list[0])
                if accepted:
                    material_type = "nist"
                    material_compound = xraylib.GetCompoundDataNISTByName(matching_compound_list[0])
                else:
                    print("No matching material found")
                    sys.exit(1)
        else:
            print("Found " + str(len(matching_compound_list)) + " matching materials. Please specify what you mean: " + str(matching_compound_list))
            sys.exit(1)
    if material_type == "nist":                      
        if density is None:
            density = material_compound["density"]
    else:
        if density is not None:
            density = density
        elif material_compound["nElements"] == 1:
            density = xraylib.ElementDensity(material_compound["Elements"][0])
        else:
            print("Please provide density of element compounds!")
    #absorption_edges = get_absorption_edges_in_interval(material_compound["Elements"])

    refractive_index = np.zeros(energies.shape[0], dtype=np.cdouble)
    for j in range(energies.shape[0]):
        refractive_index[j] = xraylib.Refractive_Index(material_name, energies[j], density)
    if output is not None:
        np.savetxt(output + get_filename(energies, material_name),
                np.c_[energies, 1 - refractive_index.real, refractive_index.imag], 
                header=material_name + ", density = " + str(density) + " g/cm**3 " + "\n" + "Energy range: [{:.2e}".format(energies[0]) + ": {:.2e}".format(energies[-1]) + "] keV \n" + "Energies[keV] \t delta \t \t \t beta")
    return refractive_index


if __name__ == "__main__":
    args = parse_args()  
    energies = np.linspace(args.e_0, args.e_n, num=int((args.e_n - args.e_0) / args.delta_e) + 1)
    nist_material_list = xraylib.GetCompoundDataNISTList()
    material_type = None
    for i in range(len(args.material)):
        material_name = args.material[i]
        if args.density is not None:
            density = args.density[i]
        else:
            density = None
        refractive_index = get_refractive_index_from_xraylib(energies, material_name, output=args.output, density=density)
        print("Refractive inices written to: " + args.output + get_filename(energies, material_name))


                    
