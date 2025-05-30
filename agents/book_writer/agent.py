from agno.agent import Agent
from agno.models.openai import OpenAIChat # Or use Claude, etc.
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.openai import OpenAIEmbedder
from textwrap import dedent
import os
import dotenv

dotenv.load_dotenv()

# --- Configuration ---
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DATA_PATH = os.path.join(AGENT_DIR, "data/pdfs")
VECTOR_DB_PATH = os.path.join(AGENT_DIR, "vector_db")
VECTOR_TABLE_NAME = "book_knowledge"
MODEL_ID = "gpt-4o" # Choose a powerful model
EMBEDDER_ID = "text-embedding-3-small" # Choose an embedder
# ---------------------

# Ensure the vector DB directory exists
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# --- Knowledge Base Setup ---
# Check if the PDF directory exists, warn if not
if not os.path.exists(PDF_DATA_PATH) or not os.listdir(PDF_DATA_PATH):
    print(f"Warning: PDF data directory '{PDF_DATA_PATH}' is empty or does not exist.")
    print("Please create it and add PDF files for the knowledge base.")
    # Initialize with None or an empty knowledge base if you prefer
    book_knowledge = None
else:
    book_knowledge = PDFKnowledgeBase(
        path=PDF_DATA_PATH,
        vector_db=LanceDb(
            uri=VECTOR_DB_PATH,
            table_name=VECTOR_TABLE_NAME,
            search_type=SearchType.hybrid, # Or SearchType.vector
            embedder=OpenAIEmbedder(id=EMBEDDER_ID),
        ),
        # Using the default PDFReader which chunks text
        reader=PDFReader(chunk=True),
    )
# --------------------------


# --- Agent Definition ---
writer_agent = Agent(
    name="Book Writer Agent",
    model=OpenAIChat(id=MODEL_ID),
    description=dedent("""\
        You are an expert writer, skilled in composing paragraphs, articles,
        or book chapters. You leverage an internal knowledge base derived from
        PDF documents to inform your writing and adopt the tone, style,
        and perspective found within those documents."""),
    instructions=[
        "Carefully analyze the user's request for the writing topic.",
        "Search your knowledge base (derived from PDFs) for relevant information, concepts, and stylistic examples.",
        "Synthesize the information from your knowledge base to generate the requested text (paragraph, article, chapter).",
        "**CRITICAL: Emulate the specific tone, voice, style, and perspective present in the source PDF documents.** Your writing should feel like it came from the same author.",
        "Ensure the output is coherent, well-structured, and directly addresses the user's request.",
        "The length should be appropriate for the requested format (e.g., a chapter could be multiple paragraphs).",
        "Output only the generated text, without conversational filler or explanations about your process unless specifically asked.",
    ],
    knowledge=book_knowledge,
    # Agentic RAG is default, but explicitly enabling search_knowledge can be clearer
    # search_knowledge=True,
    show_tool_calls=True, # Useful for seeing if/how knowledge is searched
    markdown=True, # Format output using Markdown
)
# -----------------------

# --- Execution Logic ---
if __name__ == "__main__":
    # --- Knowledge Loading ---
    # Set to True only when you need to initially load or update the knowledge base
    # Set to False for subsequent runs to avoid reloading
    LOAD_KNOWLEDGE_FIRST_TIME = False # <-- SET TO TRUE ON FIRST RUN or when PDFs change

    if writer_agent.knowledge and LOAD_KNOWLEDGE_FIRST_TIME:
        print(f"Loading knowledge from PDFs in: {PDF_DATA_PATH}")
        print(f"Storing vectors in: {VECTOR_DB_PATH}/{VECTOR_TABLE_NAME}")
        # recreate=True will delete existing data before loading
        writer_agent.knowledge.load(recreate=True)
        print("Knowledge base loaded.")
    elif not writer_agent.knowledge:
         print("Skipping knowledge loading as no knowledge base is configured (PDF directory might be empty).")
    else:
        print("Skipping knowledge loading (LOAD_KNOWLEDGE_FIRST_TIME is False).")
    # -------------------------

    # --- Agent Invocation ---
    # Replace this with the actual topic you want the agent to write about
    writing_prompt = """
        Write a chapter discussing Are you ready for a world where banks run on Bitcoin, not dollars?

        @Jack Mallers’s @Twenty One Capital is emerging as a publicly traded “Bitcoin bank” supported by Tether, SoftBank, BitFinex, and Cantonal Fritzgerald.

        Their treasury holds over 42,000 BTC.

        Their goal is to create innovative Bitcoin-based financial products and increase Bitcoin exposure.

        Strategy (formerly MicroStrategy) made history by adopting Bitcoin as a treasury asset. Twenty One Capital aims to go further and develop an entire financial ecosystem built on Bitcoin.

        If successful, this could change how we understand money and markets.

        Why does this matter?

        🇯🇵 SoftBank connects Bitcoin to Japan’s struggles with economic stagnation and ultra-low interest rates.
        🟠 Bitcoin offers decentralization and a neutral solution to dollar-dominated systems.
        🏦 Institutions now have the opportunity to directly engage with Bitcoin, paving the way for lending and capital market products.

        The possibility feels closer than ever: Bitcoin banks are coming—neutral, internet-native money beyond national control.

        Are we witnessing the start of a financial revolution?
        """

    print(f"\nInvoking Book Writer Agent with prompt: '{writing_prompt}'")
    print("-" * 30)

    # Run the agent
    # stream=True provides real-time output
    writer_agent.print_response(writing_prompt, stream=True)

    print("-" * 30)
    print("Agent finished.")
    # -----------------------
# -----------------------
