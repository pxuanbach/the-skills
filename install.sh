#!/usr/bin/env bash
# install.sh - Interactive remote skill installer for coding agents
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/pxuanbach/the-skills/main/install.sh | bash
# Or:
#   ./install.sh [--targets pi,claude,antigravity,all] [--skills wiki-manager,constructor,all]

set -e

REPO_OWNER="pxuanbach"
REPO_NAME="the-skills"
BRANCH="main"

# Color helpers
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m'

# Fallback skills
FALLBACK_SKILLS=(
  "constructor"
  "quality-reviewer"
  "requirement-analyzer"
  "research-workflow"
  "review-skill"
  "screenshot"
  "security-reviewer"
  "user-designer"
  "wiki-manager"
)

# Parse args
CLI_TARGETS=""
CLI_SKILLS=""

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --targets) CLI_TARGETS="$2"; shift ;;
    --skills) CLI_SKILLS="$2"; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

get_target_path() {
  case "$1" in
    pi) echo "$HOME/.pi/agent/skills" ;;
    claude) echo "$HOME/.claude/skills" ;;
    antigravity) echo "$HOME/.gemini/config/skills" ;;
    *) echo "" ;;
  esac
}

get_target_name() {
  case "$1" in
    pi) echo "Pi Agent" ;;
    claude) echo "Claude Code" ;;
    antigravity) echo "Antigravity / Gemini CLI" ;;
    *) echo "$1" ;;
  esac
}

# Fetch remote skill list
fetch_skills() {
  local list
  list=$(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/contents/skills" 2>/dev/null | grep '"name":' | grep -v 'skills' | sed -E 's/.*"name": "([^"]+)".*/\1/' || true)
  if [ -n "$list" ]; then
    echo "$list"
  else
    printf "%s\n" "${FALLBACK_SKILLS[@]}"
  fi
}

download_skill() {
  local skill="$1"
  local dest_dir="$2"
  local target_path="$dest_dir/$skill"
  
  mkdir -p "$target_path"
  echo -e "  -> Installing '${CYAN}$skill${NC}'..."

  # Fetch tree for all files in skill
  local tree_json
  tree_json=$(curl -s "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/git/trees/$BRANCH?recursive=1" 2>/dev/null || true)
  local files
  files=$(echo "$tree_json" | grep -o "\"skills/$skill/[^\"]*\"" | tr -d '"' || true)

  if [ -z "$files" ]; then
    files="skills/$skill/SKILL.md"
  fi

  for file in $files; do
    local subpath="${file#skills/$skill/}"
    local dest_file="$target_path/$subpath"
    mkdir -p "$(dirname "$dest_file")"
    curl -sSL "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/$file" -o "$dest_file"
  done
  echo -e "    ${GREEN}[OK] Installed $skill${NC}"
}

echo -e "${CYAN}==========================================================${NC}"
echo -e "${YELLOW}         AI Agent Skills Installer ($REPO_NAME)           ${NC}"
echo -e "${CYAN}==========================================================${NC}\n"

# 1. Target Agent Selection
CHOSEN_TARGETS=()
if [ -n "$CLI_TARGETS" ]; then
  if [ "$CLI_TARGETS" = "all" ]; then
    CHOSEN_TARGETS=("pi" "claude" "antigravity")
  else
    IFS=',' read -ra ADDR <<< "$CLI_TARGETS"
    for i in "${ADDR[@]}"; do CHOSEN_TARGETS+=("$(echo "$i" | tr -d ' ')"); done
  fi
else
  echo -e "${YELLOW}1. Select Coding Agent(s) to install skills to:${NC}"
  echo "  [1] Pi Agent (~/.pi/agent/skills)"
  echo "  [2] Claude Code (~/.claude/skills)"
  echo "  [3] Antigravity / Gemini CLI (~/.gemini/config/skills)"
  echo "  [A] All Agents"
  echo ""
  read -p "Enter selections separated by comma (e.g. 1,2) [default: A]: " target_input < /dev/tty || target_input="A"
  target_input="${target_input:-A}"

  if [[ "$target_input" =~ ^[Aa]$ ]]; then
    CHOSEN_TARGETS=("pi" "claude" "antigravity")
  else
    IFS=',' read -ra ADDR <<< "$target_input"
    for choice in "${ADDR[@]}"; do
      case "$(echo "$choice" | tr -d ' ')" in
        1) CHOSEN_TARGETS+=("pi") ;;
        2) CHOSEN_TARGETS+=("claude") ;;
        3) CHOSEN_TARGETS+=("antigravity") ;;
      esac
    done
  fi
fi

if [ ${#CHOSEN_TARGETS[@]} -eq 0 ]; then
  echo -e "${YELLOW}No agent target selected. Exiting.${NC}"
  exit 0
fi

# 2. Skill Selection
ALL_SKILLS=()
while IFS= read -r line; do
  [ -n "$line" ] && ALL_SKILLS+=("$line")
done < <(fetch_skills)

CHOSEN_SKILLS=()
if [ -n "$CLI_SKILLS" ]; then
  if [ "$CLI_SKILLS" = "all" ]; then
    CHOSEN_SKILLS=("${ALL_SKILLS[@]}")
  else
    IFS=',' read -ra ADDR <<< "$CLI_SKILLS"
    for i in "${ADDR[@]}"; do CHOSEN_SKILLS+=("$(echo "$i" | tr -d ' ')"); done
  fi
else
  echo -e "\n${YELLOW}2. Select Skill(s) to download and install:${NC}"
  for i in "${!ALL_SKILLS[@]}"; do
    printf "  [%2d] %s\n" "$((i+1))" "${ALL_SKILLS[$i]}"
  done
  echo "  [ A] All Skills"
  echo ""
  read -p "Enter skill numbers separated by comma (e.g. 1,3,9) [default: A]: " skill_input < /dev/tty || skill_input="A"
  skill_input="${skill_input:-A}"

  if [[ "$skill_input" =~ ^[Aa]$ ]]; then
    CHOSEN_SKILLS=("${ALL_SKILLS[@]}")
  else
    IFS=',' read -ra ADDR <<< "$skill_input"
    for choice in "${ADDR[@]}"; do
      num="$(echo "$choice" | tr -d ' ')"
      if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#ALL_SKILLS[@]}" ]; then
        CHOSEN_SKILLS+=("${ALL_SKILLS[$((num-1))]}")
      fi
    done
  fi
fi

if [ ${#CHOSEN_SKILLS[@]} -eq 0 ]; then
  echo -e "${YELLOW}No skills selected. Exiting.${NC}"
  exit 0
fi

echo -e "\n${YELLOW}Starting Installation...${NC}"
echo -e "${GRAY}Selected Skills: ${CHOSEN_SKILLS[*]}${NC}\n"

for target in "${CHOSEN_TARGETS[@]}"; do
  dest="$(get_target_path "$target")"
  name="$(get_target_name "$target")"
  echo -e "${MAGENTA}==> Target: $name ($dest)${NC}"
  mkdir -p "$dest"
  for skill in "${CHOSEN_SKILLS[@]}"; do
    download_skill "$skill" "$dest"
  done
  echo ""
done

echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${CYAN}Restart or refresh your coding agent to load the new skills.${NC}\n"
