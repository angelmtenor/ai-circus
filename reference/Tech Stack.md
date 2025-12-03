# Tech Stack – Lessons from Experience

This file outlines the main components, tools, and frameworks of our software and GenAI stack. Complementary details and supporting content are provided in separate files within the same folder.

---



## Python Environment / Tools

| Component | Description | Documentation/Link |
| :--- | :--- | :--- |
| **Python Package Manager** | **uv** (Installer/resolver) | [uv Documentation](https://docs.astral.sh/uv) |
| **Linter & Formatter** | **ruff** (Fast Python linter and formatter) | [ruff Documentation](https://docs.astral.sh/ruff) |
| **QA/Code Quality** | **pre-commit** (Manages hooks) | [pre-commit Documentation](https://pre-commit.com) |
| **Build Automation** | **Makefile** | [Makefile Tutorial By Example](https://makefiletutorial.com) |
| **IDE** | **Visual Studio Code** | [Visual Studio Code](https://code.visualstudio.com) |
---

## Architecture & DevOps Tools

### Diagramming (Arch Tools)

* **excalidraw:** https://excalidraw.com
* **swimlanes.io:** https://swimlanes.io
* **draw.io:** https://app.diagrams.net

### CI / CD

* **Jenkins:** [Getting started with the Guided Tour](https://www.jenkins.io/doc/pipeline/tour)

### Infrastructure as Code (IaC)

* **Terraform:** https://developer.hashicorp.com/terraform
* **CloudFormation (AWS):** https://aws.amazon.com/cloudformation/getting-started

---

## Generative AI (GenAI)

### Newsletters & Leaderboards
- **The Batch (DeepLearning.AI):** https://www.deeplearning.ai/the-batch/
- **Model Leaderboard:** https://artificialanalysis.ai/leaderboards/models

### Agents Frameworks

* **OpenAI SDK:** https://github.com/openai/openai-agents-python
* **LangChain:** https://python.langchain.com/docs/

### Model Context Protocol (MCP)

* **MCP Definition:** https://modelcontextprotocol.com
* **FastMCP 2.0:** https://github.com/jlowin/fastmcp
* **LangChain MCP Integration:** https://docs.langchain.com/oss/python/langchain/mcp

### Agentic Connectivity

* **Agentgateway:** https://github.com/agentgateway/agentgateway

### Evaluation & Testing

* **Opik:** https://github.com/comet-ml/opik
* **Giskard:** https://github.com/Giskard-AI/giskard-oss

### Real-time Voice Communication
* **Pipecat:** https://github.com/pipecat-ai/pipecat

---


## Cloud

### AWS AgentCore

* **Runtime:** https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html
* **Workshop:** https://catalog.workshops.aws/agentcore-deep-dive/en-US
* **Repo:** https://github.com/awslabs/amazon-bedrock-agentcore-samples

### Cloud & DevOps Extras

* **LocalStack:** https://github.com/localstack/localstack
* **Coder:** https://github.com/coder/coder

### API / Testing Tools
- Swagger Editor → https://editor.swagger.io/
- Postman → https://www.postman.com/
- JWT.io → https://jwt.io
- Lens (K8s) → https://lenshq.io/

---


## Additional GenAI / LLM Tools

### Local / Open-Source LLM Tools

- **Ollama:** https://ollama.com/
- **Open WebUI:** https://github.com/open-webui/open-webui
- **Chainlit:** https://github.com/Chainlit/chainlit
- **OpenRouter:** https://openrouter.ai/
- **Perplexity:** https://www.perplexity.ai/

### Vector Stores / Embedding Databases

- **OpenSearch:** https://opensearch.org/
- **Milvus, Qdrant, Faiss, Pinecone, Weaviate**

---

## Python Data Science Libraries

### Core Libraries

| Category                  | Libraries                                                                                 |
|----------------------------|------------------------------------------------------------------------------------------|
| **Deep Learning (DL)**     | PyTorch, Keras                                                                          |
| **Machine Learning (ML)**  | scikit-learn, shap, shapiq                                                              |
| **Natural Language Processing (NLP)** | nltk, gensim, gluonnlp                                                      |
| **Data Handling & Manipulation** | pandas, numpy, collections, re (regex), datetime, pickle, networkx               |
| **Visualization & Plotting** | seaborn, matplotlib, pandas plot, plotly, missingno                                     |
| **Web & APIs**             | beautifulsoup4                                                                          |
| **Generic Utilities**      | random, time, os, pathlib, warnings                                                    |
| **Scaling / Parallelism**  | dask, swifter
| **Cryptography / Security** | cryptography

### Additional Useful Libraries
- **MLflow:** ML lifecycle platform
- **Optuna:** Hyperparameter optimization
- **Talos / Hyperas:** Hyperparameter scanning for Keras
- **kerasplotlib / livelossplot:** Training visualization
- **autokeras:** Automated ML → http://autokeras.com/
- **missingno:** Visualize missing data
- **fancyimpute:** Advanced imputation
- **chardet:** Detect text encoding
- **fuzzywuzzy:** String similarity
- **ludwig:** Declarative deep learning
- **Finetune:** Scikit-learn style finetuning for NLP




