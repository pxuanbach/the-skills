# How to read one paper

## Input parameters

- Memory (brain): Ask user to provide MEMORY.md OR search the context in current workspace (AGENTS.md, CLAUDE.md, SYSTEM.md, docs/*). MEMORY.md is your knowlegde in the domain/fields that the paper content was written, agent read and know what's your need? / what's your attention? / what can you use yourself?
- Output dir: If user provides specific directory where to store the output - follow it. Otherwise, use `docs/paper_summary/` to store the output.

## Don't start from the first page and finish at last one

Read it in multiple passes

Phase 1: Read the title, abstract, and illustrations. In the fields of AI and Deep Learning, many papers can be summarized in just one or two figures!

Phase 2: Focus on the Introduction and Conclusion, review the figures, and skim through the remaining sections.
These two sections usually provide the most accurate overview of the paper's content and key contributions.

Phase 3: Read the entire paper, skipping the mathematical sections at the beginning if necessary. You can revisit them later if you need a deeper understanding.

Phase 4: Read whatever sections you need, but do not try to understand everything immediately. Not every part of cutting-edge research papers is important or easy to grasp—sometimes not even for the authors themselves.

## Try to answer while reading a paper

- What did the author try to accomplish here?
- Key elements of the approach?
- What can you use yourself? -&gt; references to MEMORY.md to answer
- What other references do you want to follow? -&gt; references to MEMORY.md to answer

## What is the OUTPUT?

### Core method

Summarize paper follow PACES Method. 

The PACES Method: A Framework for Research Paper Analysis The PACES framework is designed to help researchers systematically deconstruct scientific papers, ensuring a deep understanding of both technical depth and high-level contributions. 

1. P – Purpose (The "Why")
  - Identify the core problem the authors are trying to solve and its significance. 
  - Focus: Problem statement, research gaps, and motivation. 
  - Key Indicators: Phrases like "This paper addresses...", "A critical challenge in...", or "Existing methods are limited by..." 
  - Goal: Understand the "pain point" in the current landscape that necessitates this research.
2. A – Approach (The "How")
  - Examine the proposed solution and how it diverges from existing state-of-the-art methods. 
  - Focus: Technical methodology, system architecture, algorithms, and implementation details. 
  - Analysis: Look for the novelty—is it a new architecture, a more efficient algorithm, or a unique combination of existing tools? 
  - Execution: Summarize the workflow concisely, focusing on the core logic.
3. C – Claims (The "What")
  - Identify the specific assertions made by the authors based on their scientific findings. 
  - Types of Claims: Performance breakthroughs, novel capabilities, theoretical contributions, or empirical discoveries. 
  - Evidence Location: Found in experimental results, mathematical proofs, and comparative tables. 
  - Requirement: State these claims clearly and highlight the most impactful results (e.g., "Achieved a 15% increase in efficiency").
4. E – Evaluation (The "Proof")
  - Critically assess the validity of the claims through the lens of the experiments. 
  - Experimental Setup: Datasets used, hardware/software environment, and parameters. 
  - Metrics &amp; Baselines: What KPIs (e.g., Accuracy, Latency, Throughput) were measured, and which existing models were used for comparison?
  - Validation: Look for statistical significance, hypothesis testing, and ablation studies (to see which part of the approach actually matters).
  - This section requires specific comparative indicators and evaluation results, rather than hypothetical terminology.
5. S – Synthesis (The "Big Picture")
  - Connect the paper to the broader field and evaluate its long-term impact. 
  - Focus: Overall significance, relationship to related works, and practical applications. 
  - Future Work: Identify the limitations admitted by the authors and the suggested next steps for the research community. 
  - Source: Primarily found in the Introduction, Discussion, and Conclusion sections.

### Output format

Markdown / HTML depends on user input. Default is Markdown.

Template:

```markdown
---
title: Paper name
description: short description about paper content, topic, domain
published_year: 2026
author: <list of authors>
domain: <list of domains in which the article's content is written.>
keywords: <list of keywords mentioned in the article content>
---

1. P – Purpose (The "Why") 
<paragraphs>

2. A – Approach (The "How") 
<paragraphs>

<an image to demonstrate proposed solution>

3. C – Claims (The "What")
<paragraphs>

4. E – Evaluation (The "Proof") 
<paragraph & metrics & charts>

5. S – Synthesis (The "Big Picture") 
<paragraph>

<a diagram to show the "Big Picture">

```

