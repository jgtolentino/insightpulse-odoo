#!/bin/bash

# Create symlinks for all Skills in .claude/skills/
find docs/claude-code-skills -name "SKILL.md" -exec dirname {} \; | while read skill_dir; do
  skill_name=$(basename "$skill_dir")
  ln -sf "../../$skill_dir" ".claude/skills/$skill_name"
  echo "Linked: $skill_name"
done

echo "Done! All skills linked to .claude/skills/"
