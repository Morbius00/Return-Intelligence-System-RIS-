# Documentation Index

This index points to the updated documentation for the current feedback intelligence pipeline.

## Start Here

- ../README.md: Main setup and deployment guide
- GETTING_STARTED_WINDOWS.md: Fast setup for Windows
- QUICK_SETUP_REFERENCE.md: Command-first operations guide

## Core System Docs

- PROJECT_OVERVIEW.md: High-level business and architecture overview
- TECHNICAL_SUMMARY.md: Technical design and model behavior
- PIPELINE_FLOW_DIAGRAM.md: Pipeline flow and sequence diagrams
- ARCHITECTURE_DETAILS.md: Module-level architecture details
- COMPLETE_DOCUMENTATION.md: End-to-end reference

## Integrations

- GOOGLE_SHEETS_SETUP.md: Service account setup and Sheets workflows

## Fast Navigation by Task

- Train models: ../README.md and QUICK_SETUP_REFERENCE.md
- Run local API: ../README.md and GETTING_STARTED_WINDOWS.md
- Understand prediction payloads: ../README.md and COMPLETE_DOCUMENTATION.md
- Operate CSV or Sheets batch flows: QUICK_REFERENCE.md and GOOGLE_SHEETS_SETUP.md
- Deploy with Docker and Render: ../README.md

## Current Pipeline Snapshot

Input -> Spam Detection -> Sentiment Detection ->
- Negative path: issue category + severity
- Positive path: satisfaction category + goodwill
- Neutral path: no category score assignment

Version in API metadata: 2.0.0


