/**
 * Installation Guides Resource
 */

export async function getInstallationGuides() {
  return {
    contents: [
      {
        uri: 'oca://guides/installation',
        mimeType: 'text/markdown',
        text: 'Installation guides coming soon',
      },
    ],
  };
}
