# Platform Planning Document

Milestones, phases, and KPIs for InsightPulse Odoo platform.

## Timeline Overview

**Phase 1**: Foundation (2025-11-01 to 2025-12-31)
**Phase 2**: MVP (2026-01-01 to 2026-03-31)
**Phase 3**: Scale (2026-04-01 to 2026-06-30)

## Phase 1: Foundation (Q4 2025)

### Objectives
- Establish project structure and documentation
- Implement core multi-tenancy and BIR compliance
- Set up CI/CD automation
- Deploy to DigitalOcean

### Milestones

#### M1.1: Spec-Kit Documentation (Week 1-2)
- ✅ Create PRD_PLATFORM.md
- ✅ Create planning.md (this file)
- ✅ Create tasks.md
- ✅ Create CHANGELOG.md
- ✅ Create doc.yaml
- ✅ Create platform_spec.json

#### M1.2: CI/CD Infrastructure (Week 3-4)
- ✅ Create spec-guard.yml workflow
- ✅ Create ci-odoo.yml skeleton
- ✅ Create ci-supabase.yml skeleton
- ✅ Create ci-superset.yml skeleton
- ✅ Create cd-odoo-prod.yml skeleton
- ✅ Create docs-ci.yml skeleton
- ✅ Create pages-deploy.yml skeleton
- Create validate_spec.py script
- Configure GitHub Secrets

#### M1.3: Core Platform (Week 5-8)
- Implement multi-tenant `company_id` isolation
- Create BIR compliance module (forms 2307, 2316)
- Set up PostgreSQL + Supabase
- Deploy Odoo CE 19 to DigitalOcean droplet

#### M1.4: Authentication (Week 9-10)
- Configure Google OAuth SSO
- Set up authorized origins and redirect URIs
- Test OAuth flow across all domains

#### M1.5: Documentation Platform (Week 11-12)
- Deploy GitHub Pages (docs-ci.yml, pages-deploy.yml)
- Create getting-started.md, architecture.md
- Create guides and deployment docs
- Create Pulser spec-kit

### KPIs for Phase 1
- [ ] All spec-kit docs complete and validated
- [ ] CI/CD workflows green (all passing)
- [ ] Multi-tenancy working (company_id isolation)
- [ ] BIR compliance module deployed
- [ ] Google OAuth SSO operational
- [ ] GitHub Pages docs site live

## Phase 2: MVP (Q1 2026)

### Objectives
- Implement OCR expense processing
- Deploy Apache Superset analytics
- Launch Pulser v4.0.0 AI orchestration
- Onboard first 3 companies

### Milestones

#### M2.1: OCR Integration (Week 13-16)
- Integrate PaddleOCR for receipt scanning
- Implement DeepSeek LLM validation
- Create auto-expense-creation workflow
- Deploy OCR service to SGP1 droplet

#### M2.2: Apache Superset (Week 17-18)
- Deploy Superset to App Platform
- Create expense dashboard
- Create BIR compliance dashboard
- Integrate with Odoo + Supabase data

#### M2.3: Pulser AI (Week 19-20)
- Deploy MCP Coordinator to App Platform
- Configure Dash, Maya, Echo agents
- Test agent coordination workflows

#### M2.4: Production Hardening (Week 21-24)
- Performance testing and optimization
- Security audit
- Backup and disaster recovery setup
- Production monitoring and alerting

### KPIs for Phase 2
- [ ] OCR accuracy >60% on test receipts
- [ ] Superset dashboards operational
- [ ] Pulser agents responding correctly
- [ ] 3 companies onboarded and active
- [ ] >99% uptime in production

## Phase 3: Scale (Q2 2026)

### Objectives
- Onboard 10+ companies
- Achieve >80% OCR auto-approval rate
- Keep infrastructure costs <$1k/month
- Launch mobile app (optional)

### Milestones

#### M3.1: Company Onboarding (Week 25-28)
- Onboard companies 4-10
- Create onboarding playbook
- Automate company setup process

#### M3.2: OCR Optimization (Week 29-30)
- Improve OCR accuracy to >80%
- Reduce manual review rate
- Optimize DeepSeek LLM prompts

#### M3.3: Cost Optimization (Week 31-32)
- Optimize Docker images (reduce size)
- Review DigitalOcean usage
- Scale down unused services
- Target: <$1k/month total infrastructure

#### M3.4: Mobile App (Week 33-36) [Optional]
- React Native or Flutter prototype
- OCR receipt capture
- Approval workflows
- Dashboard views

### KPIs for Phase 3
- [ ] 10+ companies active
- [ ] >80% OCR auto-approval rate
- [ ] <$1k/month infrastructure costs
- [ ] Mobile app MVP launched (optional)
- [ ] >99.5% uptime

## Resource Allocation

### Team
- **Product Owner**: Jake Tolentino
- **Tech Lead**: Jake Tolentino
- **DevOps**: Jake Tolentino + CI/CD automation
- **AI/ML**: Pulser v4.0.0 agents (Dash, Maya, Echo)

### Infrastructure Budget

**Development** (Free):
- Local Docker Compose
- GitHub Actions (free tier)
- Supabase (free tier)

**Production** (Monthly):
- DigitalOcean Droplets: $24/month (2 x $12)
- DigitalOcean App Platform: $240/month (3 apps x $5)
- Domain + DNS: $12/month
- **Total**: ~$300/month (vs $4k+ for SaaS)

**Cost Savings**: $50k+ annually by replacing:
- SAP Concur: $15k/year → Odoo Expense
- SAP Ariba: $12k/year → Odoo Procurement
- Tableau: $8.4k/year → Apache Superset
- Slack Enterprise: $12.6k/year → Mattermost/Rocket.Chat
- Odoo Enterprise: $4.7k/year → Odoo CE + OCA

## Risk Management

### Technical Risks

**R1: BIR e-invoicing delayed**
- **Impact**: High (blocks production)
- **Probability**: Medium (government delays)
- **Mitigation**: Build pluggable connector, wait for official API

**R2: OCR accuracy <60%**
- **Impact**: Medium (manual review burden)
- **Probability**: Medium (receipt quality varies)
- **Mitigation**: DeepSeek LLM validation, manual review workflow

**R3: DigitalOcean outage**
- **Impact**: High (service downtime)
- **Probability**: Low (DO SLA 99.99%)
- **Mitigation**: Multi-region deployment, backup to AWS

### Operational Risks

**R4: Company migration issues**
- **Impact**: Medium (delays onboarding)
- **Probability**: Medium (data quality varies)
- **Mitigation**: Thorough testing, onboarding playbook

**R5: Support burden**
- **Impact**: Medium (team capacity)
- **Probability**: High (new users need help)
- **Mitigation**: Comprehensive documentation, AI chatbot

## Success Metrics

### Technical Metrics
- **Uptime**: >99.5% (measured via DigitalOcean monitoring)
- **Performance**: <3s page load, <500ms API response (95th percentile)
- **Test Coverage**: >80% on critical modules
- **CI/CD Success Rate**: >95% (green workflows)

### Business Metrics
- **Cost Savings**: >$50k/year vs SaaS alternatives
- **Company Adoption**: 10+ companies by Q2 2026
- **User Satisfaction**: >80% positive feedback
- **OCR Automation**: >80% auto-approval rate

### Quality Metrics
- **BIR Compliance**: 100% forms generated correctly
- **Multi-Tenancy**: 0 cross-company data leaks
- **Security**: 0 critical vulnerabilities (audited quarterly)
- **Documentation**: 100% spec-kit compliance

## Next Steps

**Immediate** (This Week):
1. ✅ Complete spec-kit documentation
2. ✅ Validate all CI/CD workflows
3. Run validate_spec.py locally
4. Deploy GitHub Pages

**Near-term** (Next 2 Weeks):
1. Implement multi-tenant company_id isolation
2. Create BIR compliance module
3. Set up DigitalOcean droplets
4. Configure Google OAuth SSO

**Medium-term** (Next 4 Weeks):
1. Deploy Odoo CE 19 to production
2. Integrate OCR service
3. Deploy Apache Superset
4. Launch Pulser v4.0.0

## References

- [PRD](PRD_PLATFORM.md) - Product requirements
- [Tasks](tasks.md) - Detailed task breakdown
- [CHANGELOG](CHANGELOG.md) - Version history
- [Platform Spec](../../spec/platform_spec.json) - Canonical specification
