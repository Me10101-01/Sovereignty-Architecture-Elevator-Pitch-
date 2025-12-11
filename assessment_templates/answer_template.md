# Answer Framework Template

## Q[NUMBER]: [QUESTION TITLE]

### Executive Summary
<!-- 2-3 sentence overview of your approach -->
[Provide a high-level summary of your solution strategy]

### Solution Architecture
<!-- Detailed design with diagrams -->

#### Overview
[Describe the overall architecture and approach]

#### Component Breakdown
[List and describe each major component]

#### Data Flow
[Explain how data moves through the system]

#### Integration Points
[Identify where this integrates with existing systems]

#### Diagrams
```mermaid
[Insert Mermaid diagram here]
```

### Implementation

#### Prerequisites
```yaml
prerequisites:
  - [List required systems, tools, or configurations]
```

#### Configuration
```yaml
# Configuration files
[Provide actual YAML/JSON configuration]
```

#### Code
```[language]
# Implementation code
[Provide working code that can be executed]
```

#### Deployment Steps
1. [Step-by-step deployment instructions]
2. [Make them executable, not theoretical]

### Failure Modes

#### Failure Mode 1: [Name]
- **Symptom**: [How you detect it]
- **Impact**: [What breaks]
- **Mitigation**: [How to prevent]
- **Recovery**: [How to fix if it happens]

#### Failure Mode 2: [Name]
- **Symptom**: [How you detect it]
- **Impact**: [What breaks]
- **Mitigation**: [How to prevent]
- **Recovery**: [How to fix if it happens]

[Add more failure modes as needed]

#### Escape Hatch
[The emergency "break glass" procedure when all else fails]

### Success Criteria

#### Functional Requirements
- [ ] [Requirement 1 with measurable outcome]
- [ ] [Requirement 2 with measurable outcome]
- [ ] [Requirement 3 with measurable outcome]

#### Non-Functional Requirements
- [ ] **Performance**: [Metric and target]
- [ ] **Reliability**: [Metric and target]
- [ ] **Security**: [Metric and target]
- [ ] **Observability**: [Metric and target]

#### Validation Tests
```bash
# Test 1: [Description]
[Actual test command]

# Test 2: [Description]
[Actual test command]
```

### Time to Implement

#### Breakdown
- **Design**: [X hours]
- **Implementation**: [Y hours]
- **Testing**: [Z hours]
- **Documentation**: [W hours]
- **Total**: [Sum hours/days]

#### Assumptions
- [List what you're assuming exists or is available]

### Dependencies

#### External Services
- [Service 1]: [Version/requirement]
- [Service 2]: [Version/requirement]

#### Internal Systems
- [System 1]: [What you need from it]
- [System 2]: [What you need from it]

#### Tools & Libraries
```yaml
dependencies:
  - name: [Tool/library name]
    version: [Version]
    purpose: [Why needed]
```

### Maintenance Burden

#### Ongoing Costs
- **Time**: [Hours per week/month]
- **Money**: [$ per month for services/licenses]
- **Complexity**: [Low/Medium/High]

#### Monitoring Requirements
- [Metric 1 to watch]
- [Metric 2 to watch]
- [Alert conditions]

#### Update Frequency
- **Configuration**: [How often needs tuning]
- **Dependencies**: [Update cadence]
- **Documentation**: [When to refresh]

#### Bus Factor
- **Minimum team size**: [Number of people]
- **Knowledge concentration**: [How specialized]
- **Handoff difficulty**: [Easy/Medium/Hard]

---

## Sovereignty Alignment Analysis

### Vendor Lock-in Reduction
[How does this solution reduce dependency on specific vendors?]

### Antifragility Enhancement
[How does this make the system stronger under stress?]

### Transparency & Auditability
[How is this solution observable and verifiable?]

---

## Alternative Approaches Considered

### Alternative 1: [Name]
- **Pros**: [Benefits]
- **Cons**: [Drawbacks]
- **Why not chosen**: [Reason]

### Alternative 2: [Name]
- **Pros**: [Benefits]
- **Cons**: [Drawbacks]
- **Why not chosen**: [Reason]

---

## References & Resources

### Documentation
- [Link to relevant docs]
- [Link to relevant docs]

### Code Examples
- [Link to example implementation]
- [Link to similar solution]

### Standards & Best Practices
- [Relevant RFC, standard, or guideline]

---

## Appendix: Extended Technical Details

### [Optional] Detailed Algorithm
[If complex logic is involved, break it down here]

### [Optional] Performance Benchmarks
[If performance is critical, show benchmarks]

### [Optional] Security Analysis
[If security is critical, show threat model]

---

**Author**: [Your name/identifier]  
**Date**: [YYYY-MM-DD]  
**Version**: [1.0]  
**Signature**: [GPG signature]  
**Timestamp**: [OpenTimestamps proof]
