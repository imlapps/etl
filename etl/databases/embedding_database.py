from pathlib import Path
from typing import Self

from langchain.docstore.document import Document
from langchain_community.vectorstores import VectorStore

from etl.databases import Database
from etl.pipelines import OpenaiEmbeddingPipeline
from etl.resources import OpenaiSettings


class EmbeddingDatabase(Database):

    def __init__(
        self,
        *,
        embedding_store: VectorStore,
        embeddings_cache_directory_path: Path,
    ) -> None:
        self.__embedding_store = embedding_store
        self.__embeddings_cache_directory_path = embeddings_cache_directory_path

    @classmethod
    def create(
        cls,
        *,
        documents: tuple[Document, ...],
        openai_settings: OpenaiSettings,
        embeddings_cache_directory_path: Path,
    ) -> Self:

        return cls(
            embedding_store=OpenaiEmbeddingPipeline(
                openai_settings=openai_settings,
                openai_embeddings_cache_directory_path=embeddings_cache_directory_path,
            ).create_embedding_store(documents=documents),
            embeddings_cache_directory_path=embeddings_cache_directory_path,
        )

    @property
    def descriptor(self) -> Database.Descriptor:

        return EmbeddingDatabase.Descriptor(self.__embeddings_cache_directory_path)

    @classmethod
    def open(
        cls,
        *,
        documents: tuple[Document, ...],
        descriptor: Database.Descriptor,
        openai_settings: OpenaiSettings,
    ) -> Self:

        return cls(
            embedding_store=OpenaiEmbeddingPipeline(
                openai_settings=openai_settings,
                openai_embeddings_cache_directory_path=descriptor.path,
            ).create_embedding_store(documents=documents),
            embeddings_cache_directory_path=descriptor.path,
        )

    def read(
        self,
    ) -> VectorStore:
        return self.__embedding_store
