from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import GROQ_API_KEY
from app.vectorstore.chroma_store import get_store

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
    temperature=0,
    max_tokens=8192,           # Leave room for both reasoning and the answer.
    reasoning_effort="low",    # Use less reasoning and prioritize the response.
)
FORMAT_RULES = """
Formatting rules (Markdown):
- Start with a 1-2 line direct answer or summary.
- Use ## headings when the answer has more than one part.
- Use bullet or numbered lists for steps and tables for comparisons.
- Put ALL code in fenced code blocks with the language name (python, java, js, ...).
- Use backticks for file names, functions and classes.
- Be concise. No filler, do not repeat the question.
- Do NOT add a Sources section, the app shows sources separately.
"""

def format_docs(docs) -> str:
    """Join retrieved chunks and label each one with its source file."""
    return "\n\n---\n\n".join(
        f"# FILE: {d.metadata['source']}\n{d.page_content}" for d in docs
    )


def retrieve(task: str, k: int = 6, file: str | None = None, repo: str | None = None):
    store = get_store()

    def make_filter(f):
        conds = []
        if f:
            conds.append({"source": f})
        if repo:
            conds.append({"repo": repo})
        if not conds:
            return None
        return conds[0] if len(conds) == 1 else {"$and": conds}

    # Try both Windows (\) and Linux (/) path formats.
    variants = [file] if not file else list({file, file.replace("\\", "/"), file.replace("/", "\\")})
    for f in variants:
        docs = store.similarity_search(task, k=k, filter=make_filter(f))
        if docs:
            return docs
    return []


def generate(system_prompt: str, task: str, docs) -> dict:
    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt + "\n" + FORMAT_RULES),
    ("human", "CODE CONTEXT:\n{context}\n\nTASK:\n{task}"),
    ])
    chain = prompt | llm | StrOutputParser()
    context = format_docs(docs)

    answer = chain.invoke({"context": context, "task": task})
    if not answer.strip():
        answer = chain.invoke({
            "context": context,
            "task": task + "\n\nIf the context is insufficient, say exactly what is missing.",
        })
    if not answer.strip():
        answer = "The model returned an empty response. Please make the task more specific."

    return {"answer": answer, "sources": sorted({d.metadata["source"] for d in docs})}


def run_agent(system_prompt: str, task: str, k: int = 6,
              file: str | None = None, repo: str | None = None) -> dict:
    docs = retrieve(task, k, file, repo)
    if not docs:
        return {
            "answer": "No indexed code chunks were found. Check the repository and file name.",
            "sources": [],
        }
    return generate(system_prompt, task, docs)
