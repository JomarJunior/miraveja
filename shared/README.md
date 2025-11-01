# MiravejaCore

Shared domain models, application use cases, and infrastructure interfaces for the MiraVeja project.

## Structure

- `Shared/` - Common utilities, logging, error handling, UnitOfWork, events
- `Gallery/` - Gallery bounded context (domain models, application use cases)
- `Member/` - Member bounded context (domain models, application use cases)

## Usage

This package is used by both the API and Worker services to share business logic.

```python
from MiravejaCore.Gallery.Domain.Models import Image
from MiravejaCore.Gallery.Application.RegisterImageMetadata import RegisterImageMetadataHandler
```

## Installation

```bash
pip install -e .
```
