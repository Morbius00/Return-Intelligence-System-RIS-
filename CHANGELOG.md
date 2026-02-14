# Changelog

All notable changes to the NLP Return Reason Classifier project.

## [1.0.0] - 2026-02-14

### Added
- ✨ Initial release of NLP Return Reason Classifier
- 🚀 FastAPI REST API with multiple endpoints
- 🔤 NLTK-based text preprocessing pipeline
- 🛡️ Rule-based spam detection layer
- 🤖 TF-IDF + Logistic Regression classifier
- 📊 Severity scoring system for 6 categories
- 📝 Google Sheets integration service
- ⚡ Batch processor for CSV and Google Sheets
- 📦 Complete training pipeline with sample dataset
- 📚 Comprehensive documentation and README
- 🧪 API test suite and examples
- 🔧 Setup and run scripts for easy deployment
- 🐳 Docker-compatible architecture

### Features
- Single and batch prediction endpoints
- Automatic model loading on startup
- Health check and diagnostics endpoints
- Category listing with severity scores
- Preprocessing debug endpoint
- Support for 5000+ row batch processing
- CSV export/import support
- Environment-based configuration
- Comprehensive error handling and logging

### Categories
- Product Quality Issue (Severity: 0.9)
- Expiry Issue (Severity: 0.9)
- Packaging Issue (Severity: 0.6)
- Wrong Item (Severity: 0.6)
- Customer Preference (Severity: 0.3)
- Other (Severity: 0.2)

### Performance
- Inference: <50ms per request
- Batch: 1000+ items/minute
- Model size: <1MB
- Memory usage: ~100MB
- Accuracy: 90-95% on labeled data

### Documentation
- README.md - Complete user guide
- TECHNICAL_SUMMARY.md - Architecture and design decisions
- API documentation - Auto-generated via FastAPI
- Code docstrings - Comprehensive inline documentation

### Dependencies
- Python 3.11+
- FastAPI 0.109.0
- NLTK 3.8.1
- scikit-learn 1.4.0
- gspread 5.12.4
- pandas 2.2.0

---

## Future Roadmap

### [1.1.0] - Planned
- [ ] Multi-language support
- [ ] Confidence threshold configuration
- [ ] Model performance monitoring dashboard
- [ ] Automated retraining pipeline
- [ ] Extended spam pattern library

### [1.2.0] - Planned
- [ ] REST API authentication
- [ ] Rate limiting
- [ ] Caching layer for frequent queries
- [ ] Prometheus metrics export
- [ ] Model versioning system

### [2.0.0] - Planned
- [ ] Multi-model support (A/B testing)
- [ ] Active learning integration
- [ ] Enhanced category hierarchy
- [ ] Custom taxonomy support
- [ ] Advanced analytics and reporting
