# Project Overview

## What the Project Does

This project classifies customer feedback into actionable business signals using lightweight NLP and classical ML.

For each feedback item, the API returns:
- Spam flag
- Sentiment type: Positive, Negative, or Neutral
- Negative path outputs: issue_category and severity_score
- Positive path outputs: satisfaction_category and goodwill_score
- Model confidence

## Why This Pipeline

The pipeline is optimized for fast, explainable, low-cost inference:
- Classical ML instead of large deep models
- Domain-specific categories and score mappings
- Deterministic preprocessing and scoring behavior

## End-to-End Flow

1. Receive feedback text and optional rating
2. Block obvious spam/placeholder content
3. Detect sentiment using text-first rules and optional rating tiebreaker
4. Route to the corresponding sub-model
5. Return structured response fields for downstream automation

## Categories and Scores

### Negative Sentiment
- Product Quality Issue -> 0.9
- Expiry Issue -> 0.9
- Packaging Issue -> 0.6
- Wrong Item -> 0.6
- Customer Preference -> 0.3
- Other -> 0.2
- Uncertain -> 0.1

### Positive Sentiment
- Product Appreciation -> 0.9
- Overall Positive Experience -> 0.85
- Service Satisfaction -> 0.8
- Packaging Praise -> 0.7
- General Positive -> 0.6

## API Surface

Main endpoints:
- GET /health
- GET /categories
- POST /predict
- POST /predict/batch
- POST /predict/file
- POST /sheets/process
- POST /sheets/update
- POST /sheets/append

## Data Interfaces

### Input keys
- customer_feedback (required)
- rating (optional for /predict)
- customer_feedbacks and ratings (for /predict/batch)

### File upload expectations
- Customer_Feedback column required
- Rating column optional if the column name contains rating

## Deployment

The project is deployment-ready using:
- Dockerfile for containerized runtime
- render.yaml for Render Blueprint auto-deploy

## Typical Use Cases

- Real-time support ticket enrichment
- Google Sheets workflow automation
- Bulk feedback analysis from CSV/Excel
- Sentiment-based triage and escalation


