# Graduation Project: E-commerce System with AI Chatbot & Recommendations

This repository contains the source code for a comprehensive e-commerce graduation project. The system is built using a microservices architecture, integrating a headless commerce engine, a modern frontend, and AI-powered services.

## 🏗 Project Structure

The project is organized into the following modules:

| Module | Directory | Description | Tech Stack |
|--------|-----------|-------------|------------|
| **Storefront** | [`vercel-commerce`](./vercel-commerce) | Customer-facing frontend application. | Next.js 13, React, Tailwind CSS |
| **Backend** | [`my-medusa-store`](./my-medusa-store) | Headless e-commerce backend engine. | MedusaJS, Node.js, PostgreSQL |
| **Chatbot Service** | [`chatbot-service`](./chatbot-service) | AI Chatbot for customer support and product discovery. | Python, FastAPI, OpenAI, LangChain |
| **Recommendation** | [`recommendation-service`](./recommendation-service) | Personalized product recommendation engine. | Python, FastAPI, Collaborative Filtering |
| **Tools** | [`tools`](./tools) | Utility scripts for data import/export and maintenance. | Python Scripts |

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v16 or later)
- **Python** (v3.9 or later)
- **PostgreSQL**
- **Redis**
- **Docker** (optional, for containerized deployment)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/graduation-project.git
    cd graduation-project
    ```

2.  **Setup individual modules:**
    Please refer to the `README.md` in each subdirectory for specific installation instructions.

    - [Backend Setup Guide](./my-medusa-store/README.md)
    - [Storefront Setup Guide](./vercel-commerce/README.md)
    - [Chatbot Service Setup Guide](./chatbot-service/README.md)
    - [Recommendation Service Setup Guide](./recommendation-service/README.md)

### 🐳 Docker Support

A `docker-compose.yml` file is provided at the root to spin up the entire stack (or specific services) easily.

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d chatbot-service
```

## 📚 Documentation

Additional documentation can be found in the [`docs`](./docs) directory, including:
- [Architecture Overview](./docs/ARCHITECTURE.md)
- [Decision Tree](./docs/DECISION_TREE.md)
- [Progress Report](./docs/PROGRESS.md)

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
