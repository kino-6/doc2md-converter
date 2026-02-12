# Heading Level Offset Feature

## Overview

The heading level offset feature allows users to adjust all heading levels in the converted Markdown output by a specified offset value. This is useful when embedding converted documents into larger documents where you need to shift heading hierarchy.

**Requirements**: 8.1

## How It Works

The `heading_offset` configuration parameter adjusts all heading levels by adding (or subtracting) the offset value:

- **Positive offset**: Increases heading levels (H1 → H2, H2 → H3, etc.)
- **Negative offset**: Decreases heading levels (H2 → H1, H3 → H2, etc.)
- **Zero offset** (default): No change to heading levels

### Level Clamping

Heading levels are automatically clamped to the valid Markdown range (H1-H6):

- Minimum level: H1 (level 1)
- Maximum level: H6 (level 6)

Examples:
- H5 with offset +2 → H6 (clamped, not H7)
- H1 with offset -2 → H1 (clamped, not H-1)

## Usage

### Command Line

Use the `--heading-offset` option:

```bash
# Increase all headings by 1 level
doc2md -i document.docx -o output.md --heading-offset 1

# Decrease all headings by 1 level
doc2md -i document.docx -o output.md --heading-offset -1

# No offset (default)
doc2md -i document.docx -o output.md --heading-offset 0
```

### Configuration File

Add `heading_offset` to your YAML configuration file:

```yaml
# config.yaml
heading_offset: 1  # Increase all headings by 1 level
table_style: standard
include_metadata: false
output_encoding: utf-8
```

Then use the config file:

```bash
doc2md -i document.docx -o output.md -c config.yaml
```

### Python API

```python
from src.config import ConversionConfig
from src.conversion_orchestrator import ConversionOrchestrator
from src.logger import Logger, LogLevel

# Create config with heading offset
config = ConversionConfig(
    input_path="document.docx",
    output_path="output.md",
    heading_offset=1  # Increase all headings by 1 level
)

# Create orchestrator and convert
logger = Logger(log_level=LogLevel.INFO)
orchestrator = ConversionOrchestrator(config, logger)
result = orchestrator.convert("document.docx")
```

## Examples

### Example 1: Positive Offset

**Input document** (Word/PDF/Excel):
```
# Main Title
## Section 1
### Subsection 1.1
## Section 2
```

**With `heading_offset=1`**:
```markdown
## Main Title
### Section 1
#### Subsection 1.1
### Section 2
```

### Example 2: Negative Offset

**Input document**:
```
## Section Title
### Subsection
#### Sub-subsection
```

**With `heading_offset=-1`**:
```markdown
# Section Title
## Subsection
### Sub-subsection
```

### Example 3: Clamping at Upper Bound

**Input document**:
```
#### Level 4
##### Level 5
###### Level 6
```

**With `heading_offset=2`**:
```markdown
###### Level 4
###### Level 5
###### Level 6
```

All headings are clamped to H6 (maximum level).

### Example 4: Clamping at Lower Bound

**Input document**:
```
# Level 1
## Level 2
### Level 3
```

**With `heading_offset=-2`**:
```markdown
# Level 1
# Level 2
# Level 3
```

All headings are clamped to H1 (minimum level).

## Use Cases

1. **Embedding in Larger Documents**: When converting a document that will be included as a section in a larger document, increase heading levels to maintain hierarchy.

2. **Flattening Hierarchy**: When you want to reduce the depth of heading hierarchy, use negative offset.

3. **Standardization**: Ensure all converted documents start at a specific heading level (e.g., always start at H2 instead of H1).

4. **Documentation Generation**: When generating documentation from multiple sources, adjust heading levels to create a consistent structure.

## Implementation Details

### Components

1. **ConversionConfig** (`src/config.py`):
   - Stores the `heading_offset` value (default: 0)
   - Supports loading from YAML config files
   - CLI arguments override config file values

2. **MarkdownSerializer** (`src/markdown_serializer.py`):
   - Applies the offset in the `serialize_heading()` method
   - Implements level clamping (1-6 range)
   - Formula: `level = max(1, min(6, heading.level + self.heading_offset))`

3. **ConversionOrchestrator** (`src/conversion_orchestrator.py`):
   - Passes the `heading_offset` from config to the serializer
   - Ensures consistent offset application across all documents

### Testing

The feature is thoroughly tested with:

- **Unit tests** (`tests/test_heading_offset.py`):
  - Positive and negative offsets
  - Upper and lower bound clamping
  - Large offset values
  - Boundary conditions
  - Text preservation

- **Integration tests** (`tests/test_heading_offset_integration.py`):
  - End-to-end conversion with offset
  - Config file loading
  - CLI override behavior
  - Deep document hierarchies
  - Content preservation

All tests pass successfully with 100% coverage of the heading offset feature.

## Configuration Priority

When both CLI and config file specify `heading_offset`, the CLI value takes precedence:

```bash
# config.yaml has heading_offset: 1
# CLI specifies heading_offset: 2
doc2md -i document.docx -c config.yaml --heading-offset 2

# Result: heading_offset=2 (CLI wins)
```

## Limitations

1. **Fixed Offset**: The same offset is applied to all headings in the document. Individual heading adjustments are not supported.

2. **Level Clamping**: Headings that would exceed H6 or go below H1 are clamped, which may result in multiple headings at the same level.

3. **No Semantic Analysis**: The offset is applied mechanically without understanding document structure or semantic meaning.

## Future Enhancements

Potential improvements for future versions:

1. **Smart Offset**: Automatically detect optimal offset based on document structure
2. **Selective Offset**: Apply different offsets to different sections
3. **Preserve Relative Hierarchy**: Maintain relative heading differences even when clamping occurs
4. **Warning Messages**: Alert users when clamping occurs
