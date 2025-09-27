# LLM apps with LangChain

A collection of focused projects and hands‑on examples for AI engineering, primarily using LangChain, LLM integrations, and related tooling. Each subproject is intended as a practical, runnable example to help you prototype features and stay productive when building with LLMs.

This repository contains individual example projects (each with its own README) that demonstrate patterns, integrations, and best practices for working with LLMs and LangChain in real applications.

## Purpose

This repository provides hands-on, runnable projects that demonstrate core LangChain patterns, LLM integration techniques, and practical engineering approaches for building production-capable AI services. Each example focuses on a narrow problem—fetching and cleaning data, prompt/chain design, or UI/backend integration—so you can learn and iterate quickly. The content emphasizes reproducibility, testing, and safety considerations (e.g., rate limits, redaction, chunking) to help bridge prototyping and production. Use these projects to accelerate prototyping, validate architectural choices, and extract practical recipes you can adapt into your own systems. Contributions and improvements are welcome—please open an issue or submit a PR with fixes, enhancements, or additional examples.

## Quick notes

- I use the `uv` (https://docs.astral.sh/uv/) as the default package manager
- If you don't have `uv` installed, refer installation documentation - https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
- Each subproject includes its own `README` with detailed setup and run instructions
- Use isolated virtual environments per project (recommended) or a shared environment for quick experiments
- Store secrets in `.env` files (see each subproject's `.env.example`) and never commit credentials to source control
- Recommended Python version: `3.10+`

## Todo

- [ ] Ability to switch to self-hosted LLMs
- [ ] Add tests cases
- [ ] Add docker files for each subproject
- [ ] Set up CI workflow to run linting and test suites on pull requests
- [ ] Publish a reusable project template for bootstrapping new LangChain demos
