from search import search_documents, format_context
import sys

query = "Qual o faturamento da Empresa SuperTechIABrazil?"
if len(sys.argv) > 1:
    query = sys.argv[1]

print(f"Query: {query}")
results = search_documents(query, k=50)

print(f"Found {len(results)} documents.")
for i, (doc, score) in enumerate(results):
    print(f"--- Doc {i} (Score: {score}) ---")
    print(doc.page_content[:200] + "...") # Print first 200 chars
    if "SuperTechIABrazil" in doc.page_content:
        print(">>> 'SuperTechIABrazil' FOUND in this chunk! <<<")
