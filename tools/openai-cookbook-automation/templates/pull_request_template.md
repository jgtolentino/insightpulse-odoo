## Summary

<!-- Briefly describe what this PR does and why -->

## Type of Change

- [ ] New example notebook
- [ ] Update to existing notebook
- [ ] Documentation update
- [ ] Bug fix
- [ ] Infrastructure/CI change

## Notebook Checklist (if applicable)

### Quality Checks
- [ ] Code runs without errors
- [ ] All cells execute successfully
- [ ] No hardcoded API keys or secrets
- [ ] Uses environment variables for sensitive data (e.g., `OPENAI_API_KEY`)
- [ ] Code follows Python best practices (PEP 8)
- [ ] Includes clear markdown explanations

### Metadata
- [ ] Added `cookbook` metadata to notebook:
  ```json
  {
    "metadata": {
      "cookbook": {
        "title": "Clear, Descriptive Title",
        "difficulty": "beginner|intermediate|advanced",
        "tags": ["tag1", "tag2"],
        "category": "chat|embeddings|fine-tuning|etc",
        "estimated_time": "15 minutes",
        "openai_models": ["gpt-4", "etc"],
        "prerequisites": ["Optional list"],
        "author": "Your Name (optional)",
        "last_updated": "2025-01-15 (optional)"
      }
    }
  }
  ```

### Documentation
- [ ] Includes "Overview" or introduction section
- [ ] Lists prerequisites (required knowledge, packages, setup)
- [ ] Includes usage instructions
- [ ] Has cleanup/teardown instructions (if applicable)
- [ ] Demonstrates one clear concept/use case

### Testing
- [ ] Tested locally with latest `openai` SDK
- [ ] Verified structure tests pass: `python tools/notebook_test_runner.py --mode structure --pattern "path/to/notebook.ipynb"`
- [ ] Verified metadata is valid: `python tools/notebook_metadata_validator.py --pattern "path/to/notebook.ipynb"`
- [ ] (Optional) Ran smoke test: `OPENAI_API_KEY=sk-... python tools/notebook_test_runner.py --mode smoke --pattern "path/to/notebook.ipynb"`

## OpenAI SDK Version

<!-- Which version did you test with? -->
- [ ] Latest (`pip install --upgrade openai`)
- [ ] Specific version: `openai==___`

## Related Issues

<!-- Link related issues -->
- Fixes #
- Related to #

## Screenshots / Examples

<!-- If applicable, add screenshots or example outputs -->

## Additional Notes

<!-- Any other context or information -->

---

## Pre-submission Checklist

Before submitting, please ensure:

- [ ] I have read the contribution guidelines
- [ ] My code follows the repository's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where needed
- [ ] I have tested the notebook end-to-end
- [ ] CI checks pass locally (structure + metadata validation)

---

**For Reviewers:**
- [ ] Notebook executes without errors
- [ ] Metadata is complete and accurate
- [ ] Code quality is good
- [ ] Documentation is clear
- [ ] Demonstrates valuable use case
