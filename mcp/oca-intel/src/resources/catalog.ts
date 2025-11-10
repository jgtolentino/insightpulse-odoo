/**
 * Module Catalog Resource
 */

export async function getModuleCatalog() {
  return {
    contents: [
      {
        uri: 'oca://modules/catalog',
        mimeType: 'application/json',
        text: 'Module catalog coming soon',
      },
    ],
  };
}
