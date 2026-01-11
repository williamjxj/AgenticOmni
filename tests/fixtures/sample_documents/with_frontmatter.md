---
title: "API Documentation"
author: "John Doe"
date: "2026-01-10"
tags:
  - api
  - documentation
  - rest
category: "engineering"
published: true
version: 1.0
---

# API Documentation

This markdown file contains YAML frontmatter for testing metadata extraction.

## Overview

The frontmatter above contains structured metadata that should be extracted separately from the document content.

## Frontmatter Fields

The following fields are defined in the frontmatter:
- **title**: Document title
- **author**: Document author
- **date**: Publication date
- **tags**: Array of tags for categorization
- **category**: Primary category
- **published**: Publication status
- **version**: Document version

## Content Body

This is the main content of the document, which should be parsed separately from the frontmatter metadata.

### API Endpoints

1. GET /api/users
2. POST /api/users
3. PUT /api/users/{id}
4. DELETE /api/users/{id}

## Testing

This document is used to verify that:
1. Frontmatter is correctly extracted as JSONB metadata
2. Content body is parsed independently
3. Both frontmatter and content are properly stored
