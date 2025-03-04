# RadReportParser

<!-- badges: start -->
[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental) [![codecov](https://codecov.io/gh/Lightbridge-KS/radreportparser/graph/badge.svg?token=6W2CZHZ311)](https://codecov.io/gh/Lightbridge-KS/radreportparser)
<!-- badges: end -->


> **Parse and extract key sections from radiology reports text**

`radreportparser` is a Python package that helps you extract structured information from free-text radiology reports using regular expressions.


- **Package website:** <https://lightbridge-ks.github.io/radreportparser/>



## Key Features

- 📋 Extract common radiology report sections 
  - Included: Title, History, Technique, Comparison, Findings, and Impression
- 🔍 Flexible pattern matching with customizable section markers
- 🔄 Convert extracted sections to Python dictionaries or JSON

## Installation

Install the development version from GitHub:

```bash
python -m pip install git+https://github.com/Lightbridge-KS/radreportparser
```

## Quick Start

### Extract Report

Here's a simple example of extracting sections from a radiology report:

```python
from radreportparser import RadReportExtractor

# Sample brain CT report (note the markdown formatting)
report_text = """
EMERGENCY MDCT OF THE BRAIN

**HISTORY:** A 25-year-old female presents with headache. Physical examination reveals no focal neurological deficits.

TECHNIQUE: Axial helical scan of the brain performed with coronal and sagittal reconstructions.

*Comparison:* None.

Findings:
The brain shows age-appropriate volume with normal parenchymal attenuation and gray-white differentiation. No acute infarction or hemorrhage identified. The ventricles are normal in size without intraventricular hemorrhage. No extra-axial collection, midline shift, or brain herniation. The vascular structures appear normal. The calvarium and skull base show no fracture. Visualized paranasal sinuses, mastoids, and upper cervical spine are unremarkable.

**IMPRESSION**:
- No intracranial hemorrhage, acute large territorial infarction, extra-axial collection, midline shift, brain herniation, or skull fracture identified.
"""

# Initialize extractor and parse the report
extractor = RadReportExtractor()
report = extractor.extract_all(report_text)
report
```

**Access individual sections:**

```python
print(report.history)
```


### Convert to dictionary or JSON

```python
report.to_dict()
```

```python
report.to_json()
```


**Note:** The pattern matching mechanism can extract sections from text with plain text or markdown formatting. 

