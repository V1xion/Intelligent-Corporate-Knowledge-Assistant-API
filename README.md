# Intelligent Corporate Knowledge Assistant API
# Bernard Owens Wiladjaja

Simple RAG-based API untuk menjawab pertanyaan berdasarkan dokumen kebijakan internal perusahaan menggunakan **FastAPI, ChromaDB, Sentence Transformers, dan Ollama**.

## 1. Instruksi Menjalankan Code

### A. Persiapan Environment

Pastikan sudah terinstall:

* Python 3.10+
* Ollama
* Git

Clone repository:

```bash
git clone https://github.com/USERNAME/intelligent-corporate-knowledge-assistant.git
cd intelligent-corporate-knowledge-assistant
```

Buat dan aktifkan virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### B. Setup Ollama

Pastikan Ollama sudah terinstall dan model yang digunakan sudah tersedia.

Contoh:

```bash
ollama pull llama3.2
```

Test model:

```bash
ollama run llama3.2
```

Jika model dapat memberikan response, keluar dengan:

```text
/bye
```

### C. Setup `.env`

Buat file `.env` di folder utama project:

```env
LLM_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

CHUNK_SIZE=700
CHUNK_OVERLAP=100
TOP_K=4
SIMILARITY_THRESHOLD=0.35
```

### D. Jalankan API

Jalankan:

```bash
uvicorn app.main:app --reload
```

API akan tersedia di:

```text
http://127.0.0.1:8000
```

Swagger API dapat dibuka di:

```text
http://127.0.0.1:8000/docs
```

### E. Test API

#### 1. Ingest Document

Gunakan:

```text
POST /ingest
```

Upload file policy dari folder:

```text
data/sample_documents/
```

Contoh:

```text
kebijakan_sdm_2025.txt
```

#### 2. Chat

Gunakan:

```text
POST /chat
```

Contoh request:

```json
{
    "question": "Berapa hari cuti tahunan yang didapat karyawan tetap?"
}
```

API akan mencari informasi yang relevan dari dokumen yang sudah di-ingest dan menggunakan Ollama untuk menghasilkan jawaban.

#### 3. Test Guardrail

Contoh:

```json
{
    "question": "Siapa presiden Amerika Serikat?"
}
```

Pertanyaan yang tidak berhubungan dengan kebijakan internal akan ditolak oleh sistem.

API juga dapat dites menggunakan **Postman** dengan endpoint yang sama.

---

# 2. Penjelasan Singkat

## A. Strategi Chunking

Project ini menggunakan fixed-size chunking dengan ukuran 700 karakter dan overlap 100 karakter.

text
CHUNK_SIZE=700
CHUNK_OVERLAP=100

Strategi ini dipilih karena sederhana dan cukup untuk prototype dengan dokumen policy yang relatif pendek. Overlap digunakan agar informasi yang berada di batas antar chunk tidak mudah kehilangan context ketika dokumen dipisahkan.

Untuk production, strategi ini dapat dikembangkan menggunakan semantic chunking atau pendekatan yang mempertimbangkan struktur dokumen.

---

## B. System Prompt

System prompt digunakan untuk membatasi LLM agar menjawab berdasarkan context yang diberikan dari hasil retrieval.

Secara sederhana, prompt menginstruksikan model untuk:

* hanya menggunakan informasi dari dokumen internal yang diberikan
* tidak membuat atau mengarang aturan policy
* menolak pertanyaan yang tidak berhubungan dengan kebijakan internal
* memberikan jawaban dalam bahasa yang digunakan user
* menyebutkan sumber dokumen jika memungkinkan

Selain system prompt, terdapat similarity threshold pada proses retrieval. Jika tidak ditemukan context yang cukup relevan, sistem akan menolak pertanyaan sebelum diteruskan ke LLM.

---

## C. Scaling ke Microsoft Fabric / Azure

Untuk prototype, project menggunakan **ChromaDB dan Ollama secara lokal** agar mudah dijalankan.

Jika dikembangkan ke production, komponen tersebut dapat diganti dengan layanan cloud yang lebih scalable.

Contoh desain:

```text
User
  ↓
FastAPI / Azure App Service
  ↓
Azure OpenAI
  ↑
Azure AI Search
  ↑
Azure Blob Storage
  ↑
Internal Documents
```

Dokumen dapat disimpan di **Azure Blob Storage**, sedangkan **Azure AI Search** dapat digunakan untuk vector/semantic search. LLM lokal melalui Ollama dapat diganti dengan **Azure OpenAI** untuk kebutuhan production.

Jika perusahaan menggunakan **Microsoft Fabric**, Fabric dapat digunakan sebagai bagian dari data platform untuk mengelola data, pipeline, dan analytics. API RAG dapat tetap menjadi layer aplikasi yang mengambil knowledge dari sistem tersebut.

Dengan desain ini, komponen utama seperti ingestion, retrieval, dan generation tetap terpisah sehingga lebih mudah dikembangkan dan di-scale di masa depan.
