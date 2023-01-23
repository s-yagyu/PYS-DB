"""
Read mol file to extract incetance and meta.

Drawing an organic figure from a smile

additional install pckege
rdkit, (pubchempy)

"""
__author__ = 'Shinjiro Yagyu'
__email__ = 'yagyu.shinjiro@gmail.com'
__version__ = '1.0'
__license__ = 'BSD-3'
__date__= "22 Aug 2022"


from pathlib import Path

from rdkit import Chem
from rdkit.Chem import inchi
from rdkit.Chem import Draw

# import pubchempy


def mol2meta(mol_file_path,mol_name=None,printf=False,size=(300,300)):
    """ make a figure from mol file

    Args:
        mol_file_path (str): mol file path
        mol_name (str, optional): save mol figure name. Defaults to None.
        printf (bool, optional): data print. Defaults to False.

    Returns:
        dict: molmeta, molobj
        keys: meta:['smiles',inchi','inchikey'], obj:['img',mol_object']
    """
    mol_p = Path(mol_file_path)
    m_ = Chem.MolFromMolFile(str(mol_p))
    m_img = Draw.MolToImage(m_,size=size)
    # isomericSmiles
    m_smiles = Chem.MolToSmiles(m_)
    m_inchi = inchi.MolToInchi(m_, options='', logLevel=None, treatWarningAsError=False)
    m_inchikey = Chem.MolToInchiKey(m_)
    
    if printf:
        print(m_smiles)
        print(m_inchi)
        Draw.MolToImage(m_)
        if mol_name is None:
            mol_name =  mol_p.with_suffix('.png')
            Draw.MolToFile(m_,f'{mol_name}',size=size)
  
    return {'smiles': m_smiles,'inchi': m_inchi,'inchikey':m_inchikey}, {'img': m_img,'mol_object': m_}


def smiles2mol(smiles_,draw=True,save=False,save_name=None):
    """convert smiles to mol data

    Args:
        smiles_ (str): smiles string
        draw (bool, optional): draw. Defaults to True.
        save (bool, optional): save. Defaults to False.
        save_name (str, optional): save file name. Defaults to None.

    Returns:
        mol opject
    """
    smol = Chem.MolFromSmiles(smiles_)
    simg = Draw.MolToImage(smol)
    
    if draw:
        Draw.MolToImage(smol)
        
    if save:
        if save_name is None:
            save_name = 'smiles.png'
        Draw.MolToFile(smol,save_name,size=(300, 300))
        
    return smol, simg

# def iupac_name_pubchem(smiles_):
#     """
#     Args:
#         smiles_ (str): smiles

#     Returns:
#        dict: iupac name
       
#     ref:
#         Converting SMILES to chemical name or IUPAC name using rdkit or other python module
#         https://stackoverflow.com/questions/64329049/converting-smiles-to-chemical-name-or-iupac-name-using-rdkit-or-other-python-mod
        
        
#     """
#     compounds = pubchempy.get_compounds(smiles_, namespace='smiles')
#     try:
#         match = compounds[0]
#         print(match.iupac_name)
#         return {'iupac': match.iupac_name}
    
#     except Exception as e:
#         print(e)
#         return {'iupac': None}
        

if __name__ == '__main__':
    # mol_file_path = r'C:\Users\me\Desktop\4MeOPEPTC.mol'
    # a,b = mol2meta(mol_file_path,mol_name=None,printf=False,size=(300,300))
    # print(a)
    pass
    