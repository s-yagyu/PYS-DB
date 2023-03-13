# MDR 登録用yamlファイル作成
# PyYAML,Yamale モジュールが必要

from pathlib import Path

import json
import toml
import yaml

def toml2json(tfile, save=False):
    """Read toml file -> convert json format

    Args:
        tfile (str or pathlib): file name
        save (bool, optional): save json. Defaults to False.

    Returns:
        dict, json
    
    Examples:
        Toml-> JSON
        fn2=r'validationData\AC3_off.toml'
        jd,js = toml2json(tfile=fn2, save=True)
    """
    tpath = Path(tfile)
    with open(tpath) as file:
        # toml to dict
        dict_obj = toml.load(file)
        # dict to toml
        js = json.dumps(dict_obj)
        # print(js)
        
        if save:
            with open(tpath.with_suffix('.json'),'w') as f:
                json.dump(dict_obj ,f, indent=4)
        
    return dict_obj, js

def yaml2json(yfile, save=False):
    """Read yaml file -> convert json format

    Args:
        yfile (str or pathlib): file name
        save (bool, optional): save json. Defaults to False.

    Returns:
        dict, json
    
    Examples:
        yaml-> JSON
        fn2=r'validationData\AC3_off.yml'
        jd,js = yaml2json(yfile=fn2, save=True)
    """
    ypath = Path(yfile)
    
    with open(ypath,encoding="utf-8") as file:
        # YAML to dict
        dict_obj = yaml.safe_load(file)
        # dict to JSON
        js = json.dumps(dict_obj,)
        # print(js)
        
        if save:
            with open(ypath.with_suffix('.json'),'w') as f:
                json.dump(dict_obj ,f, indent=4)
        
    return dict_obj, js

def dic2yml(ydict,save=True,file_name=None):
    
    if save:
        if file_name  is None:
            file_name = 'temp.yaml'
        with open(file=file_name, mode='w', encoding='utf-8') as f:
            yaml.dump(
                    data=ydict,
                    stream=f,
                    allow_unicode=True,  # Unicode 文字をデコードされた文字列で表現
                    sort_keys=False)
                
    yml_out = yaml.dump(data=ydict,
                        allow_unicode=True,
                        sort_keys=False)

    return  yml_out

# ------
# MDR登録定義ファイル　inputの箇所をExcelファイルのキーから取り出して記入する
Default_MDR_dict={
            'id': None, 
           'titles': [{'title': '_datasetTitle_',  # input
                       'title_type': 'original', 
                       'lang': 'ja'}],
            'identifiers': [{'identifier': '_folder_name_'}], # input
           
           'resource_type': 'dataset', 
           'descriptions': [{'description': 'This dataset is part of the photoelectron Yield Spectroscopy Database.', 'lang': 'en'}], 
           'subjects': [{'subject': 'PYS'}, {'subject': 'Photoelectron yield spectroscopy'}], 
           'creators': [{'name': '_dataProvider_', # input
                         'orcid': None, 'e_rad': None, 'role': 'author', 
                         'organization': '_providerOrganization_', # input
                         'department': None, 
                         'ror': None}], 
            
           'contact_agents': [{'name':'Yagyu Shinjiro',  
                               'email':'yagyu.shinjiro@nims.go.jp',  
                               'organization': 'NIMS', 
                               'ror': None}], 
           
           'publisher': {'organization': 'NIMS', 'ror': 'https://ror.org/026v1ze26'}, 
           'state': 'draft', 
           'collections': [{'title': 'MDR PYS DB', 
                            'identifier': '6a203d7f-add0-4ea7-a0ea-16d2e8191cd9',
                            'description':'A digital database of photoelectron yield spectroscopy (PYS) datasets'}], 
  
           'first_published_url': '_webReference_', # input
           'visibility': 'open_to_public', 
           'rights': [{'description': '_dataLicense_', # input
                       'date_licensed': None, 
                       'condition_of_use': None, 
                       'identifier': '_dataLicense_'}], # input
           
           'data_origins': [{'data_origin_type': 'experiment'}], 
           'managing_organization': {'ror': 'https://ror.org/026v1ze26', 'organization': 'NIMS', 'department': None},
           'instruments': [{'name': 'AC series',  
                            'identifier': None, 'description': None,  
                            'function_vocabulary': None, 'function_description': None, 
                            'manufacturer': 'Rikenkeiki'}],
        }

def MDR_meta(mg_list_dict, id_name):
    """JSONファイルからDict形式に変換したメタデータからMDRの登録用のDictファイルを作成する。

    Args:
        mg_list_dict (dict): JSONファイルからDict形式に変換したメタデータ
        id_name (str): Folder name contained in dat data

    Returns:
        dict: MDRの登録用のDictファイル
    """
    
    temp_dict = Default_MDR_dict.copy()
    
    # folder_path = Path(folderPath)
    # folder_name = f'{folder_path.resolve().name}'
    temp_dict['identifiers'][0]['identifier'] = id_name
    
    for k,v in mg_list_dict[0].items():
             
        if k == 'datasetTitle':
            temp_dict['titles'][0]['title'] = v
            
        elif k == 'providerOrganization':
            temp_dict['creators'][0]['organization'] = v
            # temp_dict['contact_agents'][0]['organization']= v
            
        elif k == 'dataProvider' :
            temp_dict['creators'][0]['name'] = v
            # temp_dict['contact_agents'][0]['name']= v
            
        elif k == 'dataLicense' :
            if 'CC-BY':
                right_description = 'Creative Commons BY Attribution 4.0 International'
                right_https = 'https://creativecommons.org/licenses/by/4.0/legalcode'
            
            elif 'CC-BY-SA' :
                right_description = 'Creative Commons BY-SA Attribution 4.0 International'
                right_https = 'https://creativecommons.org/licenses/by-sa/4.0/legalcode'
            else:
                right_description = 'None'
                right_https = 'None'
            
            temp_dict['rights'][0]['description'] = right_description
            temp_dict['rights'][0]['identifier']  = right_https
        
        elif k == 'webReference':
            if v is None:
                temp_dict['first_published_url'] = None
                
            else:
                vtemp = v.replace('\/', '/')
                temp_dict['first_published_url'] = vtemp
        else:
            pass        
                
    return temp_dict        

def json2MDR_yaml(json_data_path,printf=True):
    
    folder_path = Path(json_data_path)
    
    with folder_path.open( mode="rt", encoding="utf-8") as f:
        data = json.load(f)		# JSONのファイル内容をdictに変換する。

    folder_name = f'{folder_path.resolve().stem}'
    ymdict = MDR_meta(data, folder_name)
    if printf:
        print(ymdict)
        
    dic2yml(ymdict,save=True,file_name=f'{folder_name}.yml')
    
if __name__=='__main__':
    pass
    # json_data_path =r''
    # json2MDR_yaml(json_data_path,printf=False)
    
    