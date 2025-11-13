from typing import Optional, List, Union
from .base import Step
from ..utils.logging import get_logger
from deepfix_core.models import (
    ArtifactPath,
    DatasetArtifacts,
    DeepchecksArtifacts,
    Artifacts,
    TrainingArtifacts,
    ModelCheckpointArtifacts,
)
from ..integrations import MLflowManager
from ..artifacts import ArtifactsManager


class LoadArtifact(Step):
    def __init__(
        self,
        artifact_key: ArtifactPath,
        mlflow_manager: MLflowManager,
        artifact_sqlite_path: str,
        run_id: Optional[str] = None,
    ):
        self.mlflow_manager = mlflow_manager
        self.artifact_key = artifact_key
        self.artifact_mgr = ArtifactsManager(
            sqlite_path=artifact_sqlite_path, mlflow_manager=self.mlflow_manager
        )
        self.run_id = run_id or self.mlflow_manager.run_id
        self.logger = get_logger(self.__class__.__name__)

    def run(self,context: dict, **kwargs) -> Artifacts:
        if self.run_id is None:
            raise ValueError(
                f"run_id must be set in MLflowManager for artifact: {self.artifact_key}"
            )
        self.logger.info(
            f"Loading artifact: {self.artifact_key} for run_id: {self.run_id}"
        )
        artifact = self.artifact_mgr.load_artifact(
            run_id=self.run_id, artifact_key=self.artifact_key, download_if_missing=True
        )
        context[self.artifact_key.value] = artifact
        return artifact

    def get_name(self) -> str:
        return self.artifact_key.value


class LoadTrainingArtifact(LoadArtifact):
    def __init__(self, mlflow_manager: MLflowManager, artifact_sqlite_path: str, run_name: str):
        super().__init__(
            artifact_key=ArtifactPath.TRAINING,
            mlflow_manager=mlflow_manager,
            artifact_sqlite_path=artifact_sqlite_path,
            run_id=run_name,
        )

    def run(self,context: dict, **kwargs) -> TrainingArtifacts:
        return super().run(context=context)


class LoadDeepchecksArtifacts(LoadArtifact):
    def __init__(self, mlflow_manager: MLflowManager, artifact_sqlite_path: str, run_name: str):
        super().__init__(
            artifact_key=ArtifactPath.DEEPCHECKS,
            mlflow_manager=mlflow_manager,
            artifact_sqlite_path=artifact_sqlite_path,
            run_id=run_name,
        )

    def run(self,context: dict, **kwargs) -> DeepchecksArtifacts:
        return super().run(context=context)


class LoadModelCheckpoint(LoadArtifact):
    def __init__(self, mlflow_manager: MLflowManager, artifact_sqlite_path: str, run_name: str):
        super().__init__(
            artifact_key=ArtifactPath.MODEL_CHECKPOINT,
            mlflow_manager=mlflow_manager,
            artifact_sqlite_path=artifact_sqlite_path,
            run_id=run_name,
        )

    def run(self,context: dict, **kwargs) -> ModelCheckpointArtifacts:
        return super().run(context=context)


class LoadDatasetArtifact(LoadArtifact):
    def __init__(
        self,
        run_name: str,
        mlflow_manager: MLflowManager,
        artifact_sqlite_path: str,
    ):
        super().__init__(
            artifact_key=ArtifactPath.DATASET,
            mlflow_manager=mlflow_manager,
            artifact_sqlite_path=artifact_sqlite_path,
            run_id=run_name,
        )

    def run(self,context: dict, **kwargs) -> DatasetArtifacts:
        return super().run(context=context)
