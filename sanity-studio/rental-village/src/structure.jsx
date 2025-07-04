export const structure = (S) => {
  return S.list()
    .title('Rental Village Content Management')
    .items([
      // 📝 CONTENT CREATION WORKFLOW
      S.listItem()
        .title('📝 Content Creation')
        .child(
          S.list()
            .title('Content Workflow')
            .items([
              // Social Content Management
              S.documentTypeListItem('socialContent')
                .title('All Social Content')
                .icon(() => '📱'),
              
              // Content by Status
              S.listItem()
                .title('📊 Content by Status')
                .child(
                  S.list()
                    .title('Content Status')
                    .items([
                      S.listItem()
                        .title('✏️ Draft')
                        .child(
                          S.documentList()
                            .title('Draft Posts')
                            .filter('_type == "socialContent" && status == "draft"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('🔧 Generated')
                        .child(
                          S.documentList()
                            .title('Generated Posts')
                            .filter('_type == "socialContent" && status == "generated"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('👍 Approved')
                        .child(
                          S.documentList()
                            .title('Approved Posts')
                            .filter('_type == "socialContent" && status == "approved"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('✅ Published')
                        .child(
                          S.documentList()
                            .title('Published Posts')
                            .filter('_type == "socialContent" && status == "published"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('🗄️ Archived')
                        .child(
                          S.documentList()
                            .title('Archived Posts')
                            .filter('_type == "socialContent" && status == "archived"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        )
                    ])
                ),
              
              // Content by Pillar
              S.listItem()
                .title('🎯 Content by Pillar')
                .child(
                  S.list()
                    .title('Content Pillars')
                    .items([
                      S.listItem()
                        .title('🔦 Equipment Spotlight')
                        .child(
                          S.documentList()
                            .title('Equipment Spotlight Content')
                            .filter('_type == "socialContent" && content_pillar == "equipment_spotlight"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('🏗️ Project Showcase')
                        .child(
                          S.documentList()
                            .title('Project Showcase Content')
                            .filter('_type == "socialContent" && content_pillar == "project_showcase"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('🌦️ Seasonal Content')
                        .child(
                          S.documentList()
                            .title('Seasonal Content')
                            .filter('_type == "socialContent" && content_pillar == "seasonal_content"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('⛑️ Safety & Training')
                        .child(
                          S.documentList()
                            .title('Safety & Training Content')
                            .filter('_type == "socialContent" && content_pillar == "safety_training"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('🏭 Industry Focus')
                        .child(
                          S.documentList()
                            .title('Industry Focus Content')
                            .filter('_type == "socialContent" && content_pillar == "industry_focus"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('📚 Educational Content')
                        .child(
                          S.documentList()
                            .title('Educational Content')
                            .filter('_type == "socialContent" && content_pillar == "educational_content"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        ),
                      
                      S.listItem()
                        .title('📝 General Content')
                        .child(
                          S.documentList()
                            .title('General Content')
                            .filter('_type == "socialContent" && content_pillar == "general_content"')
                            .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                        )
                    ])
                )
            ])
        ),

      S.divider(),

      // 🏗️ EQUIPMENT MANAGEMENT
      S.listItem()
        .title('🏗️ Equipment Management')
        .child(
          S.list()
            .title('Equipment Data')
            .items([
              // All Equipment
              S.documentTypeListItem('equipment')
                .title('All Equipment')
                .icon(() => '🚜'),
              
              S.divider(),
              
              // Equipment by Availability
              S.listItem()
                .title('📊 By Availability')
                .child(
                  S.list()
                    .title('Equipment Availability')
                    .items([
                      S.listItem()
                        .title('✅ Available')
                        .child(
                          S.documentList()
                            .title('Available Equipment')
                            .filter('_type == "equipment" && availability.status == "available"')
                            .defaultOrdering([{field: 'name', direction: 'asc'}])
                        ),
                      
                      S.listItem()
                        .title('🔒 Rented')
                        .child(
                          S.documentList()
                            .title('Rented Equipment')
                            .filter('_type == "equipment" && availability.status == "rented"')
                            .defaultOrdering([{field: 'name', direction: 'asc'}])
                        )
                    ])
                ),
              
              // Equipment by Category
              S.listItem()
                .title('📂 By Category')
                .child(
                  S.list()
                    .title('Equipment Categories')
                    .items([
                      S.listItem()
                        .title('Construction')
                        .child(
                          S.documentList()
                            .title('Construction Equipment')
                            .filter('_type == "equipment" && "Construction" in categories[]')
                            .defaultOrdering([{field: 'name', direction: 'asc'}])
                        ),
                      
                      S.listItem()
                        .title('Landscaping')
                        .child(
                          S.documentList()
                            .title('Landscaping Equipment')
                            .filter('_type == "equipment" && "Landscaping" in categories[]')
                            .defaultOrdering([{field: 'name', direction: 'asc'}])
                        )
                    ])
                )
            ])
        ),

      S.divider(),

      // ⚙️ CONFIGURATION & SETTINGS
      S.listItem()
        .title('⚙️ Configuration & Settings')
        .child(
          S.list()
            .title('System Configuration')
            .items([
              // === CORE BUSINESS SETTINGS ===
              S.listItem()
                .title('🏢 Core Business')
                .child(
                  S.list()
                    .title('Business Configuration')
                    .items([
                      S.documentTypeListItem('businessContext')
                        .title('Business Context')
                        .icon(() => '🏢'),
                      
                      S.documentTypeListItem('contentStrategy')
                        .title('Content Strategy')
                        .icon(() => '📊')
                    ])
                ),
              
              // === CONTENT GENERATION SETTINGS ===
              S.listItem()
                .title('📝 Content Generation')
                .child(
                  S.list()
                    .title('Content Generation Settings')
                    .items([
                      S.documentTypeListItem('contentPrompt')
                        .title('Content Prompts')
                        .icon(() => '📋'),
                      
                      S.documentTypeListItem('seasonalSettings')
                        .title('Seasonal Settings')
                        .icon(() => '🌦️'),
                      
                      S.documentTypeListItem('imageGenerationSettings')
                        .title('Image Generation')
                        .icon(() => '🎨')
                    ])
                ),
              
              // === PLATFORM SETTINGS ===
              S.listItem()
                .title('📱 Platform Configuration')
                .child(
                  S.list()
                    .title('Platform Settings')
                    .items([
                      S.documentTypeListItem('platformSettings')
                        .title('Platform Settings')
                        .icon(() => '📱')
                    ])
                )
            ])
        ),

      S.divider(),

      // 📈 ANALYTICS & INSIGHTS
      S.listItem()
        .title('📈 Analytics & Insights')
        .child(
          S.list()
            .title('Performance Insights')
            .items([
              S.listItem()
                .title('⏰ Recent Content')
                .child(
                  S.documentList()
                    .title('Latest Content (7 days)')
                    .filter('_type == "socialContent" && _createdAt > dateTime(now()) - 7*24*60*60')
                    .defaultOrdering([{field: '_createdAt', direction: 'desc'}])
                ),
              
              S.listItem()
                .title('📊 Equipment Usage')
                .child(
                  S.documentList()
                    .title('Most Featured Equipment')
                    .filter('_type == "equipment"')
                    .defaultOrdering([{field: 'popularity_score', direction: 'desc'}])
                )
            ])
        )
    ])
}

// Default document node resolver for custom views
export const defaultDocumentNodeResolver = (S, { schemaType }) => {
  switch (schemaType) {
    case 'socialContent':
      return S.document().views([
        S.view.form()
      ])
    
    case 'equipment':
      return S.document().views([
        S.view.form()
      ])
    
    case 'contentStrategy':
      return S.document().views([
        S.view.form()
      ])
    
    default:
      return S.document().views([S.view.form()])
  }
}