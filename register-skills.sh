#!/bin/bash
# register-skills.sh - Register all skills from this repo to the global pi agent
# Usage: ./register-skills.sh

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="${SCRIPT_DIR}/skills"

# Target directory in pi agent
SKILLS_TARGET="$HOME/.pi/agent/skills"

# Verify source exists
if [ ! -d "$SKILLS_SOURCE" ]; then
    echo "Error: Skills directory not found at $SKILLS_SOURCE"
    exit 1
fi

# Verify target exists
if [ ! -d "$SKILLS_TARGET" ]; then
    echo "Error: Pi agent skills directory not found at $SKILLS_TARGET"
    echo "Please ensure pi agent is installed"
    exit 1
fi

echo "Registering skills from $SKILLS_SOURCE to $SKILLS_TARGET"

# Loop through all skill directories in the skills folder
for skill_dir in "$SKILLS_SOURCE"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        target_path="${SKILLS_TARGET}/${skill_name}"

        # Check if SKILL.md exists
        if [ -f "${skill_dir}/SKILL.md" ]; then
            # Remove existing symlink or directory if present
            if [ -L "$target_path" ]; then
                rm "$target_path"
                echo "  Updated: $skill_name (symlink)"
            elif [ -d "$target_path" ]; then
                echo "  Skipped: $skill_name (directory already exists)"
                continue
            fi

            # Create symlink
            ln -s "$skill_dir" "$target_path"
            echo "  Registered: $skill_name"
        else
            echo "  Skipped: $skill_name (no SKILL.md found)"
        fi
    fi
done

echo "Done!"
