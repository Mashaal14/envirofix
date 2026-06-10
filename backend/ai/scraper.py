import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
import hashlib
import json
from datetime import datetime

SOURCES = [
    "https://www.kali.org/blog/",
    "https://www.kali.org/docs/general-use/",
    "https://www.kali.org/docs/troubleshooting/",
    "https://www.kali.org/tools/",
    "https://pkg.kali.org/pkg/metasploit-framework",
    "https://pkg.kali.org/pkg/nmap",
    "https://pkg.kali.org/pkg/python3",
    "https://pkg.kali.org/pkg/libssl-dev",
    "https://pkg.kali.org/pkg/linux-headers-amd64",
]

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client   = chromadb.PersistentClient(path="./envirofix_knowledge")
col      = client.get_or_create_collection("kali_docs")

def scrape_and_index(url):
    try:
        r = requests.get(url, timeout=15,
            headers={"User-Agent": "EnviroFix/1.0"})
        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script","style","nav","footer","header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        chunks = []
        for i in range(0, len(words), 400):
            chunk = " ".join(words[i:i+500])
            if len(chunk) > 100:
                chunks.append(chunk)

        for i, chunk in enumerate(chunks):
            doc_id    = hashlib.md5(f"{url}{i}".encode()).hexdigest()
            embedding = embedder.encode(chunk).tolist()
            col.upsert(
                ids        = [doc_id],
                documents  = [chunk],
                embeddings = [embedding],
                metadatas  = [{"source": url,
                               "chunk": i,
                               "scraped_at": datetime.now().isoformat()}]
            )
        print(f"Indexed {len(chunks)} chunks from {url}")
        return len(chunks)

    except Exception as e:
        print(f"Failed {url}: {e}")
        return 0

def run_full_scrape():
    total = 0
    for url in SOURCES:
        total += scrape_and_index(url)
    print(f"\nTotal chunks indexed: {total}")
    with open("./envirofix_knowledge/last_scrape.json", "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(),
                   "chunks": total}, f)

if __name__ == "__main__":
    run_full_scrape()
