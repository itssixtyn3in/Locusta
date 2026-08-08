# Locusta

Locusta is an offensive security research framework designed for Microsoft 365 environments, focusing on enterprise AI collaboration surfaces, indirect prompt injection lure creation, and post-exploitation propagation analysis

## Overview

Locusta provides red team operators with a structured toolkit to assess the security posture of enterprise AI integrations like Microsoft 365 Copilot and Outlook/OWA workflows. By leveraging device code authentication flows, the framework allows operators to manage active sessions, map out tenant attack surfaces, automate the generation and injection of indirect prompt injection lures into documents, and execute precise file sharing and collaboration analysis via the Microsoft Graph API.

## Features & Modules

* **Auth (`auth.py`)**: Handles Microsoft device code authentication flows and session token management.
* **Collaboration (`collab.py`)**: Analyzes organizational collaboration exposure, shared files, and cross-user propagation paths.
* **Enumeration (`enumeration.py`)**: Enumerate tenant attack surfaces including users, SharePoint sites, file searches, writable documents, and sharing permission tests.
* **Generation (`generation.py`)**: Automates the creation of indirect prompt injection payload templates.
* **Graph (`graph.py`)**: Interacts with Microsoft Graph resources and mappings.
* **Injection (`inject.py`)**: Automatically injects hidden content/payloads into writable DOCX files.
* **Runner (`runner.py`)**: Orchestrates automated end-to-end workflow execution chains.
* **Sessions (`sessions.py`)**: Manages and lists saved authentication token sessions.
* **Share (`share.py`)**: Manages file uploads, recipient selection, and Graph API sharing invitations.

## Document Generation Techniques

| Technique | Description | Supported Document Formats |
| :--- | :--- | :--- |
| **Hidden Text** | Inject hidden white text | `.docx`, `.xlsx`, `.pptx` |
| **Header / Footer** | Hide prompts inside headers and footers | `.docx`, `.xlsx` |
| **Off Page** | Place prompts outside visible page boundaries | `.docx`, `.pptx` |
| **Orphan Stream** | Inject orphan OOXML streams and hidden XML | `.docx`, `.xlsx` |
| **Hidden Comment** | Hide prompts inside comments and metadata | `.docx`, `.xlsx` |
| **Style Steganography** | Encode prompts into style metadata | `.docx` |
| **Image Steganography** | Hide prompts inside embedded images | `.docx` |
