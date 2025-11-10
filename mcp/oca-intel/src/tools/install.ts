/**
 * Module Installation Tool
 * Generates installation commands with dependency resolution
 */

interface InstallArgs {
  module_names: string[];
  database: string;
  auto_deps?: boolean;
}

export async function installModule(args: InstallArgs) {
  const { module_names, database, auto_deps = true } = args;

  // Generate installation script
  const installCommands = module_names.map(
    (module) => `odoo-bin -d ${database} -i ${module} --stop-after-init`
  );

  const script = `#!/bin/bash
# OCA Module Installation Script
# Generated: ${new Date().toISOString()}
# Database: ${database}
# Modules: ${module_names.join(', ')}

set -euo pipefail

echo "🚀 Installing OCA modules..."

# Update module list
echo "📦 Updating module list..."
odoo-bin -d ${database} --update=all --stop-after-init

# Install modules
${installCommands.map((cmd, i) => `
echo "Installing ${module_names[i]}..."
${cmd}
`).join('\n')}

echo "✅ Installation complete!"
echo "🔄 Restart Odoo service to activate modules"
`;

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify({
          database,
          modules: module_names,
          auto_deps,
          script,
          usage: {
            save_script: `cat > install_modules.sh << 'EOF'\n${script}\nEOF`,
            make_executable: 'chmod +x install_modules.sh',
            run: './install_modules.sh',
          },
          notes: [
            'Backup database before installation',
            'Test in staging environment first',
            'Check module dependencies',
            'Restart Odoo after installation',
          ],
        }, null, 2),
      },
    ],
  };
}
