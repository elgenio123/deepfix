from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional, Union

import requests
from deepfix_core.models import APIRequest, APIResponse, ArtifactPath, DataType
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

from .config import ArtifactConfig, MLflowConfig

if TYPE_CHECKING:
    from .data.datasets import BaseDataset


console = Console()


class DeepFixClient:
    """Main client for interacting with the DeepFix server.

    This client provides a high-level interface for diagnosing ML datasets,
    ingesting data with quality checks, and leveraging AI-powered recommendations
    to improve your ML workflows.

    Attributes:
        mlflow_config (MLflowConfig): Configuration for MLflow integration.
        api_url (str): Base URL of the DeepFix server.
        timeout (int): Request timeout in seconds.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8844",
        mlflow_config: Optional[MLflowConfig] = None,
        timeout: int = 30,
    ):
        """Initialize the DeepFixClient.

        Args:
            api_url (str, optional): URL of the DeepFix server. Defaults to "http://localhost:8844".
            mlflow_config (MLflowConfig, optional): MLflow configuration for experiment tracking.
                If not provided, a default MLflowConfig is created. Defaults to None.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.

        Example:
            >>> client = DeepFixClient(
            ...     api_url="http://localhost:8844",
            ...     timeout=120
            ... )
        """
        self.mlflow_config = mlflow_config or MLflowConfig()
        self.api_url = api_url
        self.timeout = timeout

        self._analyze_endpoint = f"{self.api_url}/v1/analyse"

    def get_diagnosis(
        self,
        train_data: BaseDataset,
        test_data: Optional[BaseDataset] = None,
        model: Any = None,
        model_name: Optional[str] = None,
        batch_size: int = 8,
        language: str = "english",
    ) -> APIResponse:
        """Ingest and diagnose a model in a single operation.

        This convenience method combines ingestion and diagnosis into a single call.
        It first ingests the dataset and model (if provided), then immediately runs
        diagnosis on them to get analysis results and recommendations.

        Args:
            train_data (BaseDataset): Training dataset to ingest. Must be an instance
                of an appropriate dataset class (e.g., ImageClassificationDataset,
                TabularDataset, NLPDataset).
            test_data (BaseDataset, optional): Test/validation dataset. If provided,
                enables cross-dataset validation checks. Defaults to None.
            model (Any, optional): Model to ingest. Must be an instance of a model class.
                Defaults to None.
            model_name (str, optional): Name of the model. Defaults to None.
            batch_size (int, optional): Batch size for processing the dataset.
                Defaults to 8.
            language (str, optional): Language for analysis output. Defaults to "english".

        Returns:
            APIResponse: Response object containing:
                - Analysis results and findings
                - Actionable recommendations

        Raises:
            ValueError: If dataset with the same name exists and overwrite=False, or
                if dataset artifacts cannot be found after ingestion.
            Exception: If ingestion fails, or if the analysis request fails (non-200 status code).

        Example:
            >>> from deepfix_sdk.data import TabularDataset
            >>> import pandas as pd
            >>> df = pd.read_csv("train.csv")
            >>> label = "target"
            >>> cat_features = ["cat_feature1", "cat_feature2"]
            >>> dataset_name = "my-dataset"
            >>> train_dataset = TabularDataset(dataset=df, dataset_name=dataset_name, label=label, cat_features=cat_features)
            >>> response = client.get_diagnosis(
            ...     model_name="my-model",
            ...     train_data=train_dataset,
            ...     batch_size=16
            ... )
            >>> print(response.to_text())
        """
        assert isinstance(train_data, BaseDataset), "train_data must be an instance of BaseDataset"
        assert test_data is None or isinstance(test_data, BaseDataset), "test_data must be an instance of BaseDataset"

        dataset_name = self.get_dataset_name(train_data, test_data)

        # First, ingest the dataset and model
        self.ingest(
            train_data=train_data,
            test_data=test_data,
            model=model,
            model_name=model_name,
            batch_size=batch_size,
            overwrite=True,
        )
        # Then, diagnose the ingested dataset/model
        return self.diagnose(
            dataset_name=dataset_name,
            model_name=model_name,
            language=language,
        )

    def diagnose(
        self,
        dataset_name: str,
        language: str = "english",
        model_name: Optional[str] = None,
    ) -> APIResponse:
        """Analyze a run and return diagnostic results with recommendations.

        This method performs a comprehensive analysis of the specified run to identify
        potential issues, quality problems, and provides AI-powered recommendations for
        improvement.

        Args:
            run_name (str): Name of the run to analyze. Must match a run
                that has been previously ingested.
            language (str, optional): Language for analysis output. Defaults to "english".
            dataset_name (str, optional): Name of the dataset. Defaults to None.
        Returns:
            APIResponse: Response object containing:
                - Analysis results and findings
                - Quality metrics
                - Actionable recommendations
                - Dataset statistics

        Raises:
            ValueError: If dataset artifacts cannot be found for the specified dataset.
            Exception: If the analysis request fails (non-200 status code).

        Example:
            >>> response = client.diagnose(run_name="my-run")
            >>> print(response.to_text())
        """
        from .pipelines import ArtifactLoadingPipeline

        artifact_config = ArtifactConfig(
            load_dataset_metadata=True,
            load_checks=True,
            load_model_checkpoint=True,
            load_training=False,
        )
        loaded_artifacts = ArtifactLoadingPipeline(
            mlflow_config=self.mlflow_config,
            artifact_config=artifact_config,
            dataset_name=dataset_name,
            model_name=model_name,
        ).run()
        request = self._create_request(
            dataset_name=dataset_name,
            model_name=model_name,
            language=language,
            loaded_artifacts=loaded_artifacts,
        )
        response = self._send_request(request)
        return response

    def ingest(
        self,
        train_data: BaseDataset,
        test_data: Optional[BaseDataset] = None,
        model: Any = None,
        model_name: Optional[str] = None,
        batch_size: int = 8,
        overwrite: bool = False,
    ) -> None:
        """Ingest a dataset with optional quality validation.

        This method uploads a dataset to the DeepFix server and optionally performs
        validation checks on the data. Supports multiple data types including images,
        tabular data, NLP text, and general vision datasets.

        Args:
            dataset_name (str): Unique name for the dataset.
            train_data (BaseDataset): Training dataset to ingest. Must be an instance
                of an appropriate dataset class (e.g., ImageClassificationDataset,
                TabularDataset, NLPDataset).
            test_data (BaseDataset, optional): Test/validation dataset. If provided,
                enables cross-dataset validation checks. Defaults to None.
            model (Any, optional): Model to ingest. Must be an instance of a model class.
                Defaults to None.
            model_name (str, optional): Name of the model. Defaults to None.
            batch_size (int, optional): Batch size for processing the dataset.
                Defaults to 8.
            overwrite (bool, optional): If True, overwrite existing dataset with the
                same name. If False, raise an error if dataset exists. Defaults to False.

        Raises:
            ValueError: If dataset with the same name exists and overwrite=False.
            Exception: If data validation fails or ingestion fails.

        Example:
            >>> from deepfix_sdk.data.datasets import TabularDataset
            >>> import pandas as pd
            >>> df = pd.read_csv("train.csv")
            >>> train_dataset = TabularDataset(
            ...     dataset_name="my-dataset",
            ...     data=df
            ... )
            >>> client.ingest(
            ...     train_data=train_dataset,
            ...     batch_size=16
            ... )
        """
        from .pipelines import IngestionPipeline

        data_type = self._get_data_type(train_data, test_data)
        dataset_name = self.get_dataset_name(train_data, test_data)

        dataset_logging_pipeline = IngestionPipeline(
            dataset_name=dataset_name,
            data_type=data_type,
            train_test_validation=test_data is not None,
            data_integrity=True,
            model_evaluation=model is not None,
            batch_size=batch_size,
            overwrite=overwrite,
            model_name=model_name,
        )
        dataset_logging_pipeline.run(
            train_data=train_data, test_data=test_data, model=model
        )

    def _create_request(
        self,
        dataset_name: str,
        model_name: str,
        language: str = "english",
        loaded_artifacts: dict = None,
    ):
        """Create an API request for analysis.

        Internal method that loads dataset artifacts and constructs an APIRequest
        object for sending to the DeepFix server.

        Args:
            dataset_name (str): Name of the dataset.
            model_name (str): Name of the model.
            language (str, optional): Language for analysis. Defaults to "english".
            loaded_artifacts (dict): Loaded artifacts from the server.
        Returns:
            APIRequest: Request object configured with dataset artifacts and language.

        Raises:
            ValueError: If dataset artifacts are not found or have unexpected format.
        """
        cfg = {
            "dataset_name": dataset_name,
            "language": language,
            "model_name": model_name,
        }
        request = APIRequest(**cfg)
        request.dataset_artifacts = loaded_artifacts.get(
            ArtifactPath.DATASET.value, None
        )
        request.deepchecks_artifacts = loaded_artifacts.get(
            ArtifactPath.DEEPCHECKS.value, None
        )
        request.model_checkpoint_artifacts = loaded_artifacts.get(
            ArtifactPath.MODEL_CHECKPOINT.value, None
        )
        return request

    def _send_request(self, request: APIRequest) -> APIResponse:
        """Send an analysis request to the DeepFix server.

        Internal method that sends the API request to the server and handles the response.
        Displays a progress spinner during the request and returns the parsed response.

        Args:
            request (APIRequest): The API request object to send to the server.

        Returns:
            APIResponse: Parsed response object from the server containing analysis results.

        Raises:
            Exception: If the server returns a non-200 status code or if the request times out.

        Note:
            Requires the DEEPFIX_API_KEY environment variable to be set for authentication.
        """
        with Live(
            Spinner("dots", text="[cyan]Running analysis...[/cyan]", style="cyan"),
            console=console,
            refresh_per_second=10,
        ):
            payload = request.model_dump()
            headers = {"X-API-Key": os.getenv("DEEPFIX_API_KEY")}
            response = requests.post(
                self._analyze_endpoint,
                json=payload,
                timeout=self.timeout,
                headers=headers,
            )

            if response.status_code != 200:
                console.print("[red]✗[/red] Analysis failed", style="bold red")
                raise Exception(
                    f"Error during analysis: status code: {response.status_code} \nand message: {response.text}"
                )

        console.print("[green]✓[/green] Analysis complete!", style="bold green")
        return APIResponse(**response.json())

    def _get_data_type(self, train_data: BaseDataset, test_data: Optional[BaseDataset] = None) -> DataType:
        data_type = train_data.data_type
        if test_data is not None:
            test_data_type = test_data.data_type
            if test_data_type != data_type:
                raise ValueError(f"Test data type {test_data_type} does not match train data type {data_type}")
        return data_type

    def get_dataset_name(self, train_data: BaseDataset, test_data: Optional[BaseDataset] = None) -> str:
        dataset_name = train_data.name
        if test_data is not None:
            if test_data.name != dataset_name:
                dataset_name = f"{dataset_name}_vs_{test_data.name}"
        return dataset_name