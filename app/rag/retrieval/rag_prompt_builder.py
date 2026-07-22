from app.llm.llm_schemas import Message
from app.prompts.system_prompt_builder import SystemPromptBuilder
from app.rag.rag_schemas import Chunk


RAG_SYSTEM_PROMPT = """
You are a fitness assistant.

Answer the user's question using only the provided knowledge base.

Instructions:
- Prioritize answer what you're sure first before coming up with what's not.
- Asking follow up question at the end if it's related to fitness, nutrition, workout.
- Use the provided knowledge base as the source of truth, but do not mention it.
- If the answer is not supported by the knowledge base, say that you don't know.
- Do not invent facts or use outside knowledge.
- Keep your answer accurate, concise, and helpful.
- If the request asks for medical diagnosis or treatment advice, politely refuse and recommend consulting a qualified healthcare professional.
"""

RESPONSE_RULES = """
Return schema:

{
  "answer": "Muscles don't grow in the gym — they grow during recovery. Training creates micro-damage to muscle fibers. Recovery is when the body repairs and strengthens those fibers (supercompensation). Protein functionally support muscle repair and growth, ...",
  "sources": [
    "knowledge/12-muscle-recovery.md",
    "knowledge/13-nutrition-basics.md"
  ]
}

- "sources" must contain only the document sources that directly support the answer.
- Do not include documents that were not used.
- Every source must exactly match a source provided in the knowledge base.
- Return JSON only.
""".strip()


class RAGPromptBuilder:
    """Builds the prompt for the answer generation model."""

    def __init__(
        self,
        system_prompt_builder: SystemPromptBuilder,
    ) -> None:
        self._system_prompt_builder = system_prompt_builder

    def build(
        self,
        query: str,
        chunks: list[Chunk],
    ) -> list[Message]:
        """Build the prompt for the generator."""

        context = self._build_context(chunks)

        return [
            Message(
                role="system",
                content=RAG_SYSTEM_PROMPT,
            ),
            *self._system_prompt_builder.build_rag_prompt(),
            Message(
                role="system",
                content=RESPONSE_RULES,
            ),
            Message(
                role="system",
                content=(
                    "The following information was retrieved from the "
                    "knowledge base. Use it as the primary source for "
                    "answering the user's question.\n\n"
                    f"{context}"
                ),
            ),
            Message(
                role="user",
                content=query,
            ),
        ]

    @staticmethod
    def _build_context(
        chunks: list[Chunk],
    ) -> str:
        """Format retrieved chunks."""

        return "\n\n".join(
            (
                f"Source: {chunk.source}\n"
                f"{chunk.content}"
            )
            for chunk in chunks
        )