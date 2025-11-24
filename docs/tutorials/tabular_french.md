# Evaluer la qualité de votre préparation de données et de votre Modèle

---



## Installer DeepFix

Accéder à la documentation de DeepFix: [link text](https://delcaux-labs.github.io/deepfix/)


```python
!curl -LsSf https://astral.sh/uv/install.sh | sh
```


```python
!uv pip install git+https://github.com/delcaux-labs/deepfix.git
```

## **Re-démarrer votre session Colab avant de continuer!**
``Runtime > 'Restart session'``
Ceci est dû à un problème de conflit entre différentes version de *numpy*

### Charger les donnees


```python
from deepfix_sdk import DeepFixClient
import os
```


```python
os.environ["DEEPFIX_API_KEY"] = "sk-empty"
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
# train_data.data.head()
```

### Evaluer la qualité de votre préparation de données


```python
# Ingestion des données
result = client.get_diagnosis(
    train_data=train_data,
    test_data=val_data,
    language="french",
)
```


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
