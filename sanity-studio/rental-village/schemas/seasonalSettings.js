export default {
  name: 'seasonalSettings',
  title: 'Seasonal Content Settings',
  type: 'document',
  icon: () => '🌦️',
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
      description: 'Only one seasonal setting can be active at a time',
      initialValue: true
    },
    {
      name: 'currentSeason',
      title: 'Current Season',
      type: 'string',
      options: {
        list: [
          { title: 'Spring', value: 'spring' },
          { title: 'Summer', value: 'summer' },
          { title: 'Fall', value: 'fall' },
          { title: 'Winter', value: 'winter' }
        ]
      },
      validation: Rule => Rule.required()
    },
    {
      name: 'seasonalKeywords',
      title: 'Seasonal Keywords',
      type: 'object',
      description: 'Keywords associated with each season for content matching',
      fields: [
        {
          name: 'spring',
          title: 'Spring Keywords',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['spring', 'landscaping', 'gardening', 'planting', 'cleanup', 'preparation']
        },
        {
          name: 'summer',
          title: 'Summer Keywords',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['summer', 'construction', 'outdoor', 'hot weather', 'irrigation', 'maintenance']
        },
        {
          name: 'fall',
          title: 'Fall Keywords',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['fall', 'autumn', 'harvest', 'leaf removal', 'preparation', 'winterizing']
        },
        {
          name: 'winter',
          title: 'Winter Keywords',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['winter', 'snow', 'cold', 'ice', 'heating', 'indoor projects']
        }
      ]
    },
    {
      name: 'seasonalEquipmentPriority',
      title: 'Seasonal Equipment Priority',
      type: 'object',
      description: 'Equipment categories to prioritize for each season',
      fields: [
        {
          name: 'spring',
          title: 'Spring Equipment',
          type: 'array',
          of: [{ type: 'string' }],
          options: {
            list: [
              { title: 'Landscaping', value: 'landscaping' },
              { title: 'Excavation', value: 'excavation' },
              { title: 'Lawn Care', value: 'lawn-care' },
              { title: 'Compaction', value: 'compaction' },
              { title: 'Material Handling', value: 'material-handling' }
            ]
          }
        },
        {
          name: 'summer',
          title: 'Summer Equipment',
          type: 'array',
          of: [{ type: 'string' }],
          options: {
            list: [
              { title: 'Construction', value: 'construction' },
              { title: 'Concrete', value: 'concrete' },
              { title: 'Demolition', value: 'demolition' },
              { title: 'Pumps', value: 'pumps' },
              { title: 'Generators', value: 'generators' }
            ]
          }
        },
        {
          name: 'fall',
          title: 'Fall Equipment',
          type: 'array',
          of: [{ type: 'string' }],
          options: {
            list: [
              { title: 'Leaf Blowers', value: 'leaf-blowers' },
              { title: 'Chippers', value: 'chippers' },
              { title: 'Excavation', value: 'excavation' },
              { title: 'Landscaping', value: 'landscaping' },
              { title: 'Cleanup', value: 'cleanup' }
            ]
          }
        },
        {
          name: 'winter',
          title: 'Winter Equipment',
          type: 'array',
          of: [{ type: 'string' }],
          options: {
            list: [
              { title: 'Snow Removal', value: 'snow-removal' },
              { title: 'Heaters', value: 'heaters' },
              { title: 'Indoor Tools', value: 'indoor-tools' },
              { title: 'Pumps', value: 'pumps' },
              { title: 'Generators', value: 'generators' }
            ]
          }
        }
      ]
    },
    {
      name: 'seasonalContentThemes',
      title: 'Seasonal Content Themes',
      type: 'object',
      description: 'Content themes and messaging for each season',
      fields: [
        {
          name: 'spring',
          title: 'Spring Themes',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['Spring Preparation', 'Landscaping Projects', 'Clean-up Time', 'Garden Ready']
        },
        {
          name: 'summer',
          title: 'Summer Themes',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['Summer Projects', 'Beat the Heat', 'Outdoor Work', 'Construction Season']
        },
        {
          name: 'fall',
          title: 'Fall Themes',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['Fall Cleanup', 'Harvest Time', 'Winter Prep', 'Leaf Season']
        },
        {
          name: 'winter',
          title: 'Winter Themes',
          type: 'array',
          of: [{ type: 'string' }],
          initialValue: ['Winter Solutions', 'Snow Management', 'Indoor Projects', 'Cold Weather Tools']
        }
      ]
    },
    {
      name: 'seasonalBoosts',
      title: 'Seasonal Content Boosts',
      type: 'object',
      description: 'Multipliers for seasonal content priority',
      fields: [
        {
          name: 'currentSeasonBoost',
          title: 'Current Season Boost',
          type: 'number',
          description: 'Multiplier for current season content',
          validation: Rule => Rule.min(1).max(5),
          initialValue: 2.0
        },
        {
          name: 'upcomingSeasonBoost',
          title: 'Upcoming Season Boost',
          type: 'number',
          description: 'Multiplier for upcoming season content',
          validation: Rule => Rule.min(1).max(5),
          initialValue: 1.5
        },
        {
          name: 'offSeasonPenalty',
          title: 'Off-Season Penalty',
          type: 'number',
          description: 'Multiplier for off-season content (should be < 1)',
          validation: Rule => Rule.min(0.1).max(1),
          initialValue: 0.3
        }
      ]
    },
    {
      name: 'weatherConsiderations',
      title: 'Weather Considerations',
      type: 'object',
      fields: [
        {
          name: 'temperatureRanges',
          title: 'Temperature Ranges',
          type: 'object',
          fields: [
            {
              name: 'spring',
              title: 'Spring (°F)',
              type: 'object',
              fields: [
                { name: 'min', title: 'Min', type: 'number', initialValue: 45 },
                { name: 'max', title: 'Max', type: 'number', initialValue: 75 }
              ]
            },
            {
              name: 'summer',
              title: 'Summer (°F)',
              type: 'object',
              fields: [
                { name: 'min', title: 'Min', type: 'number', initialValue: 70 },
                { name: 'max', title: 'Max', type: 'number', initialValue: 95 }
              ]
            },
            {
              name: 'fall',
              title: 'Fall (°F)',
              type: 'object',
              fields: [
                { name: 'min', title: 'Min', type: 'number', initialValue: 40 },
                { name: 'max', title: 'Max', type: 'number', initialValue: 70 }
              ]
            },
            {
              name: 'winter',
              title: 'Winter (°F)',
              type: 'object',
              fields: [
                { name: 'min', title: 'Min', type: 'number', initialValue: 20 },
                { name: 'max', title: 'Max', type: 'number', initialValue: 50 }
              ]
            }
          ]
        },
        {
          name: 'equipmentTemperatureRatings',
          title: 'Equipment Temperature Ratings',
          type: 'boolean',
          description: 'Consider equipment temperature ratings when selecting',
          initialValue: true
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
      season: 'currentSeason'
    },
    prepare(selection) {
      const { title, active, season } = selection
      const seasonEmoji = {
        spring: '🌱',
        summer: '☀️',
        fall: '🍂',
        winter: '❄️'
      }
      return {
        title: title,
        subtitle: `${active ? 'Active' : 'Inactive'} - Current: ${season}`,
        media: () => seasonEmoji[season] || '🌦️'
      }
    }
  }
}