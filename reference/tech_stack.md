# Tech Stack

This document outlines the core components and tools used in our Generative AI (GenAI) stack.

---

## Python Environment / Tools

| Component | Description | Documentation/Link |
| :--- | :--- | :--- |
| **Python Package Manager** | **uv** (Installer/resolver) | [uv Documentation](https://astral.sh/uv/docs) |
| **Linter & Formatter** | **ruff** (Fast Python linter and formatter) | [ruff Documentation](https://docs.astral.sh/ruff/) |
| **QA/Code Quality** | **pre-commit** (Manages hooks) | [pre-commit Documentation](https://pre-commit.com/) |
| **Build Automation** | **Makefile** | [Makefile Tutorial By Example](https://makefiletutorial.com/) |
| **IDE** | **Visual Studio Code** | [Visual Studio Code](https://code.visualstudio.com/) |
| **Reference Repo** | N/A | [angelmtenor/ai-circus](https://github.com/angelmtenor/ai-circus) |

---


## Architecture & DevOps Tools

### Diagramming (Arch Tools)

* **excalidraw:** [https://excalidraw.com/](https://excalidraw.com/)
* **swimlanes.io:** [https://swimlanes.io](https://swimlanes.io)
* **draw.io:** [https://draw.io](https://draw.io)

### CI / CD

* **Jenkins:** [Getting started with the Guided Tour](https://www.jenkins.io/doc/pipeline/tour/)

### Infrastructure as Code (IaC)

* **Terraform:** [Terraform | HashiCorp Developer](https://developer.hashicorp.com/terraform)
* **Cloud Formation (AWS):** [Getting started with CloudFormation](https://aws.amazon.com/cloudformation/getting-started/)

---

## Generative AI (GenAI)

### Agents Frameworks

* **OpenAI SDK:** [GitHub - openai/openai-agents-python](https://github.com/openai/openai-agents-python)
* **LangChain:** [Overview Documentation](https://docs.langchain.com/docs/)

### Model Context Protocol (MCP)

* **MCP Definition:** [What is the Model Context Protocol (MCP)?](https://www.modelcontextprotocol.com/definition)
* **FastMCP 2.0:** [Welcome to FastMCP 2.0!](https://fastmcp.com/)

### Agentic Connectivity

* **Agentgateway:** [agentgateway/agentgateway: Next Generation Agentic Proxy for AI Agents and MCP servers](https://github.com/agentgateway/agentgateway)

### AWS AgentCore
* **Runtime:** Host agent or tools with Amazon Bedrock AgentCore Runtime - [Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)
* **Workshop:** Deep dive into Bedrock AgentCore - [Diving Deep into Bedrock AgentCore](https://catalog.workshops.aws/diving-deep-into-bedrock-agentcore/en-US)
* **Samples:** Code samples - [amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
