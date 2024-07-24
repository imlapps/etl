import json

from langchain.docstore.document import Document
from langchain.schema.runnable import RunnableSequence
from langchain_community.vectorstores import FAISS
from pytest_mock import MockFixture

from etl.assets import (
    documents_of_wikipedia_articles_with_summaries,
    wikipedia_anti_recommendations,
    wikipedia_anti_recommendations_json_file,
    wikipedia_articles_embedding_store,
    wikipedia_articles_from_storage,
    wikipedia_articles_with_summaries,
    wikipedia_articles_with_summaries_json_file,
)
from etl.models import (
    AntiRecommendationKeysByKeyTuple,
    DocumentTuple,
    RecordTuple,
    wikipedia,
)
from etl.models.types import ModelResponse, RecordKey
from etl.resources import (
    InputDataFilesConfig,
    OpenaiPipelineConfig,
    OpenaiSettings,
    OutputConfig,
)


def test_wikipedia_articles_from_storage(
    input_data_files_config: InputDataFilesConfig,
) -> None:
    """Test that wikipedia_articles_from_storage successfully materializes a tuple of Wikipedia articles."""

    assert isinstance(
        wikipedia_articles_from_storage(input_data_files_config).records[0], wikipedia.Article  # type: ignore[attr-defined]
    )


def test_wikipedia_articles_with_summaries(
    session_mocker: MockFixture,
    openai_pipeline_config: OpenaiPipelineConfig,
    tuple_of_articles_with_summaries: tuple[wikipedia.Article, ...],
    article_with_summary: wikipedia.Article,
    openai_model_response: ModelResponse,
) -> None:
    """Test that wikipedia_articles_with_summaries succesfully materializes a tuple of Wikipedia articles with summaries."""

    # Mock RunnableSequence.invoke and return a ModelResponse
    session_mocker.patch.object(
        RunnableSequence, "invoke", return_value=openai_model_response
    )

    assert (
        wikipedia_articles_with_summaries(  # type: ignore[attr-defined]
            RecordTuple(records=tuple_of_articles_with_summaries),
            openai_pipeline_config,
        )
        .records[0]
        .model_dump(by_alias=True)["summary"]
        == article_with_summary.summary
    )


def test_wikipedia_articles_with_summaries_json_file(
    tuple_of_articles_with_summaries: tuple[wikipedia.Article, ...],
    output_config: OutputConfig,
    openai_settings: OpenaiSettings,  # noqa: ARG001
) -> None:
    """Test that wikipedia_articles_with_summaries_json_file writes articles to a JSON file."""

    wikipedia_articles_with_summaries_json_file(
        RecordTuple(records=tuple_of_articles_with_summaries), output_config
    )

    with output_config.parse().wikipedia_articles_with_summaries_file_path.open() as wikipedia_json_file:

        iter_tuples_of_articles_with_summaries = iter(tuple_of_articles_with_summaries)

        for wikipedia_json_line in wikipedia_json_file:
            wikipedia_json = json.loads(wikipedia_json_line)
            assert wikipedia.Article(**(wikipedia_json)) == next(
                iter_tuples_of_articles_with_summaries
            )


def test_documents_of_wikipedia_articles_with_summaries(
    tuple_of_articles_with_summaries: tuple[wikipedia.Article, ...],
    document_of_article_with_summary: Document,
) -> None:
    """Test that documents_of_wikipedia_articles_with_summaries successfully materializes a tuple of Documents."""

    assert (
        documents_of_wikipedia_articles_with_summaries(  # type: ignore[attr-defined]
            RecordTuple(records=tuple_of_articles_with_summaries),
        ).documents[0]
        == document_of_article_with_summary
    )


def test_wikipedia_articles_embeddings(
    session_mocker: MockFixture,
    openai_settings: OpenaiSettings,
    output_config: OutputConfig,
    faiss: FAISS,
    document_of_article_with_summary: Document,
) -> None:
    """Test that wikipedia_articles_embedding_store calls a method that is required to create an embedding store."""

    mock_faiss__from_documents = session_mocker.patch.object(
        FAISS, "from_documents", return_value=faiss
    )

    wikipedia_articles_embedding_store(
        DocumentTuple(documents=(document_of_article_with_summary,)),
        openai_settings,
        output_config,
    )

    mock_faiss__from_documents.assert_called_once()


def test_wikipedia_anti_recommendations(
    openai_settings: OpenaiSettings,
    output_config: OutputConfig,
    document_of_article_with_summary: Document,
    article: wikipedia.Article,
    anti_recommendation_keys_by_key_tuple: tuple[
        dict[RecordKey, tuple[RecordKey, ...]], ...
    ],
) -> None:
    """Test that wikipedia_anti_recommendations successfully returns an anti_recommendations_by_key dict."""

    assert (
        wikipedia_anti_recommendations(  # type: ignore[attr-defined]
            RecordTuple(records=(article,)),
            DocumentTuple(documents=(document_of_article_with_summary,)),
            openai_settings,
            output_config,
        ).anti_recommendations_by_key[0]
        == anti_recommendation_keys_by_key_tuple[0]
    )


def test_wikipedia_anti_recommendations_json_file(
    output_config: OutputConfig,
    anti_recommendation_keys_by_key_tuple: tuple[
        dict[RecordKey, tuple[RecordKey, ...]], ...
    ],
) -> None:
    """Test that wikipedia_anti_recommendations_json_file successfully writes an anti_recommendation_keys_by_key dict to a JSON file."""

    wikipedia_anti_recommendations_json_file(
        AntiRecommendationKeysByKeyTuple(
            anti_recommendation_keys_by_key=anti_recommendation_keys_by_key_tuple
        ),
        output_config,
    )

    with output_config.parse().wikipedia_anti_recommendations_file_path.open() as wikipedia_anti_recommendations_json_file:

        for wikipedia_json_line in wikipedia_anti_recommendations_json_file:

            assert (
                json.loads(wikipedia_json_line)["Mouseion"][-1]
                == anti_recommendation_keys_by_key_tuple[0]["Mouseion"][-1]
            )
