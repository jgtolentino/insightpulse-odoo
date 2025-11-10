/**
 * Compatibility Matrix Resource
 */

export async function getCompatibilityMatrix() {
  return {
    contents: [
      {
        uri: 'oca://compatibility/matrix',
        mimeType: 'application/json',
        text: 'Compatibility matrix coming soon',
      },
    ],
  };
}
