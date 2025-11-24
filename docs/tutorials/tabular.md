```python
import os
from deepfix_sdk import DeepFixClient
```

    d:\workspace\repos\deepfix\.venv\Lib\site-packages\deepchecks\core\serialization\dataframe\html.py:16: UserWarning:
    
    pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.
    
    


```python
os.environ["DEEPFIX_API_KEY"] = "sk-empty"
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

    No categorical features provided, will automatically detect them. (Not Recommended)
    No categorical features provided, will automatically detect them. (Not Recommended)
    


```python
#train_data.data.head()
```


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
    deepchecks - INFO - Calculating permutation feature importance. Expected to finish in 15 seconds
    


    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Downloading artifacts:   0%|          | 0/1 [00:00<?, ?it/s]



    Output()



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">✓ Analysis complete!</span>
</pre>




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
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">The cross-artifact analysis reveals a concerning disconnect between excellent current model performance (AUC &gt;0.99) </span> <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">and significant underlying data quality and configuration issues. The Deepchecks analysis identified severe </span>         <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">multicollinearity (27 feature pairs with correlation &gt;0.9) and potential data leakage (3 features with PPS &gt;0.7), </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">while the ModelCheckpoint analysis shows restrictive model parameters (max_depth=3) with no regularization and </span>      <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">critical missing deployment metadata. These issues are compounded by non-deterministic configuration and unused </span>     <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">high-variance features. Despite the current strong performance, the model appears to be leveraging redundant feature</span> <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">relationships in a potentially unsustainable way. Immediate actions should focus on feature selection to address </span>    <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">multicollinearity, model reconfiguration with proper regularization, and ensuring complete production metadata </span>      <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">before deployment.</span>                                                                                                   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                      Summary Statistics                                      </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Metric                          Value                                                        </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Total Findings                 </span><span style="color: #000000; text-decoration-color: #000000"> 4                                                            </span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold"> Severity Distribution          </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">HIGH: 2  </span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold">MEDIUM: 2  </span><span style="color: #000000; text-decoration-color: #000000">                                         </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                  HIGH Severity Issues (2)                                   </span>
<span style="color: #800000; text-decoration-color: #800000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> #   </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Finding                                  </span><span style="color: #800000; text-decoration-color: #800000">┃</span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold"> Action                                   </span><span style="color: #800000; text-decoration-color: #800000">┃</span>
<span style="color: #800000; text-decoration-color: #800000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Severe multicollinearity and potential   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Implement comprehensive feature          </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> data leakage in features                 </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> selection to remove redundant features   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: 27 feature pairs with </span><span style="color: #000000; text-decoration-color: #000000">         </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> and investigate high-PPS features for    </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">correlation &gt;0.9 identified by </span><span style="color: #000000; text-decoration-color: #000000">          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> data leakage                             </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Deepchecks, combined with 3 features </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">High correlation causes </span><span style="color: #000000; text-decoration-color: #000000">                 </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">exceeding 0.7 predictive power score </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">multicollinearity issues while high PPS </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">threshold, suggesting redundant features</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">scores may indicate improper data </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">and possible label information leakage</span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">separation or target information leakage</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">into features</span><span style="color: #000000; text-decoration-color: #000000">                            </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 2   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Critical production readiness gaps in    </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Include complete model metadata          </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> model deployment metadata                </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> (classes_, feature_names_in_, training   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Missing classes_, </span><span style="color: #000000; text-decoration-color: #000000">             </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> metrics) and set fixed random_state      </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">feature_names_in_, n_iter_, and training</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> before production deployment             </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">metrics from checkpoint, combined with </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Essential metadata is required for </span><span style="color: #000000; text-decoration-color: #000000">      </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">non-deterministic random_state=None </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">correct inference, model interpretation,</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">configuration</span><span style="color: #000000; text-decoration-color: #000000">                            </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">and reproducible results in production </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">environments</span><span style="color: #000000; text-decoration-color: #000000">                             </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                 MEDIUM Severity Issues (2)                                  </span>
<span style="color: #808000; text-decoration-color: #808000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> #   </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Finding                                  </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Action                                   </span><span style="color: #808000; text-decoration-color: #808000">┃</span>
<span style="color: #808000; text-decoration-color: #808000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Suboptimal model configuration with      </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Increase model capacity (max_depth=6-10) </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> restrictive parameters and missing       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> and add moderate regularization          </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> regularization                           </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> (L2=0.1-1.0) while implementing proper   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Model uses max_depth=3 with no</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> feature selection                        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">L2 regularization </span><span style="color: #000000; text-decoration-color: #000000">                       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">More flexible model architecture with </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(l2_regularization=0.0) while ignoring </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">proper regularization can better capture</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">16 high-variance features, creating </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">complex patterns while preventing </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">underfitting risk despite current </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">overfitting on the correlated feature </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">excellent performance</span><span style="color: #000000; text-decoration-color: #000000">                    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">set</span><span style="color: #000000; text-decoration-color: #000000">                                      </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 2   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Excellent current performance masks      </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Address fundamental data quality and     </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> underlying data quality and              </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> model configuration issues before        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> configuration issues                     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> relying on current performance metrics   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: AUC &gt;0.99 with minimal drift </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> for production decisions                 </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">despite high feature correlation, </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Current excellent performance may be </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">restrictive model parameters, and </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">unsustainable and mask underlying </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">missing regularization - suggesting the </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">problems that could cause failures when </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">model is leveraging redundant feature </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">data distributions shift or features </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">relationships</span><span style="color: #000000; text-decoration-color: #000000">                            </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">change</span><span style="color: #000000; text-decoration-color: #000000">                                   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>






    ''


