# White-Label Social Media Platform Initialization Guide

## Business Configuration Setup

This document guides you through configuring the white-label social media content generation platform for your specific business type. Complete this setup before deployment.

---

## Step 1: Business Type Selection

Choose your business vertical to configure appropriate schemas and content strategies:

### Available Business Types

**Equipment Rental** (Default)
- Primary Entity: Equipment/Machinery
- Content Focus: Equipment showcases, project examples, seasonal demand
- Schema: `equipment.js`
- Manager: `equipment_manager.py`

**SaaS/Software**
- Primary Entity: Products/Features
- Content Focus: Feature highlights, use cases, customer success
- Schema: `product.js`
- Manager: `product_manager.py`

**Professional Services**
- Primary Entity: Services/Expertise
- Content Focus: Service showcases, case studies, industry insights
- Schema: `service.js` 
- Manager: `service_manager.py`

**E-commerce/Retail**
- Primary Entity: Products/Inventory
- Content Focus: Product features, seasonal promotions, customer reviews
- Schema: `inventory.js`
- Manager: `inventory_manager.py`

**Healthcare/Medical**
- Primary Entity: Services/Treatments
- Content Focus: Service education, patient success, health awareness
- Schema: `treatment.js`
- Manager: `treatment_manager.py`

**Real Estate**
- Primary Entity: Properties/Listings
- Content Focus: Property showcases, market insights, neighborhood features
- Schema: `property.js`
- Manager: `property_manager.py`

---

## Step 2: Business Profile Configuration

### Basic Business Information
```json
{
  "business_name": "Your Business Name",
  "business_type": "equipment_rental", // equipment_rental, saas, services, ecommerce, healthcare, real_estate
  "industry": "construction", // specific industry within business type
  "primary_location": {
    "city": "Your City",
    "state": "Your State",
    "country": "Your Country"
  },
  "target_audience": {
    "primary": "contractors",
    "secondary": "diy_enthusiasts",
    "demographics": "25-55 years old"
  }
}
```

### Content Strategy Configuration
```json
{
  "content_pillars": {
    // Equipment Rental Pillars
    "equipment_spotlight": 25,
    "project_showcase": 20,
    "seasonal_content": 15,
    "safety_training": 15,
    "educational_content": 10,
    "industry_focus": 10,
    "customer_success": 5
  },
  // OR SaaS Pillars
  "content_pillars_saas": {
    "feature_highlight": 25,
    "use_case_demo": 20,
    "customer_success": 15,
    "industry_insights": 15,
    "educational_content": 10,
    "product_updates": 10,
    "team_behind_product": 5
  },
  // OR Services Pillars
  "content_pillars_services": {
    "service_showcase": 25,
    "case_study": 20,
    "industry_expertise": 15,
    "client_testimonials": 15,
    "educational_content": 10,
    "behind_the_scenes": 10,
    "community_involvement": 5
  }
}
```

---

## Step 3: Schema Configuration

### Dynamic Schema Generation

Based on your business type, the following schemas will be generated:

**Equipment Rental** → `equipment.js`
```javascript
export default {
  name: 'equipment',
  title: 'Equipment Catalog',
  type: 'document',
  fields: [
    // Equipment-specific fields
    {name: 'name', type: 'string', title: 'Equipment Name'},
    {name: 'category', type: 'string', title: 'Category'},
    {name: 'rental_rate', type: 'number', title: 'Daily Rate'},
    {name: 'availability', type: 'string', title: 'Availability Status'}
  ]
}
```

**SaaS** → `product.js`
```javascript
export default {
  name: 'product',
  title: 'Product Catalog',
  type: 'document',
  fields: [
    // Product-specific fields
    {name: 'name', type: 'string', title: 'Product Name'},
    {name: 'category', type: 'string', title: 'Feature Category'},
    {name: 'pricing_tier', type: 'string', title: 'Pricing Tier'},
    {name: 'release_status', type: 'string', title: 'Release Status'}
  ]
}
```

**Professional Services** → `service.js`
```javascript
export default {
  name: 'service',
  title: 'Service Catalog',
  type: 'document',
  fields: [
    // Service-specific fields
    {name: 'name', type: 'string', title: 'Service Name'},
    {name: 'category', type: 'string', title: 'Service Category'},
    {name: 'duration', type: 'string', title: 'Typical Duration'},
    {name: 'expertise_level', type: 'string', title: 'Expertise Required'}
  ]
}
```

---

## Step 4: Content Algorithm Configuration

### Business-Specific Weighting

**Equipment Rental Algorithm**
```python
factors = {
    'recency_bias': 0.3,        # Prevent equipment repetition
    'availability': 0.25,       # Available equipment priority
    'seasonal_relevance': 0.2,  # Seasonal demand patterns
    'performance_history': 0.15, # Past content success
    'margin_priority': 0.1      # Rental profitability
}
```

**SaaS Algorithm**
```python
factors = {
    'recency_bias': 0.3,        # Prevent feature repetition
    'feature_adoption': 0.25,   # Popular features priority
    'release_recency': 0.2,     # New features boost
    'user_engagement': 0.15,    # High-engagement features
    'conversion_impact': 0.1    # Revenue-driving features
}
```

**Services Algorithm**
```python
factors = {
    'recency_bias': 0.3,        # Prevent service repetition
    'demand_seasonality': 0.25, # Seasonal service demand
    'expertise_showcase': 0.2,  # Highlight specializations
    'client_success_rate': 0.15, # Proven service results
    'margin_priority': 0.1      # Service profitability
}
```

---

## Step 5: Platform Integration

### Social Media Configuration

```json
{
  "platforms": {
    "facebook": {
      "enabled": true,
      "page_id": "your_page_id",
      "access_token": "your_access_token",
      "content_format": "visual_heavy"
    },
    "instagram": {
      "enabled": true,
      "account_id": "your_account_id",
      "access_token": "your_access_token",
      "content_format": "visual_story"
    },
    "linkedin": {
      "enabled": true,
      "company_id": "your_company_id",
      "access_token": "your_access_token",
      "content_format": "professional"
    },
    "twitter": {
      "enabled": false,
      "account_id": "",
      "access_token": "",
      "content_format": "concise"
    }
  }
}
```

---

## Step 6: Environment Setup

### Environment Variables Template

```bash
# Business Configuration
BUSINESS_TYPE=equipment_rental
BUSINESS_NAME="Your Business Name"
INDUSTRY=construction

# Primary Entity Configuration
PRIMARY_ENTITY=equipment
ENTITY_MANAGER=equipment_manager
ENTITY_SCHEMA=equipment

# Content Strategy
CONTENT_PILLARS_CONFIG=equipment_rental_pillars.json

# Sanity Configuration
SANITY_PROJECT_ID=your_project_id
SANITY_DATASET=production
SANITY_TOKEN=your_sanity_token

# Social Media APIs
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id
LINKEDIN_COMPANY_ID=your_company_id

# Container Configuration
CONTAINER_PREFIX=your_business_slug
```

---

## Step 7: Deployment Commands

### Initialize White-Label Instance

```bash
# 1. Clone white-label template
git clone https://github.com/your-org/social-content-template.git your-business-name-social-bot

# 2. Navigate to project
cd your-business-name-social-bot

# 3. Run initialization script
./scripts/init-white-label.sh

# 4. Configure business type
./scripts/configure-business-type.sh --type equipment_rental

# 5. Set up environment
cp .env.template .env
# Edit .env with your specific values

# 6. Generate schemas
./scripts/generate-schemas.sh --business-type equipment_rental

# 7. Deploy containers
docker-compose up -d --build

# 8. Initialize data
./scripts/setup-initial-data.sh
```

---

## Step 8: Validation Checklist

### Pre-Production Validation

- [ ] Business type correctly configured
- [ ] Primary entity schema generated and deployed
- [ ] Content pillars match business vertical
- [ ] Algorithm weights appropriate for business model
- [ ] Social media platforms connected and tested
- [ ] Container services healthy and communicating
- [ ] Initial content generation successful
- [ ] Data backup and sync systems operational

### Post-Deployment Testing

- [ ] Generate sample content for review
- [ ] Test social media posting to each platform
- [ ] Verify analytics tracking functionality
- [ ] Confirm backup/restore procedures
- [ ] Validate performance monitoring
- [ ] Test error handling and graceful degradation

---

## Business Type Templates

### Quick Setup Commands

**Equipment Rental**
```bash
./scripts/quick-setup.sh --type equipment_rental --name "ABC Equipment Rental"
```

**SaaS**
```bash
./scripts/quick-setup.sh --type saas --name "XYZ Software Solutions"
```

**Professional Services**
```bash
./scripts/quick-setup.sh --type services --name "Premier Consulting Group"
```

**E-commerce**
```bash
./scripts/quick-setup.sh --type ecommerce --name "Fashion Forward Store"
```

---

## Support and Customization

### Custom Business Types

If your business doesn't fit the predefined types, you can create custom configurations:

1. **Define Custom Entity**: Create your primary business entity (e.g., `membership.js` for gyms)
2. **Configure Content Pillars**: Define content strategy specific to your industry
3. **Customize Algorithm**: Adjust weighting factors for your business priorities
4. **Update Templates**: Modify content generation templates for your terminology

### Getting Help

- **Documentation**: `/docs/white-label-guide.md`
- **Examples**: `/examples/` directory contains sample configurations
- **Support**: Contact your implementation team for custom requirements

---

## Next Steps

After completing this initialization:

1. **Content Review**: Generate sample content and review for brand alignment
2. **Team Training**: Train your team on the Sanity Studio interface
3. **Launch Strategy**: Plan your social media content calendar
4. **Monitoring Setup**: Configure alerts and performance tracking
5. **Optimization**: Monitor performance and adjust algorithm weights as needed

---

*This white-label platform is designed to be flexible and scalable. Each business type template provides a solid foundation that can be further customized to meet specific needs.*