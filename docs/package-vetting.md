# Package Security Vetting Workflow

## Overview

This document provides comprehensive guidance for the **Package Security Vetting** GitHub Actions workflow. This automated process enables developers to request security assessments for third-party packages before adoption, ensuring supply chain security across all projects.

## Workflow Architecture

The vetting process combines multiple security assessment tools:
- **Sonatype OSS Index**: Free vulnerability database with 2.6+ million packages
- **OSV-Scanner**: Google's universal vulnerability scanner for source code analysis
- **Repository Analysis**: GitHub metrics, license compliance, and maintenance indicators
- **Risk Scoring**: Automated decision matrix for approval recommendations

## Supported Ecosystems

| Ecosystem | Auto-Detection | Package Manager | Example |
|-----------|----------------|-----------------|---------|
| **.NET** | `*.Net*` pattern | NuGet | `Handlebars.Net` |
| **JavaScript** | `@*` or simple names | npm/yarn | `react`, `@angular/core` |
| **Python** | Manual selection | pip/PyPI | `django` |
| **Java** | Manual selection | Maven/Gradle | `spring-boot` |
| **Go** | Manual selection | Go modules | `gin` |

## Workflow Parameters

| Parameter | Description | Required | Default | Examples |
|-----------|-------------|----------|---------|----------|
| `package_name` | Package name to evaluate | ✅ Yes | `Handlebars.Net` | `react`, `django`, `spring-boot` |
| `package_version` | Specific version to vet | ✅ Yes | `2.1.6` | `18.0.0`, `4.2.0` |
| `github_repo_url` | Optional GitHub API URL | ❌ No | _(auto-detected)_ | `https://api.github.com/repos/facebook/react` |
| `ecosystem` | Override auto-detection | ❌ No | `auto` | `dotnet`, `npm`, `python`, `java`, `go` |

## How to Use the Workflow [package-vetting.yml](../.github/workflows/package-vetting.yml)

### Step 1: Access Workflow
1. Navigate to your repository on GitHub
2. Click the **Actions** tab
3. Select **Package Security Vetting** from the workflow list
4. Click **Run workflow** button

### Step 2: Configure Parameters
Fill in the workflow parameters:
Package Name: Handlebars.Net
Package Version: 2.1.6
GitHub Repo URL: (leave blank for auto-detection)
Ecosystem: auto


### Step 3: Monitor Execution
- Watch the workflow progress in real-time
- View step-by-step execution logs
- Check the workflow summary for immediate results

### Step 4: Review Results
- **GitHub Summary**: Quick overview with risk score and decision
- **Download Artifacts**: Comprehensive reports for detailed analysis
- **Issues Created**: Automatic issues for high-risk packages requiring manual review

## Understanding Results

### Risk Assessment Matrix

| Risk Score | Status | Action Required |
|------------|--------|-----------------|
| **0** | ✅ **APPROVED** | Immediate use authorized |
| **1-2** | ⚠️ **CONDITIONAL** | Use with monitoring |
| **3+** | ❌ **REQUIRES REVIEW** | Manual security assessment needed |

### Risk Factors
- **Vulnerabilities**: +3 points for any security issues
- **Low Popularity**: +1 point for <100 GitHub stars
- **License Issues**: +1 point for non-standard licenses

### Generated Reports

1. **Comprehensive Vetting Report** (`package-vetting-report.txt`)
   - Executive summary with clear recommendation
   - Detailed vulnerability analysis
   - Repository metrics and adoption statistics
   - Installation instructions for approved packages

2. **Raw Scan Data** (`oss-index-results.json`, `osv-scan.json`)
   - Complete vulnerability database responses
   - Technical details for security team review
   - Audit trail for compliance requirements

3. **GitHub Issues** (for high-risk packages)
   - Automatically created with security labels
   - Detailed risk assessment summary
   - Action items for security team
