# GenAI Notes – Lessons from Experience


## 1. GenAI / Chatbot Best Practices

### Quality & Consistency

* Use state-of-the-art GenAI models
* Ensure deterministic responses for similar inputs
* Accurate retrieval (vector search)

### Deployment & Integration

* Support cloud or on-premises deployment
* Integrate vector storage (Milvus, FAISS, Qdrant, Pinecone)
* Provide custom endpoints & APIs

### Security & Compliance

* Data encryption & anonymization
* PII detection
* Ethical & sentiment checks

### Monitoring & Evaluation

* Real-time system monitoring
* Ground-truth evaluation
* User feedback loops

### Automation & Workflow

* Context-aware bots
* Custom workflows & dynamic ingestion

### Common Pitfalls

* Non-intent-based chatbots
* Overly complex Python backends
* Custom authentication instead of managed services
* Skipping structured outputs → unreliable tool calling
