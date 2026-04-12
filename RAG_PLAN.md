# MovieAI RAG Plan

## 1. Goal

Build the most suitable RAG workflow for `MovieAI` based on the current architecture:

- frontend: Next.js
- backend: FastAPI
- relational data: PostgreSQL
- vector store: Qdrant
- LLM stack: OpenAI + LangChain

The core objective is not a generic document QA system, but a movie recommendation RAG system:

- understand natural-language movie intent
- retrieve semantically relevant movies from the movie library
- combine semantic retrieval with structured ranking signals
- generate concise recommendation reasons for the frontend

## 2. Fit For This Project

`MovieAI` is better suited to recommendation-oriented RAG than document-oriented RAG.

This means:

- RAG is responsible for semantic recall
- PostgreSQL is responsible for structured metadata lookup and filtering
- ranking logic is responsible for improving result order
- LLM is responsible for explanation, not free-form movie discovery

So the correct pipeline is:

`user query -> semantic retrieval -> structured rerank -> LLM explanation`

not:

`user query -> LLM invents recommendations directly`

## 3. Recommended Architecture

### 3.1 Phase 1: Single-Movie Single-Vector

This is the best starting point for the current codebase.

Each movie row becomes:

- one `rag_text`
- one embedding
- one Qdrant point

At this stage:

- `1 movie = 1 semantic document = 1 vector`

This avoids unnecessary chunk aggregation and keeps the system simple to debug.

### 3.2 Phase 2: Hybrid Search + Rerank

After the first phase is stable:

- combine vector similarity with `vote_average`
- combine vector similarity with `popularity`
- optionally add SQL-side filters for genre, director, year, language

Recommended lightweight rerank formula:

```text
final_score = 0.70 * vector_score + 0.20 * rating_score + 0.10 * popularity_score
```

### 3.3 Phase 3: Multi-Source Movie Chunks

Only after phase 1 and 2 are stable.

At this stage, one movie may have several semantic chunks:

- `plot`
- `keywords`
- `reviews_summary`
- `style`

Then retrieval is chunk-level, but final output is still movie-level by grouping on `movie_id`.

## 4. Data Design

### 4.1 Source Table

Current main source:

- `movies`

Important available fields:

- `title`
- `original_title`
- `overview`
- `tagline`
- `genres`
- `keywords`
- `director`
- `original_language`
- `release_date`
- `runtime`
- `vote_average`
- `popularity`
- `rag_text`

### 4.2 `rag_text` Design

For this project, `rag_text` should be a semi-structured semantic description of a movie.

Recommended template:

```text
Title: Inception
Original title: Inception
Overview: A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO.
Tagline: Your mind is the scene of the crime.
Genres: Action, Science Fiction, Adventure
Keywords: dream, subconscious, heist, mind-bending
Director: Christopher Nolan
Original language: en
Release year: 2010
Runtime: 148 minutes
```

Rules:

- skip empty fields
- parse `genres` and `keywords` into readable names before joining
- avoid dumping raw JSON directly into embeddings
- keep text stable and deterministic so re-indexing is predictable

### 4.3 Qdrant Collection

Recommended collection name:

```text
movie_semantic
```

Each point should contain:

- `id`: movie id
- `vector`: embedding of `rag_text`
- `payload`: structured fields for filtering and display

Recommended payload:

```json
{
  "movie_id": 680,
  "title": "Inception",
  "genres": ["Action", "Science Fiction", "Adventure"],
  "keywords": ["dream", "subconscious", "heist", "mind-bending"],
  "director": "Christopher Nolan",
  "original_language": "en",
  "release_year": 2010,
  "vote_average": 8.4,
  "popularity": 220.3
}
```

## 5. End-To-End Workflow

### 5.1 Offline Indexing Workflow

1. Read movie rows from PostgreSQL
2. Build `rag_text` for each movie
3. Write `rag_text` back into `movies.rag_text`
4. Generate embeddings
5. Upsert embeddings into Qdrant

### 5.2 Online Recommendation Workflow

1. User sends natural-language request
2. Backend embeds the query
3. Query vector searches Qdrant for top-k movies
4. Backend fetches full movie metadata from PostgreSQL
5. Backend reranks candidate movies
6. Backend passes top-N candidates to LLM
7. LLM generates recommendation reasons
8. API returns structured recommendation result

## 6. LangChain Responsibilities

LangChain should be used lightly and only where it adds value.

Recommended usage:

- `OpenAIEmbeddings`
- `QdrantVectorStore`
- retriever wrapper
- prompt + output parsing

Not recommended in phase 1:

- heavy agent workflows
- autonomous tool use
- over-complicated chains

The system should remain mostly backend-controlled and deterministic.

## 7. Backend Module Plan

Recommended new modules:

- `backend/app/services/rag_service.py`
- `backend/app/services/rag_indexer.py`
- `backend/scripts/build_movie_index.py`

### 7.1 `rag_service.py`

Responsibilities:

- embed query
- retrieve candidate movies from Qdrant
- fetch movie rows from PostgreSQL
- rerank candidate results
- prepare prompt context for the LLM

Recommended functions:

- `build_movie_rag_text(movie: dict) -> str`
- `retrieve_movies(query: str, limit: int = 10) -> list[dict]`
- `fetch_movies_by_ids(movie_ids: list[int]) -> list[dict]`
- `rerank_movies(candidates: list[dict]) -> list[dict]`
- `generate_recommendation_reasons(query: str, movies: list[dict]) -> list[dict]`

### 7.2 `rag_indexer.py`

Responsibilities:

- parse and normalize source fields
- batch embedding
- Qdrant upsert
- optional reindex / incremental index logic

### 7.3 `build_movie_index.py`

Responsibilities:

- run indexing from the command line
- update `movies.rag_text`
- create the collection if missing
- batch upsert all or only missing movies

## 8. API Design

### 8.1 Main Endpoint

Current endpoint:

- `POST /api/ai/recommend`

Recommended request:

```json
{
  "query": "我想看类似星际穿越、带哲思感的科幻电影",
  "user_id": 123,
  "max_results": 8,
  "include_reasons": true
}
```

Recommended response:

```json
{
  "query": "我想看类似星际穿越、带哲思感的科幻电影",
  "items": [
    {
      "movie_id": 157336,
      "title": "Interstellar",
      "relevance_score": 0.9321,
      "reason": "这部电影同样强调太空探索、时间与情感主题，整体气质与用户需求高度匹配。"
    }
  ],
  "total_time_ms": 420
}
```

### 8.2 Search Endpoint

Current endpoint:

- `GET /api/ai/search`

This endpoint should evolve into hybrid search:

- vector recall
- optional structured filters
- lightweight rerank

## 9. Prompt Strategy

The LLM should never be asked to invent movies.

It should only:

- read the retrieved candidate list
- pick the best matches
- explain why they match

Recommended prompt constraints:

- only use provided candidate movies
- do not fabricate titles
- produce concise reasons
- prefer structured JSON output

## 10. Phase Plan

### Phase 1: MVP

- generate `rag_text` for each movie
- build `movie_semantic` collection
- implement semantic retrieval in `/api/ai/recommend`
- return top-k movies with similarity score

Success criteria:

- user can describe a movie need in natural language
- backend returns semantically relevant movies
- result order is reasonable

### Phase 2: Better Ranking

- add SQL filters before retrieval when explicit constraints exist
- add score fusion with rating and popularity
- reduce duplicate or weak results

Success criteria:

- better ranking quality than pure vector search
- lower rate of irrelevant recommendations

### Phase 3: Explanation Layer

- generate recommendation reasons with LLM
- support frontend card explanations

Success criteria:

- each recommendation has a short, credible reason
- LLM output stays grounded in retrieved candidates

### Phase 4: Personalization

- combine collaborative filtering outputs with semantic recall
- use favorites, watch history, ratings, and search behavior

Success criteria:

- logged-in users get better personalized recommendations
- AI recommendations reflect both query intent and user taste

## 11. Qdrant Deployment Recommendation

### 11.1 Local Qdrant

Recommended when:

- you are still developing locally
- dataset size is small or medium
- you want fast debugging and low cost
- you are still iterating on schema and indexing logic

Pros:

- easy to start
- no additional cloud cost
- fast local iteration
- ideal for development and debugging

Cons:

- weaker persistence and operational reliability unless you manage it properly
- not ideal for production traffic
- local environment is harder to share across machines

### 11.2 Cloud Qdrant

Recommended when:

- you are preparing for demo or production use
- you want stable persistence and remote availability
- multiple environments or collaborators need access

Pros:

- managed service
- easier persistence and backup
- easier deployment with frontend/backend separation
- more production-friendly

Cons:

- additional cost
- slower to iterate during early experimentation
- schema mistakes cost more time to fix

### 11.3 Recommendation For MovieAI

Best choice right now:

- use local Qdrant during phase 1 and phase 2
- move to cloud Qdrant when the index schema and retrieval quality are stable

So the recommended path is:

```text
development -> local Qdrant
staging/production/demo -> cloud Qdrant
```

This is the best balance between speed, cost, and stability.

## 12. Key Risks

### 12.1 Weak Recall Quality

Cause:

- poor `rag_text`
- inconsistent keyword parsing
- too little semantic signal in source text

Mitigation:

- improve `overview`, `genres`, `keywords`, `tagline`, `director`
- validate retrieval examples manually

### 12.2 LLM Hallucination

Cause:

- prompt too open-ended
- model allowed to recommend arbitrary movies

Mitigation:

- force candidate-grounded output
- structured output only

### 12.3 Low Ranking Quality

Cause:

- pure vector similarity is not enough

Mitigation:

- add rerank layer
- combine semantic score with rating and popularity

## 13. Deliverables

Planned deliverables:

- `RAG_PLAN.md`
- movie `rag_text` generation function
- indexing script
- Qdrant collection initialization
- FastAPI semantic retrieval flow
- optional LLM explanation flow

## 14. Final Recommendation

For `MovieAI`, the most suitable RAG implementation is:

- phase 1: single-movie single-vector semantic retrieval
- phase 2: hybrid rerank with SQL metadata
- phase 3: LLM explanation
- phase 4: integration with collaborative filtering and user behavior

Do not start with multi-chunk movie indexing.
Do not start with heavy agent-style LangChain flows.
Do start with deterministic movie-level semantic retrieval and grow from there.
