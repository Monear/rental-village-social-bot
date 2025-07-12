# Claude Senior Developer Instructions

## App Summary - White-Label Social Media Content Generation Template

The **White-Label Social Media Content Generation Template** is a deployable template repository designed for equipment rental and service businesses. This system serves as a foundation that can be cloned and customized for individual clients, with each deployment running in its own isolated environment (LXC container).

### Template-Based Architecture

**Template Foundation**:
- **Containerized template system** using Podman for deployment consistency
- **Environment-driven configuration** enabling complete customization per client
- **Unified content generation engine** with advanced weighting algorithms
- **Simplified data schemas** optimized for quick client deployment
- **Clone-and-deploy model** for rapid client onboarding

### Deployment Architecture

**🚀 TEMPLATE-BASED DEPLOYMENT**: Each client gets their own complete instance:
- **Base Template Repository**: Clean, configurable content generation system
- **Client Deployment Process**: `git clone` → configure → deploy to dedicated LXC
- **Complete Isolation**: Each client has their own Sanity Studio, Notion workspace, and infrastructure
- **Independent Scaling**: Clients can scale their instance based on their needs
- **Zero Client Interference**: No shared resources between client deployments

**Core Template Services**:
```yaml
# Template Container Stack (Per Client Deployment)
services:
  sanity-studio:     # Client-specific content management interface
  mcp-server:        # Data processing and tool integration
  content-generation: # AI content generation engine
  social-automation: # Multi-platform posting automation
```

**Container Orchestration**:
- **Podman Compose** for all deployments (development and production)
- **Environment-based configuration** via client-specific environment files
- **Health checks** and monitoring for all services
- **Resource limits** appropriate for LXC container deployment
- **Automated deployment scripts** for new client setup

**Key Template Components**:
- `core/content_engine.py`: Unified content generation with diversity algorithms
- `core/equipment_manager.py`: Equipment data management and weighting
- `core/platform_publisher.py`: Multi-platform publishing automation
- `config/`: Template configuration files for client customization
- `sanity-schemas/`: Business-agnostic data models ready for client deployment

## CURRENT PRIORITY: Template System Creation

### Template Architecture Goals

**1. Clean Foundation** → **No Technical Debt**
- Build from scratch with proper architecture
- 4 core modules instead of 18 scattered utility files
- Clean separation of concerns with defined interfaces
- Eliminate all hardcoded client-specific values

**2. Advanced Content Algorithm** → **Weighted Diversity System**
- Implement recency bias to prevent equipment repetition
- Add category rotation for balanced coverage
- Performance feedback loop for continuous improvement
- Conditional logic for missing data graceful degradation

**3. Streamlined Data Models** → **Template-Ready Schemas**
- 5 essential schemas optimized for any business type
- Environment-driven customization without code changes
- Rapid client deployment with minimal configuration
- Clear separation between template and client-specific data

### New Content Generation Algorithm

```python
# Conditional Weighted Equipment Selection
def calculate_equipment_score(equipment, content_history):
    # Adaptive weights based on available data
    has_performance_data = check_performance_data_availability()
    has_availability_data = check_availability_data_reliability()
    
    if has_performance_data and has_availability_data:
        # Full algorithm with all factors
        factors = {
            'recency_bias': 0.3,        # Prevent repetition
            'availability': 0.25,       # Available equipment priority  
            'seasonal_relevance': 0.2,  # Seasonal demand patterns
            'performance_history': 0.15, # Past content success rates
            'margin_priority': 0.1      # Business profitability
        }
    else:
        # Practical algorithm for current data state
        factors = {
            'recency_bias': 0.4,        # Prevent repetition (increased)
            'seasonal_relevance': 0.3,  # Seasonal demand patterns
            'manual_priority': 0.2,     # Popularity score + newness
            'category_diversity': 0.1   # Category distribution balance
        }
    
    return weighted_score_calculation(equipment, factors)
```

**Content Diversity Features**:
- **Recency tracking**: Prevents same equipment in consecutive posts
- **Category rotation**: Ensures balanced equipment coverage
- **Platform optimization**: Tailored content for each social platform
- **Performance feedback**: Learns from engagement metrics

## Template Repository Architecture

### Template Directory Structure

```
social-content-generation-template/
├── podman/                      # Podman container configuration
│   ├── compose/                 # Podman Compose configurations
│   │   ├── podman-compose.yml   # Production deployment
│   │   ├── podman-compose.dev.yml # Development environment
│   │   └── podman-compose.test.yml # Testing environment
│   └── images/                  # Container image definitions
│       ├── Containerfile.content   # Content generation service
│       ├── Containerfile.mcp       # MCP server service
│       ├── Containerfile.social    # Social automation service
│       └── Containerfile.studio    # Sanity Studio service
├── src/                         # Application source code
│   ├── core/                    # Core template system
│   │   ├── content_engine.py    # Unified content generation
│   │   ├── equipment_manager.py # Equipment data management
│   │   ├── platform_publisher.py # Multi-platform posting
│   │   └── analytics_tracker.py # Performance analytics
│   ├── mcp_server/             # MCP server implementation
│   └── automation/             # Social media automation
├── config/                      # Template configuration
│   ├── template.env            # Environment template for client setup
│   ├── business_profile.json   # Business info template
│   ├── content_strategy.json   # Content strategy template
│   ├── platform_settings.json  # Social platform configuration template
│   └── equipment_categories.json # Equipment categorization template
├── sanity-studio/              # Sanity Studio template
│   ├── package.json            # Studio dependencies
│   ├── sanity.config.js        # Studio configuration template
│   └── schemas/                # Template schemas
│       ├── equipment.js        # Equipment catalog schema
│       ├── businessProfile.js  # Business profile schema
│       ├── socialContent.js    # Content workflow schema
│       ├── appSettings.js      # Application settings schema
│       └── contentAnalytics.js # Performance tracking schema
├── deployment/                 # Deployment automation
│   ├── scripts/               # Deployment scripts
│   │   ├── setup-client.sh    # New client setup script
│   │   ├── deploy.sh          # Deployment script
│   │   ├── backup.sh          # Data backup script
│   │   └── monitor.sh         # Health monitoring script
│   └── templates/             # Deployment templates
│       ├── systemd/           # Systemd service templates
│       └── nginx/             # Nginx configuration templates
└── docs/                       # Template documentation
    ├── DEPLOYMENT.md           # Deployment instructions
    ├── CONFIGURATION.md        # Configuration guide
    └── CLIENT_SETUP.md         # Client setup guide
```

### Client Deployment Process

**1. Template-Based Client Setup**
```bash
# Clone template repository
git clone https://github.com/your-org/social-content-generation-template.git client-name-social-bot

# Run client setup script
cd client-name-social-bot
./deployment/scripts/setup-client.sh --client-name "Client Name" --domain "client.example.com"

# Configure client-specific settings
cp config/template.env .env
# Edit .env with client-specific values

# Deploy to LXC container
./deployment/scripts/deploy.sh --environment production
```

**2. Isolated Client Deployment**
```bash
# Each client gets their own:
# - LXC container with dedicated resources
# - Sanity Studio instance with custom branding
# - Notion workspace for content management
# - Social media automation with client credentials
# - Independent scaling and monitoring
```

**3. Development Environment**
```bash
# Template development and testing
podman-compose -f podman/compose/podman-compose.dev.yml up -d
# Volume mounts for code changes
# Debug ports exposed for development tools
```

**Container Service Dependencies**:
- **Sanity Studio** → **MCP Server** → **Content Generation** → **Social Automation**
- **Health checks** ensure service availability before dependent services start
- **Graceful shutdown** and restart capabilities for zero-downtime deployments
- **Resource limits** appropriate for LXC container deployment

## Simplified Sanity Schemas

### Core Schema Consolidation

**Before**: 8 fragmented schemas
**After**: 5 unified schemas

```javascript
// 1. equipment.js - 5 logical tabs (reduced from 9)
tabs: ['basic', 'commercial', 'content', 'technical', 'metadata']

// 2. businessProfile.js - Unified business data
fields: [business_info, branding, contact, locations, social_accounts]

// 3. socialContent.js - Content workflow tracking
workflow: ['draft', 'approved', 'scheduled', 'published', 'archived']

// 4. appSettings.js - All configurations consolidated
sections: [content_strategy, platform_settings, seasonal_config, image_settings]

// 5. contentAnalytics.js - Performance tracking
metrics: [engagement_rates, equipment_performance, platform_analytics]
```

### Schema Benefits

**Simplification Benefits**:
- **90% reduction** in configuration complexity
- **Unified data models** with consistent naming
- **Faster deployment** for new clients
- **Easier maintenance** and updates

**Scalability Features**:
- **Client-specific overrides** without core schema changes
- **Modular customization** for different business types
- **Automated migration** tools for schema updates

## Content Generation Fundamentals

### Weighted Selection Algorithm

```python
class ContentDiversityEngine:
    def select_equipment(self, content_history, available_equipment):
        # Calculate weighted scores
        scores = {}
        for equipment in available_equipment:
            score = (
                self.recency_score(equipment, content_history) * 0.3 +
                self.availability_score(equipment) * 0.25 +
                self.seasonal_relevance(equipment) * 0.2 +
                self.performance_history(equipment) * 0.15 +
                self.margin_priority(equipment) * 0.1
            )
            scores[equipment.id] = score
        
        # Select top candidates with randomization
        return self.weighted_random_selection(scores)
```

### Content Pillars & Distribution

**Strategic Content Pillars**:
- `equipment_spotlight`: 25% - Feature specific equipment
- `project_showcase`: 20% - Real-world usage examples
- `seasonal_content`: 15% - Seasonal demand alignment
- `safety_training`: 15% - Build trust and compliance
- `educational_content`: 10% - Establish expertise
- `industry_focus`: 10% - Target specific sectors
- `customer_success`: 5% - Social proof and testimonials

**Distribution Algorithm**:
- **Pillar rotation** prevents content type clustering
- **Platform optimization** adapts content for each channel
- **Seasonal adjustment** boosts relevant content timing

## Notion-to-Sanity Backup System

### Automated Synchronization

```python
class NotionSanitySync:
    def sync_content(self):
        # 1. Fetch new/updated Notion content
        # 2. Transform to Sanity schema format
        # 3. Validate data integrity
        # 4. Batch upload to Sanity
        # 5. Update sync status tracking
        
    def backup_schedule(self):
        # Hourly: New content sync
        # Daily: Full content validation
        # Weekly: Performance analytics sync
```

**Backup Features**:
- **Incremental sync** for efficiency
- **Conflict resolution** for simultaneous edits
- **Data validation** ensures schema compliance
- **Rollback capability** for error recovery

## Role Definition

You are Claude, the **Senior Developer** for the White-Label Social Media Content Generation Platform. Your role encompasses:

### Technical Leadership
- **Architecture decisions** for scalable white-label system
- **Code review** for all core modules and client integrations
- **Performance optimization** for multi-tenant deployments
- **Security implementation** for client data isolation

### Client Onboarding
- **New client setup** using standardized templates
- **Custom configuration** for business-specific needs
- **Integration support** for existing client systems
- **Training delivery** for client content teams

### Platform Evolution
- **Feature development** for core content generation engine
- **Algorithm improvements** for content diversity and performance
- **Integration expansion** for new social media platforms
- **Analytics enhancement** for business intelligence

## Implementation Roadmap

### Phase 1: Core Platform (Current)
- ✅ **Architecture redesign** with white-label foundation
- ✅ **Schema consolidation** for simplified data models
- ✅ **Content diversity algorithm** implementation
- 🔄 **Notion-to-Sanity sync** system development

### Phase 2: Multi-Client Support
- **Client template system** for rapid deployment
- **Configuration management** for client-specific settings
- **Automated onboarding** workflow
- **Multi-tenant testing** and validation

### Phase 3: Platform Expansion
- **New business verticals** (automotive, beauty, services)
- **Advanced analytics** with client dashboards
- **API development** for third-party integrations
- **SaaS deployment** model

## Current Status: Architecture Overhaul Complete

**🚀 FOUNDATION REBUILT**: White-label platform architecture implemented

The platform has been restructured from a single-client solution to a scalable white-label system. Key improvements:

- ✅ **Unified content generation** with proper weighting algorithms
- ✅ **Simplified Sanity schemas** for scalability
- ✅ **Modular architecture** supporting multiple clients
- ✅ **Content diversity engine** preventing repetitive output
- ✅ **Performance tracking** with analytics integration

**Ready for Implementation**: The foundation is established for both immediate Rental Village improvements and future client deployments.

---

## Development Notes

### Code Quality Standards
- **Modular design** with clear interfaces
- **Comprehensive testing** for all core functions
- **Documentation** for client onboarding
- **Security practices** for multi-tenant data

### Performance Targets
- **Sub-2-second** content generation
- **99.9% uptime** for automated posting
- **Scalable to 100+ clients** on single infrastructure
- **Real-time analytics** with dashboard updates

### Security Requirements
- **Client data isolation** in multi-tenant deployments
- **API authentication** for all external integrations
- **Encryption at rest** for sensitive business data
- **Audit logging** for compliance and debugging

**Next Priority**: Complete Notion-to-Sanity sync system and begin client template development.

---

## Implementation Guidelines

### Critical Requirements for Agents

**Containerization Requirements**:
- **All development MUST occur in containers** - no local Python environments
- **Service isolation** - each component runs in its own container
- **Environment variable configuration** - no hardcoded values in code
- **Health check implementation** for all services
- **Graceful shutdown handling** for container lifecycle management
- **Resource limits** defined for all containers to prevent resource conflicts

**Data Validation Requirements**:
- **Always verify Sanity data availability** before using in algorithms
- **Implement fallback mechanisms** for missing or unreliable data
- **Test with current data state** before deploying new features
- **Log data availability issues** for monitoring and improvement

**Algorithm Implementation Rules**:
- **Conditional logic required** for all data-dependent features
- **Graceful degradation** when expected data is missing
- **Extensible design** that can incorporate new data sources
- **Performance monitoring** for algorithm effectiveness

**Container Development Workflow**:
```bash
# 1. Start development environment
docker-compose -f docker/compose/docker-compose.dev.yml up -d

# 2. Access service for development
docker-compose exec content-generation bash

# 3. Test changes in isolated environment
docker-compose exec content-generation python src/suggest_content.py --num-ideas 1

# 4. Deploy to production
docker-compose -f docker/compose/docker-compose.yml up -d --build
```

### Migration Strategy

**Phase 1: Current State Optimization**
1. **Implement conditional algorithms** with current data constraints
2. **Validate all Sanity data assumptions** before using in production
3. **Create fallback mechanisms** for unavailable data points
4. **Test content diversity** with existing equipment database

**Phase 2: Data Infrastructure Enhancement**
1. **Implement reliable availability tracking** in Sanity
2. **Add performance metrics collection** for engagement data
3. **Create data validation tools** for quality assurance
4. **Enable full algorithm features** as data becomes available

**Phase 3: Advanced Features**
1. **Machine learning integration** for content optimization
2. **Predictive analytics** for equipment demand forecasting
3. **Real-time performance tracking** with automated adjustments
4. **Cross-platform content coordination** for campaign management

### Testing Requirements

**Algorithm Testing**:
- **Dry-run equipment selection** with historical data
- **Diversity analysis** of generated content plans
- **Performance comparison** between old and new algorithms
- **Edge case handling** for missing data scenarios

**Data Integration Testing**:
- **Sanity connection reliability** testing
- **Schema validation** for all data operations
- **Backup system verification** for data integrity
- **Performance benchmarking** for query optimization

### Error Handling Standards

**Graceful Degradation**:
```python
def robust_content_generation():
    try:
        # Attempt advanced algorithm
        return advanced_content_generation()
    except DataUnavailableError:
        logger.warning("Using fallback algorithm due to data constraints")
        return fallback_content_generation()
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return emergency_content_fallback()
```

**Monitoring Requirements**:
- **Algorithm performance metrics** tracking
- **Data availability monitoring** with alerts
- **Content quality assessment** with automated scoring
- **Error rate tracking** with threshold-based notifications

### Client Onboarding Checklist

**Pre-Deployment Validation**:
- [ ] **Container environment setup** with client-specific configurations
- [ ] **Docker image builds** for all services with client customizations
- [ ] **Environment variable configuration** in clients/{client_name}/.env
- [ ] **Sanity schema deployment** and configuration in containerized studio
- [ ] **Equipment data import** and categorization via container scripts
- [ ] **Business profile setup** with branding guidelines
- [ ] **Content pillar configuration** for industry relevance
- [ ] **Algorithm testing** with client-specific data in isolated containers
- [ ] **Social media platform integration** and authentication
- [ ] **Container health checks** and service dependencies validation
- [ ] **Backup system configuration** for data protection
- [ ] **Performance monitoring** setup and baseline establishment
- [ ] **Resource limits** and scaling configuration

**Container Deployment Process**:
```bash
# 1. Create client configuration
./deployment/scripts/deploy-client.sh {client_name}

# 2. Deploy client stack
docker-compose -f clients/{client_name}/docker-compose.yml up -d

# 3. Verify all services are healthy
docker-compose -f clients/{client_name}/docker-compose.yml ps

# 4. Run initial content generation test
docker-compose exec content-generation python src/suggest_content.py --num-ideas 1
```

**Post-Deployment Monitoring**:
- [ ] **Container health status** monitoring and alerting
- [ ] **Content generation quality** assessment
- [ ] **Algorithm performance** tracking and optimization
- [ ] **Data synchronization** verification between containers
- [ ] **Resource utilization** monitoring and optimization
- [ ] **Container logs** analysis for error detection
- [ ] **Client feedback integration** and system improvements
- [ ] **Backup verification** and disaster recovery testing