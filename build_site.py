import json

DATA_PATH = "토픽_어휘_목록.json"
TEMPLATE_PATH = "site_template.html"
OUTPUT_PATH = "index.html"


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    vocab = data["vocabulary"]
    compact = [[v["level"], v["word"], v.get("guide", ""), v["pos"], v.get("word_zh", "")] for v in vocab]
    vocab_json = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    if "__VOCAB_DATA__" not in template:
        raise RuntimeError("site_template.html is missing the __VOCAB_DATA__ placeholder")

    output = template.replace("__VOCAB_DATA__", vocab_json)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Built {OUTPUT_PATH}: {len(vocab)} entries, {len(vocab_json)} chars of embedded data")


if __name__ == "__main__":
    main()
