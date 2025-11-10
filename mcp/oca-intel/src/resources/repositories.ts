/**
 * OCA Repositories Resource
 */

export async function getOCARepositories() {
  const repositories = {
    accounting: [
      { name: 'account-financial-reporting', branch_18: true, stars: 450 },
      { name: 'account-financial-tools', branch_18: true, stars: 380 },
      { name: 'account-analytic', branch_18: true, stars: 120 },
    ],
    documents: [
      { name: 'dms', branch_18: true, stars: 250 },
    ],
    helpdesk: [
      { name: 'helpdesk', branch_18: true, stars: 180 },
    ],
    hr: [
      { name: 'hr-payroll', branch_18: true, stars: 320 },
      { name: 'hr-attendance', branch_18: true, stars: 150 },
    ],
    purchase: [
      { name: 'purchase-workflow', branch_18: true, stars: 200 },
    ],
    infrastructure: [
      { name: 'server-tools', branch_18: true, stars: 500 },
      { name: 'web', branch_18: true, stars: 400 },
      { name: 'reporting-engine', branch_18: true, stars: 300 },
    ],
  };

  return {
    contents: [
      {
        uri: 'oca://repositories/all',
        mimeType: 'application/json',
        text: JSON.stringify(repositories, null, 2),
      },
    ],
  };
}
