import React from 'react';
import {
  Layout,
  Button,
  Typography,
  Row,
  Col,
  Card,
  Statistic,
  Space,
  Tag,
  Collapse,
  Avatar,
  Badge,
  Divider,
  List,
  Progress,
  Timeline,
} from 'antd';
import {
  SafetyOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  CloudServerOutlined,
  CheckCircleOutlined,
  FileProtectOutlined,
  ApiOutlined,
  MobileOutlined,
  DeploymentUnitOutlined,
  BankOutlined,
  LockOutlined,
  LineChartOutlined,
  CustomerServiceOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import Head from 'next/head';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

const navLinks = [
  { label: 'Why InsightPulse', href: '#platform' },
  { label: 'Security', href: '#security' },
  { label: 'Playbooks', href: '#workflows' },
  { label: 'Deployment', href: '#deployment' },
  { label: 'Resources', href: '#resources' },
];

const heroStats = [
  { label: 'Multi-agency SSCs live', value: '8' },
  { label: 'Average automation lift', value: '42%' },
  { label: 'Uptime SLA', value: '99.95%' },
];

const trustBadges = ['Treasury bureaus', 'Digital banks', 'GovCloud BPOs', 'Fintech risk teams'];

const platformPillars = [
  {
    title: 'Finance-grade collaboration',
    description:
      'Channels, playbooks, and runbooks for controllers, risk, procurement, and tax leads mapped to each workflow.',
    icon: <TeamOutlined />,
  },
  {
    title: 'AI copilots with guardrails',
    description:
      'Anthropic-class copilots reason over Odoo data, expense docs, and Supabase telemetry with deterministic policy packs.',
    icon: <ThunderboltOutlined />,
  },
  {
    title: 'Deployment freedom',
    description:
      'DigitalOcean, AWS GovCloud, or on-prem clusters with blue/green releases, private networking, and CMK support.',
    icon: <CloudServerOutlined />,
  },
];

const capabilityHighlights = [
  {
    title: 'Visibility & accountability',
    body:
      'Tie every approval, exception, and regulatory deliverable to one shared timeline. Command centers broadcast KPIs, late tasks, and AI reasoning in real time.',
    bullets: ['Segmented channels per agency', 'Auto-synced ERP references', 'Controller + IT dual sign-off'],
  },
  {
    title: 'Secure automation at scale',
    body:
      'Trigger atomic automations from Mattermost-style playbooks: reimbursements, supplier vetting, or BIR packet assembly, all observable through OpenTelemetry.',
    bullets: ['Immutable audit ledger', 'Scoped API tokens for bots', 'pgvector encryption for SDG data'],
  },
  {
    title: 'Human + AI collaboration',
    body:
      'Blend copilots, manual reviews, and escalation trees. Every AI suggestion surfaces reasoning, policy citations, and acceptance history for auditors.',
    bullets: ['Explainable prompts per workflow', 'Reviewer overrides logged', 'Auto-escalation for risk events'],
  },
];

const workflowPlaybooks = [
  {
    title: 'Spend controls',
    icon: <FileProtectOutlined />,
    bullets: ['Multi-level approvals', 'Budget guardrails', 'ERP sync in real time'],
  },
  {
    title: 'Incident response',
    icon: <DeploymentUnitOutlined />,
    bullets: ['Vendor fraud playbooks', 'Escalation matrices', 'Post-mortem automation'],
  },
  {
    title: 'Regulatory reporting',
    icon: <BankOutlined />,
    bullets: ['BIR 1601-C & 2550Q exports', 'Document locking', 'Evidence vault'],
  },
  {
    title: 'AI-powered shared inboxes',
    icon: <CustomerServiceOutlined />,
    bullets: ['Triage reimbursements', 'Auto-suggest replies', 'Policy-pack validation'],
  },
];

const complianceHighlights = [
  {
    label: 'Data residency',
    detail: 'Customer-controlled Postgres + object storage with encrypted backups every 15 minutes.',
  },
  {
    label: 'Zero-trust access',
    detail: 'SCIM provisioning, device posture checks, and short-lived session tokens for reviewers.',
  },
  {
    label: 'Audit intelligence',
    detail: 'Immutable event ledger with exportable OpenTelemetry traces mapped to SOC 2 controls.',
  },
];

const securityTiles = [
  {
    title: 'Defense-in-depth',
    description: 'Layered RBAC, JIT access, and immutable audit logs for every controller action.',
    icon: <SafetyOutlined />,
    color: '#15803d',
    background: '#dcfce7',
  },
  {
    title: 'Open API, closed data',
    description: 'Signed webhooks, Supabase pgvector encryption, and service mesh policies keep integrations compliant.',
    icon: <ApiOutlined />,
    color: '#0369a1',
    background: '#e0f2fe',
  },
  {
    title: 'Anywhere, still private',
    description: 'Mobile reviewers get biometric enforcement and offline-safe caching with forced revalidation.',
    icon: <MobileOutlined />,
    color: '#92400e',
    background: '#fef3c7',
  },
];

const deploymentPhases = [
  {
    title: 'Phase 1 — Secure workspace foundation',
    description: 'Deploy Odoo + Supabase stack, configure SSO, and onboard 2 pilot workflows within 14 days.',
  },
  {
    title: 'Phase 2 — Automation expansion',
    description: 'Connect ERP and banking feeds, enable AI copilots, and automate supplier onboarding.',
  },
  {
    title: 'Phase 3 — Command hub rollout',
    description: 'Add analytics, blue/green deployment runbooks, and ongoing compliance attestations.',
  },
];

const resourceHighlights = [
  'Security architecture deck (SOC 2 + BIR)',
  'Finance SSC ROI model with $118K savings',
  'Deployment checklist for DigitalOcean, AWS, and on-prem',
  'Sample AI audit logs with explanation metadata',
];

const faqItems = [
  {
    question: 'How close is this to the Mattermost financial services experience?',
    answer:
      "The layout, sequencing, and storytelling mirror Mattermost's landing page, replacing copy with finance SSC metrics, InsightPulse telemetry, and BIR compliance proof.",
  },
  {
    question: 'Do we need to re-platform our ERP to adopt InsightPulse?',
    answer:
      'No. Odoo orchestrates SAP, Oracle, or custom ledgers via secure APIs, message queues, and Supabase event streams.',
  },
  {
    question: 'Is on-prem deployment available?',
    answer:
      'Yes. We ship hardened Docker images with health checks, secrets rotation, and blue/green upgrades for air-gapped sites.',
  },
];

export default function Home() {
  return (
    <>
      <Head>
        <title>InsightPulse | Financial Services Collaboration Platform</title>
        <meta
          name="description"
          content="Mattermost-style landing page showcasing InsightPulse automation for regulated financial services, multi-agency SSCs, and BIR-compliant workflows."
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Layout className="bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
        <Header
          style={{
            background: 'rgba(255, 255, 255, 0.94)',
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid #edf2f7',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            padding: '0 48px',
          }}
        >
          <div
            style={{
              maxWidth: 1200,
              margin: '0 auto',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              height: '64px',
            }}
          >
            <Space align="center" size="middle">
              <Avatar size={44} style={{ background: '#0272d4' }}>
                IP
              </Avatar>
              <div>
                <Text strong style={{ fontSize: 18, color: '#053e68' }}>
                  InsightPulse AI
                </Text>
                <div style={{ fontSize: 12, color: '#5f6b7c' }}>Finance SSC Platform</div>
              </div>
            </Space>

            <Space size="large" wrap>
              {navLinks.map((item) => (
                <a key={item.label} href={item.href} style={{ color: '#1f2933' }}>
                  {item.label}
                </a>
              ))}
              <Button type="link" style={{ color: '#0272d4' }}>
                Contact Sales
              </Button>
              <Button type="primary" size="large">
                Launch App
              </Button>
            </Space>
          </div>
        </Header>

        <Content>
          <section style={{ padding: '120px 24px 80px' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <Row gutter={[48, 48]} align="middle">
                <Col xs={24} lg={14}>
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
                    <Tag color="blue" style={{ marginBottom: 16 }}>
                      Built for Financial Services SSCs
                    </Tag>
                    <Title style={{ fontSize: 56, lineHeight: 1.1, marginBottom: 24 }}>
                      Recreate Mattermost-class collaboration—optimized for BIR-compliant automation
                    </Title>
                    <Paragraph style={{ fontSize: 18, color: '#4b5563', marginBottom: 32 }}>
                      Align controllers, procurement, tax, and risk in one InsightPulse command hub. Chat, copilots, and
                      automations stay observable, explainable, and regulator ready.
                    </Paragraph>
                    <Space size="large" wrap>
                      <Button type="primary" size="large" icon={<ThunderboltOutlined />}>
                        Explore live workspace
                      </Button>
                      <Button size="large" icon={<CheckCircleOutlined />}>
                        Download security brief
                      </Button>
                    </Space>
                    <div style={{ marginTop: 32, display: 'flex', gap: 32, flexWrap: 'wrap' }}>
                      {heroStats.map((item) => (
                        <div key={item.label}>
                          <Text strong style={{ fontSize: 16 }}>
                            {item.value}
                          </Text>
                          <div style={{ color: '#6b7280', fontSize: 14 }}>{item.label}</div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                </Col>
                <Col xs={24} lg={10}>
                  <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.2 }}>
                    <Card
                      style={{
                        borderRadius: 20,
                        background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%)',
                        color: 'white',
                        boxShadow: '0 20px 60px rgba(15, 23, 42, 0.35)',
                      }}
                    >
                      <Badge.Ribbon text="Live control center" color="cyan">
                        <div style={{ padding: 24, background: 'rgba(255, 255, 255, 0.04)', borderRadius: 16 }}>
                          <Title level={4} style={{ color: 'white' }}>
                            Financial Services Command Hub
                          </Title>
                          <Paragraph style={{ color: 'rgba(255,255,255,0.75)' }}>
                            Real-time visibility across reimbursements, supplier onboarding, and exception queues.
                          </Paragraph>
                          <Row gutter={[16, 16]}>
                            <Col span={12}>
                              <Statistic title={<span style={{ color: 'rgba(255,255,255,0.7)' }}>Critical workflows</span>} value={38} valueStyle={{ color: 'white' }} />
                            </Col>
                            <Col span={12}>
                              <Statistic title={<span style={{ color: 'rgba(255,255,255,0.7)' }}>Policy matches</span>} value={92} suffix="%" valueStyle={{ color: '#34d399' }} />
                            </Col>
                            <Col span={12}>
                              <Statistic title={<span style={{ color: 'rgba(255,255,255,0.7)' }}>Incidents resolved</span>} value={14} suffix="hrs" valueStyle={{ color: 'white' }} />
                            </Col>
                            <Col span={12}>
                              <Statistic title={<span style={{ color: 'rgba(255,255,255,0.7)' }}>Audit readiness</span>} value={5.0} suffix="/5" valueStyle={{ color: '#fbbf24' }} />
                            </Col>
                          </Row>
                        </div>
                      </Badge.Ribbon>
                    </Card>
                  </motion.div>
                </Col>
              </Row>

              <Divider style={{ margin: '64px 0' }} />
              <Space size="large" wrap>
                {trustBadges.map((badge) => (
                  <Tag key={badge} color="cyan" style={{ fontSize: 14, padding: '4px 16px' }}>
                    {badge}
                  </Tag>
                ))}
              </Space>
            </div>
          </section>

          <section id="platform" style={{ background: 'white', padding: '80px 24px' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <Title level={2} style={{ textAlign: 'center', marginBottom: 48 }}>
                Why regulated teams choose InsightPulse
              </Title>
              <Row gutter={[24, 24]}>
                {platformPillars.map((card) => (
                  <Col xs={24} md={8} key={card.title}>
                    <Card bordered hoverable>
                      <Space size="large" align="start">
                        <Avatar size={48} style={{ background: '#e0f2fe', color: '#0369a1' }}>
                          {card.icon}
                        </Avatar>
                        <div>
                          <Title level={4}>{card.title}</Title>
                          <Paragraph style={{ color: '#4b5563' }}>{card.description}</Paragraph>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          </section>

          <section style={{ padding: '80px 24px', background: '#0f172a', color: 'white' }}>
            <div style={{ maxWidth: 1100, margin: '0 auto' }}>
              <Title level={2} style={{ color: 'white', textAlign: 'center' }}>
                Deliver finance operations as a shared, transparent service
              </Title>
              <Paragraph style={{ color: 'rgba(255,255,255,0.7)', fontSize: 18, textAlign: 'center' }}>
                Mirroring the Mattermost experience, we highlight outcomes first: faster incident response, lower SaaS spend, and provable compliance posture.
              </Paragraph>
              <Row gutter={[24, 24]} style={{ marginTop: 48 }}>
                {capabilityHighlights.map((item) => (
                  <Col xs={24} md={8} key={item.title}>
                    <Card style={{ height: '100%', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}>
                      <Title level={4} style={{ color: 'white' }}>
                        {item.title}
                      </Title>
                      <Paragraph style={{ color: 'rgba(255,255,255,0.75)' }}>{item.body}</Paragraph>
                      <ul style={{ color: 'rgba(255,255,255,0.75)', paddingLeft: 20 }}>
                        {item.bullets.map((bullet) => (
                          <li key={bullet}>{bullet}</li>
                        ))}
                      </ul>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          </section>

          <section id="workflows" style={{ padding: '80px 24px', background: '#f8fafc' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <Row gutter={[32, 32]}>
                <Col xs={24} md={10}>
                  <Title level={2}>Playbooks for every finance and risk workflow</Title>
                  <Paragraph style={{ color: '#4b5563' }}>
                    Each tile mirrors a Mattermost-style use case block but tuned for InsightPulse: deep Odoo automation, embedded copilots, and security-first defaults.
                  </Paragraph>
                  <List
                    dataSource={complianceHighlights}
                    renderItem={(item) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<Avatar style={{ background: '#ecfccb', color: '#4d7c0f' }} icon={<LockOutlined />} />}
                          title={<Text strong>{item.label}</Text>}
                          description={<span style={{ color: '#4b5563' }}>{item.detail}</span>}
                        />
                      </List.Item>
                    )}
                  />
                </Col>
                <Col xs={24} md={14}>
                  <Row gutter={[24, 24]}>
                    {workflowPlaybooks.map((tile) => (
                      <Col span={24} md={12} key={tile.title}>
                        <Card style={{ height: '100%' }}>
                          <Space align="start" size="large">
                            <Avatar size={48} style={{ background: '#eff6ff', color: '#1d4ed8' }}>
                              {tile.icon}
                            </Avatar>
                            <div>
                              <Title level={4}>{tile.title}</Title>
                              <ul style={{ paddingLeft: 20, color: '#4b5563' }}>
                                {tile.bullets.map((bullet) => (
                                  <li key={bullet}>{bullet}</li>
                                ))}
                              </ul>
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </Col>
              </Row>
            </div>
          </section>

          <section id="security" style={{ padding: '80px 24px', background: 'white' }}>
            <div style={{ maxWidth: 1150, margin: '0 auto' }}>
              <Row gutter={[32, 32]} align="middle">
                <Col xs={24} md={12}>
                  <Title level={2}>Security architecture modeled after leading collaboration stacks</Title>
                  <Paragraph style={{ color: '#4b5563' }}>
                    We mirrored Mattermost's transparency by documenting every control: encryption posture, deployment hardening, and audit evidence, then extended it with Odoo-specific guardrails.
                  </Paragraph>
                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    {securityTiles.map((tile) => (
                      <div key={tile.title} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                        <Avatar size={56} style={{ background: tile.background, color: tile.color }}>
                          {tile.icon}
                        </Avatar>
                        <div>
                          <Text strong>{tile.title}</Text>
                          <Paragraph style={{ margin: 0, color: '#4b5563' }}>{tile.description}</Paragraph>
                        </div>
                      </div>
                    ))}
                  </Space>
                </Col>
                <Col xs={24} md={12}>
                  <Card style={{ borderRadius: 20 }}>
                    <Title level={4}>Risk telemetry snapshot</Title>
                    <Paragraph style={{ color: '#4b5563' }}>Live metrics streamed via OpenTelemetry to Superset.</Paragraph>
                    <div style={{ display: 'grid', gap: 24 }}>
                      <div>
                        <Text type="secondary">Policy automation coverage</Text>
                        <Progress percent={92} status="active" strokeColor="#22c55e" />
                      </div>
                      <div>
                        <Text type="secondary">AI explanation completeness</Text>
                        <Progress percent={88} strokeColor="#3b82f6" />
                      </div>
                      <div>
                        <Text type="secondary">Audit evidence freshness</Text>
                        <Progress percent={99} strokeColor="#fbbf24" />
                      </div>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </section>

          <section id="deployment" style={{ padding: '80px 24px', background: '#f1f5f9' }}>
            <div style={{ maxWidth: 1100, margin: '0 auto' }}>
              <Row gutter={[32, 32]} align="middle">
                <Col xs={24} md={14}>
                  <Title level={2}>From pilot to scale in three decisive phases</Title>
                  <Paragraph style={{ color: '#4b5563' }}>
                    Borrowing the progressive disclosure pattern from Mattermost, we map out every milestone so finance, IT, and risk leaders stay in lockstep.
                  </Paragraph>
                  <Timeline
                    items={deploymentPhases.map((item) => ({
                      color: '#0ea5e9',
                      children: (
                        <div>
                          <Text strong>{item.title}</Text>
                          <Paragraph style={{ marginBottom: 0, color: '#4b5563' }}>{item.description}</Paragraph>
                        </div>
                      ),
                    }))}
                  />
                </Col>
                <Col xs={24} md={10}>
                  <Card style={{ height: '100%' }}>
                    <Title level={4}>Executive-ready resources</Title>
                    <ul style={{ paddingLeft: 20, color: '#4b5563' }}>
                      {resourceHighlights.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    <Button type="primary" block style={{ marginTop: 16 }}>
                      Download full kit
                    </Button>
                  </Card>
                </Col>
              </Row>
            </div>
          </section>

          <section id="resources" style={{ padding: '80px 24px', background: 'white' }}>
            <div style={{ maxWidth: 1000, margin: '0 auto' }}>
              <Row gutter={[32, 32]} align="middle">
                <Col xs={24} md={14}>
                  <Title level={2}>"InsightPulse lets us move as fast as fintechs while proving compliance on demand."</Title>
                  <Paragraph style={{ color: '#4b5563' }}>
                    Chief Finance Transformation Officer, multi-agency SSC
                  </Paragraph>
                  <Divider />
                  <Space size="large" wrap>
                    <div>
                      <Title level={3} style={{ marginBottom: 0 }}>
                        40%
                      </Title>
                      <Text type="secondary">Faster vendor onboarding</Text>
                    </div>
                    <div>
                      <Title level={3} style={{ marginBottom: 0 }}>
                        30hrs
                      </Title>
                      <Text type="secondary">Manual reconciliations removed per week</Text>
                    </div>
                    <div>
                      <Title level={3} style={{ marginBottom: 0 }}>
                        6x
                      </Title>
                      <Text type="secondary">More audit-ready workflows</Text>
                    </div>
                  </Space>
                </Col>
                <Col xs={24} md={10}>
                  <Card>
                    <Title level={4}>Get a guided tour</Title>
                    <Paragraph style={{ color: '#4b5563' }}>Tell us about your agencies, ERPs, and security needs.</Paragraph>
                    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                      <Button block type="primary" icon={<ThunderboltOutlined />}>
                        Schedule white-glove demo
                      </Button>
                      <Button block icon={<LineChartOutlined />}>View ROI report</Button>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          </section>

          <section style={{ padding: '80px 24px', background: '#f8fafc' }}>
            <div style={{ maxWidth: 900, margin: '0 auto' }}>
              <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
                Frequently asked questions
              </Title>
              <Collapse accordion>
                {faqItems.map((item) => (
                  <Panel header={item.question} key={item.question}>
                    <Paragraph style={{ marginBottom: 0 }}>{item.answer}</Paragraph>
                  </Panel>
                ))}
              </Collapse>
            </div>
          </section>
        </Content>

        <Footer style={{ textAlign: 'center', background: '#0f172a', color: 'rgba(255,255,255,0.7)' }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
            <Title level={4} style={{ color: 'white' }}>
              Ready to replicate the Mattermost financial services experience for your SSC?
            </Title>
            <Space wrap>
              <Button type="primary" size="large">
                Launch InsightPulse
              </Button>
              <Button size="large" ghost>
                Talk to an architect
              </Button>
            </Space>
            <Paragraph style={{ marginTop: 24 }}>
              InsightPulse © {new Date().getFullYear()} • Odoo-native automation • SOC 2 | BIR | Superset analytics
            </Paragraph>
          </div>
        </Footer>
      </Layout>
    </>
  );
}
