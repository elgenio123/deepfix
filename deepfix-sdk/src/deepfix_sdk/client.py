from typing import Optional, Union, Any, Optional
import os
import requests
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

from deepfix_core.models import APIRequest, APIResponse, ArtifactPath, DataType

from .pipelines import ArtifactLoadingPipeline, IngestionPipeline
from .config import MLflowConfig, ArtifactConfig
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
        self.artifacts_loader: Optional[ArtifactLoadingPipeline] = None
        self.timeout = timeout

        self._analyze_endpoint = f"{self.api_url}/v1/analyse"

    def diagnose_dataset(self, dataset_name: str, language: str = "english") -> APIResponse:
        """Analyze a dataset and return diagnostic results with recommendations.

        This method performs a comprehensive analysis of the specified dataset to identify
        potential issues, quality problems, and provides AI-powered recommendations for
        improvement.

        Args:
            dataset_name (str): Name of the dataset to analyze. Must match a dataset
                that has been previously ingested.
            language (str, optional): Language for analysis output. Defaults to "english".

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
            >>> response = client.diagnose_dataset(dataset_name="my-dataset")
            >>> print(response.to_text())
        """
        artifact_config = ArtifactConfig(
            load_dataset_metadata=True,
            load_checks=False,
            load_model_checkpoint=False,
            load_training=False,
        )
        self.artifacts_loader = ArtifactLoadingPipeline(
            mlflow_config=self.mlflow_config,
            artifact_config=artifact_config,
            dataset_name=dataset_name,
        )
        request = self._create_dataset_request(dataset_name=dataset_name, language=language)
        response = self._send_request(request)
        return response

    def ingest(
        self,
        dataset_name: str,
        data_type: Union[str, DataType],
        train_data: BaseDataset,
        test_data: Optional[BaseDataset] = None,
        model: Any = None,
        model_name:Optional[str]=None,
        batch_size: int = 8,
        overwrite: bool = False,
    ) -> None:
        """Ingest a dataset with optional quality validation.

        This method uploads a dataset to the DeepFix server and optionally performs
        validation checks on the data. Supports multiple data types including images,
        tabular data, NLP text, and general vision datasets.

        Args:
            dataset_name (str): Unique name for the dataset.
            data_type (str | DataType): Type of data to ingest. Valid values:
                - "image": Image classification datasets
                - "tabular": Structured tabular/DataFrame data
                - "nlp": Natural language processing datasets
                - "vision": General vision/computer vision datasets
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
            ...     dataset_name="my-dataset",
            ...     data_type="tabular",
            ...     train_data=train_dataset,
            ...     batch_size=16
            ... )
        """
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
            train_data=train_data,
            test_data=test_data,
            model=model
        )

    def _create_dataset_request(self, dataset_name: str, language: str = "english"):
        """Create an API request for dataset analysis.

        Internal method that loads dataset artifacts and constructs an APIRequest
        object for sending to the DeepFix server.

        Args:
            dataset_name (str): Name of the dataset to create request for.
            language (str, optional): Language for analysis. Defaults to "english".

        Returns:
            APIRequest: Request object configured with dataset artifacts and language.

        Raises:
            ValueError: If dataset artifacts are not found or have unexpected format.
        """
        output = self.artifacts_loader.run()
        cfg = {"dataset_name": dataset_name, "language": language}
        value = output.get(ArtifactPath.DATASET.value)
        if value is None:
            raise ValueError(f"Dataset artifacts not found for dataset {dataset_name}")
        if not isinstance(value, dict):
            raise ValueError(f"Expected a dictionary, got {type(value)}")
        cfg["dataset_artifacts"] = value.get(ArtifactPath.DATASET.value)
        cfg["deepchecks_artifacts"] = value.get(ArtifactPath.DEEPCHECKS.value)
        return APIRequest(**cfg)

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
                self._analyze_endpoint, json=payload, timeout=self.timeout, headers=headers
            )

            if response.status_code != 200:
                console.print("[red]✗[/red] Analysis failed", style="bold red")
                raise Exception(
                    f"Error during analysis: status code: {response.status_code} \nand message: {response.text}"
                )

        console.print("[green]✓[/green] Analysis complete!", style="bold green")
        return APIResponse(**response.json())
