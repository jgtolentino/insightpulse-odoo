#!/usr/bin/env node
/**
 * Upload Visual Regression Artifacts to Cloud Storage
 *
 * Uploads diff screenshots and reports to S3, Azure Blob, or OSS
 * Usage: npm run visual:upload
 */

import fs from 'fs';
import path from 'path';

// This is a template - implement based on your cloud provider
// Supported providers: AWS S3, Azure Blob Storage, Alibaba OSS

interface UploadConfig {
  provider: 's3' | 'azure' | 'oss' | 'local';
  bucket?: string;
  containerName?: string;
  region?: string;
  accessKeyId?: string;
  secretAccessKey?: string;
}

/**
 * Get upload configuration from environment
 */
function getUploadConfig(): UploadConfig {
  const provider = (process.env.VISUAL_STORAGE_PROVIDER || 'local') as UploadConfig['provider'];

  return {
    provider,
    bucket: process.env.VISUAL_STORAGE_BUCKET,
    containerName: process.env.VISUAL_STORAGE_CONTAINER,
    region: process.env.VISUAL_STORAGE_REGION,
    accessKeyId: process.env.VISUAL_STORAGE_ACCESS_KEY,
    secretAccessKey: process.env.VISUAL_STORAGE_SECRET_KEY,
  };
}

/**
 * Upload to AWS S3
 */
async function uploadToS3(files: string[], config: UploadConfig): Promise<string[]> {
  // Implementation example (requires aws-sdk or @aws-sdk/client-s3)
  console.log('📦 Uploading to AWS S3...');

  /*
  const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

  const client = new S3Client({
    region: config.region,
    credentials: {
      accessKeyId: config.accessKeyId!,
      secretAccessKey: config.secretAccessKey!,
    },
  });

  const urls: string[] = [];

  for (const file of files) {
    const key = `visual-regression/${Date.now()}/${path.basename(file)}`;
    const fileContent = fs.readFileSync(file);

    await client.send(new PutObjectCommand({
      Bucket: config.bucket,
      Key: key,
      Body: fileContent,
      ContentType: 'image/png',
    }));

    const url = `https://${config.bucket}.s3.${config.region}.amazonaws.com/${key}`;
    urls.push(url);
    console.log(`  ✅ ${path.basename(file)} -> ${url}`);
  }

  return urls;
  */

  throw new Error('S3 upload not implemented. Install @aws-sdk/client-s3 and uncomment the code above.');
}

/**
 * Upload to Azure Blob Storage
 */
async function uploadToAzure(files: string[], config: UploadConfig): Promise<string[]> {
  console.log('📦 Uploading to Azure Blob Storage...');

  /*
  const { BlobServiceClient } = require('@azure/storage-blob');

  const connectionString = process.env.AZURE_STORAGE_CONNECTION_STRING;
  const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString!);
  const containerClient = blobServiceClient.getContainerClient(config.containerName!);

  const urls: string[] = [];

  for (const file of files) {
    const blobName = `visual-regression/${Date.now()}/${path.basename(file)}`;
    const blockBlobClient = containerClient.getBlockBlobClient(blobName);

    await blockBlobClient.uploadFile(file);

    const url = blockBlobClient.url;
    urls.push(url);
    console.log(`  ✅ ${path.basename(file)} -> ${url}`);
  }

  return urls;
  */

  throw new Error('Azure upload not implemented. Install @azure/storage-blob and uncomment the code above.');
}

/**
 * Upload to Alibaba OSS
 */
async function uploadToOSS(files: string[], config: UploadConfig): Promise<string[]> {
  console.log('📦 Uploading to Alibaba OSS...');

  /*
  const OSS = require('ali-oss');

  const client = new OSS({
    region: config.region,
    accessKeyId: config.accessKeyId,
    accessKeySecret: config.secretAccessKey,
    bucket: config.bucket,
  });

  const urls: string[] = [];

  for (const file of files) {
    const objectName = `visual-regression/${Date.now()}/${path.basename(file)}`;
    const result = await client.put(objectName, file);

    urls.push(result.url);
    console.log(`  ✅ ${path.basename(file)} -> ${result.url}`);
  }

  return urls;
  */

  throw new Error('OSS upload not implemented. Install ali-oss and uncomment the code above.');
}

/**
 * Local "upload" - just copy to a public directory
 */
function uploadToLocal(files: string[], outputDir: string = 'public/visual-regression'): string[] {
  console.log('📁 Copying to local directory...');

  const targetDir = path.join(process.cwd(), outputDir, Date.now().toString());

  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  const urls: string[] = [];

  for (const file of files) {
    const targetPath = path.join(targetDir, path.basename(file));
    fs.copyFileSync(file, targetPath);

    const url = `/${path.relative(process.cwd(), targetPath)}`;
    urls.push(url);
    console.log(`  ✅ ${path.basename(file)} -> ${url}`);
  }

  return urls;
}

/**
 * Upload artifacts based on configuration
 */
async function uploadArtifacts(): Promise<string[]> {
  const config = getUploadConfig();

  // Collect files to upload
  const diffDir = path.join(process.cwd(), '__image_snapshots__', 'diff');
  const reportPath = path.join(process.cwd(), 'visual-report.html');

  const files: string[] = [];

  if (fs.existsSync(diffDir)) {
    const diffFiles = fs.readdirSync(diffDir)
      .filter(f => f.endsWith('.png'))
      .map(f => path.join(diffDir, f));
    files.push(...diffFiles);
  }

  if (fs.existsSync(reportPath)) {
    files.push(reportPath);
  }

  if (files.length === 0) {
    console.log('ℹ️  No artifacts to upload');
    return [];
  }

  console.log(`\n📤 Uploading ${files.length} files using provider: ${config.provider}\n`);

  // Upload based on provider
  switch (config.provider) {
    case 's3':
      return uploadToS3(files, config);
    case 'azure':
      return uploadToAzure(files, config);
    case 'oss':
      return uploadToOSS(files, config);
    case 'local':
    default:
      return uploadToLocal(files);
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    const urls = await uploadArtifacts();

    console.log(`\n✅ Upload complete! ${urls.length} files uploaded.\n`);
    console.log('URLs:');
    urls.forEach(url => console.log(`  - ${url}`));

    // Write URLs to file for CI/CD consumption
    const urlsPath = path.join(process.cwd(), 'visual-artifact-urls.json');
    fs.writeFileSync(urlsPath, JSON.stringify({ urls, timestamp: new Date().toISOString() }, null, 2));
    console.log(`\n📄 URLs written to: ${urlsPath}`);

  } catch (error) {
    console.error('\n❌ Upload failed:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { uploadArtifacts };
