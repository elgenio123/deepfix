```python
import os
from deepfix_sdk import DeepFixClient
```


```python
os.environ["DEEPFIX_API_KEY"] = "DEEPFIX-IS-AMAZING"
```


```python
client = DeepFixClient(api_url="https://deepfix.delcaux.com", timeout=120)
```

## Classification


```python
from deepfix_sdk.data.datasets import TabularDataset
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
```


```python
# Load data
X, y = load_breast_cancer(as_frame=True, return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
dataset_name = "breast_cancer_classification"

label = "target"
train = X_train.copy()
train[label] = y_train
cat_features = X_train.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()
if len(cat_features) > 0:
    cat_features = None

test = X_test.copy()
test[label] = y_test

train_data = TabularDataset(
    dataset=train, dataset_name=dataset_name, label=label, cat_features=cat_features
)
val_data = TabularDataset(
    dataset=test, dataset_name=dataset_name, label=label, cat_features=cat_features
)
```


```python
train_data.data.head()
```




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




```python
# Fit model
model_name = "HistGradientBoostingClassifier"
clf = HistGradientBoostingClassifier(max_depth=3)
clf = clf.fit(train_data.X, train_data.y)
```


```python
result = client.get_diagnosis(
    train_data=train_data,
    test_data=val_data,
    model_name=model_name,
    model=clf,
    language="english",
)
```


```python
# Visualize results
result.to_text(verbose=False)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">│                                               DEEPFIX ANALYSIS RESULT                                                │</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000">╭────────────────────────────────────────────────────── </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">Summary</span><span style="color: #008000; text-decoration-color: #008000"> ───────────────────────────────────────────────────────╮</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">The cross-artifact analysis reveals a critical gap between theoretical model performance and deployment readiness. </span>  <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">While the Deepchecks analysis shows excellent model performance (AUC ~1.0) with some feature optimization </span>           <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">opportunities (high redundancy, unused features), the ModelCheckpoint analysis exposes that the model cannot be </span>     <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">deployed due to missing trained model files and essential metadata. The highest priority is generating the actual </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">model artifact. Once available, feature optimization should be addressed to improve model stability and leverage </span>    <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">unused high-variance features. The excellent performance metrics are promising but meaningless without executable </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">model files.</span>                                                                                                         <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                      Summary Statistics                                      </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Metric                          Value                                                        </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Total Findings                 </span><span style="color: #000000; text-decoration-color: #000000"> 4                                                            </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Severity Distribution          </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold">MEDIUM: 2  </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">HIGH: 1  </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">LOW: 1  </span><span style="color: #000000; text-decoration-color: #000000">                                 </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                  HIGH Severity Issues (1)                                   </span>
<span style="color: #800000; text-decoration-color: #800000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> #   </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Finding                                  </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Action                                   </span><span style="color: #800000; text-decoration-color: #800000">┃</span>
<span style="color: #800000; text-decoration-color: #800000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Critical deployment blocker: Missing     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Generate and include the actual trained  </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> trained model file                       </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> model file (pickle, joblib, or ONNX      </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: ModelCheckpoint analyzer </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> format) with the configuration artifacts </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">confirms no actual model weights or </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">The model configuration alone is </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">serialized model object exists, only </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">insufficient for deployment or </span><span style="color: #000000; text-decoration-color: #000000">          </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">configuration parameters. Deepchecks </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">inference. The excellent performance </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">analysis shows excellent theoretical </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">metrics from Deepchecks are meaningless </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">performance (AUC ~1.0) but this cannot </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">without the executable model.</span><span style="color: #000000; text-decoration-color: #000000">            </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">be utilized without the model file.</span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                 MEDIUM Severity Issues (2)                                  </span>
<span style="color: #808000; text-decoration-color: #808000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> #   </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Finding                                  </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Action                                   </span><span style="color: #808000; text-decoration-color: #808000">┃</span>
<span style="color: #808000; text-decoration-color: #808000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Incomplete model metadata hinders        </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Include feature_names_in_, classes_, and </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> deployment                               </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> n_features_in_ attributes with the       </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Missing feature names, class </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> trained model, and review feature        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">labels, and feature count metadata in </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> selection strategy                       </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">ModelCheckpoint, while Deepchecks shows </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Proper metadata is essential for </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">16 high-variance features are unused and</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">deployment. The feature issues </span><span style="color: #000000; text-decoration-color: #000000">          </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">22 feature pairs have high correlation </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">(redundancy, unused features) from </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(&gt;0.9)</span><span style="color: #000000; text-decoration-color: #000000">                                   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Deepchecks analysis should inform which </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">features to include in the final </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">deployed model.</span><span style="color: #000000; text-decoration-color: #000000">                          </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 2   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Feature optimization opportunity despite </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Perform feature selection (PCA or        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> excellent performance                    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> representative feature selection) and    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Deepchecks shows high feature </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> investigate incorporating unused         </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">redundancy (22 correlated pairs &gt;0.9) </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> high-variance features                   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">and 16 unused high-variance features, </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Reducing multicollinearity can improve </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">while model maintains AUC ~1.0 with F1 </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">model stability and interpretability. </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">gain of 91.49%</span><span style="color: #000000; text-decoration-color: #000000">                           </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">The unused features may contain valuable</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">signal for robustness.</span><span style="color: #000000; text-decoration-color: #000000">                   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                   LOW Severity Issues (1)                                   </span>
<span style="color: #008000; text-decoration-color: #008000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> #   </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Finding                                  </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Action                                   </span><span style="color: #008000; text-decoration-color: #008000">┃</span>
<span style="color: #008000; text-decoration-color: #008000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Excellent model performance with         </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Monitor performance on new data and      </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> potential overfitting risk               </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> conduct feature importance analysis to   </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Deepchecks reports </span><span style="color: #000000; text-decoration-color: #000000">            </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> validate robustness                      </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">near-perfect performance (AUC ~1.0) but </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">While current performance is </span><span style="color: #000000; text-decoration-color: #000000">            </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">with heavy reliance on 3 features </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">exceptional, reliance on few features </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">showing very high predictive power (PPS </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">may make the model vulnerable to </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&gt; 0.7)</span><span style="color: #000000; text-decoration-color: #000000">                                   </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">distribution shifts in production.</span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>






    ''


