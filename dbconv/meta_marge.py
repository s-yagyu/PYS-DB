""" 
MDRの登録単位は論文ごと
・同じ論文に使われているデータは1つのフォルダーにまとめる。
・フォルダー名は、Excelファイルから拡張子を取ったものと同じ
（著者名_記入月_記入年, 例:Yagyu_09_2022)
・Example
    Yagyu_09_2022
        |-Yagyu_09_2022.xlsx
        |-AAA.dat
        |-BBB.dat
        |-CCC.dat
        |-aaa.mol
        |-bbb.mol
        |-abc.pdf
        |-def.csv
        |-ghi.xlsx

このプログラムは、MDRに登録されたデータ（フォルダー単位）から検索メタデータを作成する。  
List-TypeのJSONファイルを作成。ファイル名は、Folder名.json。

"""
from pathlib import Path

import pandas as pd

from acdatconv import datconv as dv
from . import molConv as mc
from . import sampleMetaConv as smc


def marge_files(folderPath, outpath=None):
    """
    Data Folder (Excel, dat, mol etc.)のデータからメタデータファイル（JSONファイル）を作成する
    
    Args:
        folderPath (Str or Pathlib): Data(Excel,dat,mol)が入っているフォルダーを指定する。
        outpath (str, optional): Json output path. Defaults to None. if None, outputpath is floderpath.
        研究開発用のフォルダー、と基本材料のフォルダーとに分ける

    Returns:
        marge_dict, marge_df, str(out_json_full_path)
    """
    
    folder_path = Path(folderPath)
    excel_file_path= list(folder_path.glob("*.xlsx"))

    if outpath is None:
        out_path = folder_path
    else:
        out_path = Path(outpath)  
    
    # print(excel_file_path)
    
    for fi in excel_file_path:
        try: #Excelファイルが複数入っていてもメタデータの並びに一致しないものは無視される。 (dataInvoice Excel x1 , other)
            sample_meta = smc.ReadExcelSampleMeta(fi)
            sample_meta.convert()
            sample_dict = sample_meta.data_dict_records
        except:
            print(f'Not data inovoice file:{fi}')

    # print(sample_dict)
    try: # sample_dict: Invoice Excel fileが読み込めていない場合はエラーとなる
        marge_dict = []
        for i, di in enumerate(sample_dict):
            # print(i)
            mol_file_name = di["molFileName"]
            # mol fileが含まれていない場合は、{'smiles': '','inchi': '','inchikey':''}は空欄
            try:
                if mol_file_name !=  '' or mol_file_name != '-':
                    print(mol_file_name)
                    mol_p = list(folder_path.glob(f'{mol_file_name}'))[0]
                    # print(mol_p)
                    mol_dict, molobj = mc.mol2meta(mol_p,mol_name=None, printf=False, size=(300,300))
                    print(mol_dict)
            # keys: meta:['smiles',inchi','inchikey'], obj:['img',mol_object']
            except:
                # TODO '' の方がよいかNoneの方がよいか検討が必要
                print('mol file error')
                mol_dict =  {'smiles': '','inchi': '','inchikey':''}
            
            dat_file_name = di["datFileName"]
            dat_p = list(folder_path.glob(f'{dat_file_name}'))[0]
            # print(dat_p)
            acdata = dv.AcConv(dat_p)
            acdata.convert()
            dat_dict = acdata.metadata
            
            m_dict = dict(**di, **mol_dict, **dat_dict)
            marge_dict.append(m_dict)
            
        marge_df = pd.DataFrame(marge_dict)
        out_json_name = f'{folder_path.resolve().name}.json'
        out_json_full_path = out_path / out_json_name
        marge_df.to_json(str(out_json_full_path),date_format='iso',orient='records')   
        print(f'Output Json file: {str(out_json_full_path)}')    
        return marge_dict, marge_df, str(out_json_full_path)

    except:
        print('error! check excel file')
        return "", "",""
    
if __name__ == '__main__':
    
    pass
    # folder_path =Path(r"C:\Users\me\\Desktop\Yanagida20221001")
    # md,mdf = marge_files(folder_path, outpath=r'Advance')


    # folder_path =Path(r"C:\Users\me\Desktop\OLED20220829")
    # md,mdf = marge_files(folder_path, outpath=r'Basic')

   
    # folder_path =Path(r"C:\Users\me\Desktop\OLED20220803")
    # md,mdf = marge_files(folder_path, outpath=r'Basic')
   
    # print(mdf.columns)
