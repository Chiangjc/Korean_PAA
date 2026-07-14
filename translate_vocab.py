import json
import re
import time
import urllib.request
import urllib.parse

from tqdm import tqdm

JSON_PATH = "토픽_어휘_목록.json"
CACHE_PATH = "translate_cache.json"
DELIM = " ||| "
BATCH_CHAR_LIMIT = 1500  # keep query string safely under URL limits
SLEEP_BETWEEN_REQUESTS = 0.3
MAX_RETRIES = 5


def load_cache():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def translate_batch(lines, sl="ko", tl="zh-TW"):
    text = DELIM.join(lines)
    params = {"client": "gtx", "sl": sl, "tl": tl, "dt": "t", "q": text}
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            translated = "".join(seg[0] for seg in data[0])
            parts = [s.strip() for s in translated.split(DELIM.strip())]
            if len(parts) != len(lines):
                # delimiter got mangled by translation; fall back to per-item calls
                return None
            return parts
        except Exception as e:
            wait = 2 ** attempt
            tqdm.write(f"  retry {attempt + 1}/{MAX_RETRIES} after error: {e} (sleep {wait}s)")
            time.sleep(wait)
    raise RuntimeError(f"Failed to translate batch after {MAX_RETRIES} retries: {lines[:3]}...")


def translate_unique(items, cache, desc="translating"):
    todo = [x for x in items if x not in cache]
    print(f"  {len(items)} unique strings, {len(todo)} not yet cached")
    batch = []
    batch_len = 0
    batches = []
    for item in todo:
        item_len = len(item) + len(DELIM)
        if batch and batch_len + item_len > BATCH_CHAR_LIMIT:
            batches.append(batch)
            batch = []
            batch_len = 0
        batch.append(item)
        batch_len += item_len
    if batch:
        batches.append(batch)

    with tqdm(total=len(todo), desc=desc, unit="word") as pbar:
        for b in batches:
            result = translate_batch(b)
            if result is None:
                # delimiter mismatch -> translate one by one for this batch
                result = []
                for item in b:
                    r = translate_batch([item])
                    result.append(r[0] if r else item)
                    time.sleep(SLEEP_BETWEEN_REQUESTS)
            for src, tgt in zip(b, result):
                cache[src] = tgt
            save_cache(cache)
            pbar.update(len(b))
            time.sleep(SLEEP_BETWEEN_REQUESTS)


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    vocab = data["vocabulary"]
    cache = load_cache()

    print("Translating words...")
    word_stems = sorted({re.sub(r"\d+$", "", v["word"]) for v in vocab})
    translate_unique(word_stems, cache, desc="words")

    # print("Translating guides...")
    # guides = sorted({v["guide"] for v in vocab if v.get("guide")})
    # translate_unique(guides, cache, desc="guides")

    for v in tqdm(vocab, desc="writing back", unit="entry"):
        stem = re.sub(r"\d+$", "", v["word"])
        v["word_zh"] = cache.get(stem, "")
        # v["guide_zh"] = cache.get(v["guide"], "") if v.get("guide") else ""

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Done. Updated {len(vocab)} entries in {JSON_PATH}")


if __name__ == "__main__":
    main()
