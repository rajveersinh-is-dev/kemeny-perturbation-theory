# Manuscript Build Instructions

This directory contains the complete scholarly manuscript prepared for submission to *Information and Inference: A Journal of the IMA* (Oxford University Press).

## Files
- `main.tex`: Complete LaTeX source file.
- `references.bib`: Verified BibTeX database containing primary literature references with DOIs.
- `main.pdf`: Compiled publication-quality PDF manuscript.

## Compilation Instructions

### Using Tectonic (Recommended, self-contained)
To compile the manuscript with Tectonic:
```bash
tectonic main.tex
```
Tectonic automatically resolves packages, runs BibTeX passes, and generates `main.pdf`.

### Using standard pdflatex / latexmk
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```
or
```bash
latexmk -pdf main.tex
```

## Manuscript Metadata
- **Title:** Exact Rational Perturbation Theory, Monotonicity Phase Transitions, and Fast All-Pairs Optimization for Kemeny's Constant in Complex Networks
- **Author:** Rajveersinh Vishal Pardeshi
- **Affiliation:** Independent Researcher
- **Target Journal:** *Information and Inference: A Journal of the IMA* (Oxford University Press)
- **Publishing Route:** Standard Subscription License (Zero mandatory author publication fee)
- **DOI:** [10.5281/zenodo.23572394](https://doi.org/10.5281/zenodo.23572394)
- **License:** Creative Commons Attribution 4.0 International (CC-BY 4.0)
