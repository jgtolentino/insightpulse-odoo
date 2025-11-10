/**
 * Migration Planning Prompt
 */

export async function getMigrationPrompt(args: any) {
  return {
    messages: [
      {
        role: 'user',
        content: {
          type: 'text',
          text: 'Migration prompt coming soon',
        },
      },
    ],
  };
}
