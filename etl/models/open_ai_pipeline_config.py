from dagster import Config, EnvVar

from etl.models.open_ai_settings import OpenAiSettings
from etl.models.types import EnrichmentType, RecordType


class OpenAiPipelineConfig(Config):  # type: ignore
    """A Config subclass that holds the shared parameters of OpenAI Pipelines."""

    openai_settings: OpenAiSettings
    record_type: RecordType
    enrichment_type: EnrichmentType


# openai_pipeline_config = OpenAiPipelineConfig(
#     openai_settings=OpenAiSettings(
#         openai_api_key=EnvVar("OPENAI_API_KEY").get_value("")
#     ),
#     record_type=EnvVar("RECORD_TYPE").get_value(default=RecordType.WIKIPEDIA),
#     enrichment_type=EnvVar("ENRICHMENT_TYPE").get_value(default=EnrichmentType.SUMMARY),
# )
