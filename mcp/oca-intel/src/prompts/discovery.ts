/**
 * Module Discovery Prompt
 */

export async function getModuleDiscoveryPrompt(args: any) {
  return {
    messages: [
      {
        role: 'user',
        content: {
          type: 'text',
          text: 'Module discovery prompt coming soon',
        },
      },
    ],
  };
}
