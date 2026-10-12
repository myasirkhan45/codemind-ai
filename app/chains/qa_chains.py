# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from app.config import GROQ_API_KEY
# from app.vectorstore.chroma_store import get_store

# PROMPT = ChatPromptTemplate.from_template("""
# You are CodeMind AI, an expert code assistant.
# Answer the question ONLY using the code context below.
# If the answer is not in the context, say "Context mein ye information nahi mili."
# Mention file names when you explain.

# CONTEXT:
# {context}

# QUESTION:
# {question}

# ANSWER:
# """)

# llm = ChatGroq(
#     model="openai/gpt-oss-20b",
#     api_key=GROQ_API_KEY,
#     temperature=0
# )
# def format_docs(docs) ->str:
#     """Chunks ko ek text mein jodta hai, har chunk par file ka naam ke saath."""
#     parts = []
#     for d in docs:
#         parts.append(f"# file: {d.metadata['source']}\n{d.page_content}")
#     return "\n\n---\n\n".join(parts)


# def ask(question:str, k: int=4) -> dict:
#     retriever = get_store().as_retriever(search_kwargs={"k":k})
#     docs = retriever.invoke(question)

#     context = format_docs(docs)

#     chain = PROMPT | llm | StrOutputParser()
#     answer = chain.invoke({"context":context,"question":question})

#     sources = sorted({d.metadata['source'] for d in docs})
#     return {"answer" : answer , "sources" : sources}

from app.agents.base import run_agent

SYSTEM = """You are CodeMind AI, an expert code assistant.
Answer the question ONLY using the code context.
If the answer is not in the context, say "Context mein ye information nahi mili."
Always mention file names and function/class names you used."""


def ask(question: str, repo: str | None = None, file: str | None = None, k: int = 6) -> dict:
    return run_agent(SYSTEM, question, k=k, file=file, repo=repo)