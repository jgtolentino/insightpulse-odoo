/**
 * Environment Variable Validation
 *
 * Provides runtime validation of environment variables with clear error messages.
 * Prevents crashes from missing or malformed values (e.g., literal "${VAR}" placeholders).
 */

function requireStringEnv(name: string, defaultValue?: string): string {
  const value = process.env[name] || defaultValue;

  if (!value || value.trim() === '') {
    console.error(`❌ ${name} is required but not set.`);
    console.error(`   Set it in DigitalOcean: Apps → pulse-hub-web → Settings → Environment Variables`);
    process.exit(1);
  }

  // Warn if looks like a placeholder (common misconfiguration)
  if (value.startsWith('${') && value.endsWith('}')) {
    console.error(`❌ ${name} is set to a placeholder ('${value}').`);
    console.error(`   Replace with the actual value in DigitalOcean dashboard.`);
    console.error(`   DO NOT use shell-style \${VAR} syntax in YAML value fields.`);
    process.exit(1);
  }

  return value;
}

function requireIntEnv(name: string, defaultValue?: number): number {
  const raw = process.env[name];
  const value = raw !== undefined ? raw : defaultValue?.toString();

  if (value === undefined || value.trim() === '') {
    console.error(`❌ ${name} is required but not set.`);
    console.error(`   Set it in DigitalOcean: Apps → pulse-hub-web → Settings → Environment Variables`);
    process.exit(1);
  }

  const parsed = parseInt(value, 10);
  if (isNaN(parsed)) {
    console.error(`❌ ${name} must be a number (got: '${value}').`);
    console.error(`   Check DigitalOcean dashboard for literal placeholders like '\${${name}}'`);
    process.exit(1);
  }

  return parsed;
}

function getOptionalStringEnv(name: string, defaultValue: string = ''): string {
  const value = process.env[name];

  if (!value) {
    return defaultValue;
  }

  // Warn if looks like a placeholder
  if (value.startsWith('${') && value.endsWith('}')) {
    console.warn(`⚠️  ${name} appears to be a placeholder ('${value}').`);
    console.warn(`   This may cause runtime errors. Set actual value in DigitalOcean dashboard.`);
  }

  return value;
}

// Export validated environment variables
export const env = {
  // Server configuration
  PORT: requireIntEnv('PORT', 3000),

  // GitHub App configuration
  GITHUB_APP_ID: getOptionalStringEnv('GITHUB_APP_ID'),
  GITHUB_CLIENT_ID: getOptionalStringEnv('GITHUB_CLIENT_ID'),
  GITHUB_CLIENT_SECRET: getOptionalStringEnv('GITHUB_CLIENT_SECRET'),
  GITHUB_WEBHOOK_SECRET: getOptionalStringEnv('GITHUB_WEBHOOK_SECRET'),

  // Supabase configuration
  SUPABASE_URL: requireStringEnv('SUPABASE_URL'),
  SUPABASE_SERVICE_ROLE_KEY: requireStringEnv('SUPABASE_SERVICE_ROLE_KEY'),

  // Environment
  NODE_ENV: process.env.NODE_ENV || 'development',
};

// Log loaded configuration (redact secrets)
console.log('Environment configuration loaded:');
console.log(`  PORT: ${env.PORT}`);
console.log(`  GITHUB_APP_ID: ${env.GITHUB_APP_ID ? '***' : '(not set)'}`);
console.log(`  GITHUB_CLIENT_ID: ${env.GITHUB_CLIENT_ID ? '***' : '(not set)'}`);
console.log(`  GITHUB_CLIENT_SECRET: ${env.GITHUB_CLIENT_SECRET ? '***' : '(not set)'}`);
console.log(`  GITHUB_WEBHOOK_SECRET: ${env.GITHUB_WEBHOOK_SECRET ? '***' : '(not set)'}`);
console.log(`  SUPABASE_URL: ${env.SUPABASE_URL}`);
console.log(`  SUPABASE_SERVICE_ROLE_KEY: ${env.SUPABASE_SERVICE_ROLE_KEY ? '***' : '(not set)'}`);
console.log(`  NODE_ENV: ${env.NODE_ENV}`);
console.log('');

// Export validation functions for use in other modules
export { requireStringEnv, requireIntEnv, getOptionalStringEnv };
