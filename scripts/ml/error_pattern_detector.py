#!/usr/bin/env python3
"""
Self-learning error pattern detector using scikit-learn.

Learns from historical CI failures to predict and prevent future issues.

Usage:
    # Train model on historical errors
    python error_pattern_detector.py train

    # Predict error category and get fix suggestion
    python error_pattern_detector.py predict "ERROR: No module named 'pytest_cov'"

    # Analyze error trends
    python error_pattern_detector.py analyze
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
except ImportError:
    print("❌ ML dependencies not installed. Run: pip install -e '.[self-learning]'")
    sys.exit(1)


class ErrorPatternDetector:
    """ML-based error pattern detection and classification"""

    def __init__(self, model_path="models/error_detector.pkl"):
        self.model_path = Path(model_path)
        self.pipeline = None
        self.categories = [
            "dependency_missing",
            "environment_variable",
            "api_contract_mismatch",
            "network_timeout",
            "permission_denied",
            "configuration_error",
            "syntax_error",
            "import_error",
        ]

        # Error pattern templates for initial training
        self.seed_patterns = self._generate_seed_patterns()

    def _generate_seed_patterns(self) -> List[Dict]:
        """Generate seed error patterns for initial training"""
        return [
            # Dependency missing
            {
                "message": "ModuleNotFoundError: No module named 'pytest_cov'",
                "category": "dependency_missing",
            },
            {
                "message": "ImportError: cannot import name 'foo' from 'bar'",
                "category": "dependency_missing",
            },
            {
                "message": "ERROR: Could not find a version that satisfies the requirement",
                "category": "dependency_missing",
            },
            {"message": "pip: command not found", "category": "dependency_missing"},
            {
                "message": "No module named 'anthropic'",
                "category": "dependency_missing",
            },
            # Environment variable
            {"message": "KeyError: 'OCR_HOST'", "category": "environment_variable"},
            {
                "message": "Environment variable SUPABASE_URL not set",
                "category": "environment_variable",
            },
            {
                "message": "Invalid URL 'None': No host supplied",
                "category": "environment_variable",
            },
            {
                "message": "os.environ['DATABASE_URL'] raised KeyError",
                "category": "environment_variable",
            },
            {
                "message": "Missing required environment variable: API_KEY",
                "category": "environment_variable",
            },
            # API contract mismatch
            {
                "message": "AssertionError: assert None is True",
                "category": "api_contract_mismatch",
            },
            {
                "message": "KeyError: 'ok' - response={'status': 'ok'}",
                "category": "api_contract_mismatch",
            },
            {
                "message": "JSONDecodeError: Expecting value: line 1 column 1",
                "category": "api_contract_mismatch",
            },
            {
                "message": "404 Not Found - endpoint /classify/expense",
                "category": "api_contract_mismatch",
            },
            {
                "message": "Response missing required field: 'data'",
                "category": "api_contract_mismatch",
            },
            # Network timeout
            {
                "message": "requests.exceptions.ConnectionError: Connection timed out",
                "category": "network_timeout",
            },
            {
                "message": "TimeoutError: Read timed out after 30 seconds",
                "category": "network_timeout",
            },
            {
                "message": "urllib3.exceptions.MaxRetryError: Max retries exceeded",
                "category": "network_timeout",
            },
            {
                "message": "Connection refused on port 5432",
                "category": "network_timeout",
            },
            {
                "message": "DNS resolution failed for api.example.com",
                "category": "network_timeout",
            },
            # Permission denied
            {
                "message": "PermissionError: [Errno 13] Permission denied",
                "category": "permission_denied",
            },
            {
                "message": "Error: EACCES: permission denied, open '/var/log/app.log'",
                "category": "permission_denied",
            },
            {
                "message": "Access forbidden: insufficient permissions",
                "category": "permission_denied",
            },
            {"message": "sudo: command not found", "category": "permission_denied"},
            {
                "message": "GitHub Actions: Resource not accessible by integration",
                "category": "permission_denied",
            },
            # Configuration error
            {
                "message": "YAML parsing error: mapping values are not allowed here",
                "category": "configuration_error",
            },
            {
                "message": "Invalid configuration: missing required field 'database'",
                "category": "configuration_error",
            },
            {
                "message": "ConfigParser.NoSectionError: No section: 'database'",
                "category": "configuration_error",
            },
            {
                "message": "Syntax error in .github/workflows/ci.yml line 42",
                "category": "configuration_error",
            },
            {
                "message": "Invalid value for 'timeout': expected int, got str",
                "category": "configuration_error",
            },
            # Syntax error
            {
                "message": "SyntaxError: invalid syntax at line 15",
                "category": "syntax_error",
            },
            {
                "message": "IndentationError: unexpected indent",
                "category": "syntax_error",
            },
            {
                "message": "NameError: name 'variabel' is not defined",
                "category": "syntax_error",
            },
            {
                "message": "TypeError: unsupported operand type(s) for +",
                "category": "syntax_error",
            },
            {
                "message": "AttributeError: 'NoneType' object has no attribute 'get'",
                "category": "syntax_error",
            },
            # Import error
            {
                "message": "ImportError: attempted relative import with no known parent",
                "category": "import_error",
            },
            {
                "message": "ModuleNotFoundError: No module named 'addons.custom'",
                "category": "import_error",
            },
            {
                "message": "Circular import detected: module A imports module B",
                "category": "import_error",
            },
            {
                "message": "ImportError: cannot import name 'X' from partially initialized module",
                "category": "import_error",
            },
            {
                "message": "ImportError: DLL load failed while importing _ctypes",
                "category": "import_error",
            },
        ]

    def train(self, error_logs: Optional[List[Dict]] = None):
        """Train model on historical error logs or seed patterns"""
        if error_logs is None:
            error_logs = self.seed_patterns
            print(f"ℹ️  Using {len(error_logs)} seed patterns for initial training")
        else:
            print(f"📊 Training on {len(error_logs)} historical error logs")

        # Extract features from error messages
        X = [log["message"] for log in error_logs]
        y = [log["category"] for log in error_logs]

        # Split for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Build ML pipeline
        self.pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        max_features=1000,
                        ngram_range=(1, 3),
                        min_df=1,
                        lowercase=True,
                        stop_words="english",
                    ),
                ),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42,
                        class_weight="balanced",
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X_train, y_train)

        # Validate
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\n📈 Model Performance:")
        print(f"   Accuracy: {accuracy:.2%}")
        print(f"\n{classification_report(y_test, y_pred, zero_division=0)}")

        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        print(f"\n✅ Model saved to {self.model_path}")

        return accuracy

    def predict(self, error_message: str) -> Dict:
        """Predict error category and suggest fix"""
        if not self.pipeline:
            if not self.model_path.exists():
                print("❌ Model not found. Run 'train' first.")
                sys.exit(1)
            self.pipeline = joblib.load(self.model_path)

        category = self.pipeline.predict([error_message])[0]
        probabilities = self.pipeline.predict_proba([error_message])[0]
        confidence = probabilities.max()

        # Get top 3 predictions
        top_3_indices = probabilities.argsort()[-3:][::-1]
        top_3_categories = [self.pipeline.classes_[i] for i in top_3_indices]
        top_3_confidences = [probabilities[i] for i in top_3_indices]

        suggested_fix = self._get_fix_suggestion(category)

        return {
            "category": category,
            "confidence": confidence,
            "suggested_fix": suggested_fix,
            "top_3": [
                {"category": cat, "confidence": conf}
                for cat, conf in zip(top_3_categories, top_3_confidences)
            ],
        }

    def _get_fix_suggestion(self, category: str) -> str:
        """Map category to fix suggestion"""
        fixes = {
            "dependency_missing": """
1. Add missing package to pyproject.toml dependencies
2. Run: pip install -e '.[all]'
3. Update requirements.txt if needed
4. Verify installation: python -c 'import <package>'
            """,
            "environment_variable": """
1. Add default value to workflow: ${{ vars.VAR || 'default' }}
2. Set GitHub repository variable: gh variable set VAR_NAME --body "value"
3. Update .env.example with required variables
4. Document in README.md or CONTRIBUTING.md
            """,
            "api_contract_mismatch": """
1. Fetch actual API response and inspect structure
2. Update test assertions to match actual response fields
3. Add OpenAPI spec validation if available
4. Consider versioning API endpoints
            """,
            "network_timeout": """
1. Increase timeout value in request
2. Check service availability: curl -v <endpoint>
3. Verify network connectivity and DNS resolution
4. Add retry logic with exponential backoff
            """,
            "permission_denied": """
1. Check file/directory permissions: ls -la
2. Verify GitHub Actions permissions in workflow file
3. Update GITHUB_TOKEN permissions if needed
4. Consider using chmod or chown as appropriate
            """,
            "configuration_error": """
1. Validate YAML syntax: yamllint <file>
2. Check for missing required fields
3. Verify indentation (use spaces, not tabs)
4. Consult schema documentation
            """,
            "syntax_error": """
1. Review Python syntax at indicated line
2. Check indentation consistency (4 spaces)
3. Verify parentheses, brackets, quotes are balanced
4. Run: python -m py_compile <file>
            """,
            "import_error": """
1. Verify module exists in expected location
2. Check __init__.py files in package hierarchy
3. Add module path to PYTHONPATH if needed
4. Avoid circular imports by refactoring
            """,
        }
        return fixes.get(
            category, "Manual investigation required. Review error logs for details."
        )

    def analyze_trends(self, history_file="data/error_history.json"):
        """Analyze error trends from history"""
        history_path = Path(history_file)
        if not history_path.exists():
            print(f"❌ Error history not found: {history_file}")
            return

        with open(history_path) as f:
            error_logs = json.load(f)

        df = pd.DataFrame(error_logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        print(f"\n📊 Error Trends Analysis ({len(error_logs)} total errors)\n")
        print("Top Error Categories:")
        print(df["category"].value_counts())

        print("\n\nErrors by Month:")
        df["month"] = df["timestamp"].dt.to_period("M")
        print(df.groupby("month")["category"].count())

        print("\n\nAuto-Fix Success Rate:")
        if "auto_fixed" in df.columns:
            success_rate = df["auto_fixed"].mean() * 100
            print(f"   {success_rate:.1f}% successfully auto-fixed")


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    detector = ErrorPatternDetector()
    command = sys.argv[1]

    if command == "train":
        # Load historical errors if available
        history_file = Path("data/error_history.json")
        if history_file.exists():
            with open(history_file) as f:
                error_logs = json.load(f)
            detector.train(error_logs)
        else:
            print("ℹ️  No error history found, using seed patterns")
            detector.train()

    elif command == "predict":
        if len(sys.argv) < 3:
            print("Usage: error_pattern_detector.py predict '<error_message>'")
            sys.exit(1)

        error_message = sys.argv[2]
        prediction = detector.predict(error_message)

        print(f"\n🔍 Error Analysis\n")
        print(f"📋 Category: {prediction['category']}")
        print(f"🎯 Confidence: {prediction['confidence']:.2%}\n")

        print(f"💡 Suggested Fix:")
        print(prediction["suggested_fix"])

        print(f"\n📊 Top 3 Predictions:")
        for i, pred in enumerate(prediction["top_3"], 1):
            print(f"   {i}. {pred['category']:25s} ({pred['confidence']:.1%})")

    elif command == "analyze":
        detector.analyze_trends()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
