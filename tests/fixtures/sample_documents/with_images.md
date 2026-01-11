# Document with Image References

This markdown file contains various types of image references for testing image extraction.

## External Images

Here's an architecture diagram hosted externally:

![Architecture Diagram](https://example.com/images/architecture.png "System Architecture")

## Local Relative Path Images

Screenshot from the local images folder:

![Dashboard Screenshot](./images/dashboard-screenshot.png)

Another local image:

![User Profile](../assets/user-profile.jpg)

## Base64 Embedded Image

Small icon embedded as base64:

![Embedded Icon](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)

## Images with Alt Text

Important for RAG search - alt text should be included in searchable content:

![Database schema diagram showing user authentication flow](https://example.com/diagrams/db-schema.svg)

## HTML Image Tags

Sometimes markdown includes HTML img tags:

<img src="https://example.com/logo.png" alt="Company Logo" width="200">

## Image Without Alt Text

![](https://example.com/background.jpg)

## Testing Requirements

This document tests:
1. External URL image detection (https://)
2. Local relative path image detection (./images/, ../assets/)
3. Base64 embedded image detection (data:image/)
4. Alt text extraction for RAG inclusion
5. HTML img tag parsing
6. Images without alt text
7. ImageReference record creation with proper flags (is_local_path, is_base64, is_external_url)
