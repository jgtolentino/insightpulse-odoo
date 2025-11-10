/**
 * Installation Workflow Prompt
 */

export async function getInstallationPrompt(args: any) {
  return {
    messages: [
      {
        role: 'user',
        content: {
          type: 'text',
          text: 'Installation prompt coming soon',
        },
      },
    ],
  };
}
