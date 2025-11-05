# 🧪 Evals - AI Agent Evaluation Framework

This directory contains evaluation datasets and test suites for validating AI agent performance, accuracy, and reliability.

## 📁 Directory Structure

```
evals/
├── datasets/          # Evaluation datasets
│   ├── structure/     # Repository structure validation datasets
│   ├── skills/        # Skills evaluation datasets
│   └── integration/   # Integration test datasets
├── benchmarks/        # Performance benchmarks
├── results/           # Evaluation results and reports
└── configs/           # Evaluation configurations
```

## 🎯 Purpose

The evals framework provides:
- **Validation Datasets**: Ground truth data for testing AI agent outputs
- **Performance Benchmarks**: Speed and resource usage metrics
- **Quality Metrics**: Accuracy, precision, recall measurements
- **Regression Testing**: Prevent quality degradation over time

## 🚀 Usage

### Run Evaluations
```bash
# Run all evaluations
make eval

# Run specific evaluation suite
python evals/run_eval.py --suite structure

# Generate evaluation report
python evals/generate_report.py
```

### Create New Evaluation
```bash
# Create new evaluation dataset
python evals/create_dataset.py --name my_eval --type integration
```

## 📊 Evaluation Metrics

### Current Scores
- **Structure Validation**: 95%
- **Skills Maturity**: 85%
- **Integration Tests**: 90%
- **Performance**: 88%

### Success Criteria
- Accuracy >= 95%
- False positive rate <= 2%
- Processing time <= 5s
- Memory usage <= 512MB

## 📝 Evaluation Types

### 1. Structure Validation
Tests that AI agent correctly validates repository structure

### 2. Skills Evaluation
Validates that skills are properly loaded and executed

### 3. Integration Tests
End-to-end testing of complete workflows

### 4. Performance Benchmarks
Speed, memory, and resource usage testing

## 🔗 Related Documentation

- [Testing Framework](../tests/README.md)
- [Skills Documentation](../skills/README.md)
- [Validation Framework](../scripts/validate-repo-structure.py)

---

**For more information, see the main [README](../README.md)**
