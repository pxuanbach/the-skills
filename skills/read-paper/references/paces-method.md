# The PACES Method — Detailed Reference

PACES (Purpose / Approach / Claims / Evaluation / Synthesis) is a five-letter framework for decomposing a research paper so the analysis captures both the **technical content** and the **higher-order contribution**. Each letter answers a different question; conflating them is the most common failure mode.

> **Load this file before drafting the output.** Vague PACES sections blur together — this file defines the boundaries.

---

## P — Purpose (The "Why")

**Question answered:** *What problem are the authors trying to solve, and why does it matter?*

### What to extract

- The **problem statement** — phrased as a gap or limitation in current work, not as the authors' solution.
- The **research gap** — what is missing in the prior literature that this paper fills.
- The **motivation** — usually framed as economic, social, scientific, or practical stakes.
- **Scope** — what the paper does *not* try to solve (often implicit).

### Key indicators (skim these phrases)

- *"This paper addresses…"*
- *"A critical challenge in [field] is…"*
- *"Existing methods are limited by…"*
- *"Despite recent progress in X, … remains an open problem."*
- *"To the best of our knowledge, no prior work has…"*

### Length guideline

1–3 paragraphs. If `P` exceeds half a page, it is drifting into Approach.

### Worked example (good)

> Transformer-based language models achieve strong performance on standard benchmarks but are limited by quadratic attention cost, restricting context length and increasing inference latency. This work addresses that limitation by proposing a linear-time attention mechanism that preserves the expressivity of softmax attention while reducing the cost of long-context inference.

### Worked example (bad — too vague)

> This paper is about transformers and makes them better.

---

## A — Approach (The "How")

**Question answered:** *What did the authors actually do, and what is novel about it?*

### What to extract

- **Method summary** — the technical mechanism, in your own words, not copy-pasted.
- **Novelty** — what is *new* versus *composed from existing pieces*. Most papers are compositions; state this directly.
- **Architecture / algorithm** — describe the workflow step-by-step.
- **Implementation choices** — anything that's load-bearing (loss function, optimizer, normalization, etc.).

### Key indicators (look in Method / Architecture / Algorithm sections)

- *"We propose…"*
- *"Our method consists of three components: …"*
- *"Unlike [prior work], which does X, we …"*
- Equation blocks — but only summarize them, don't reproduce.
- Architecture diagrams — these are usually the single most useful figure.

### Length guideline

2–4 paragraphs. Include the embedded architecture figure here.

### Worked example (good)

> The proposed Linear Attention Transformer (LAT) replaces softmax attention with a kernel feature map $\phi$ such that $\phi(x)\phi(y)^\top \approx \exp(x^\top y)$. This allows the attention matrix to be written as a product of two matrices, reducing both compute and memory from $O(n^2 d)$ to $O(n d^2)$. The kernel is a positive random feature (PRF) approximation of the Gaussian kernel, with feature dimension $D$ chosen to bound approximation error. The full architecture wraps LAT in standard transformer blocks (residual + LayerNorm + feed-forward), making it a drop-in replacement.

### Worked example (bad — too close to the paper)

> As shown in Equation 3, the proposed mechanism computes attention as $\text{softmax}(QK^\top)V$ which is replaced by $\phi(Q)(\phi(K)^\top V)$ where $\phi$ is defined in Equation 5…

*(Critique: this is a re-statement of the math, not a description of the approach. Don't paraphrase equations; describe the workflow.)*

---

## C — Claims (The "What")

**Question answered:** *What do the authors assert as the result of their work?*

### What to extract

- **Headline claims** — typically 2–5 strong statements about what was achieved.
- **Quantitative claims** — include the numbers: "Achieves 15% efficiency improvement", "Outperforms prior SOTA by 3.2 points on GLUE".
- **Qualitative claims** — "First method to do X", "Provides a theoretical guarantee that …".
- **Scope of claims** — on which datasets, under which conditions, with which models.

### Key indicators (look in Abstract, Introduction tail, Conclusion head)

- *"We demonstrate that …"*
- *"Our results show …"*
- *"To our knowledge, this is the first …"*
- The **headline table** — usually the largest results table near the end of the experiments section.

### Length guideline

1–3 paragraphs. Use bulleted lists for multiple quantified claims.

### Worked example (good)

> The authors claim three primary results: (1) LAT matches softmax attention accuracy on language modeling (perplexity within 0.5% on WikiText-103) while reducing training time by 1.5× at sequence length 4096; (2) the same model scales to 16k context without OOM on a single GPU where softmax baselines require 4× the memory; (3) ablations confirm the kernel feature dimension D is the primary accuracy knob, with D=256 saturating performance.

### Worked example (bad — claims mixed with evidence)

> Our method achieves 15% efficiency gain because we used a 1.5× faster kernel and a smaller batch size and trained on more data for 100 epochs on 4 GPUs.

*(Critique: This mixes the claim with the experimental setup. Move the "trained on 4 GPUs, 100 epochs" to `E`.)*

---

## E — Evaluation (The "Proof")

**Question answered:** *How did the authors prove their claims? How rigorous is the evidence?*

### What to extract

- **Datasets** — name, size, source. Distinguish standard benchmarks vs. custom datasets.
- **Baselines** — which prior methods are compared. Are they strong? Recent? Properly tuned?
- **Metrics** — Accuracy, F1, BLEU, perplexity, latency, throughput, human eval, etc.
- **Hardware / software environment** — GPU type, framework, batch size.
- **Ablations** — which components are isolated and tested?
- **Statistical rigor** — confidence intervals, seed counts, hypothesis tests. Many papers are silent on this; say so.
- **Honest reporting** — where do the authors admit their method does *not* work?

### Key indicators

- Tables titled *"Comparison with state-of-the-art"*, *"Ablation study"*, *"Effect of …"*.
- Appendix sections titled *"Implementation details"*, *"Hyperparameters"*.
- Plots with error bars vs. plots without — note which.

### Length guideline

2–5 paragraphs. This is the only letter where tables and bullet lists are appropriate inside the prose.

### Worked example (good)

> The authors evaluate on three language modeling benchmarks (WikiText-103, Enwik8, LM1B) and one translation benchmark (WMT'14 En-De). Baselines include the vanilla Transformer (Vaswani et al., 2017), Performer, Linear Transformer, and Reformer. All models are trained from the same initialization recipe and matched parameter counts (~125M). The headline table reports test perplexity at convergence: LAT matches vanilla at short context (≤1k tokens) and outperforms all baselines at ≥4k tokens, with the gap widening as context grows. Ablations show that the PRF kernel dimension D has a sharp knee at D≈64, with diminishing returns above D=256. The authors do not report variance across seeds — a notable gap, especially given the stochasticity of PRF sampling.

### Worked example (bad — only numbers, no analysis)

> LAT got 18.4 perplexity on WikiText-103. Performer got 22.1. Reformer got 24.0. Vanilla got 17.9.

*(Critique: this is a table excerpt, not evaluation analysis. Add interpretation: are baselines recent? Were they tuned? What's missing?)*

---

## S — Synthesis (The "Big Picture")

**Question answered:** *What does this paper mean for the field, and what should the reader do with it?*

### What to extract

- **Significance** — is this an incremental improvement, a paradigm shift, or a niche refinement?
- **Relationship to prior work** — does it confirm, contradict, or extend prior findings?
- **Practical applications** — who would actually deploy this? In what setting?
- **Limitations acknowledged by the authors** — usually in the Discussion or Conclusion.
- **Future work suggested** — either explicit ("we leave X to future work") or implicit (open questions).
- **Your own take** — would you cite this paper? Build on it? Avoid it?

### Key indicators

- *"Despite these results, our method has limitations …"*
- *"Future work could …"*
- Discussion section header
- Conclusion paragraph(s)
- Limitation / Broader Impact sections (more common in newer venues)

### Length guideline

1–3 paragraphs. This is the only letter where your own perspective belongs — provide a take, not just a summary.

### Worked example (good)

> LAT is best understood not as a replacement for softmax attention but as evidence that the softmax is over-engineered for many practical workloads: the paper's strongest gains appear exactly where softmax is most expensive (long context, large batches), and its weakest gains appear at short context where softmax is already cheap. For practitioners, this is a strong reason to switch at ≥4k context but a weak reason to switch at 1k. The PRF approximation is the load-bearing trick — if a follow-up work can replace PRF with a deterministic kernel of similar quality, the practical case for LAT strengthens considerably. The authors are candid about two limitations: (1) the PRF approximation is stochastic and adds variance to training, and (2) the feature dimension D adds memory overhead that partially offsets the attention savings. The follow-up most worth reading is likely Katharopoulos et al.'s linear attention paper, which the LAT authors compare against but which arrived earlier — the relationship between LAT and that work deserves a careful second look.

### Worked example (bad — just restating)

> LAT is a new method. It improves on transformers. It is fast. It may be useful in the future.

*(Critique: this is content-free. Synthesis is where you earn your reading time.)*

---

## Common pitfalls across all letters

| Pitfall | Why it's wrong |
|---|---|
| Conflating `A` and `E` | Approach = what they did. Evaluation = how they proved it. Same data, different question. |
| Bulletizing the whole PACES | Each letter is paragraph-driven analysis. Use bullets only inside `E` for tables. |
| Quoting the paper verbatim | The user can read the paper. Your job is to *explain*, not to copy. |
| Skipping `S` | The "so what" is what a colleague would actually want from your analysis. |
| Padding with filler | A short, sharp analysis beats a long, vague one every time. If a letter is one paragraph, that's fine. |

---

## Quick self-check before saving

- [ ] `P` says why the paper exists, not what it does.
- [ ] `A` describes the method in *my own words*, not the paper's.
- [ ] `C` lists quantified claims with their conditions.
- [ ] `E` names baselines, datasets, ablations, and statistical rigor (or its absence).
- [ ] `S` has a take, not just a restatement.
- [ ] At least one figure is embedded (architecture or big-picture).
- [ ] `memory_links.applicable_to` links to a concrete user project or question; `used` and `follow_up` populated if relevant, or marked `none` with reason.
