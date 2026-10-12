from langchain_text_splitters import RecursiveCharacterTextSplitter, Language


def get_splitter(lang: str):
    try:
        return RecursiveCharacterTextSplitter.from_language(
            Language(lang), chunk_size=1500, chunk_overlap=200, add_start_index=True)
    except ValueError:   # Fall back to a generic splitter for unsupported languages.
        return RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200, add_start_index=True)


def split_docs(docs):
    chunks = []
    for doc in docs:
        chunks.extend(get_splitter(doc.metadata["language"]).split_documents([doc]))
    return chunks
