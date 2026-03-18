
# AgenticOmni Documentation (PoC/MVP)
---

## 🚀 PoC/MVP Overview

This documentation covers the PoC/MVP architecture, setup, and usage for enterprise demo and funding presentations.

### Key Features
* Enterprise connectors (SharePoint, Google Drive, email)
* Modular multi-agent pipeline (Document → OCR → Extraction → RAG → Summary)
* Governance dashboard (usage/cost/logs)
* Document intelligence (OCR/table extraction)
* Human-in-the-loop review UI

### Quick Start
See [quickstart.md](./quickstart.md) for setup instructions.

**Last Updated**: February 13, 2026  
**Version**: 0.2.0

> 🌐 **Online Documentation**: Visit our [GitHub Pages site](https://williamjxj.github.io/AgenticOmni) for a better reading experience

---

## 📚 Quick Navigation

### 🌐 Online Resources
- **[GitHub Pages Site](https://williamjxj.github.io/AgenticOmni)** - Browse documentation online with enhanced navigation
- **[GitHub Repository](https://github.com/williamjxj/AgenticOmni)** - Source code and issues

### Implementation & Status
- **[implementation.md](./implementation.md)** - Complete implementation status and summary (v0.2.0, 387/387 tasks)
- **[changelog.md](./changelog.md)** - Version history and release notes
- **[servers-status.md](./servers-status.md)** - Current server and service status

### Setup & Configuration
- **[../README.md](../README.md)** - Main project README with quick start
- **[quickstart.md](./quickstart.md)** - Quick start guide
- **[environment.md](./environment.md)** - Complete environment variable reference
- **[production.md](./production.md)** - Production deployment checklist

### Feature-Specific Guides
- **[malware-scanning.md](./malware-scanning.md)** - ClamAV integration and troubleshooting
- **[frontend.md](./frontend.md)** - Frontend implementation and integration guide
- **[markdown-workflow.md](./markdown-workflow.md)** - Markdown document workflow
- **[ocr-completion.md](./ocr-completion.md)** - OCR MVP completion status

### Development Guidelines
- **[versioning.md](./versioning.md)** - Documentation versioning and version control guide
- **[contributing.md](./contributing.md)** - How to contribute to the project
- **[next-steps.md](./next-steps.md)** - Next steps and future features

### Specifications
- **[../specs/001-app-skeleton-init/](../specs/001-app-skeleton-init/)** - Application skeleton specification
- **[../specs/002-doc-upload-parsing/](../specs/002-doc-upload-parsing/)** - Document upload & parsing specification

### Templates
- **[templates/ADR_TEMPLATE.md](./templates/ADR_TEMPLATE.md)** - Architecture Decision Record template
- **[templates/DOCUMENT_TEMPLATE.md](./templates/DOCUMENT_TEMPLATE.md)** - Technical documentation template

---

## 🎯 Getting Started

### For New Developers
1. Read the main **[README.md](../README.md)** for project overview
2. Follow the **[quickstart guide](./QUICKSTART.md)**
3. Review **[environment.md](./environment.md)** for setup
4. Check **[frontend.md](./frontend.md)** for UI development

### For Deployment
1. Review **[production.md](./production.md)**
2. Configure environment variables from **[environment.md](./environment.md)**
3. Check **[malware-scanning.md](./malware-scanning.md)** for ClamAV setup

### For Contributors
1. Read **[CONTRIBUTING.md](./CONTRIBUTING.md)**
2. Follow **[VERSIONING.md](./VERSIONING.md)**
3. Use **[templates/](./templates/)** for new documentation

---

## 📊 Documentation Structure

```
docs/
├── README.md (this file)           # Documentation index
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── implementation.md               # Full implementation report
├── environment.md                  # Environment setup
├── frontend.md                     # Frontend development guide
├── malware-scanning.md             # Security features
├── markdown-workflow.md            # Markdown workflow guide
├── next-steps.md                   # Next steps and roadmap
├── ocr-completion.md               # OCR MVP completion
├── production.md                   # Deployment guide
├── QUICKSTART.md                   # Quick start guide
├── servers-status.md               # Server status
├── versioning.md                   # Documentation standards
└── templates/                      # Document templates
    ├── ADR_TEMPLATE.md
    └── DOCUMENT_TEMPLATE.md
```

---

## 🔍 Find Documentation By Topic

### Architecture & Design
- System Architecture → [implementation.md](./implementation.md)
- Database Schema → [../specs/002-doc-upload-parsing/data-model.md](../specs/002-doc-upload-parsing/data-model.md)
- API Contracts → [../specs/002-doc-upload-parsing/contracts/](../specs/002-doc-upload-parsing/contracts/)

### Features & APIs
- Document Upload → [implementation.md](./implementation.md#document-upload)
- Document Parsing → [implementation.md](./implementation.md#multi-format-parsing-complete)
- Malware Scanning → [malware-scanning.md](./malware-scanning.md)
- Progress Tracking → [implementation.md](./implementation.md#processing-pipeline-complete)

### Development
- Setup & Installation → [../README.md](../README.md), [QUICKSTART.md](./QUICKSTART.md)
- Environment Config → [environment.md](./environment.md)
- Frontend Development → [frontend.md](./frontend.md)
- Versioning & Git → [versioning.md](./versioning.md)

### Deployment & Operations
- Production Deployment → [production.md](./production.md)
- Server Status → [servers-status.md](./servers-status.md)
- Monitoring → [implementation.md](./implementation.md#monitoring--metrics-complete)

---

## 🌐 GitHub Pages

This documentation is also available as a GitHub Pages site for easier browsing:

- **Live Site**: [https://williamjxj.github.io/AgenticOmni](https://williamjxj.github.io/AgenticOmni)
- **Setup Guide**: [../GITHUB_PAGES_SETUP.md](../GITHUB_PAGES_SETUP.md)
- **Auto-Deploy**: Automatically deployed via GitHub Actions on push to main branch

### Benefits of GitHub Pages
- 🎨 **Enhanced UI**: Professional theme with navigation
- 🔍 **Better Search**: Easier to find documentation
- 📱 **Mobile Friendly**: Responsive design for all devices
- 🔗 **Shareable Links**: Easy to share specific documentation pages

---

## 📝 Documentation Standards

### Writing Guidelines
- **Clear**: Write for your audience (developers, stakeholders, users)
- **Concise**: Be brief but complete
- **Structured**: Use consistent headings and formatting
- **Visual**: Include diagrams, tables, code examples
- **Tested**: Provide working examples and expected output

### Creating New Documentation
1. Use appropriate template from [templates/](./templates/)
2. Follow structure and formatting conventions
3. Update this index (README.md) with new document
4. Add entry to [CHANGELOG.md](./CHANGELOG.md)
5. Submit PR for review

### Versioning
- All major documents follow [Semantic Versioning](https://semver.org/)
- See [versioning.md](./versioning.md) for details
- Update [CHANGELOG.md](./CHANGELOG.md) with all changes

---

## 🤝 Contributing

Found an error? Want to improve documentation?

1. Check [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
2. Create an issue or PR
3. Follow documentation standards
4. Request review

---

## 📞 Support

- **Documentation Issues**: Create GitHub issue with `docs` label
- **Technical Questions**: Check [implementation.md](./implementation.md)
- **Setup Problems**: Review [environment.md](./environment.md)

---

**Maintained By**: AgenticOmni Development Team  
**Project**: [AgenticOmni](https://github.com/williamjxj/AgenticOmni)  
**Documentation**: [GitHub Pages](https://williamjxj.github.io/AgenticOmni)
