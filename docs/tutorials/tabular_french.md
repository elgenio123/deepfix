# Evaluer la qualité de votre préparation de données et de votre Modèle

---



## Installer DeepFix

Accéder à la documentation de DeepFix: [link text](https://delcaux-labs.github.io/deepfix/)


```python
!curl -LsSf https://astral.sh/uv/install.sh | sh
```

    downloading uv 0.9.11 x86_64-unknown-linux-gnu
    no checksums to verify
    installing to /usr/local/bin
      uv
      uvx
    everything's installed!
    


```python
!uv pip install git+https://github.com/delcaux-labs/deepfix.git
```

    [2mUsing Python 3.12.12 environment at: /usr[0m
    [2K[2mResolved [1m335 packages[0m [2min 28.74s[0m[0m                                      [0m
    [2K[2mPrepared [1m89 packages[0m [2min 18.43s[0m[0m                                           
    [2mUninstalled [1m10 packages[0m [2min 1.75s[0m[0m
    [2K[2mInstalled [1m89 packages[0m [2min 933ms[0m[0m0                             [0m
     [32m+[39m [1masync-lru[0m[2m==2.0.5[0m
     [32m+[39m [1mbackrefs[0m[2m==6.1[0m
     [32m+[39m [1mcatboost[0m[2m==1.2.8[0m
     [32m+[39m [1mcategory-encoders[0m[2m==2.9.0[0m
     [32m+[39m [1mchoreographer[0m[2m==1.2.1[0m
     [32m+[39m [1mcolorama[0m[2m==0.4.6[0m
     [32m+[39m [1mdacite[0m[2m==1.9.2[0m
     [32m+[39m [1mdatabricks-sdk[0m[2m==0.73.0[0m
     [32m+[39m [1mdeepchecks[0m[2m==0.18.0.dev1 (from git+https://github.com/delcaux-labs/deepchecks.git@5eec512bfd4635df8a0b27d0d2e20e3b938e9e93)[0m
     [32m+[39m [1mdeepfix[0m[2m==0.1.0 (from git+https://github.com/delcaux-labs/deepfix.git@626c913e758baee3c2c5a9f5c3465b306bd0c2e0)[0m
     [32m+[39m [1mdeepfix-core[0m[2m==0.1.0 (from git+https://github.com/delcaux-labs/deepfix.git@626c913e758baee3c2c5a9f5c3465b306bd0c2e0#subdirectory=deepfix-core)[0m
     [32m+[39m [1mdeepfix-sdk[0m[2m==0.1.0 (from git+https://github.com/delcaux-labs/deepfix.git@626c913e758baee3c2c5a9f5c3465b306bd0c2e0#subdirectory=deepfix-sdk)[0m
     [32m+[39m [1mdocker[0m[2m==7.1.0[0m
     [32m+[39m [1mfairlearn[0m[2m==0.13.0[0m
     [32m+[39m [1mfeature-engine[0m[2m==1.9.3[0m
     [32m+[39m [1mfiletype[0m[2m==1.2.0[0m
     [32m+[39m [1mfire[0m[2m==0.7.1[0m
     [32m+[39m [1mflask-cors[0m[2m==6.0.1[0m
     [32m+[39m [1mftfy[0m[2m==6.3.1[0m
     [32m+[39m [1mfuncy[0m[2m==2.0[0m
     [32m+[39m [1mgensim[0m[2m==4.4.0[0m
     [32m+[39m [1mghp-import[0m[2m==2.1.0[0m
     [32m+[39m [1mgraphene[0m[2m==3.4.3[0m
     [32m+[39m [1mgraphql-core[0m[2m==3.2.7[0m
     [32m+[39m [1mgraphql-relay[0m[2m==3.2.0[0m
     [32m+[39m [1mgriffe[0m[2m==1.15.0[0m
     [32m+[39m [1mgunicorn[0m[2m==23.0.0[0m
     [32m+[39m [1mhuey[0m[2m==2.5.4[0m
     [32m+[39m [1mimagehash[0m[2m==4.3.2[0m
     [32m+[39m [1mimgaug[0m[2m==0.4.0[0m
     [32m+[39m [1mjedi[0m[2m==0.19.2[0m
     [32m+[39m [1mjson5[0m[2m==0.12.1[0m
     [32m+[39m [1mjupyter-lsp[0m[2m==2.3.0[0m
     [32m+[39m [1mjupyterlab[0m[2m==4.5.0[0m
     [32m+[39m [1mjupyterlab-server[0m[2m==2.28.0[0m
     [32m+[39m [1mkaleido[0m[2m==1.2.0[0m
     [32m+[39m [1mkmodes[0m[2m==0.12.2[0m
     [32m+[39m [1mlightning[0m[2m==2.5.6[0m
     [32m+[39m [1mlightning-utilities[0m[2m==0.15.2[0m
     [31m-[39m [1mllvmlite[0m[2m==0.43.0[0m
     [32m+[39m [1mllvmlite[0m[2m==0.45.1[0m
     [32m+[39m [1mlogistro[0m[2m==2.0.1[0m
     [32m+[39m [1mmergedeep[0m[2m==1.3.4[0m
     [32m+[39m [1mminify-html[0m[2m==0.18.1[0m
     [32m+[39m [1mmkdocs[0m[2m==1.6.1[0m
     [32m+[39m [1mmkdocs-autorefs[0m[2m==1.4.3[0m
     [32m+[39m [1mmkdocs-get-deps[0m[2m==0.2.0[0m
     [32m+[39m [1mmkdocs-git-revision-date-localized-plugin[0m[2m==1.5.0[0m
     [32m+[39m [1mmkdocs-material[0m[2m==9.7.0[0m
     [32m+[39m [1mmkdocs-material-extensions[0m[2m==1.3.1[0m
     [32m+[39m [1mmkdocstrings[0m[2m==0.30.1[0m
     [32m+[39m [1mmkdocstrings-python[0m[2m==1.19.0[0m
     [32m+[39m [1mmlflow[0m[2m==3.6.0[0m
     [32m+[39m [1mmlflow-skinny[0m[2m==3.6.0[0m
     [32m+[39m [1mmlflow-tracing[0m[2m==3.6.0[0m
     [32m+[39m [1mmultimethod[0m[2m==1.12[0m
     [31m-[39m [1mnotebook[0m[2m==6.5.7[0m
     [32m+[39m [1mnotebook[0m[2m==7.5.0[0m
     [31m-[39m [1mnumba[0m[2m==0.60.0[0m
     [32m+[39m [1mnumba[0m[2m==0.62.1[0m
     [31m-[39m [1mnumpy[0m[2m==2.0.2[0m
     [32m+[39m [1mnumpy[0m[2m==2.3.5[0m
     [32m+[39m [1mopen-clip-torch[0m[2m==3.2.0[0m
     [31m-[39m [1mopencv-python[0m[2m==4.12.0.88[0m
     [32m+[39m [1mopencv-python[0m[2m==4.11.0.86[0m
     [31m-[39m [1mopencv-python-headless[0m[2m==4.12.0.88[0m
     [32m+[39m [1mopencv-python-headless[0m[2m==4.11.0.86[0m
     [32m+[39m [1mpaginate[0m[2m==0.5.7[0m
     [31m-[39m [1mpandas[0m[2m==2.2.2[0m
     [32m+[39m [1mpandas[0m[2m==2.3.3[0m
     [32m+[39m [1mpandas-profiling[0m[2m==3.6.6[0m
     [32m+[39m [1mpathspec[0m[2m==0.12.1[0m
     [32m+[39m [1mphik[0m[2m==0.12.5[0m
     [31m-[39m [1mplotly[0m[2m==5.24.1[0m
     [32m+[39m [1mplotly[0m[2m==6.5.0[0m
     [32m+[39m [1mpuremagic[0m[2m==1.30[0m
     [32m+[39m [1mpycaret[0m[2m==2.2.2[0m
     [32m+[39m [1mpydeck[0m[2m==0.9.1[0m
     [32m+[39m [1mpyldavis[0m[2m==3.4.1[0m
     [32m+[39m [1mpymdown-extensions[0m[2m==10.17.1[0m
     [32m+[39m [1mpynomaly[0m[2m==0.3.4[0m
     [32m+[39m [1mpyod[0m[2m==2.0.5[0m
     [32m+[39m [1mpytest-timeout[0m[2m==2.4.0[0m
     [32m+[39m [1mpytorch-ignite[0m[2m==0.5.3[0m
     [32m+[39m [1mpytorch-lightning[0m[2m==2.5.6[0m
     [32m+[39m [1mpyyaml-env-tag[0m[2m==1.1[0m
     [31m-[39m [1mrich[0m[2m==13.9.4[0m
     [32m+[39m [1mrich[0m[2m==14.2.0[0m
     [32m+[39m [1mscikit-plot[0m[2m==0.3.7[0m
     [31m-[39m [1mscipy[0m[2m==1.16.3[0m
     [32m+[39m [1mscipy[0m[2m==1.15.3[0m
     [32m+[39m [1mseqeval[0m[2m==1.2.2[0m
     [32m+[39m [1msqlmodel[0m[2m==0.0.27[0m
     [32m+[39m [1mstreamlit[0m[2m==1.51.0[0m
     [32m+[39m [1mstructlog[0m[2m==25.5.0[0m
     [32m+[39m [1msupervision[0m[2m==0.27.0[0m
     [32m+[39m [1mtorchmetrics[0m[2m==1.8.2[0m
     [32m+[39m [1mvisions[0m[2m==0.8.1[0m
     [32m+[39m [1mydata-profiling[0m[2m==4.18.0[0m
    

## **Re-démarrer votre session Colab avant de continuer!**
``Runtime > 'Restart session'``
Ceci est dû à un problème de conflit entre différentes version de *numpy*

### Charger les donnees


```python
from deepfix_sdk import DeepFixClient
import os
```


```python
os.environ["DEEPFIX_API_KEY"] = "DEEPFIX-IS-AMAZING"
```


```python
client = DeepFixClient(api_url="https://deepfix.delcaux.com", timeout=120)
```


```python
from deepfix_sdk.data.datasets import TabularDataset
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
```


```python
# Chargez les données
X,y = load_breast_cancer(as_frame=True,return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
dataset_name = "breast_cancer_classification"

label = "target"
train = X_train.copy()
train[label] = y_train
cat_features = X_train.select_dtypes(include=['object','string','category']).columns.tolist()
if len(cat_features) > 0:
    cat_features = None

test = X_test.copy()
test[label] = y_test


```


```python
# Creer les datasets
train_data = TabularDataset(dataset=train, dataset_name=dataset_name, label=label, cat_features=cat_features)
val_data = TabularDataset(dataset=test, dataset_name=dataset_name, label=label, cat_features=cat_features)
```

    WARNING:deepfix_sdk.data.datasets:No categorical features provided, will automatically detect them. (Not Recommended)
    WARNING:deepfix_sdk.data.datasets:No categorical features provided, will automatically detect them. (Not Recommended)
    


```python
train_data.data.head()
```





  <div id="df-06a771be-a640-4b9c-8618-72d9b64ef91c" class="colab-df-container">
    <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean radius</th>
      <th>mean texture</th>
      <th>mean perimeter</th>
      <th>mean area</th>
      <th>mean smoothness</th>
      <th>mean compactness</th>
      <th>mean concavity</th>
      <th>mean concave points</th>
      <th>mean symmetry</th>
      <th>mean fractal dimension</th>
      <th>...</th>
      <th>worst texture</th>
      <th>worst perimeter</th>
      <th>worst area</th>
      <th>worst smoothness</th>
      <th>worst compactness</th>
      <th>worst concavity</th>
      <th>worst concave points</th>
      <th>worst symmetry</th>
      <th>worst fractal dimension</th>
      <th>target</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>546</th>
      <td>10.32</td>
      <td>16.35</td>
      <td>65.31</td>
      <td>324.9</td>
      <td>0.09434</td>
      <td>0.04994</td>
      <td>0.01012</td>
      <td>0.005495</td>
      <td>0.1885</td>
      <td>0.06201</td>
      <td>...</td>
      <td>21.77</td>
      <td>71.12</td>
      <td>384.9</td>
      <td>0.1285</td>
      <td>0.08842</td>
      <td>0.04384</td>
      <td>0.02381</td>
      <td>0.2681</td>
      <td>0.07399</td>
      <td>1</td>
    </tr>
    <tr>
      <th>432</th>
      <td>20.18</td>
      <td>19.54</td>
      <td>133.80</td>
      <td>1250.0</td>
      <td>0.11330</td>
      <td>0.14890</td>
      <td>0.21330</td>
      <td>0.125900</td>
      <td>0.1724</td>
      <td>0.06053</td>
      <td>...</td>
      <td>25.07</td>
      <td>146.00</td>
      <td>1479.0</td>
      <td>0.1665</td>
      <td>0.29420</td>
      <td>0.53080</td>
      <td>0.21730</td>
      <td>0.3032</td>
      <td>0.08075</td>
      <td>0</td>
    </tr>
    <tr>
      <th>174</th>
      <td>10.66</td>
      <td>15.15</td>
      <td>67.49</td>
      <td>349.6</td>
      <td>0.08792</td>
      <td>0.04302</td>
      <td>0.00000</td>
      <td>0.000000</td>
      <td>0.1928</td>
      <td>0.05975</td>
      <td>...</td>
      <td>19.20</td>
      <td>73.20</td>
      <td>408.3</td>
      <td>0.1076</td>
      <td>0.06791</td>
      <td>0.00000</td>
      <td>0.00000</td>
      <td>0.2710</td>
      <td>0.06164</td>
      <td>1</td>
    </tr>
    <tr>
      <th>221</th>
      <td>13.56</td>
      <td>13.90</td>
      <td>88.59</td>
      <td>561.3</td>
      <td>0.10510</td>
      <td>0.11920</td>
      <td>0.07860</td>
      <td>0.044510</td>
      <td>0.1962</td>
      <td>0.06303</td>
      <td>...</td>
      <td>17.13</td>
      <td>101.10</td>
      <td>686.6</td>
      <td>0.1376</td>
      <td>0.26980</td>
      <td>0.25770</td>
      <td>0.09090</td>
      <td>0.3065</td>
      <td>0.08177</td>
      <td>1</td>
    </tr>
    <tr>
      <th>289</th>
      <td>11.37</td>
      <td>18.89</td>
      <td>72.17</td>
      <td>396.0</td>
      <td>0.08713</td>
      <td>0.05008</td>
      <td>0.02399</td>
      <td>0.021730</td>
      <td>0.2013</td>
      <td>0.05955</td>
      <td>...</td>
      <td>26.14</td>
      <td>79.29</td>
      <td>459.3</td>
      <td>0.1118</td>
      <td>0.09708</td>
      <td>0.07529</td>
      <td>0.06203</td>
      <td>0.3267</td>
      <td>0.06994</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 31 columns</p>
</div>
    <div class="colab-df-buttons">

  <div class="colab-df-container">
    <button class="colab-df-convert" onclick="convertToInteractive('df-06a771be-a640-4b9c-8618-72d9b64ef91c')"
            title="Convert this dataframe to an interactive table."
            style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960">
    <path d="M120-120v-720h720v720H120Zm60-500h600v-160H180v160Zm220 220h160v-160H400v160Zm0 220h160v-160H400v160ZM180-400h160v-160H180v160Zm440 0h160v-160H620v160ZM180-180h160v-160H180v160Zm440 0h160v-160H620v160Z"/>
  </svg>
    </button>

  <style>
    .colab-df-container {
      display:flex;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    .colab-df-buttons div {
      margin-bottom: 4px;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

    <script>
      const buttonEl =
        document.querySelector('#df-06a771be-a640-4b9c-8618-72d9b64ef91c button.colab-df-convert');
      buttonEl.style.display =
        google.colab.kernel.accessAllowed ? 'block' : 'none';

      async function convertToInteractive(key) {
        const element = document.querySelector('#df-06a771be-a640-4b9c-8618-72d9b64ef91c');
        const dataTable =
          await google.colab.kernel.invokeFunction('convertToInteractive',
                                                    [key], {});
        if (!dataTable) return;

        const docLinkHtml = 'Like what you see? Visit the ' +
          '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
          + ' to learn more about interactive tables.';
        element.innerHTML = '';
        dataTable['output_type'] = 'display_data';
        await google.colab.output.renderOutput(dataTable, element);
        const docLink = document.createElement('div');
        docLink.innerHTML = docLinkHtml;
        element.appendChild(docLink);
      }
    </script>
  </div>

    </div>
  </div>




### Evaluer la qualité de votre préparation de données


```python
# Ingestion des données
result = client.get_diagnosis(
    train_data=train_data,
    test_data=val_data,
    language="french",
)
```

    FutureWarning: Filesystem tracking backend (e.g., './mlruns') is deprecated. Please switch to a database backend (e.g., 'sqlite:///mlflow.db'). For feedback, see: https://github.com/mlflow/mlflow/issues/18534
    



<style>
    progress {
        -webkit-appearance: none;
        border: none;
        border-radius: 3px;
        width: 300px;
        height: 20px;
        vertical-align: middle;
        margin-right: 10px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-bar {
        border-radius: 3px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-value {
        background-color: #9d60fb;
    }
    progress::-moz-progress-bar {
        background-color: #9d60fb;
    }
</style>







    FutureWarning: DataFrame.applymap has been deprecated. Use DataFrame.map instead.
    



<style>
    progress {
        -webkit-appearance: none;
        border: none;
        border-radius: 3px;
        width: 300px;
        height: 20px;
        vertical-align: middle;
        margin-right: 10px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-bar {
        border-radius: 3px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-value {
        background-color: #9d60fb;
    }
    progress::-moz-progress-bar {
        background-color: #9d60fb;
    }
</style>








    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]


    WARNING:deepfix_sdk.artifacts.manager:Artifact model_checkpoint not found for run breast_cancer_classification
    


    Output()



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">✓ Analysis complete!</span>
</pre>




```python
# Résultats
result.to_text(False)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">│                                               DEEPFIX ANALYSIS RESULT                                                │</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000">╭────────────────────────────────────────────────────── </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">Summary</span><span style="color: #008000; text-decoration-color: #008000"> ───────────────────────────────────────────────────────╮</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">L'analyse consolidée révèle un dataset avec une qualité de base excellente mais des problèmes structurels </span>           <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">importants. Trois caractéristiques présentent des risques de fuite de données avec des scores de pouvoir prédictif </span>  <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">anormalement élevés (&gt;0.7), nécessitant une investigation immédiate. De plus, une multicolinéarité sévère affecte </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">22+ paires de caractéristiques, ce qui pourrait compromettre la stabilité et l'interprétabilité du modèle. </span>          <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">Cependant, l'intégrité des données est impeccable avec aucune duplication, conflit d'étiquettes ou problèmes de </span>     <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">nullité détectés. La distribution entre les ensembles d'entraînement et de test est également cohérente. Les </span>        <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">priorités d'action incluent l'investigation des caractéristiques suspectées de fuite de données et la réduction de </span>  <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">la multicolinéarité par sélection de caractéristiques.</span>                                                               <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                      Summary Statistics                                      </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Metric                          Value                                                        </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Total Findings                 </span><span style="color: #000000; text-decoration-color: #000000"> 3                                                            </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Severity Distribution          </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">HIGH: 1  </span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold">MEDIUM: 1  </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">LOW: 1  </span><span style="color: #000000; text-decoration-color: #000000">                                 </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                  HIGH Severity Issues (1)                                   </span>
<span style="color: #800000; text-decoration-color: #800000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> #   </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Finding                                  </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Action                                   </span><span style="color: #800000; text-decoration-color: #800000">┃</span>
<span style="color: #800000; text-decoration-color: #800000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Scores de pouvoir prédictif élevés       </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Investiger la source et le calcul des    </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> indiquant des risques potentiels de      </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> caractéristiques 'worst perimeter',      </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> fuite de données                         </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> 'worst concave points' et 'worst radius' </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Les caractéristiques 'worst </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> pour s'assurer qu'elles ne contiennent   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">perimeter' (PPS 0.77), 'worst concave </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> pas d'informations directes ou           </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">points' (PPS 0.75), et 'worst radius' </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> indirectes sur la variable cible         </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(PPS 0.71) dépassent le seuil de 0.7 </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Les valeurs PPS supérieures à 0.7 </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">dans les données d'entraînement</span><span style="color: #000000; text-decoration-color: #000000">          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">suggèrent que ces caractéristiques </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">peuvent être trop prédictives, indiquant</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">potentiellement une fuite de données ou </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">des caractéristiques trop étroitement </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">liées à la variable cible</span><span style="color: #000000; text-decoration-color: #000000">                </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                 MEDIUM Severity Issues (1)                                  </span>
<span style="color: #808000; text-decoration-color: #808000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> #   </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Finding                                  </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Action                                   </span><span style="color: #808000; text-decoration-color: #808000">┃</span>
<span style="color: #808000; text-decoration-color: #808000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Multicolinéarité sévère avec plus de 22  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Appliquer des techniques de sélection de </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> paires de caractéristiques montrant une  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> caractéristiques ou de réduction de      </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> corrélation &gt; 0.9                        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> dimensionnalité pour éliminer les        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Plusieurs paires fortement </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> caractéristiques redondantes et          </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">corrélées incluant ('mean radius', </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> améliorer la stabilité du modèle         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">'worst radius'), ('mean perimeter', </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Une multicolinéarité élevée peut causer </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">'worst perimeter'), ('mean area', 'worst</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">des coefficients de modèle instables, du</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">area') avec une corrélation &gt; 0.9</span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">sur-apprentissage et des difficultés </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">dans l'interprétation de l'importance </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">des caractéristiques</span><span style="color: #000000; text-decoration-color: #000000">                     </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                   LOW Severity Issues (1)                                   </span>
<span style="color: #008000; text-decoration-color: #008000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> #   </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Finding                                  </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Action                                   </span><span style="color: #008000; text-decoration-color: #008000">┃</span>
<span style="color: #008000; text-decoration-color: #008000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Excellente intégrité des données sans    </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Maintenir les pratiques actuelles de     </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> problèmes de qualité détectés            </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> collecte et de prétraitement des données </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Tous les contrôles d'intégrité</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> pour préserver la qualité des données    </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">des données ont été passés : 0% de </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Le dataset montre une excellente </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">données dupliquées, 0% d'étiquettes </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">intégrité sans problèmes de qualité </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">conflictuelles, pas de types de données </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">détectés, ce qui donne confiance dans la</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">mélangés, pas de problèmes de caractères</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">fiabilité des données</span><span style="color: #000000; text-decoration-color: #000000">                    </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">spéciaux</span><span style="color: #000000; text-decoration-color: #000000">                                 </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>






    ''



### Evaluer la qualité de votre modèle


```python
# Fit model
model_name = "HistGradientBoostingClassifier"
clf = HistGradientBoostingClassifier(max_depth=3)
clf = clf.fit(train_data.X, train_data.y)
```


```python
# Ingestion des données
result = client.get_diagnosis(
    train_data=train_data,
    test_data=val_data,
    model_name=model_name,
    model=clf,
    language="french",
)
```



<style>
    progress {
        -webkit-appearance: none;
        border: none;
        border-radius: 3px;
        width: 300px;
        height: 20px;
        vertical-align: middle;
        margin-right: 10px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-bar {
        border-radius: 3px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-value {
        background-color: #9d60fb;
    }
    progress::-moz-progress-bar {
        background-color: #9d60fb;
    }
</style>







    FutureWarning: DataFrame.applymap has been deprecated. Use DataFrame.map instead.
    



<style>
    progress {
        -webkit-appearance: none;
        border: none;
        border-radius: 3px;
        width: 300px;
        height: 20px;
        vertical-align: middle;
        margin-right: 10px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-bar {
        border-radius: 3px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-value {
        background-color: #9d60fb;
    }
    progress::-moz-progress-bar {
        background-color: #9d60fb;
    }
</style>









<style>
    progress {
        -webkit-appearance: none;
        border: none;
        border-radius: 3px;
        width: 300px;
        height: 20px;
        vertical-align: middle;
        margin-right: 10px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-bar {
        border-radius: 3px;
        background-color: aliceblue;
    }
    progress::-webkit-progress-value {
        background-color: #9d60fb;
    }
    progress::-moz-progress-bar {
        background-color: #9d60fb;
    }
</style>







    deepchecks - WARNING - Could not find built-in feature importance on the model, using permutation feature importance calculation instead
    WARNING:deepchecks:Could not find built-in feature importance on the model, using permutation feature importance calculation instead
    deepchecks - INFO - Calculating permutation feature importance. Expected to finish in 7 seconds
    INFO:deepchecks:Calculating permutation feature importance. Expected to finish in 7 seconds
    


    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Output()



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">✓ Analysis complete!</span>
</pre>




```python
# Résultats
result.to_text(False)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">│                                               DEEPFIX ANALYSIS RESULT                                                │</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000">╭────────────────────────────────────────────────────── </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">Summary</span><span style="color: #008000; text-decoration-color: #008000"> ───────────────────────────────────────────────────────╮</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">L'analyse croisée des artefacts révèle un modèle aux performances exceptionnelles (AUC 0.99-1.0) mais avec des </span>      <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">opportunités significatives d'amélioration. La qualité des données est excellente avec une dérive minimale, mais des</span> <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">redondances de caractéristiques et une sous-utilisation de caractéristiques à variance élevée sont identifiées. Le </span>  <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">principal défi réside dans le manque critique d'informations contextuelles et de documentation, couplé à des </span>        <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">configurations de régularisation potentiellement sous-optimales. Des actions correctives sur la documentation, la </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">configuration du modèle et l'optimisation des caractéristiques sont recommandées pour garantir la robustesse à long </span> <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">terme et la facilité d'utilisation du modèle.</span>                                                                        <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                      Summary Statistics                                      </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Metric                          Value                                                        </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Total Findings                 </span><span style="color: #000000; text-decoration-color: #000000"> 4                                                            </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Severity Distribution          </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold">MEDIUM: 3  </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">HIGH: 1  </span><span style="color: #000000; text-decoration-color: #000000">                                         </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                  HIGH Severity Issues (1)                                   </span>
<span style="color: #800000; text-decoration-color: #800000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> #   </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Finding                                  </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Action                                   </span><span style="color: #800000; text-decoration-color: #800000">┃</span>
<span style="color: #800000; text-decoration-color: #800000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Manque critique d'informations           </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Documenter complètement les métadonnées  </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> contextuelles et de configuration de     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> du modèle et réviser les paramètres de   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> régularisation dans le modèle            </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> régularisation et de feuilles            </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Absence d'informations sur la </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">L'absence d'informations contextuelles </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">taille du jeu de données, métriques de </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">empêche l'évaluation de l'adéquation du </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">performance, et régularisation L2=0.0 </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">modèle, et le manque de régularisation </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">avec min_samples_leaf=20 potentiellement</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">pourrait causer du surapprentissage à </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">restrictif</span><span style="color: #000000; text-decoration-color: #000000">                               </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">long terme</span><span style="color: #000000; text-decoration-color: #000000">                               </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                 MEDIUM Severity Issues (3)                                  </span>
<span style="color: #808000; text-decoration-color: #808000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> #   </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Finding                                  </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Action                                   </span><span style="color: #808000; text-decoration-color: #808000">┃</span>
<span style="color: #808000; text-decoration-color: #808000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Échec de l'analyse des artefacts de jeu  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Corriger l'implémentation de l'analyseur </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> de données dû à une erreur technique     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> DatasetArtifactsAnalyzer et réexécuter   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Erreur AttributeError: </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> l'analyse                                </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">'DatasetArtifacts' object has no </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">L'absence d'analyse des métadonnées du </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">attribute 'statistics' lors de la </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">jeu de données limite la compréhension </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">construction du prompt</span><span style="color: #000000; text-decoration-color: #000000">                   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">complète du contexte des données</span><span style="color: #000000; text-decoration-color: #000000">         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 2   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Redondance des caractéristiques avec     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Appliquer une réduction de               </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> corrélations élevées et caractéristiques </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> dimensionnalité (PCA) et réviser         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> sous-utilisées malgré une qualité de     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> l'importance des caractéristiques tout   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> données exceptionnelle                   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> en maintenant les pratiques de           </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: 27 paires de caractéristiques </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> validation actuelles                     </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">avec corrélation &gt;0.9, 16 </span><span style="color: #000000; text-decoration-color: #000000">               </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">L'élimination de la redondance et une </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">caractéristiques à variance élevée non </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">meilleure utilisation des </span><span style="color: #000000; text-decoration-color: #000000">               </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">utilisées, AUC 0.99-1.0, dérive minimale</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">caractéristiques à variance élevée </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(0.15 multivariée, 0.12 prédiction)</span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">pourraient améliorer encore les </span><span style="color: #000000; text-decoration-color: #000000">         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">performances malgré les excellents </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">résultats actuels</span><span style="color: #000000; text-decoration-color: #000000">                        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 3   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Configuration ambiguë des                </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Documenter le traitement des             </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> caractéristiques catégorielles et        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> caractéristiques catégorielles et        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> résultats d'arrêt anticipé manquants     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> inclure les résultats de l'arrêt         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: </span><span style="color: #000000; text-decoration-color: #000000">                               </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> anticipé                                 </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">categorical_features='from_dtype' sans </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">La clarté sur le prétraitement et la </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">documentation, early_stopping='auto' </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">convergence du modèle est essentielle </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">sans résultats de validation</span><span style="color: #000000; text-decoration-color: #000000">             </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">pour une utilisation et un déploiement </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">corrects</span><span style="color: #000000; text-decoration-color: #000000">                                 </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>






    ''



# A votre tour



1.   Chargez vos données
2.   Evaluer la qualité de votre préparation des données
3.   Evaluer la performance de votre modèle




```python

```
