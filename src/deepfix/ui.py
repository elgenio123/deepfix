from __future__ import annotations

import json
from typing import Optional

import streamlit as st
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import ArtifactConfig, MLflowConfig


@st.cache_resource(show_spinner=False)
def get_client(api_url: str = "https://deepfix.delcaux.com", mlflow_config: Optional[MLflowConfig] = None, artifact_config: Optional[ArtifactConfig] = None, timeout: int = 30) -> DeepFixClient:
    """Create a cached DeepFix client for reuse across interactions."""
    return DeepFixClient(api_url=api_url, mlflow_config=mlflow_config, artifact_config=artifact_config, timeout=timeout)


def render_dataset_overview(datasets: list[dict[str, str]]) -> None:
    """Render a simple table describing the available datasets."""
    if not datasets:
        st.warning(
            "No datasets have been ingested yet. Run `DeepFixClient.ingest` first."
        )
        return

    st.dataframe(
        datasets,
        column_config={
            "dataset_name": "Dataset",
            "status": "Status",
            "updated_at": "Updated",
            "local_path": "Cached Path",
        },
        hide_index=True,
        use_container_width=True,
    )


def run_diagnosis_ui() -> None:
    st.set_page_config(page_title="DeepFix Diagnosis", layout="wide")
    st.title("DeepFix Diagnosis")
    st.caption("Visual wrapper around `DeepFixClient.diagnose`.")

    client = get_client()
    datasets = client.list_datasets()
    render_dataset_overview(datasets)

    dataset_names = [item["dataset_name"] for item in datasets]

    with st.sidebar:
        st.header("Diagnosis Settings")
        dataset_name: Optional[str] = None
        if dataset_names:
            dataset_name = st.selectbox(
                "Dataset", options=dataset_names, placeholder="Select a dataset"
            )
        else:
            st.info("Ingest a dataset to enable diagnosis.")

        language = st.selectbox(
            "Language",
            options=["english", "spanish", "french", "german", "japanese"],
            index=0,
        )

        verbose = st.toggle("Verbose Findings", value=False)
        show_raw = st.toggle("Show Raw Response", value=False)

        run_clicked = st.button(
            "Run Diagnosis",
            type="primary",
            disabled=dataset_name is None,
            use_container_width=True,
        )

    if not run_clicked or dataset_name is None:
        return

    result_placeholder = st.empty()
    with result_placeholder, st.spinner("Running DeepFix analysis..."):
        try:
            response = client.diagnose(dataset_name=dataset_name, language=language)
        except Exception as exc:
            st.error(f"Diagnosis failed: {exc}")
            return

    st.success(f"Diagnosis complete for `{dataset_name}`.")
    if response.summary:
        st.subheader("Summary")
        st.write(response.summary)

    try:
        df = response.get_results_as_dataframe()
        st.subheader("Findings")
        st.dataframe(df, use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not convert findings to dataframe: {exc}")

    text_report = None
    try:
        text_report = response.to_text(verbose=verbose)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Unable to render formatted text report: {exc}")

    if text_report:
        st.subheader("Formatted Report")
        st.code(text_report)

    if show_raw:
        st.subheader("Raw Response JSON")
        st.code(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    run_diagnosis_ui()

