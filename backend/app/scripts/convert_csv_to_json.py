import csv
import json
import os

# Paths
csv_file_path = os.path.join(
    os.path.dirname(__file__), "../data/questions.csv"
)
json_file_path = os.path.join(
    os.path.dirname(__file__), "../data/knowledge_base.json"
)


def convert_csv():
  data = []

  if not os.path.exists(csv_file_path):
    print(f"Error: {csv_file_path} not found. Please place your CSV file there.")
    return

  with open(csv_file_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
      # Map CSV columns to your knowledge base structure
      # Adjust keys ('category', 'title', 'content') to match your CSV headers
      item = {
          "category": row.get("category", "faq"),
          "title": row.get("title", row.get("question", "Untitled")),
          "content": row.get("content", row.get("answer", "")),
      }
      data.append(item)

  # Write out to knowledge_base.json
  with open(json_file_path, mode="w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

  print(
      f"Successfully converted {len(data)} rows from CSV to"
      f" {json_file_path}!"
  )


if __name__ == "__main__":
  convert_csv()