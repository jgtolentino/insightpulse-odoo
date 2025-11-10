#!/usr/bin/env python3

"""
Generate comprehensive report on repository structure health.
"""

import json
from datetime import datetime
from pathlib import Path


class StructureHealthReport:
    """
    Generate health metrics for repository structure.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def generate_report(self) -> dict:
        """Generate complete health report."""

        return {
            "timestamp": datetime.now().isoformat(),
            "repository": str(self.repo_path.absolute()),
            "metrics": {
                "structure_compliance": self.check_structure_compliance(),
                "documentation_coverage": self.check_documentation_coverage(),
                "test_coverage": self.check_test_coverage(),
                "skill_maturity": self.check_skill_maturity(),
                "automation_level": self.check_automation_level(),
                "ci_cd_health": self.check_cicd_health(),
            },
            "scores": {},  # Will be populated by calculate_scores
            "recommendations": [],  # Will be populated by generate_recommendations
        }

    def check_structure_compliance(self) -> dict:
        """Check how well structure matches specification."""

        required_dirs = [
            ".github/workflows",
            "docs/architecture",
            "docs/knowledge-base",
            "docs/runbooks",
            "skills/core",
            "custom",
            "addons",
            "infrastructure/docker",
            "tests/ai",
            "tests/integration",
            "prompts/templates",
            "scripts/setup",
            "scripts/deployment",
        ]

        required_files = [
            "README.md",
            "Makefile",
            "docker-compose.yml",
            ".gitignore",
            "requirements.txt",
        ]

        existing_dirs = sum(1 for d in required_dirs if (self.repo_path / d).exists())
        existing_files = sum(1 for f in required_files if (self.repo_path / f).exists())

        return {
            "directories": {
                "required": len(required_dirs),
                "existing": existing_dirs,
                "percentage": (existing_dirs / len(required_dirs) * 100),
            },
            "files": {
                "required": len(required_files),
                "existing": existing_files,
                "percentage": (existing_files / len(required_files) * 100),
            },
            "overall_percentage": (
                (existing_dirs + existing_files)
                / (len(required_dirs) + len(required_files))
                * 100
            ),
        }

    def check_documentation_coverage(self) -> dict:
        """Check documentation completeness."""

        major_dirs = [
            "skills",
            "prompts",
            "evals",
            "tests",
            "monitoring",
            "custom",
            "infrastructure",
            "scripts",
        ]
        existing_major_dirs = [d for d in major_dirs if (self.repo_path / d).exists()]

        if not existing_major_dirs:
            return {"readme_coverage": 0, "code_documentation": 0, "total_md_files": 0}

        dirs_with_readme = sum(
            1
            for d in existing_major_dirs
            if (self.repo_path / d / "README.md").exists()
        )

        # Count Python files with docstrings
        py_files = list(self.repo_path.glob("scripts/**/*.py")) + list(
            self.repo_path.glob("tests/**/*.py")
        )
        total_py_files = len(py_files)
        documented_py_files = 0

        for py_file in py_files:
            try:
                with open(py_file) as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        documented_py_files += 1
            except:
                pass

        # Count total markdown files
        md_files = len(list(self.repo_path.glob("**/*.md")))

        return {
            "readme_coverage": (
                (dirs_with_readme / len(existing_major_dirs) * 100)
                if existing_major_dirs
                else 0
            ),
            "code_documentation": (
                (documented_py_files / total_py_files * 100)
                if total_py_files > 0
                else 0
            ),
            "total_md_files": md_files,
            "major_dirs_with_readme": dirs_with_readme,
            "major_dirs_total": len(existing_major_dirs),
        }

    def check_test_coverage(self) -> dict:
        """Check test coverage."""

        tests_dir = self.repo_path / "tests"

        if not tests_dir.exists():
            return {
                "test_files": 0,
                "total_files": 0,
                "test_ratio": 0,
                "target": 80,
                "status": "needs_improvement",
            }

        test_files = len(list(tests_dir.glob("**/*.py")))

        # Count Python files in scripts and custom modules
        total_py_files = 0
        if (self.repo_path / "scripts").exists():
            total_py_files += len(list((self.repo_path / "scripts").glob("**/*.py")))
        if (self.repo_path / "custom").exists():
            total_py_files += len(list((self.repo_path / "custom").glob("**/*.py")))

        # Rough estimation: test ratio
        test_ratio = (test_files / total_py_files * 100) if total_py_files > 0 else 0

        return {
            "test_files": test_files,
            "total_files": total_py_files,
            "test_ratio": test_ratio,
            "target": 80,
            "status": "good" if test_ratio >= 80 else "needs_improvement",
        }

    def check_skill_maturity(self) -> dict:
        """Check skills completeness."""

        skills_dir = self.repo_path / "skills"

        if not skills_dir.exists():
            return {"total_skills": 0, "mature_skills": 0, "maturity_rate": 0}

        skill_files = list(skills_dir.glob("**/SKILL.md"))

        mature_skills = 0
        for skill_file in skill_files:
            try:
                with open(skill_file) as f:
                    content = f.read()

                # Check maturity criteria
                has_examples = "example" in content.lower()
                has_competencies = (
                    "## Core Competencies" in content or "## Purpose" in content
                )
                has_validation = (
                    "## Validation" in content
                    or "## Success Metrics" in content
                    or len(content) > 500
                )

                if has_examples and has_competencies and has_validation:
                    mature_skills += 1
            except:
                pass

        return {
            "total_skills": len(skill_files),
            "mature_skills": mature_skills,
            "maturity_rate": (
                (mature_skills / len(skill_files) * 100) if skill_files else 0
            ),
        }

    def check_automation_level(self) -> dict:
        """Check how much is automated."""

        workflows_dir = self.repo_path / ".github" / "workflows"
        github_workflows = (
            len(list(workflows_dir.glob("*.yml"))) if workflows_dir.exists() else 0
        )

        makefile_targets = 0
        makefile = self.repo_path / "Makefile"
        if makefile.exists():
            try:
                with open(makefile) as f:
                    makefile_targets = len(
                        [
                            l
                            for l in f
                            if l.strip()
                            and ":" in l
                            and not l.startswith("#")
                            and not l.startswith("\t")
                        ]
                    )
            except:
                pass

        scripts_dir = self.repo_path / "scripts"
        scripts = len(list(scripts_dir.glob("**/*.sh"))) if scripts_dir.exists() else 0

        # Calculate automation score (out of 100)
        automation_score = min(
            100, (github_workflows * 10 + makefile_targets * 2 + scripts * 3)
        )

        return {
            "github_workflows": github_workflows,
            "makefile_targets": makefile_targets,
            "automation_scripts": scripts,
            "automation_score": automation_score,
        }

    def check_cicd_health(self) -> dict:
        """Check CI/CD pipeline health."""

        workflows_dir = self.repo_path / ".github" / "workflows"

        if not workflows_dir.exists():
            return {
                "total_workflows": 0,
                "required_workflows": 4,
                "existing_required": 0,
                "health": "poor",
            }

        workflows = list(workflows_dir.glob("*.yml"))

        required_workflows = [
            "ci",
            "test",
            "deploy",
            "security",
        ]

        existing = sum(
            1 for w in workflows if any(r in w.stem.lower() for r in required_workflows)
        )

        health = (
            "good"
            if existing >= len(required_workflows)
            else "needs_work" if existing >= 2 else "poor"
        )

        return {
            "total_workflows": len(workflows),
            "required_workflows": len(required_workflows),
            "existing_required": existing,
            "health": health,
        }

    def calculate_scores(self, metrics: dict) -> dict:
        """Calculate overall scores."""

        # Calculate weighted score
        weights = {
            "structure": 0.3,
            "documentation": 0.2,
            "testing": 0.2,
            "skills": 0.15,
            "automation": 0.15,
        }

        scores = {
            "structure": metrics["structure_compliance"]["overall_percentage"],
            "documentation": metrics["documentation_coverage"]["readme_coverage"],
            "testing": min(100, metrics["test_coverage"]["test_ratio"]),
            "skills": metrics["skill_maturity"]["maturity_rate"],
            "automation": min(100, metrics["automation_level"]["automation_score"]),
        }

        overall = sum(scores[k] * weights[k] for k in weights)

        return {
            "individual": scores,
            "overall": overall,
            "grade": self.get_grade(overall),
        }

    def get_grade(self, score: float) -> str:
        """Convert score to letter grade."""

        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def generate_recommendations(self, metrics: dict) -> list:
        """Generate recommendations based on metrics."""

        recommendations = []

        # Structure recommendations
        if metrics["structure_compliance"]["overall_percentage"] < 90:
            recommendations.append(
                {
                    "priority": "high",
                    "area": "structure",
                    "recommendation": "Complete missing directory structure",
                    "action": "Create missing directories from required structure list",
                }
            )

        # Documentation recommendations
        if metrics["documentation_coverage"]["readme_coverage"] < 80:
            recommendations.append(
                {
                    "priority": "medium",
                    "area": "documentation",
                    "recommendation": "Add README files to major directories",
                    "action": "Create README.md in directories missing documentation",
                }
            )

        # Testing recommendations
        if metrics["test_coverage"]["test_ratio"] < 50:
            recommendations.append(
                {
                    "priority": "high",
                    "area": "testing",
                    "recommendation": "Increase test coverage significantly",
                    "action": "Add more tests in tests/ directory",
                }
            )

        # Skills recommendations
        if metrics["skill_maturity"]["total_skills"] < 5:
            recommendations.append(
                {
                    "priority": "medium",
                    "area": "skills",
                    "recommendation": "Add more skills to improve AI agent capabilities",
                    "action": "Create skill definitions in skills/ directory",
                }
            )

        # Automation recommendations
        if metrics["automation_level"]["automation_score"] < 50:
            recommendations.append(
                {
                    "priority": "medium",
                    "area": "automation",
                    "recommendation": "Increase automation with more scripts and workflows",
                    "action": "Add GitHub Actions workflows and Makefile targets",
                }
            )

        # CI/CD recommendations
        if metrics["ci_cd_health"]["health"] != "good":
            recommendations.append(
                {
                    "priority": "high",
                    "area": "ci_cd",
                    "recommendation": "Improve CI/CD pipeline with essential workflows",
                    "action": "Add workflows for CI, testing, deployment, and security",
                }
            )

        return recommendations


def main():
    reporter = StructureHealthReport()

    # Generate report
    report = reporter.generate_report()

    # Calculate scores
    report["scores"] = reporter.calculate_scores(report["metrics"])

    # Generate recommendations
    report["recommendations"] = reporter.generate_recommendations(report["metrics"])

    # Print report
    print("\n" + "=" * 60)
    print("REPOSITORY STRUCTURE HEALTH REPORT")
    print("=" * 60 + "\n")

    print(
        f"Overall Score: {report['scores']['overall']:.1f}% (Grade: {report['scores']['grade']})"
    )
    print()

    print("Individual Scores:")
    for area, score in report["scores"]["individual"].items():
        bar_length = int(score / 5)  # Scale to 20 chars
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {area.capitalize():15} {bar} {score:.1f}%")
    print()

    # Detailed metrics
    print("Detailed Metrics:")
    print(f"  Structure:")
    print(
        f"    • Directories: {report['metrics']['structure_compliance']['directories']['existing']}/{report['metrics']['structure_compliance']['directories']['required']}"
    )
    print(
        f"    • Files: {report['metrics']['structure_compliance']['files']['existing']}/{report['metrics']['structure_compliance']['files']['required']}"
    )

    print(f"  Documentation:")
    print(
        f"    • README coverage: {report['metrics']['documentation_coverage']['readme_coverage']:.1f}%"
    )
    print(
        f"    • Code documentation: {report['metrics']['documentation_coverage']['code_documentation']:.1f}%"
    )
    print(
        f"    • Total MD files: {report['metrics']['documentation_coverage']['total_md_files']}"
    )

    print(f"  Testing:")
    print(f"    • Test files: {report['metrics']['test_coverage']['test_files']}")
    print(f"    • Test ratio: {report['metrics']['test_coverage']['test_ratio']:.1f}%")

    print(f"  Skills:")
    print(f"    • Total skills: {report['metrics']['skill_maturity']['total_skills']}")
    print(
        f"    • Mature skills: {report['metrics']['skill_maturity']['mature_skills']}"
    )

    print(f"  Automation:")
    print(
        f"    • GitHub workflows: {report['metrics']['automation_level']['github_workflows']}"
    )
    print(
        f"    • Makefile targets: {report['metrics']['automation_level']['makefile_targets']}"
    )
    print(
        f"    • Automation scripts: {report['metrics']['automation_level']['automation_scripts']}"
    )
    print()

    if report["recommendations"]:
        print("Recommendations:")
        for rec in report["recommendations"]:
            priority_symbol = "🔴" if rec["priority"] == "high" else "🟡"
            print(
                f"\n  {priority_symbol} [{rec['priority'].upper()}] {rec['area'].upper()}"
            )
            print(f"     {rec['recommendation']}")
            print(f"     → {rec['action']}")
    else:
        print("✅ No recommendations - structure is healthy!")

    print()

    # Save to file
    output_file = "structure-health-report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📊 Full report saved to: {output_file}")


if __name__ == "__main__":
    main()
