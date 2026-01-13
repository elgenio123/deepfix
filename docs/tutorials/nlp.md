```python
import os
from deepfix_sdk import DeepFixClient
```


```python
os.environ["DEEPFIX_API_KEY"] = ... # get your API key at https://deepfix.delcaux.com
```


```python
client = DeepFixClient(api_url="https://deepfix.delcaux.com", timeout=120)
```

## Sentence classification


```python
from deepfix_sdk.data.datasets import NLPDataset
from deepfix_sdk.zoo.datasets import load_tweet_emotion_classification
```


```python
train_data, test_data = load_tweet_emotion_classification(
    as_train_test=True, include_embeddings=True
)
dataset_name = "tweet_emotion_classification"
train_data = NLPDataset(dataset_name=dataset_name, dataset=train_data)
val_data = NLPDataset(dataset_name=dataset_name, dataset=test_data)
```


```python
result = client.get_diagnosis(
    train_data=train_data,
    test_data=val_data,
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







    deepchecks - WARNING - Could not find model's classes, using the observed classes. In order to make sure the classes used by the model are inferred correctly, please use the model_classes argument
    UserWarning: n_jobs value 1 overridden to 1 by setting random_state. Use no seed for parallelism.
    UserWarning: n_jobs value 1 overridden to 1 by setting random_state. Use no seed for parallelism.




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







    FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.
    FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.



```python
# Visualize results
result.to_text()
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">│                                               DEEPFIX ANALYSIS RESULT                                                │</span>
<span style="color: #000080; text-decoration-color: #000080; font-weight: bold">╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #008000; text-decoration-color: #008000">╭────────────────────────────────────────────────────── </span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold">Summary</span><span style="color: #008000; text-decoration-color: #008000"> ───────────────────────────────────────────────────────╮</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">The cross-artifact analysis was partially successful. The DatasetArtifactsAnalyzer encountered a technical error and</span> <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">could not provide results. However, the DeepchecksArtifactsAnalyzer identified critical data quality issues. The </span>    <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">most severe finding is a high-confidence label distribution drift between train and test sets, which poses a </span>        <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">significant risk to model validity. Additional concerns include a high ratio of outliers in text toxicity and the </span>   <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">presence of unknown tokens, both rated as medium severity. A low-severity text embeddings drift was also noted. </span>     <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">Recommendations focus on data preprocessing, tokenizer updates, and careful performance monitoring to ensure model </span>  <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">robustness. The failure of one analyzer highlights a potential need to review the artifact analysis pipeline for </span>    <span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span> <span style="color: #000000; text-decoration-color: #000000">stability.</span>                                                                                                           <span style="color: #008000; text-decoration-color: #008000">│</span>
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
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Significant label distribution drift     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> Re-examine the train-test split          </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> between train and test sets              </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> methodology to ensure proper             </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Label drift check failed with </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> stratification                           </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Cramer's V score of 0.22, exceeding the </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Label distribution mismatch can lead to </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">0.15 threshold, indicating substantial </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">unreliable performance metrics and model</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">distribution shift in emotion labels</span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #800000; text-decoration-color: #800000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">overfitting to train-specific patterns</span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #800000; text-decoration-color: #800000">│</span>
<span style="color: #800000; text-decoration-color: #800000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                 MEDIUM Severity Issues (2)                                  </span>
<span style="color: #808000; text-decoration-color: #808000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> #   </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Finding                                  </span><span style="color: #808000; text-decoration-color: #808000">┃</span><span style="color: #808000; text-decoration-color: #808000; font-weight: bold"> Action                                   </span><span style="color: #808000; text-decoration-color: #808000">┃</span>
<span style="color: #808000; text-decoration-color: #808000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> High outlier ratio in text properties,   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Investigate and clean outliers in the    </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> particularly Toxicity                    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Toxicity property, or implement robust   </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Text property outliers check </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> preprocessing                            </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">failed with Toxicity property showing </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">High outlier ratios can distort feature </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">16.43% outlier ratio, significantly </span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">relationships and model training, </span><span style="color: #000000; text-decoration-color: #000000">       </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">above the 5% threshold</span><span style="color: #000000; text-decoration-color: #000000">                   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">potentially leading to poor </span><span style="color: #000000; text-decoration-color: #000000">             </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">generalization</span><span style="color: #000000; text-decoration-color: #000000">                           </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 2   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Presence of unknown tokens indicating    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> Update tokenizer vocabulary or           </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> tokenizer coverage gaps                  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> preprocess text to handle unknown tokens </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Unknown tokens check failed </span><span style="color: #000000; text-decoration-color: #000000">   </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> appropriately                            </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">with ratios of 0.79% and 0.68%, </span><span style="color: #000000; text-decoration-color: #000000">         </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Unknown tokens can degrade model </span><span style="color: #000000; text-decoration-color: #000000">        </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">indicating unsupported tokens in the </span><span style="color: #000000; text-decoration-color: #000000">    </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">performance and introduce noise in text </span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">dataset</span><span style="color: #000000; text-decoration-color: #000000">                                  </span><span style="color: #808000; text-decoration-color: #808000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">representations</span><span style="color: #000000; text-decoration-color: #000000">                          </span><span style="color: #808000; text-decoration-color: #808000">│</span>
<span style="color: #808000; text-decoration-color: #808000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                   LOW Severity Issues (1)                                   </span>
<span style="color: #008000; text-decoration-color: #008000">┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</span>
<span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> #   </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Finding                                  </span><span style="color: #008000; text-decoration-color: #008000">┃</span><span style="color: #008000; text-decoration-color: #008000; font-weight: bold"> Action                                   </span><span style="color: #008000; text-decoration-color: #008000">┃</span>
<span style="color: #008000; text-decoration-color: #008000">┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f"> 1   </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Moderate text embeddings drift           </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> Monitor model performance closely and    </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> suggesting domain shift                  </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> consider domain adaptation techniques if </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Evidence: Text embeddings drift showed </span><span style="color: #000000; text-decoration-color: #000000">  </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> performance degrades                     </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">AUC of 0.6, indicating some domain shift</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">Domain shift can affect model </span><span style="color: #000000; text-decoration-color: #000000">           </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">between train and test distributions</span><span style="color: #000000; text-decoration-color: #000000">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">generalization, though the current level</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">     </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000">                                          </span><span style="color: #008000; text-decoration-color: #008000">│</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #7f7f7f; text-decoration-color: #7f7f7f; font-style: italic">may be acceptable for deployment</span><span style="color: #000000; text-decoration-color: #000000">         </span><span style="color: #008000; text-decoration-color: #008000">│</span>
<span style="color: #008000; text-decoration-color: #008000">└─────┴──────────────────────────────────────────┴──────────────────────────────────────────┘</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
</pre>






    ''
