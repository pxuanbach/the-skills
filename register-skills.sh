#!/bin/bash
# register-skills.sh - Register all skills from this repo to global agents
# Usage: ./register-skills.sh [--target pi|claude|all]
# Default: all targets

set -e

TARGET="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            TARGET="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--target pi|claude|all]"
            exit 1
            ;;
    esac
done

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE="${SCRIPT_DIR}/skills"

# Target directories
declare -A TARGETS
TARGETS["pi"]="$HOME/.pi/agent/skills"
TARGETS["claude"]="$HOME/.claude/skills"

# Filter targets
if [[ "$TARGET" == "all" ]]; then
    ACTIVE_TARGETS=("pi" "claude")
else
    ACTIVE_TARGETS=("$TARGET")
fi

echo "Registering skills from $SKILLS_SOURCE"

# Loop through all skill directories in the skills folder
for skill_dir in "$SKILLS_SOURCE"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")

        for target in "${ACTIVE_TARGETS[@]}"; do
            SKILLS_TARGET="${TARGETS[$target]}"

            echo -e "\n==> Target: $target ($SKILLS_TARGET)"

            # Create target directory if it doesn't exist
            if [ ! -d "$SKILLS_TARGET" ]; then
                echo "  Directory not found, creating..."
                mkdir -p "$SKILLS_TARGET" || {
                    echo "  Skipped: Cannot create directory"
                    continue
                }
            fi

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
        done
    fi
done

echo -e "\nDone!"
