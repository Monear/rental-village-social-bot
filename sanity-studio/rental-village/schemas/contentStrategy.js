export default {
  name: 'contentStrategy',
  title: 'Content Strategy Configuration',
  type: 'document',
  icon: () => '📊',
  fields: [
    {
      name: 'title',
      title: 'Strategy Name',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'active',
      title: 'Active Strategy',
      type: 'boolean',
      description: 'Only one strategy can be active at a time',
      initialValue: true
    },
    {
      name: 'pillarWeights',
      title: 'Content Pillar Weights',
      type: 'object',
      description: 'Probability weights for content pillar selection (must sum to 1.0)',
      fields: [
        {
          name: 'equipmentSpotlight',
          title: 'Equipment Spotlight',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(1),
          initialValue: 0.3
        },
        {
          name: 'seasonalContent',
          title: 'Seasonal Content',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(1),
          initialValue: 0.25
        },
        {
          name: 'safetyTraining',
          title: 'Safety & Training',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(1),
          initialValue: 0.15
        },
        {
          name: 'educationalContent',
          title: 'Educational Content',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(1),
          initialValue: 0.1
        },
        {
          name: 'dadJokes',
          title: 'Dad Jokes',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(1),
          initialValue: 0.05
        },
      ],
      validation: Rule => Rule.custom(weights => {
        if (!weights) return true
        const sum = Object.values(weights).reduce((a, b) => a + b, 0)
        return Math.abs(sum - 1.0) < 0.01 ? true : 'Weights must sum to 1.0'
      })
    },
    {
      name: 'platformPreferences',
      title: 'Platform Distribution',
      type: 'object',
      description: 'Preferred platform distribution percentages',
      fields: [
        {
          name: 'facebook',
          title: 'Facebook',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(100),
          initialValue: 40
        },
        {
          name: 'instagram',
          title: 'Instagram',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(100),
          initialValue: 35
        },
        {
          name: 'blog',
          title: 'Blog',
          type: 'number',
          validation: Rule => Rule.required().min(0).max(100),
          initialValue: 25
        }
      ],
      validation: Rule => Rule.custom(prefs => {
        if (!prefs) return true
        const sum = Object.values(prefs).reduce((a, b) => a + b, 0)
        return Math.abs(sum - 100) < 1 ? true : 'Platform percentages must sum to 100'
      })
    },
    {
      name: 'equipmentSelectionRules',
      title: 'Equipment Selection Rules',
      type: 'object',
      fields: [
        {
          name: 'prioritizeNewEquipment',
          title: 'Prioritize New Equipment',
          type: 'boolean',
          description: 'Give preference to recently added equipment',
          initialValue: true
        },
        {
          name: 'prioritizeUnderutilized',
          title: 'Prioritize Underutilized Equipment',
          type: 'boolean',
          description: 'Favor equipment that hasn\'t been featured recently',
          initialValue: true
        },
        {
          name: 'prioritizeHighMargin',
          title: 'Prioritize High-Margin Equipment',
          type: 'boolean',
          description: 'Focus on equipment with higher profit margins',
          initialValue: false
        },
        {
          name: 'excludeUnavailable',
          title: 'Exclude Unavailable Equipment',
          type: 'boolean',
          description: 'Only feature equipment that is currently available',
          initialValue: true
        },
        {
          name: 'maxEquipmentAge',
          title: 'Maximum Equipment Age (days)',
          type: 'number',
          description: 'Don\'t feature equipment older than this many days',
          validation: Rule => Rule.min(0),
          initialValue: 365
        }
      ]
    },
    {
      name: 'contentQualityRules',
      title: 'Content Quality Rules',
      type: 'object',
      fields: [
        {
          name: 'minImageQuality',
          title: 'Minimum Image Quality Score',
          type: 'number',
          description: 'Minimum quality score for images (1-10)',
          validation: Rule => Rule.min(1).max(10),
          initialValue: 7
        },
        {
          name: 'requireEquipmentImages',
          title: 'Require Equipment Images',
          type: 'boolean',
          description: 'All content must include equipment images',
          initialValue: true
        },
        {
          name: 'maxContentLength',
          title: 'Maximum Content Length',
          type: 'object',
          fields: [
            {
              name: 'facebook',
              title: 'Facebook (characters)',
              type: 'number',
              initialValue: 2000
            },
            {
              name: 'instagram',
              title: 'Instagram (characters)',
              type: 'number',
              initialValue: 2200
            },
            {
              name: 'blog',
              title: 'Blog (words)',
              type: 'number',
              initialValue: 1500
            }
          ]
        },
        {
          name: 'minContentLength',
          title: 'Minimum Content Length',
          type: 'object',
          fields: [
            {
              name: 'facebook',
              title: 'Facebook (characters)',
              type: 'number',
              initialValue: 100
            },
            {
              name: 'instagram',
              title: 'Instagram (characters)',
              type: 'number',
              initialValue: 125
            },
            {
              name: 'blog',
              title: 'Blog (words)',
              type: 'number',
              initialValue: 300
            }
          ]
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
      active: 'active'
    },
    prepare(selection) {
      const { title, active } = selection
      return {
        title: title,
        subtitle: active ? 'Active Strategy' : 'Inactive',
        media: () => active ? '✅' : '⏸️'
      }
    }
  }
}