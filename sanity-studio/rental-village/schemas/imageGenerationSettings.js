export default {
  name: 'imageGenerationSettings',
  title: 'Image Generation Settings',
  type: 'document',
  icon: () => '🎨',
  fields: [
    {
      name: 'title',
      title: 'Settings Name',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'active',
      title: 'Active Settings',
      type: 'boolean',
      description: 'Only one image generation setting can be active at a time',
      initialValue: true
    },
    {
      name: 'brandGuidelines',
      title: 'Brand Guidelines',
      type: 'object',
      description: 'Brand consistency rules for image generation',
      fields: [
        {
          name: 'brandColors',
          title: 'Brand Colors',
          type: 'array',
          of: [
            {
              type: 'object',
              fields: [
                { name: 'name', title: 'Color Name', type: 'string' },
                { name: 'hex', title: 'Hex Code', type: 'string', validation: Rule => Rule.regex(/^#[0-9A-F]{6}$/i) },
                { name: 'usage', title: 'Usage', type: 'string' }
              ]
            }
          ],
          initialValue: [
            { name: 'Primary Blue', hex: '#1E40AF', usage: 'Main brand color' },
            { name: 'Secondary Orange', hex: '#F59E0B', usage: 'Accent color' },
            { name: 'Neutral Gray', hex: '#6B7280', usage: 'Text and backgrounds' }
          ]
        },
        {
          name: 'logoUsage',
          title: 'Logo Usage Guidelines',
          type: 'text',
          initialValue: 'Do not attempt to generate or include logos in images. Images should be clean and logo-free to maintain brand integrity.'
        },
        {
          name: 'fontPreferences',
          title: 'Font Preferences',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['Arial Bold', 'Helvetica', 'Sans-serif']
        },
        {
          name: 'visualStyle',
          title: 'Visual Style',
          type: 'string',
          options: {
            list: [
              { title: 'Professional', value: 'professional' },
              { title: 'Friendly', value: 'friendly' },
              { title: 'Modern', value: 'modern' },
              { title: 'Industrial', value: 'industrial' },
              { title: 'Clean', value: 'clean' }
            ]
          },
          initialValue: 'professional'
        }
      ]
    },
    {
      name: 'imageEnhancementPrompts',
      title: 'Image Enhancement Prompts',
      type: 'object',
      description: 'Prompts for enhancing equipment images by content pillar',
      fields: [
        {
          name: 'equipmentSpotlight',
          title: 'Equipment Spotlight',
          type: 'text',
          initialValue: 'Enhance this equipment image with professional lighting, clean background, and dynamic positioning. Add subtle brand colors and ensure the equipment is the focal point. Make it look premium and well-maintained.'
        },
        {
          name: 'projectShowcase',
          title: 'Project Showcase',
          type: 'text',
          initialValue: 'Show this equipment in action on a realistic job site. Add appropriate scenery, other complementary equipment, and workers if relevant. Make it look like a successful, professional project in progress.'
        },
        {
          name: 'seasonalContent',
          title: 'Seasonal Content',
          type: 'text',
          initialValue: 'Enhance this equipment image with appropriate seasonal elements. Add weather conditions, seasonal landscapes, and contextual details that match the current season. Ensure the equipment looks ready for seasonal challenges.'
        },
        {
          name: 'safetyTraining',
          title: 'Safety & Training',
          type: 'text',
          initialValue: 'Emphasize safety features of this equipment. Add safety equipment, proper operator attire, warning signs, and safety-focused visual elements. Make safety the prominent theme while showcasing the equipment.'
        },
        {
          name: 'educationalContent',
          title: 'Educational Content',
          type: 'text',
          initialValue: 'Create an educational diagram or infographic style image highlighting key features of this equipment. Add labels, specifications, and visual callouts that help explain how the equipment works.'
        }
      ]
    },
    {
      name: 'imageQualityStandards',
      title: 'Image Quality Standards',
      type: 'object',
      fields: [
        {
          name: 'minResolution',
          title: 'Minimum Resolution',
          type: 'object',
          fields: [
            { name: 'width', title: 'Width (px)', type: 'number', initialValue: 1080 },
            { name: 'height', title: 'Height (px)', type: 'number', initialValue: 1080 }
          ]
        },
        {
          name: 'preferredAspectRatios',
          title: 'Preferred Aspect Ratios',
          type: 'object',
          fields: [
            { name: 'facebook', title: 'Facebook', type: 'string', initialValue: '1:1' },
            { name: 'instagram', title: 'Instagram', type: 'string', initialValue: '1:1' },
            { name: 'blog', title: 'Blog', type: 'string', initialValue: '16:9' }
          ]
        },
        {
          name: 'imageFormats',
          title: 'Accepted Image Formats',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['PNG', 'JPEG', 'WebP']
        },
        {
          name: 'maxFileSize',
          title: 'Maximum File Size (MB)',
          type: 'number',
          validation: Rule => Rule.min(1).max(50),
          initialValue: 10
        }
      ]
    },
    {
      name: 'generationRules',
      title: 'Generation Rules',
      type: 'object',
      fields: [
        {
          name: 'maxImagesPerPost',
          title: 'Maximum Images per Post',
          type: 'number',
          validation: Rule => Rule.min(1).max(10),
          initialValue: 3
        },
        {
          name: 'fallbackToOriginal',
          title: 'Fallback to Original Images',
          type: 'boolean',
          description: 'Use original equipment images if generation fails',
          initialValue: true
        },
        {
          name: 'requireEquipmentVisibility',
          title: 'Require Equipment Visibility',
          type: 'boolean',
          description: 'Ensure equipment is clearly visible in generated images',
          initialValue: true
        },
        {
          name: 'includeWatermark',
          title: 'Include Watermark',
          type: 'boolean',
          description: 'Do not add watermarks to generated images - maintain clean, professional imagery',
          initialValue: false
        },
        {
          name: 'watermarkPosition',
          title: 'Watermark Position',
          type: 'string',
          options: {
            list: [
              { title: 'Bottom Right', value: 'bottom-right' },
              { title: 'Bottom Left', value: 'bottom-left' },
              { title: 'Top Right', value: 'top-right' },
              { title: 'Top Left', value: 'top-left' },
              { title: 'Center', value: 'center' }
            ]
          },
          initialValue: 'bottom-right'
        }
      ]
    },
    {
      name: 'textSuppressionSettings',
      title: 'Text Suppression Settings',
      type: 'object',
      description: 'Settings to prevent text generation in images',
      fields: [
        {
          name: 'suppressAllText',
          title: 'Suppress All Text',
          type: 'boolean',
          description: 'Prevent any text, words, or writing from appearing in generated images',
          initialValue: true
        },
        {
          name: 'noTextPrompts',
          title: 'No Text Prompts',
          type: 'array',
          of: [{ type: 'string' }],
          description: 'Specific prompts to ensure no text appears in images',
          initialValue: [
            'no text visible',
            'no words in image',
            'no writing or labels',
            'no signs with text',
            'no readable text',
            'text-free image',
            'clean image without any text overlay'
          ]
        },
        {
          name: 'textProhibitions',
          title: 'Text Prohibitions',
          type: 'array',
          of: [{ type: 'string' }],
          description: 'Specific text elements to avoid in image generation',
          initialValue: [
            'social media post layouts',
            'text overlays',
            'written descriptions',
            'captions in image',
            'promotional text',
            'advertising copy',
            'social media templates',
            'text-based graphics',
            'logos or watermarks',
            'brand marks',
            'company logos',
            'watermark overlays'
          ]
        },
        {
          name: 'focusOnVisuals',
          title: 'Focus on Visuals Only',
          type: 'boolean',
          description: 'Emphasize pure visual content without textual elements',
          initialValue: true
        },
        {
          name: 'visualOnlyPrompts',
          title: 'Visual-Only Enhancement Prompts',
          type: 'array',
          of: [{ type: 'string' }],
          description: 'Prompts that emphasize visual elements only',
          initialValue: [
            'focus on equipment details and visual appeal',
            'emphasize colors, textures, and composition',
            'highlight visual storytelling without text',
            'create compelling visual narrative',
            'showcase equipment through pure imagery'
          ]
        }
      ]
    },
    {
      name: 'safetyFilters',
      title: 'Safety Filters',
      type: 'object',
      description: 'Content safety filters for image generation',
      fields: [
        {
          name: 'prohibitedElements',
          title: 'Prohibited Elements',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: [
            'unsafe working conditions',
            'missing safety equipment',
            'inappropriate attire',
            'dangerous operations',
            'unsecured equipment'
          ]
        },
        {
          name: 'requiredSafetyElements',
          title: 'Required Safety Elements',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: [
            'proper safety equipment',
            'professional operators',
            'secure equipment positioning',
            'clear warning signs',
            'safe operating distances'
          ]
        },
        {
          name: 'automaticSafetyCheck',
          title: 'Automatic Safety Check',
          type: 'boolean',
          description: 'Automatically validate generated images for safety compliance',
          initialValue: true
        }
      ]
    },
    {
      name: 'performanceSettings',
      title: 'Performance Settings',
      type: 'object',
      fields: [
        {
          name: 'maxGenerationTime',
          title: 'Maximum Generation Time (seconds)',
          type: 'number',
          validation: Rule => Rule.min(5).max(300),
          initialValue: 60
        },
        {
          name: 'retryAttempts',
          title: 'Retry Attempts',
          type: 'number',
          validation: Rule => Rule.min(1).max(5),
          initialValue: 3
        },
        {
          name: 'batchSize',
          title: 'Batch Size',
          type: 'number',
          validation: Rule => Rule.min(1).max(10),
          initialValue: 1
        }
      ]
    },
    {
      name: 'createdAt',
      title: 'Created At',
      type: 'datetime',
      initialValue: () => new Date().toISOString()
    },
    {
      name: 'updatedAt',
      title: 'Updated At',
      type: 'datetime',
      initialValue: () => new Date().toISOString()
    }
  ],
  preview: {
    select: {
      title: 'title',
      active: 'active',
      style: 'brandGuidelines.visualStyle'
    },
    prepare(selection) {
      const { title, active, style } = selection
      return {
        title: title,
        subtitle: `${active ? 'Active' : 'Inactive'} - Style: ${style}`,
        media: () => active ? '✅' : '⏸️'
      }
    }
  }
}