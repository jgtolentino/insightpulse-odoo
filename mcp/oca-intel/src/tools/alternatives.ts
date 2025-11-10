/**
 * Enterprise Alternatives Suggester
 * Maps Odoo Enterprise modules to OCA alternatives
 */

interface AlternativesArgs {
  enterprise_module: string;
  version?: string;
}

const ENTERPRISE_TO_OCA_MAP: Record<string, any> = {
  web_studio: {
    alternative: 'Direct development (no GUI alternative)',
    oca_repos: [],
    install_instead: ['base_automation'],
    notes: 'Studio has no direct OCA alternative. Use XML views + Python models.',
    parity: '60%',
  },
  account_reports: {
    alternative: 'account_financial_report',
    oca_repos: ['account-financial-reporting'],
    install_instead: ['account_financial_report', 'mis_builder', 'report_xlsx'],
    notes: '95% feature parity with Enterprise accounting reports',
    parity: '95%',
  },
  documents: {
    alternative: 'dms',
    oca_repos: ['dms'],
    install_instead: ['dms', 'dms_field', 'attachment_preview'],
    notes: 'Full document management system with folder hierarchy',
    parity: '85%',
  },
  helpdesk: {
    alternative: 'helpdesk_mgmt',
    oca_repos: ['helpdesk'],
    install_instead: ['helpdesk_mgmt', 'helpdesk_mgmt_timesheet', 'helpdesk_mgmt_project'],
    notes: 'Complete helpdesk solution with SLA tracking',
    parity: '90%',
  },
  sign: {
    alternative: 'agreement_legal',
    oca_repos: ['contract'],
    install_instead: ['agreement', 'agreement_legal'],
    notes: 'Contract management without e-signature (use DocuSign/HelloSign API)',
    parity: '50%',
  },
  planning: {
    alternative: 'resource_booking',
    oca_repos: ['calendar'],
    install_instead: ['resource_booking', 'resource_calendar'],
    notes: 'Resource planning and scheduling',
    parity: '70%',
  },
  quality_control: {
    alternative: 'quality_control',
    oca_repos: ['manufacture'],
    install_instead: ['quality_control', 'quality_control_stock'],
    notes: 'QC inspections and tests',
    parity: '80%',
  },
  approvals: {
    alternative: 'base_tier_validation',
    oca_repos: ['server-tools'],
    install_instead: ['base_tier_validation', 'purchase_tier_validation', 'sale_tier_validation'],
    notes: 'Multi-tier approval workflows',
    parity: '85%',
  },
  hr_appraisal: {
    alternative: 'hr_appraisal',
    oca_repos: ['hr'],
    install_instead: ['hr_appraisal'],
    notes: 'Employee appraisal management',
    parity: '75%',
  },
  hr_recruitment: {
    alternative: 'hr_recruitment',
    oca_repos: ['hr'],
    install_instead: ['hr_recruitment'],
    notes: 'Recruitment and candidate management',
    parity: '80%',
  },
};

export async function suggestAlternatives(args: AlternativesArgs) {
  const { enterprise_module, version = '18.0' } = args;

  const alternative = ENTERPRISE_TO_OCA_MAP[enterprise_module];

  if (!alternative) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            enterprise_module,
            found: false,
            message: `No OCA alternative found for ${enterprise_module}`,
            suggestion: 'Consider custom development or third-party integrations',
          }, null, 2),
        },
      ],
    };
  }

  // Generate installation script
  const installScript = alternative.install_instead
    .map((mod: string) => `odoo-bin -d database -i ${mod} --stop-after-init`)
    .join('\n');

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          enterprise_module,
          found: true,
          version,
          alternative: {
            ...alternative,
            installation: {
              command: installScript,
              steps: [
                'Update module list: odoo-bin -d database --update=all',
                ...alternative.install_instead.map((m: string) => `Install ${m}`),
                'Restart Odoo service',
              ],
            },
            cost_savings: {
              enterprise_license: '$4,728/year',
              oca_alternative: '$0/year',
              savings: '$4,728/year',
            },
          },
        }, null, 2),
      },
    ],
  };
}
