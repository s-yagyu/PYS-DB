"""
import module
    pandas, streamlit, streamlit_aggrid

```
conda install -c conda-forge streamlit
```

```
pip install streamlit_aggrid
pip install japanize-matplotlib

```

original module
    datconv

Stremlit操作
run:
    streamlit run  .py

デフォルトでは 8501 ポートで Streamlit のアプリケーションサーバが起動する。
ブラウザで開いて結果を確認

open:
    http://localhost:8501

Stop:
    ctl + c

"""

__author__ = 'Shinjiro Yagyu'
__version__ = '2.1'
__license__ = '3BSD'
__date__= "23 Jan 2023"
__update__= "14 Apr 2023"


import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

#日本語フォント対応
import matplotlib
matplotlib.rcParams['font.family'] = "MS Gothic"


import numpy as np
from PIL import Image

import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from st_aggrid.shared import JsCode

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from acdatconv import datconv as dc
from dbconv import molConv as mc
from dbconv import sampleMetaConv as smc


# JSON  Data list 
BASIC = Path(r'./Basic')
ADVANCE = Path(r'./Advance')

# @st.cache_data # Versin依存
#１度呼ばれたらそれ以降は呼ばれても無視される。
@st.cache 
def marge_data_list(basic, advance):
    
    def read_marge_json(path):
        temp_path = Path(path)
        temp_json_list= list(temp_path.glob("*.json"))

        temp_df_list =[]
        for dfi in temp_json_list:
            df_temp = pd.read_json(str(dfi), orient='records')
            temp_df_list.append(df_temp)
            
        return temp_df_list
    
    basic_df_list =  read_marge_json(basic)
    advance_df_list = read_marge_json(advance) 

    return basic_df_list, advance_df_list

basic_df_list, advance_df_list = marge_data_list(BASIC, ADVANCE)

df_basic = pd.concat(basic_df_list)  
df_advance = pd.concat(advance_df_list)
df_all = pd.concat(basic_df_list + advance_df_list)


def main():
    st.title('PYS DB')

    # sidebar serch conditons
    st.sidebar.write('Search conditon')

    df_select = df_all[['sampleAbbreviation',  'thresholdEnergy', 'uvIntensity59', 'sampleDescription',
                        'substrateName', 'sampleShape', 'generalName','smiles', 'slope', 'bg',]]
     
    if 'df' not in st.session_state: 
        st.session_state['df'] = df_select

    def query_on_click():
 
        if  query_select == "Name":
            query_msg = f'sampleName.str.contains("{sample_name}", case=False)'

        elif  query_select == "Abbreviation":
            query_msg = f'sampleAbbreviation.str.contains("{sample_name}", case=False)'
                        
        elif  query_select == "Smiles":
            query_msg = f'smiles.str.contains("{sample_name}", case=False)'
            
        elif  query_select == "inchi":
            query_msg = f'inchi.str.contains("{sample_name}", case=False)'
            
        elif  query_select == "inchikey":
            query_msg = f'inchikey.str.contains("{sample_name}", case=False)'
            
        elif  query_select == "Threshold":
            query_msg = f'{th_min} < thresholdEnergy <= {th_max}'
            
        elif  query_select == "Power":
            query_msg = f'{pw_min} < targetUv <= {pw_max}'


        if dbsource == 'Basic':
            df_r = df_basic.query(query_msg, engine='python')
        elif dbsource =='Advance':
            df_r = df_advance.query(query_msg, engine='python')
        elif dbsource =='All':
             df_r = df_all.query(query_msg, engine='python')
             
        df_r_select = df_r[['sampleAbbreviation',  'thresholdEnergy', 'uvIntensity59', 'sampleDescription',
                            'substrateName', 'sampleShape', 'generalName','smiles', 'slope', 'bg']]

        st.session_state['df'] = df_r_select
        
        # データフレームを書き出す場合
        # st.dataframe(df_r_select)

    def query_clear_click():
        st.session_state['df'] = df_select
        

    # Wegit
    dbsource = st.sidebar.radio("Data Source",('All','Basic', 'Advance'))
    query_select = st.sidebar.selectbox("Search parameter", 
                        ("Name","Abbreviation","Smiles","inchi", "inchikey", 
                         "Threshold", "Power"),
                        index=5)

    st.sidebar.markdown('### Name, smiles, inchi query')
    sample_name = st.sidebar.text_input('Sample Name:',value='si')

    st.sidebar.markdown('### Threshold query')
    th_min = st.sidebar.number_input(label='min', value=4.0)
    th_max = st.sidebar.number_input(label='max', value=6.5)
  
    st.sidebar.markdown('### Power query')
    pw_min = st.sidebar.number_input(label='min', value=9.0)
    pw_max = st.sidebar.number_input(label='max', value=300.0)

    query_button = st.sidebar.button("Query", on_click=query_on_click)
    clear_button = st.sidebar.button("Query Clear", on_click=query_clear_click)

    # ---

    nu_length =  len(st.session_state['df'])
    st.write(f'number of rows: {nu_length}')

    gb = GridOptionsBuilder.from_dataframe(st.session_state['df'])
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)

    gridOptions = gb.build()

    data = AgGrid(st.session_state['df'], 
                gridOptions=gridOptions, 
                enable_enterprise_modules=True, 
                allow_unsafe_jscode=True, 
                update_mode=GridUpdateMode.SELECTION_CHANGED)

    # --- plot
    
    selected_rows = data["selected_rows"]
    # print(f'select rows:{selected_rows}')
    
    selected_rows_df = pd.DataFrame(selected_rows)
    # print(selected_rows)
   
    if len(selected_rows) != 0:
        for th, sl, gn in zip(selected_rows_df["thresholdEnergy"], selected_rows_df["slope"],selected_rows_df['generalName']):

            # TODO:場当たり的な書き方をしている。
            # 選ばれたDFには、スペクトルのデータが含まれていないために、大本の表から値が一致するデータを検索して抜き出している。       
            df_fig = df_all[(df_all['thresholdEnergy'] == th) & 
                            (df_all['generalName'] == gn) &
                            (df_all['slope'] ==sl)]
            
           
            # df_fig = df_fig.infer_objects()
            # print('----')
            # print(df_fig)
            # print(df_fig.columns)
            
            # シリーズの戻り値に注意 
            # print(df_fig['smiles'])-> 0    COc1ccc(CCN2C(=O)c3ccc4c5ccc6c7c(ccc(c8ccc(c3c...Name: smiles, dtype: object
            # print(df_fig['smiles'].values) ->['COc1ccc(CCN2C(=O)c3ccc4c5ccc6c7c(ccc(c8ccc(c3c48)C2=O)c75)C(=O)N(CCc2ccc(OC)cc2)C6=O)cc1']
            # print(df_fig['smiles'].values[0]) -> COc1ccc(CCN2C(=O)c3ccc4c5ccc6c7c(ccc(c8ccc(c3c48)C2=O)c75)C(=O)N(CCc2ccc(OC)cc2)C6=O)cc1
            
            width_u = 5.2
            height_u = 4
            nrows=1
            ncols=2
            fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*width_u,nrows*height_u), squeeze=False,)
            
            # ネストしているリストを解消している（必要ないかもしれない）
            energy = np.array(sum(df_fig["uvEnergy"], []))
            nayield = np.array(sum(df_fig["nayield"], []))
            guid = np.array(sum(df_fig["guideline"], []))
            # energy = np.array(df_fig["uvEnergy"])
            # nayield = np.array(df_fig["nayield"])
            # guid = np.array(df_fig["guideline"])
            
            ax[0,0].plot(energy, nayield,'ro-',label='Data')
            ax[0,0].plot(energy, guid,'b-',label='Guid')
            ax[0,0].set_title(f"{df_fig['file_name'].values[0]}")
            ax[0,0].set_xlabel('Energy [eV]')
            ax[0,0].set_ylabel(f"Yield^{df_fig['powerNumber'].values[0]:.2f}")
            ax[0,0].grid()
            ax[0,0].legend(title=f"Power: {df_fig['uvIntensity59'].values[0]:.2f}nw\nTh: {df_fig['thresholdEnergy'].values[0]:.2f}eV\nslop: {df_fig['slope'].values[0]:.2f}",
                        loc='upper left')
            
            if df_fig['smiles'].values[0] is None or df_fig['smiles'].values[0] == '' :
                ax[0,1].axis("off")
                # fig.delaxes(ax[0,1])
                
            else:
                smol, simg = mc.smiles2mol(df_fig['smiles'].values[0],draw=False,save=False,save_name=None)
                mol_img = np.array(simg)
                ax[0,1].set_title(f"{df_fig['sampleName'].values[0]}")
                ax[0,1].imshow(mol_img)
                ax[0,1].set_xticks([])
                ax[0,1].set_yticks([])
                
            # fig.suptitle(title)
            plt.tight_layout()
            
            st.pyplot(fig)
      

if __name__ == '__main__':
    main()
