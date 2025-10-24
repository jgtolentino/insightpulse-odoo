---
name: odoo-apps-manager
description: Comprehensive Odoo apps management using SuperClaude framework - install, activate, upgrade all apps with sub-agent coordination
version: 1.0.0
tags: [odoo, apps, management, installation, activation, upgrade, deployment, superclaude]
requires:
  files:
    - superclaude/knowledge/ODOO_19_REFERENCE.md
    - vendor/oca-apps-store/apps/
uses:
  skills:
    - oca-module-discovery
    - oca-compliance-check
    - odoo-sh-devops
    - connector-integration-expert
---

# Odoo Apps Manager Skill

## Purpose

Manage complete Odoo application lifecycle using SuperClaude framework - install, activate, upgrade all apps with coordinated sub-agent execution for your InsightPulseAI Odoo instance.

## When to use

- Installing and activating all Odoo applications
- Upgrading existing modules and apps
- Managing app dependencies and compatibility
- Coordinating multiple sub-agents for deployment
- Handling app configuration and customization
- Monitoring app performance and health

## Actions

1. **App Discovery**: Scan and identify all available Odoo apps
2. **Dependency Analysis**: Analyze app dependencies and requirements
3. **Installation Coordination**: Install apps with proper dependency order
4. **Activation Management**: Activate and configure installed apps
5. **Upgrade Planning**: Plan and execute app upgrades
6. **Health Monitoring**: Monitor app performance and functionality
7. **Sub-Agent Coordination**: Coordinate specialized agents for different app categories

## Inputs

- `odoo_url`: Odoo instance URL (https://insightpulseai.net/odoo)
- `action_type`: Install, activate, upgrade, or all
- `app_categories`: Specific app categories to manage
- `upgrade_strategy`: Upgrade approach (incremental, batch, all)
- `sub_agent_coordination`: Use sub-agents for specialized tasks

## Outputs

- Complete app installation/activation report
- Dependency resolution plan
- Upgrade execution strategy
- Health monitoring dashboard
- Sub-agent coordination logs
- Performance optimization recommendations

## Examples

### Example 1: Complete App Installation
```
User: "Install and activate all Odoo apps for InsightPulseAI"

Agent:
1. Scans https://insightpulseai.net/odoo for current app status
2. Coordinates sub-agents:
   - oca-module-discovery: Finds all available OCA modules
   - oca-compliance-check: Validates module compatibility
   - odoo-sh-devops: Manages deployment pipeline
3. Installs apps in dependency order:
   - Core modules first (base, web, mail)
   - Business apps (crm, sales, project)
   - Specialized modules (hr, accounting, inventory)
4. Activates and configures all apps
5. Provides comprehensive installation report
```

### Example 2: App Upgrade Coordination
```
User: "Upgrade all apps to latest versions"

Agent:
1. Analyzes current app versions and available upgrades
2. Coordinates sub-agents for specialized upgrades:
   - CRM apps: Sales, marketing, customer service
   - Operations apps: Inventory, manufacturing, purchase
   - Finance apps: Accounting, invoicing, expenses
   - HR apps: Employee management, payroll, recruitment
3. Executes upgrades with rollback planning
4. Tests functionality after upgrades
5. Provides upgrade success metrics
```

### Example 3: Health Monitoring & Optimization
```
User: "Monitor and optimize all installed apps"

Agent:
1. Deploys monitoring sub-agents for each app category
2. Coordinates performance optimization:
   - Database optimization for large datasets
   - Cache configuration for frequently accessed data
   - UI optimization for user experience
   - API performance for integrations
3. Provides health dashboard with KPIs
4. Recommends optimization actions
```

## SuperClaude Sub-Agent Architecture

### App Category Specialization
```python
# Sub-agent coordination for different app categories
sub_agents = {
    'crm_sales': {
        'skills': ['oca-module-discovery', 'connector-integration-expert'],
        'apps': ['crm', 'sale', 'marketing_automation', 'website_sale'],
        'responsibilities': ['lead_management', 'sales_pipeline', 'customer_engagement']
    },
    'operations': {
        'skills': ['oca-compliance-check', 'odoo-sh-devops'],
        'apps': ['purchase', 'stock', 'mrp', 'quality'],
        'responsibilities': ['supply_chain', 'inventory', 'manufacturing']
    },
    'finance': {
        'skills': ['oca-module-discovery', 'connector-integration-expert'],
        'apps': ['account', 'account_accountant', 'l10n_us', 'payment'],
        'responsibilities': ['accounting', 'invoicing', 'tax_compliance']
    },
    'hr': {
        'skills': ['oca-compliance-check', 'odoo-studio-integration'],
        'apps': ['hr', 'hr_recruitment', 'hr_payroll', 'hr_holidays'],
        'responsibilities': ['employee_management', 'payroll', 'recruitment']
    }
}
```

### Installation Coordination
```python
# Coordinated installation process
class AppInstallationManager:
    """Manage app installation with sub-agent coordination"""
    
    def __init__(self, odoo_url):
        self.odoo_url = odoo_url
        self.sub_agents = {}
        self.installation_queue = []
        
    def coordinate_installation(self, app_list):
        """Coordinate installation across sub-agents"""
        # Group apps by category
        categorized_apps = self._categorize_apps(app_list)
        
        # Deploy sub-agents for each category
        for category, apps in categorized_apps.items():
            sub_agent = self._deploy_sub_agent(category, apps)
            self.sub_agents[category] = sub_agent
            
        # Execute coordinated installation
        return self._execute_coordinated_installation()
        
    def _deploy_sub_agent(self, category, apps):
        """Deploy specialized sub-agent for app category"""
        agent_config = sub_agents[category]
        return SuperClaudeSubAgent(
            skills=agent_config['skills'],
            target_apps=apps,
            responsibilities=agent_config['responsibilities']
        )
```

## Installation Strategies

### Dependency-Based Installation
```python
# Dependency resolution and installation order
def resolve_dependencies(apps):
    """Resolve app dependencies and determine installation order"""
    dependency_graph = build_dependency_graph(apps)
    installation_order = topological_sort(dependency_graph)
    
    return {
        'core_modules': ['base', 'web', 'mail', 'bus'],
        'framework_modules': ['base_import', 'web_editor', 'web_kanban'],
        'business_apps': ['crm', 'sale', 'purchase', 'account'],
        'specialized_apps': ['project', 'hr', 'stock', 'mrp'],
        'enhancement_apps': ['website', 'portal', 'auth_oauth']
    }
```

### Batch Installation with Rollback
```python
# Safe batch installation with rollback capability
class BatchInstaller:
    """Install apps in batches with rollback safety"""
    
    def install_batch(self, batch_apps):
        """Install a batch of apps with rollback protection"""
        checkpoint = self._create_system_checkpoint()
        
        try:
            for app in batch_apps:
                self._install_single_app(app)
                self._verify_installation(app)
                
            self._run_post_installation_tests()
            return True
            
        except InstallationError as e:
            self._rollback_to_checkpoint(checkpoint)
            raise e
```

## Upgrade Management

### Smart Upgrade Planning
```python
# Intelligent upgrade planning and execution
class UpgradeManager:
    """Manage app upgrades with minimal disruption"""
    
    def plan_upgrades(self, current_versions, target_versions):
        """Plan upgrade strategy"""
        upgrades = self._analyze_upgrade_paths(current_versions, target_versions)
        
        return {
            'immediate_upgrades': self._get_critical_upgrades(upgrades),
            'scheduled_upgrades': self._get_non_critical_upgrades(upgrades),
            'dependency_upgrades': self._get_dependency_upgrades(upgrades),
            'compatibility_checks': self._check_compatibility(upgrades)
        }
        
    def execute_upgrades(self, upgrade_plan):
        """Execute upgrades according to plan"""
        # Coordinate with sub-agents for specialized upgrades
        for category, upgrades in upgrade_plan.items():
            sub_agent = self.sub_agents[category]
            sub_agent.execute_upgrades(upgrades)
```

## Health Monitoring

### Comprehensive Monitoring System
```python
# Health monitoring for all installed apps
class AppHealthMonitor:
    """Monitor health and performance of all apps"""
    
    def __init__(self):
        self.monitoring_agents = {}
        
    def deploy_monitoring(self):
        """Deploy monitoring for all app categories"""
        for category in sub_agents.keys():
            monitoring_agent = MonitoringSubAgent(category)
            self.monitoring_agents[category] = monitoring_agent
            monitoring_agent.start_monitoring()
            
    def get_health_dashboard(self):
        """Generate comprehensive health dashboard"""
        health_data = {}
        for category, agent in self.monitoring_agents.items():
            health_data[category] = agent.get_health_metrics()
            
        return {
            'overall_health': self._calculate_overall_health(health_data),
            'category_health': health_data,
            'performance_metrics': self._get_performance_metrics(),
            'recommendations': self._generate_recommendations(health_data)
        }
```

## Integration with InsightPulseAI Odoo

### Custom Configuration for InsightPulseAI
```python
# InsightPulseAI specific configuration
insightpulseai_config = {
    'odoo_url': 'https://insightpulseai.net/odoo',
    'preferred_apps': {
        'analytics': ['bi_superset_agent', 'knowledge_notion_clone'],
        'operations': ['project', 'timesheet', 'helpdesk'],
        'integration': ['connector_integration_expert', 'api_manager']
    },
    'custom_workflows': {
        'data_analytics': 'bi_superset_agent → knowledge_notion_clone',
        'project_management': 'project → timesheet → helpdesk',
        'customer_engagement': 'crm → sale → marketing_automation'
    }
}
```

### Deployment Coordination
```python
# Coordinate deployment for InsightPulseAI
def deploy_insightpulseai_apps():
    """Deploy all apps for InsightPulseAI Odoo instance"""
    manager = AppInstallationManager('https://insightpulseai.net/odoo')
    
    # Get app list from OCA discovery
    available_apps = manager.discover_available_apps()
    
    # Filter for InsightPulseAI preferences
    target_apps = manager.filter_apps_by_preferences(
        available_apps, 
        insightpulseai_config['preferred_apps']
    )
    
    # Coordinate installation with sub-agents
    installation_result = manager.coordinate_installation(target_apps)
    
    # Configure custom workflows
    manager.configure_custom_workflows(
        insightpulseai_config['custom_workflows']
    )
    
    return installation_result
```

## Success Metrics

### Installation Success
- **App Activation Rate**: 100% successful installation and activation
- **Dependency Resolution**: Zero dependency conflicts
- **Performance Impact**: < 5% performance degradation during installation
- **User Experience**: Seamless transition for existing users

### Upgrade Performance
- **Upgrade Success Rate**: ≥ 95% successful upgrades
- **Downtime Minimization**: < 30 minutes total downtime
- **Data Integrity**: Zero data loss during upgrades
- **Functionality Preservation**: All existing features remain functional

### Monitoring Effectiveness
- **Health Monitoring**: Real-time health status for all apps
- **Performance Tracking**: Continuous performance metrics
- **Issue Detection**: Proactive problem identification
- **Optimization Success**: Measurable performance improvements

## Usage Commands

### Complete App Management
```bash
# Install and activate all apps
claude "Use odoo-apps-manager to install all apps for InsightPulseAI Odoo"

# Upgrade all apps to latest versions
claude "Use odoo-apps-manager to upgrade all InsightPulseAI apps"

# Monitor app health and performance
claude "Use odoo-apps-manager to monitor InsightPulseAI app health"

# Coordinate specialized installations
claude "Use odoo-apps-manager with sub-agents for CRM app installation"
```

This skill transforms the SuperClaude framework into a comprehensive Odoo application management system specifically tailored for your InsightPulseAI Odoo instance, using coordinated sub-agents for specialized tasks across all app categories.
