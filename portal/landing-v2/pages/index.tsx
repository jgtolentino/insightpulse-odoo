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
} from 'antd';
import {
  RocketOutlined,
  SafetyOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  BarChartOutlined,
  CloudServerOutlined,
  AuditOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import Head from 'next/head';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

export default function Home() {
  return (
    <>
      <Head>
        <title>InsightPulse AI | Transform Finance SSC with Open-Source Innovation</title>
        <meta
          name="description"
          content="Multi-tenant, BIR-compliant Finance Shared Service Center platform. Save $52.7k/year by replacing SAP Concur, Ariba, and Tableau with 100% open-source solutions."
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Layout className="bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Navigation */}
        <Header
          style={{
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid #f0f0f0',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            padding: '0 50px',
          }}
        >
          <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Avatar size={40} style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                IP
              </Avatar>
              <div>
                <Text strong style={{ fontSize: 18 }}>InsightPulse AI</Text>
                <div style={{ fontSize: 12, color: '#666' }}>Finance SSC Automation</div>
              </div>
            </div>

            <Space size="large">
              <a href="#features" style={{ color: '#333' }}>Product</a>
              <a href="#compliance" style={{ color: '#333' }}>Compliance</a>
              <a href="#pricing" style={{ color: '#333' }}>Pricing</a>
              <Button type="primary" size="large" href="/app">
                Get Started
              </Button>
            </Space>
          </div>
        </Header>

        <Content>
          {/* Hero Section */}
          <section style={{ padding: '100px 50px', maxWidth: 1200, margin: '0 auto' }}>
            <Row gutter={[48, 48]} align="middle">
              <Col xs={24} lg={12}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                >
                  <Tag color="blue" style={{ marginBottom: 16 }}>
                    🚀 Save $52.7k/year with open-source
                  </Tag>

                  <Title level={1} style={{ fontSize: 56, marginBottom: 24, lineHeight: 1.2 }}>
                    Transform Finance SSC with{' '}
                    <span style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                      AI-Powered Automation
                    </span>
                  </Title>

                  <Paragraph style={{ fontSize: 18, color: '#666', marginBottom: 32 }}>
                    Multi-tenant, BIR-compliant Finance Shared Service Center platform built on Odoo 18 CE.
                    Replace SAP Concur, Ariba, and Tableau with 100% open-source solutions trusted by 8 Philippine agencies.
                  </Paragraph>

                  <Space size="large">
                    <Button type="primary" size="large" icon={<RocketOutlined />}>
                      Start Free Trial
                    </Button>
                    <Button size="large">
                      Book Demo
                    </Button>
                  </Space>

                  <div style={{ marginTop: 32 }}>
                    <Text type="secondary" style={{ fontSize: 14 }}>
                      ✓ 99.9% uptime SLA &nbsp;•&nbsp; ✓ BIR-compliant &nbsp;•&nbsp; ✓ Multi-tenant ready
                    </Text>
                  </div>
                </motion.div>
              </Col>

              <Col xs={24} lg={12}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <Card
                    style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      border: 'none',
                      borderRadius: 16,
                      boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
                    }}
                  >
                    <div style={{ color: 'white' }}>
                      <Badge.Ribbon text="Live System" color="green">
                        <div style={{ padding: 24, background: 'rgba(255, 255, 255, 0.1)', borderRadius: 12 }}>
                          <Title level={4} style={{ color: 'white', marginBottom: 16 }}>
                            Finance SSC Dashboard
                          </Title>

                          <Row gutter={[16, 16]}>
                            <Col span={12}>
                              <Statistic
                                title={<span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Expenses Processed</span>}
                                value={1284}
                                suffix="/month"
                                valueStyle={{ color: 'white' }}
                              />
                            </Col>
                            <Col span={12}>
                              <Statistic
                                title={<span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Auto-Approval Rate</span>}
                                value={87}
                                suffix="%"
                                valueStyle={{ color: '#52c41a' }}
                              />
                            </Col>
                            <Col span={12}>
                              <Statistic
                                title={<span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>OCR Accuracy</span>}
                                value={94.3}
                                suffix="%"
                                valueStyle={{ color: 'white' }}
                              />
                            </Col>
                            <Col span={12}>
                              <Statistic
                                title={<span style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Processing Time</span>}
                                value={18}
                                suffix="sec"
                                valueStyle={{ color: 'white' }}
                              />
                            </Col>
                          </Row>
                        </div>
                      </Badge.Ribbon>
                    </div>
                  </Card>
                </motion.div>
              </Col>
            </Row>
          </section>

          {/* Cost Savings Section */}
          <section style={{ padding: '80px 50px', background: 'white' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <div style={{ textAlign: 'center', marginBottom: 60 }}>
                <Title level={2}>Replace expensive SaaS tools with open-source excellence</Title>
                <Paragraph style={{ fontSize: 16, color: '#666' }}>
                  Save $52,700 annually while gaining full control and customization
                </Paragraph>
              </div>

              <Row gutter={[24, 24]}>
                {[
                  { name: 'SAP Concur', replacement: 'Odoo Expense', savings: '$15,000' },
                  { name: 'SAP Ariba', replacement: 'Odoo Procurement', savings: '$12,000' },
                  { name: 'Tableau', replacement: 'Apache Superset', savings: '$8,400' },
                  { name: 'Slack Enterprise', replacement: 'Mattermost', savings: '$12,600' },
                  { name: 'Odoo Enterprise', replacement: 'Odoo CE + OCA', savings: '$4,700' },
                ].map((item, index) => (
                  <Col xs={24} sm={12} lg={8} key={index}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      viewport={{ once: true }}
                    >
                      <Card hoverable style={{ height: '100%' }}>
                        <div style={{ textAlign: 'center' }}>
                          <DollarOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 16 }} />
                          <Title level={4} style={{ marginBottom: 8 }}>{item.replacement}</Title>
                          <Text type="secondary" style={{ textDecoration: 'line-through' }}>
                            {item.name}
                          </Text>
                          <div style={{ marginTop: 16 }}>
                            <Tag color="green" style={{ fontSize: 16, padding: '4px 12px' }}>
                              Save {item.savings}/year
                            </Tag>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  </Col>
                ))}
              </Row>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" style={{ padding: '80px 50px', background: '#fafafa' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <div style={{ textAlign: 'center', marginBottom: 60 }}>
                <Title level={2}>Enterprise-grade features for Finance SSC</Title>
                <Paragraph style={{ fontSize: 16, color: '#666' }}>
                  Built for Philippine compliance, multi-agency operations, and scale
                </Paragraph>
              </div>

              <Row gutter={[32, 32]}>
                <Col xs={24} md={12} lg={6}>
                  <Card bordered={false} style={{ textAlign: 'center', height: '100%' }}>
                    <AuditOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
                    <Title level={4}>BIR Compliance</Title>
                    <Paragraph style={{ color: '#666' }}>
                      Automated Forms 1601-C, 1702-RT, 2550Q/M generation. Immutable audit trails for PH tax requirements.
                    </Paragraph>
                  </Card>
                </Col>

                <Col xs={24} md={12} lg={6}>
                  <Card bordered={false} style={{ textAlign: 'center', height: '100%' }}>
                    <GlobalOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
                    <Title level={4}>Multi-Tenant</Title>
                    <Paragraph style={{ color: '#666' }}>
                      Legal entity isolation with company_id. Serve 8 agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB.
                    </Paragraph>
                  </Card>
                </Col>

                <Col xs={24} md={12} lg={6}>
                  <Card bordered={false} style={{ textAlign: 'center', height: '100%' }}>
                    <BarChartOutlined style={{ fontSize: 48, color: '#722ed1', marginBottom: 16 }} />
                    <Title level={4}>Analytics & BI</Title>
                    <Paragraph style={{ color: '#666' }}>
                      Apache Superset dashboards, SQL views, and real-time metrics. Tableau Cloud alternative.
                    </Paragraph>
                  </Card>
                </Col>

                <Col xs={24} md={12} lg={6}>
                  <Card bordered={false} style={{ textAlign: 'center', height: '100%' }}>
                    <CloudServerOutlined style={{ fontSize: 48, color: '#eb2f96', marginBottom: 16 }} />
                    <Title level={4}>Cloud Native</Title>
                    <Paragraph style={{ color: '#666' }}>
                      DigitalOcean App Platform, Supabase PostgreSQL, and Docker containers. 99.9% uptime SLA.
                    </Paragraph>
                  </Card>
                </Col>
              </Row>
            </div>
          </section>

          {/* Compliance Section */}
          <section id="compliance" style={{ padding: '80px 50px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <Row gutter={[48, 48]} align="middle">
                <Col xs={24} lg={12}>
                  <Title level={2} style={{ color: 'white' }}>
                    BIR-compliant by design
                  </Title>
                  <Paragraph style={{ fontSize: 16, color: 'rgba(255, 255, 255, 0.9)', marginBottom: 32 }}>
                    InsightPulse AI is built from the ground up to meet Philippine Bureau of Internal Revenue requirements.
                    Every transaction, every document, every approval is tracked with immutable audit trails.
                  </Paragraph>

                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    <Card style={{ background: 'rgba(255, 255, 255, 0.1)', border: 'none' }}>
                      <Space>
                        <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                        <div>
                          <Text strong style={{ color: 'white', display: 'block' }}>Immutable Records</Text>
                          <Text style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                            Posted journal entries cannot be modified, only reversed
                          </Text>
                        </div>
                      </Space>
                    </Card>

                    <Card style={{ background: 'rgba(255, 255, 255, 0.1)', border: 'none' }}>
                      <Space>
                        <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                        <div>
                          <Text strong style={{ color: 'white', display: 'block' }}>Automated Tax Forms</Text>
                          <Text style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                            Forms 1601-C, 1702-RT, 2550Q/M generated automatically
                          </Text>
                        </div>
                      </Space>
                    </Card>

                    <Card style={{ background: 'rgba(255, 255, 255, 0.1)', border: 'none' }}>
                      <Space>
                        <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                        <div>
                          <Text strong style={{ color: 'white', display: 'block' }}>E-Invoice Ready</Text>
                          <Text style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                            Prepared for 2025 BIR e-invoicing rollout
                          </Text>
                        </div>
                      </Space>
                    </Card>
                  </Space>
                </Col>

                <Col xs={24} lg={12}>
                  <Card>
                    <Title level={4}>Monthly Processing Volume</Title>
                    <Divider />
                    <Row gutter={[16, 16]}>
                      <Col span={8}>
                        <Statistic
                          title="Expenses"
                          value={1284}
                          suffix="docs"
                          valueStyle={{ color: '#1890ff' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="Invoices"
                          value={856}
                          suffix="docs"
                          valueStyle={{ color: '#52c41a' }}
                        />
                      </Col>
                      <Col span={8}>
                        <Statistic
                          title="Payments"
                          value={342}
                          suffix="txns"
                          valueStyle={{ color: '#722ed1' }}
                        />
                      </Col>
                    </Row>
                    <Divider />
                    <Title level={5}>Active Agencies</Title>
                    <Space wrap style={{ marginTop: 16 }}>
                      {['RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB'].map((agency) => (
                        <Tag key={agency} color="blue" style={{ fontSize: 14, padding: '4px 12px' }}>
                          {agency}
                        </Tag>
                      ))}
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          </section>

          {/* Use Cases Section */}
          <section style={{ padding: '80px 50px', background: 'white' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
              <div style={{ textAlign: 'center', marginBottom: 60 }}>
                <Title level={2}>Built for Finance SSC operations</Title>
                <Paragraph style={{ fontSize: 16, color: '#666' }}>
                  Streamline workflows across procurement, expense management, and analytics
                </Paragraph>
              </div>

              <Collapse
                defaultActiveKey={['1']}
                expandIconPosition="end"
                ghost
                items={[
                  {
                    key: '1',
                    label: <Title level={4}>OCR-Powered Expense Automation</Title>,
                    children: (
                      <Paragraph style={{ fontSize: 16, color: '#666' }}>
                        PaddleOCR with DeepSeek LLM validation extracts receipt data with 94% accuracy.
                        Automated policy validation, multi-level approvals, and BIR Form 2307 generation.
                        87% auto-approval rate with sub-30-second processing.
                      </Paragraph>
                    ),
                  },
                  {
                    key: '2',
                    label: <Title level={4}>Multi-Agency Procurement</Title>,
                    children: (
                      <Paragraph style={{ fontSize: 16, color: '#666' }}>
                        Replace SAP Ariba with Odoo Procurement. RFQ workflows, vendor management,
                        purchase orders, and three-way matching. Privacy-compliant vendor portals
                        with role-based access control for rate inquiries.
                      </Paragraph>
                    ),
                  },
                  {
                    key: '3',
                    label: <Title level={4}>Analytics & Business Intelligence</Title>,
                    children: (
                      <Paragraph style={{ fontSize: 16, color: '#666' }}>
                        Apache Superset dashboards integrated with Odoo analytics.
                        SQL views, materialized views, and real-time metrics.
                        Replace Tableau Cloud at 1/10th the cost with full customization.
                      </Paragraph>
                    ),
                  },
                  {
                    key: '4',
                    label: <Title level={4}>Month-End Closing Automation</Title>,
                    children: (
                      <Paragraph style={{ fontSize: 16, color: '#666' }}>
                        Automated journal entries, bank reconciliation, trial balance generation,
                        and multi-agency consolidation. BIR-compliant audit trails and
                        immutable accounting records ensure regulatory compliance.
                      </Paragraph>
                    ),
                  },
                ]}
              />
            </div>
          </section>

          {/* CTA Section */}
          <section style={{ padding: '100px 50px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', textAlign: 'center' }}>
            <div style={{ maxWidth: 800, margin: '0 auto' }}>
              <Title level={2}>Ready to transform your Finance SSC?</Title>
              <Paragraph style={{ fontSize: 18, color: '#666', marginBottom: 40 }}>
                Join 8 Philippine agencies saving $52.7k/year with open-source excellence
              </Paragraph>

              <Space size="large">
                <Button type="primary" size="large" icon={<RocketOutlined />}>
                  Start Free Trial
                </Button>
                <Button size="large">
                  Schedule Demo
                </Button>
              </Space>

              <div style={{ marginTop: 40 }}>
                <Text type="secondary">
                  No credit card required • 14-day free trial • Cancel anytime
                </Text>
              </div>
            </div>
          </section>
        </Content>

        {/* Footer */}
        <Footer style={{ background: '#001529', color: 'rgba(255, 255, 255, 0.65)', textAlign: 'center' }}>
          <Row gutter={[32, 32]} style={{ maxWidth: 1200, margin: '0 auto', textAlign: 'left' }}>
            <Col xs={24} sm={12} md={6}>
              <Title level={5} style={{ color: 'white' }}>Product</Title>
              <Space direction="vertical">
                <a href="#features" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Features</a>
                <a href="#compliance" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Compliance</a>
                <a href="#pricing" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Pricing</a>
              </Space>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Title level={5} style={{ color: 'white' }}>Resources</Title>
              <Space direction="vertical">
                <a href="https://jgtolentino.github.io/insightpulse-odoo/" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Documentation</a>
                <a href="/api" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>API Reference</a>
                <a href="https://github.com/jgtolentino/insightpulse-odoo" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>GitHub</a>
              </Space>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Title level={5} style={{ color: 'white' }}>Company</Title>
              <Space direction="vertical">
                <a href="/about" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>About</a>
                <a href="https://insightpulseai.net" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Status</a>
                <a href="/contact" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Contact</a>
              </Space>
            </Col>

            <Col xs={24} sm={12} md={6}>
              <Title level={5} style={{ color: 'white' }}>Legal</Title>
              <Space direction="vertical">
                <a href="/privacy" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Privacy</a>
                <a href="/terms" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Terms</a>
                <a href="/security" style={{ color: 'rgba(255, 255, 255, 0.65)' }}>Security</a>
              </Space>
            </Col>
          </Row>

          <Divider style={{ borderColor: 'rgba(255, 255, 255, 0.2)', margin: '40px 0 24px' }} />

          <Text style={{ color: 'rgba(255, 255, 255, 0.45)' }}>
            © 2025 InsightPulse AI. Built with ❤️ for Philippine Finance SSC.
          </Text>
        </Footer>
      </Layout>

      <style jsx global>{`
        body {
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
        }

        * {
          box-sizing: border-box;
        }

        a {
          text-decoration: none;
          transition: all 0.3s ease;
        }

        a:hover {
          opacity: 0.8;
        }
      `}</style>
    </>
  );
}
